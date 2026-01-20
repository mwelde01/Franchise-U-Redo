from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


# Podcast Schemas
class PodcastBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    author: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = None


class PodcastCreate(PodcastBase):
    pass


class PodcastUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    author: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = None


class PodcastResponse(PodcastBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    episode_count: Optional[int] = 0

    class Config:
        orm_mode = True


# Tag Schemas
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class TagCreate(TagBase):
    is_preset: bool = False


class TagResponse(TagBase):
    id: int
    is_preset: bool
    usage_count: int
    created_at: datetime

    class Config:
        orm_mode = True


# Transcript Segment Schemas
class TranscriptSegmentBase(BaseModel):
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., ge=0)
    text: str = Field(..., min_length=1)
    speaker: Optional[str] = None
    sequence_number: int = Field(..., ge=0)
    confidence: Optional[float] = Field(None, ge=0, le=1)

    @validator('end_time')
    def end_time_after_start(cls, v, values):
        if 'start_time' in values and v < values['start_time']:
            raise ValueError('end_time must be >= start_time')
        return v


class TranscriptSegmentCreate(TranscriptSegmentBase):
    pass


class TranscriptSegmentResponse(TranscriptSegmentBase):
    id: int
    episode_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Episode Schemas
class EpisodeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    episode_number: Optional[int] = Field(None, ge=1)
    season_number: Optional[int] = Field(None, ge=1)
    publish_date: Optional[datetime] = None


class EpisodeCreate(EpisodeBase):
    podcast_id: int
    tag_names: Optional[List[str]] = []


class EpisodeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    episode_number: Optional[int] = Field(None, ge=1)
    season_number: Optional[int] = Field(None, ge=1)
    publish_date: Optional[datetime] = None
    tag_names: Optional[List[str]] = None


class EpisodeResponse(EpisodeBase):
    id: int
    podcast_id: int
    audio_file_path: str
    audio_file_size: Optional[int]
    duration: Optional[float]
    audio_format: Optional[str]
    summary: Optional[str]
    summary_generated_at: Optional[datetime]
    is_processed: bool
    processing_error: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    tags: List[TagResponse] = []
    podcast_name: Optional[str] = None

    class Config:
        orm_mode = True


class EpisodeDetailResponse(EpisodeResponse):
    """Extended response with transcript segments"""
    transcript_segments: List[TranscriptSegmentResponse] = []

    class Config:
        orm_mode = True


# Upload Schemas
class TranscriptUpload(BaseModel):
    """Schema for uploading transcript data"""
    segments: List[TranscriptSegmentCreate]


class EpisodeUploadResponse(BaseModel):
    """Response after uploading an episode"""
    episode_id: int
    message: str
    audio_uploaded: bool
    transcript_uploaded: bool
    processing_started: bool


# Search Schemas
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    podcast_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None
    limit: int = Field(50, ge=1, le=200)


class TranscriptSearchResult(BaseModel):
    episode_id: int
    episode_title: str
    podcast_name: str
    segment_id: int
    start_time: float
    end_time: float
    text: str
    speaker: Optional[str]


class SearchResponse(BaseModel):
    results: List[TranscriptSearchResult]
    total_count: int


# Theme Discovery Schema
class ThemeDiscoveryResponse(BaseModel):
    discovered_tags: List[str]
    common_themes: List[dict]
    tag_relationships: dict


# Summary Request Schema
class SummaryRequest(BaseModel):
    episode_id: int
    regenerate: bool = False


class SummaryResponse(BaseModel):
    episode_id: int
    summary: str
    tags: List[str]
    generated_at: datetime
