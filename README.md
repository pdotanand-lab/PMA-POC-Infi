# Post-Meeting Analysis POC

A full-stack proof-of-concept that ingests recorded meetings (audio/video), transcribes with **whisper.cpp**, summarizes & extracts insights via **Ollama**, stores embeddings in **ChromaDB** for semantic search, and visualizes topics on a simple graph.

## Stack
- **Backend:** FastAPI (Python), SQLite (SQLModel), ChromaDB (persistent), nltk VADER, sklearn, librosa
- **AI:** whisper.cpp (CLI), Ollama (LLM + embeddings)
- **Frontend:** React + Tailwind + Vite, recharts, react-force-graph

## Repo Structure
```
backend/
  main.py
  models.py
  schemas.py
  database.py
  config.py
  utils_audio.py
  services/
    transcription.py
    diarization.py
    sentiment.py
    llm.py
    topics.py
    vector_store.py
  requirements.txt
  .env.example
  run.sh
frontend/
  package.json
  vite.config.js
  tailwind.config.js
  postcss.config.js
  index.html
  src/
    main.jsx
    index.css
    api/api.js
    components/...
    pages/App.jsx
  .env.example
docs/
  API.md
  TECHNICAL_WRITEUP.md
```

## End-to-end Setup (Local)

1) **Install prerequisites**
- Python 3.10+
- Node 18+
- ffmpeg (on PATH)
- whisper.cpp binary + a GGUF model (e.g., `ggml-base.en.gguf`)
- Ollama running locally:
  ```bash
  ollama pull llama3.1:8b
  ollama pull nomic-embed-text
  ```

2) **Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # edit WHISPER_* and OLLAMA_* values
bash run.sh             # starts FastAPI on :8000
```

3) **Frontend**
```bash
cd frontend
npm install
cp .env.example .env    # set VITE_API_URL to http://localhost:8000
npm run dev             # opens at :5173
```

4) **Workflow**
- Upload MP4/WAV/MP3 in the UI
- The API launches a background pipeline:
  - ffmpeg -> WAV 16k mono
  - whisper.cpp -> JSON segments (start/end/text)
  - lightweight MFCC + KMeans -> speaker labels (1–3 spk)
  - VADER -> per-segment sentiment
  - Ollama (LLM) -> overview, topics, decisions, actions, risks, vibe
  - Chroma -> embeddings for semantic search
- Refresh meeting list and open the latest one

## Notes
- This is a POC: diarization uses simple clustering (no external heavy diarization model).
- For high-fidelity diarization, swap in `pyannote.audio` or `whisperX` downstream of whisper.cpp.
- All endpoints documented at `/docs` (Swagger).

