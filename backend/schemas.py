from typing import List, Optional
from pydantic import BaseModel

class UploadResponse(BaseModel):
    meeting_id: int
    filename: str

class ProcessRequest(BaseModel):
    force: bool = False

class SegmentOut(BaseModel):
    id: int
    start: float
    end: float
    text: str
    speaker: str
    sentiment: float

class SummaryOut(BaseModel):
    overview: str
    key_topics: List[str]
    decisions: List[str]
    action_items: List[str]
    risks: List[str] | None = None
    vibe: str | None = None

class MeetingOut(BaseModel):
    id: int
    title: str
    filename: str
    duration_sec: float | None = None
    created_at: str
    tags: List[str]
    summary: SummaryOut | None = None
    status: str
    error_message: str | None = None

class SearchHit(BaseModel):
    meeting_id: int
    meeting_title: str
    segment_id: int
    start: float
    end: float
    text: str
    score: float
