from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import datetime


# Association table for many-to-many relationship between episodes and tags
episode_tags = Table(
    'episode_tags',
    Base.metadata,
    Column('episode_id', Integer, ForeignKey('episodes.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


class Podcast(Base):
    """Represents a podcast show"""
    __tablename__ = 'podcasts'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    website = Column(String(512), nullable=True)
    image_url = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    episodes = relationship("Episode", back_populates="podcast", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Podcast(id={self.id}, name='{self.name}')>"


class Episode(Base):
    """Represents a podcast episode"""
    __tablename__ = 'episodes'

    id = Column(Integer, primary_key=True, index=True)
    podcast_id = Column(Integer, ForeignKey('podcasts.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Audio file information
    audio_file_path = Column(String(1024), nullable=False)
    audio_file_size = Column(Integer, nullable=True)  # in bytes
    duration = Column(Float, nullable=True)  # in seconds
    audio_format = Column(String(50), nullable=True)  # mp3, wav, etc.

    # Episode metadata
    episode_number = Column(Integer, nullable=True)
    season_number = Column(Integer, nullable=True)
    publish_date = Column(DateTime(timezone=True), nullable=True)

    # AI-generated content
    summary = Column(Text, nullable=True)
    summary_generated_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)

    # Relationships
    podcast = relationship("Podcast", back_populates="episodes")
    transcript_segments = relationship("TranscriptSegment", back_populates="episode", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=episode_tags, back_populates="episodes")

    def __repr__(self):
        return f"<Episode(id={self.id}, title='{self.title}')>"


class Tag(Base):
    """Represents a tag or theme"""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_preset = Column(Boolean, default=False)  # True if from preset list, False if AI-discovered
    usage_count = Column(Integer, default=0)  # Number of episodes with this tag
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    episodes = relationship("Episode", secondary=episode_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', preset={self.is_preset})>"


class TranscriptSegment(Base):
    """Represents a segment of transcript with timestamp"""
    __tablename__ = 'transcript_segments'

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey('episodes.id', ondelete='CASCADE'), nullable=False)

    # Timing information
    start_time = Column(Float, nullable=False)  # in seconds
    end_time = Column(Float, nullable=False)  # in seconds

    # Content
    text = Column(Text, nullable=False)
    speaker = Column(String(255), nullable=True)  # Speaker name if available

    # Metadata
    sequence_number = Column(Integer, nullable=False)  # Order in transcript
    confidence = Column(Float, nullable=True)  # Transcription confidence score if available

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    episode = relationship("Episode", back_populates="transcript_segments")

    def __repr__(self):
        return f"<TranscriptSegment(id={self.id}, episode_id={self.episode_id}, time={self.start_time}-{self.end_time})>"


# Indexes for common queries
from sqlalchemy import Index

# Index for searching transcript text
Index('idx_transcript_text', TranscriptSegment.text, postgresql_using='gin', postgresql_ops={'text': 'gin_trgm_ops'})

# Index for time-based queries
Index('idx_transcript_time', TranscriptSegment.episode_id, TranscriptSegment.start_time)

# Index for episode queries
Index('idx_episode_podcast', Episode.podcast_id, Episode.created_at)
