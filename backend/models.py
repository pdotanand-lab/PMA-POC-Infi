from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class Meeting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    filename: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    duration_sec: Optional[float] = None
    status: str = Field(default="uploaded")  # uploaded, processing, completed, failed
    error_message: Optional[str] = None

    segments: List["TranscriptSegment"] = Relationship(back_populates="meeting")
    summary: Optional["Summary"] = Relationship(back_populates="meeting")
    tags: List["Tag"] = Relationship(back_populates="meeting")

class TranscriptSegment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    meeting_id: int = Field(foreign_key="meeting.id")
    start: float = 0.0
    end: float = 0.0
    text: str
    speaker: Optional[str] = None
    sentiment: Optional[float] = None

    meeting: Optional[Meeting] = Relationship(back_populates="segments")

class Summary(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    meeting_id: int = Field(foreign_key="meeting.id", unique=True)
    overview: str
    key_topics: str  # JSON string list
    decisions: str   # JSON string list
    action_items: str  # JSON string list
    risks: Optional[str] = None  # JSON string list
    vibe: Optional[str] = None

    meeting: Optional[Meeting] = Relationship(back_populates="summary")

class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    meeting_id: int = Field(foreign_key="meeting.id")
    name: str

    meeting: Optional[Meeting] = Relationship(back_populates="tags")
