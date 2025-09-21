import os
import json
import logging
import traceback
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import select
from datetime import datetime

from config import CORS_ORIGINS, UPLOAD_DIR, PROCESSED_DIR
from database import init_db, get_session, engine
from models import Meeting, TranscriptSegment, Summary, Tag
from schemas import UploadResponse, ProcessRequest, SegmentOut, SummaryOut, MeetingOut, SearchHit

from utils_audio import extract_audio_to_wav
from services.transcription import transcribe_with_whisper_cpp
from services.diarization import assign_speakers
from services.sentiment import score_sentiment
from services.llm import summarize_and_extract
from services.topics import simple_keywords, build_topic_graph
from services.vector_store import upsert_meeting_segments, search as vector_search

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    init_db()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("Application started")

    yield
    # Shutdown (if needed)

app = FastAPI(title="Post-Meeting Analysis POC", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5176", "http://127.0.0.1:5176", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload", response_model=UploadResponse)
def upload_meeting(file: UploadFile = File(...)):
    # Save upload
    fname = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    dest = os.path.join(UPLOAD_DIR, fname)
    with open(dest, "wb") as f:
        f.write(file.file.read())
    # Create DB entry
    with get_session() as s:
        m = Meeting(title=os.path.splitext(file.filename)[0], filename=fname)
        s.add(m); s.commit(); s.refresh(m)
    return UploadResponse(meeting_id=m.id, filename=fname)

@app.post("/meetings/{meeting_id}/process")
def process_meeting(meeting_id: int, req: ProcessRequest, bg: BackgroundTasks):
    with get_session() as s:
        m = s.get(Meeting, meeting_id)
        if not m:
            raise HTTPException(status_code=404, detail="Meeting not found")

        if m.status == "processing":
            return {"status": "already processing", "meeting_id": meeting_id}

        if m.status == "completed" and not req.force:
            return {"status": "already completed", "meeting_id": meeting_id}

    # Kick off background processing
    bg.add_task(_process_pipeline, meeting_id)
    return {"status": "processing started", "meeting_id": meeting_id}

@app.get("/meetings/{meeting_id}/status")
def get_processing_status(meeting_id: int):
    with get_session() as s:
        m = s.get(Meeting, meeting_id)
        if not m:
            raise HTTPException(status_code=404, detail="Meeting not found")

        return {
            "meeting_id": meeting_id,
            "status": m.status,
            "error_message": m.error_message
        }

def _process_pipeline(meeting_id: int):
    logger = logging.getLogger(__name__)
    logger.info(f"Starting processing for meeting {meeting_id}")

    try:
        with get_session() as s:
            m = s.get(Meeting, meeting_id)
            if not m:
                logger.error(f"Meeting {meeting_id} not found")
                return

            # Update status to processing
            m.status = "processing"
            m.error_message = None
            s.add(m)
            s.commit()
            logger.info(f"Set meeting {meeting_id} status to processing")

            input_path = os.path.join(UPLOAD_DIR, m.filename)
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Upload file not found: {input_path}")

            logger.info(f"Extracting audio from {input_path}")
            wav_path, duration = extract_audio_to_wav(input_path, PROCESSED_DIR, target_sr=16000)
            m.duration_sec = duration
            s.add(m)
            s.commit()
            logger.info(f"Audio extracted, duration: {duration}s")

            # Transcribe
            logger.info("Starting transcription...")
            segs = transcribe_with_whisper_cpp(wav_path, PROCESSED_DIR)
            logger.info(f"Transcription completed, {len(segs)} segments")

            if not segs:
                raise ValueError("No transcript segments generated")

            # Diarize (assign speakers) & Sentiment
            logger.info("Assigning speakers...")
            speakers = assign_speakers(wav_path, segs, max_speakers=3)
            logger.info("Scoring sentiment...")
            sentiments = score_sentiment(segs)

            # Persist segments
            logger.info("Persisting segments to database...")
            db_segments = []
            for i, (seg, spk, sent) in enumerate(zip(segs, speakers, sentiments)):
                dbs = TranscriptSegment(
                    meeting_id=m.id, start=seg['start'], end=seg['end'],
                    text=seg['text'], speaker=spk, sentiment=sent
                )
                s.add(dbs)
                db_segments.append(dbs)
            s.commit()
            for dbs in db_segments:
                s.refresh(dbs)
            logger.info(f"Persisted {len(db_segments)} segments")

            # Summary via LLM
            logger.info("Generating summary...")
            full_transcript = "\n".join([f"[{dbs.start:.1f}-{dbs.end:.1f}] {dbs.speaker}: {dbs.text}" for dbs in db_segments])
            summary_obj = summarize_and_extract(full_transcript)

            summary_row = Summary(
                meeting_id=m.id,
                overview=summary_obj.get("overview",""),
                key_topics=json.dumps(summary_obj.get("key_topics", [])),
                decisions=json.dumps(summary_obj.get("decisions", [])),
                action_items=json.dumps(summary_obj.get("action_items", [])),
                risks=json.dumps(summary_obj.get("risks", [])),
                vibe=summary_obj.get("vibe", "neutral"),
            )
            s.add(summary_row)

            # Tags (topics)
            logger.info("Extracting topics...")
            topics = summary_obj.get("key_topics", []) or simple_keywords(full_transcript, top_k=8)
            for t in topics:
                s.add(Tag(meeting_id=m.id, name=str(t)[:64]))
            s.commit()

            # Upsert vectors
            logger.info("Creating vector embeddings...")
            upsert_meeting_segments(
                meeting_id=m.id,
                meeting_title=m.title,
                segments=[(seg.id, seg.text) for seg in db_segments]
            )

            # Mark as completed
            m.status = "completed"
            s.add(m)
            s.commit()
            logger.info(f"Processing completed successfully for meeting {meeting_id}")

    except Exception as e:
        logger.error(f"Processing failed for meeting {meeting_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        try:
            with get_session() as s:
                m = s.get(Meeting, meeting_id)
                if m:
                    m.status = "failed"
                    m.error_message = str(e)
                    s.add(m)
                    s.commit()
        except Exception as db_e:
            logger.error(f"Failed to update meeting status: {str(db_e)}")

@app.get("/meetings", response_model=List[MeetingOut])
def list_meetings():
    with get_session() as s:
        ms = s.exec(select(Meeting)).all()
        out = []
        for m in ms:
            tags = [t.name for t in s.exec(select(Tag).where(Tag.meeting_id==m.id)).all()]
            summ = s.exec(select(Summary).where(Summary.meeting_id==m.id)).first()
            summ_out = None
            if summ:
                summ_out = SummaryOut(
                    overview=summ.overview,
                    key_topics=json.loads(summ.key_topics or "[]"),
                    decisions=json.loads(summ.decisions or "[]"),
                    action_items=json.loads(summ.action_items or "[]"),
                    risks=json.loads(summ.risks or "[]") if summ.risks else [],
                    vibe=summ.vibe
                )
            out.append(MeetingOut(
                id=m.id, title=m.title, filename=m.filename, duration_sec=m.duration_sec,
                created_at=m.created_at.isoformat(), tags=tags, summary=summ_out,
                status=m.status, error_message=m.error_message
            ))
        return out

@app.get("/meetings/{meeting_id}/segments", response_model=List[SegmentOut])
def get_segments(meeting_id: int):
    with get_session() as s:
        segs = s.exec(select(TranscriptSegment).where(TranscriptSegment.meeting_id==meeting_id)).all()
        return [SegmentOut(
            id=x.id, start=x.start, end=x.end, text=x.text, speaker=x.speaker or "SPEAKER", sentiment=x.sentiment or 0.0
        ) for x in segs]

@app.get("/meetings/{meeting_id}/summary", response_model=SummaryOut | None)
def get_summary(meeting_id: int):
    with get_session() as s:
        summ = s.exec(select(Summary).where(Summary.meeting_id==meeting_id)).first()
        if not summ:
            return None
        return SummaryOut(
            overview=summ.overview,
            key_topics=json.loads(summ.key_topics or "[]"),
            decisions=json.loads(summ.decisions or "[]"),
            action_items=json.loads(summ.action_items or "[]"),
            risks=json.loads(summ.risks or "[]") if summ.risks else [],
            vibe=summ.vibe
        )

@app.get("/search", response_model=List[SearchHit])
def search(q: str, top_k: int = 8):
    hits = vector_search(q, top_k=top_k)
    # augment with timing info
    with get_session() as s:
        out = []
        for h in hits:
            seg = s.get(TranscriptSegment, h["segment_id"])
            if not seg:
                continue
            out.append(SearchHit(
                meeting_id=h["meeting_id"],
                meeting_title=h["meeting_title"],
                segment_id=h["segment_id"],
                start=seg.start,
                end=seg.end,
                text=h["text"],
                score=h["score"]
            ))
        return out

@app.get("/meetings/{meeting_id}/graph")
def graph(meeting_id: int):
    with get_session() as s:
        segs = s.exec(select(TranscriptSegment).where(TranscriptSegment.meeting_id==meeting_id)).all()
        summ = s.exec(select(Summary).where(Summary.meeting_id==meeting_id)).first()
        topics = json.loads(summ.key_topics or "[]") if summ else []
        seg_texts = [x.text for x in segs]
        g = build_topic_graph(topics, seg_texts)
        return g

@app.get("/debug/config")
def debug_config():
    """Debug endpoint to check configuration"""
    from config import WHISPER_MODEL, OLLAMA_BASE, OLLAMA_MODEL, UPLOAD_DIR, PROCESSED_DIR
    import whisper

    # Check if whisper models are available
    try:
        available_models = whisper.available_models()
        whisper_model_available = WHISPER_MODEL in available_models
    except Exception:
        available_models = []
        whisper_model_available = False

    return {
        "whisper_model": WHISPER_MODEL,
        "whisper_model_available": whisper_model_available,
        "available_whisper_models": list(available_models),
        "ollama_base": OLLAMA_BASE,
        "ollama_model": OLLAMA_MODEL,
        "upload_dir": UPLOAD_DIR,
        "upload_dir_exists": os.path.exists(UPLOAD_DIR),
        "processed_dir": PROCESSED_DIR,
        "processed_dir_exists": os.path.exists(PROCESSED_DIR)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
