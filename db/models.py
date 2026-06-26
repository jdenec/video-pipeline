"""
Video Pipeline — Database Models

This file defines what a "job" looks like in our database.
Every video that enters the pipeline gets one row in this table.

SQLAlchemy turns these Python classes into database tables automatically.
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime
from db.database import Base


class JobStatus(str, enum.Enum):
    """
    Every job moves through these states in order.
    The worker checks the current status to know what to do next.
    
    QUEUED      → Waiting for the worker to pick it up
    TRANSCRIBING  → faster-whisper is running
    GENERATING_METADATA → OpenAI is generating title/description/thumbnail
    EDITING     → moviepy/ffmpeg is editing the video
    READY_FOR_REVIEW → Waiting for you to approve on the dashboard
    APPROVED    → You clicked approve (triggers publishing)
    PUBLISHING  → Uploading to YouTube/X/Threads
    COMPLETE    → All done
    FAILED      → Something went wrong (error_message has details)
    """
    QUEUED = "QUEUED"
    TRANSCRIBING = "TRANSCRIBING"
    GENERATING_METADATA = "GENERATING_METADATA"
    EDITING = "EDITING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    APPROVED = "APPROVED"
    PUBLISHING = "PUBLISHING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class Job(Base):
    """
    A single video processing job.
    
    Each column is a piece of data we track:
    - id: unique number (auto-incremented)
    - filename: the original video file name
    - status: where in the pipeline this job is
    - created_at: when the job was created (auto-set)
    - original_path: full path to the source video
    - edited_video_path: path to the finished video
    - transcript: the text transcription
    - title: YouTube title (from GPT)
    - description: YouTube description (from GPT)
    - tags: comma-separated tags (from GPT)
    - thumbnail_path: path to the generated thumbnail image
    - error_message: if FAILED, why
    """

    __tablename__ = "jobs"

    # Primary key — every row needs a unique ID
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # File info
    filename = Column(String(500), nullable=False)
    original_path = Column(String(1000), nullable=True)
    edited_video_path = Column(String(1000), nullable=True)
    
    # Pipeline state
    status = Column(Enum(JobStatus), default=JobStatus.QUEUED, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    
    # Generated metadata
    transcript = Column(Text, nullable=True)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)
    thumbnail_path = Column(String(1000), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        """How this job looks when printed — useful for debugging."""
        return f"<Job {self.id}: {self.filename} [{self.status.value}]>"