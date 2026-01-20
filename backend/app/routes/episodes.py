"""API routes for episode management"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from app.database import get_db
from app.models import Episode, Podcast, Tag, TranscriptSegment, episode_tags
from app.schemas import (
    EpisodeCreate, EpisodeUpdate, EpisodeResponse, EpisodeDetailResponse,
    EpisodeUploadResponse, TranscriptSegmentCreate, TranscriptUpload
)
from app.services.audio_service import AudioService
from app.services.ai_service import AIService
from app.services.transcript_service import TranscriptService

router = APIRouter(prefix="/episodes", tags=["episodes"])
audio_service = AudioService()
ai_service = AIService()
transcript_service = TranscriptService()


async def process_episode_ai(episode_id: int, db_session_maker):
    """Background task to process episode with AI"""
    db = db_session_maker()
    try:
        episode = db.query(Episode).filter(Episode.id == episode_id).first()
        if not episode:
            return

        # Get transcript segments
        segments = db.query(TranscriptSegment).filter(
            TranscriptSegment.episode_id == episode_id
        ).order_by(TranscriptSegment.sequence_number).all()

        if not segments:
            episode.processing_error = "No transcript available for processing"
            episode.is_processed = True
            db.commit()
            return

        # Generate summary and extract tags
        try:
            summary, tag_names = await ai_service.generate_summary_and_tags(
                episode, segments, db
            )

            # Update episode
            episode.summary = summary
            episode.summary_generated_at = datetime.utcnow()

            # Add tags
            for tag_name in tag_names:
                tag_name = tag_name.lower().strip()
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    # Create new tag
                    is_preset = tag_name in [t.lower() for t in ai_service.preset_tags]
                    tag = Tag(name=tag_name, is_preset=is_preset, usage_count=0)
                    db.add(tag)
                    db.flush()

                # Associate tag with episode if not already associated
                if tag not in episode.tags:
                    episode.tags.append(tag)
                    tag.usage_count += 1

            episode.is_processed = True
            episode.processing_error = None
            db.commit()

        except Exception as e:
            episode.processing_error = f"AI processing failed: {str(e)}"
            episode.is_processed = True
            db.commit()

    finally:
        db.close()


@router.post("/upload", response_model=EpisodeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_episode(
    background_tasks: BackgroundTasks,
    podcast_id: int = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    episode_number: Optional[int] = Form(None),
    season_number: Optional[int] = Form(None),
    publish_date: Optional[str] = Form(None),
    audio_file: UploadFile = File(...),
    transcript_file: Optional[UploadFile] = File(None),
    tag_names: Optional[str] = Form(None),  # JSON array as string
    db: Session = Depends(get_db)
):
    """
    Upload a new episode with audio and optional transcript

    Args:
        podcast_id: ID of the podcast this episode belongs to
        title: Episode title
        audio_file: Audio file (mp3, wav, etc.)
        transcript_file: Optional transcript file (txt, srt, vtt)
        tag_names: Optional JSON array of tag names
    """
    # Verify podcast exists
    podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Podcast with id {podcast_id} not found"
        )

    # Parse publish date
    pub_date = None
    if publish_date:
        try:
            pub_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
        except:
            pass

    # Create episode record (without audio first)
    db_episode = Episode(
        podcast_id=podcast_id,
        title=title,
        description=description,
        episode_number=episode_number,
        season_number=season_number,
        publish_date=pub_date,
        audio_file_path="",  # Will be updated after file save
        is_processed=False
    )
    db.add(db_episode)
    db.flush()  # Get the episode ID

    try:
        # Save audio file
        file_path, file_size, duration, audio_format = await audio_service.save_audio_file(
            audio_file, podcast_id, db_episode.id
        )

        # Update episode with audio info
        db_episode.audio_file_path = file_path
        db_episode.audio_file_size = file_size
        db_episode.duration = duration
        db_episode.audio_format = audio_format

        # Process transcript if provided
        transcript_uploaded = False
        if transcript_file:
            content = await transcript_file.read()
            transcript_text = content.decode('utf-8')

            # Parse transcript
            segments_data = transcript_service.parse_transcript_file(transcript_text)

            # Create segments
            transcript_service.create_transcript_segments(
                db, db_episode.id, segments_data
            )
            transcript_uploaded = True

        # Process tags
        if tag_names:
            try:
                tags_list = json.loads(tag_names)
                for tag_name in tags_list:
                    tag_name = tag_name.lower().strip()
                    tag = db.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        is_preset = tag_name in [t.lower() for t in ai_service.preset_tags]
                        tag = Tag(name=tag_name, is_preset=is_preset, usage_count=0)
                        db.add(tag)
                        db.flush()

                    if tag not in db_episode.tags:
                        db_episode.tags.append(tag)
                        tag.usage_count += 1
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON

        db.commit()

        # Start background AI processing if transcript is available
        processing_started = False
        if transcript_uploaded:
            from app.database import SessionLocal
            background_tasks.add_task(
                process_episode_ai,
                db_episode.id,
                SessionLocal
            )
            processing_started = True

        return EpisodeUploadResponse(
            episode_id=db_episode.id,
            message="Episode uploaded successfully",
            audio_uploaded=True,
            transcript_uploaded=transcript_uploaded,
            processing_started=processing_started
        )

    except Exception as e:
        db.rollback()
        # Clean up audio file if it was saved
        if db_episode.audio_file_path:
            audio_service.delete_audio_file(db_episode.audio_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload episode: {str(e)}"
        )


@router.get("/", response_model=List[EpisodeResponse])
def list_episodes(
    skip: int = 0,
    limit: int = 100,
    podcast_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List episodes with optional filters"""
    query = db.query(Episode)

    if podcast_id:
        query = query.filter(Episode.podcast_id == podcast_id)

    if tag_id:
        query = query.filter(
            Episode.id.in_(
                db.query(episode_tags.c.episode_id).filter(
                    episode_tags.c.tag_id == tag_id
                )
            )
        )

    episodes = query.order_by(Episode.created_at.desc()).offset(skip).limit(limit).all()

    # Add podcast names
    response_episodes = []
    for episode in episodes:
        ep_response = EpisodeResponse.model_validate(episode)
        ep_response.podcast_name = episode.podcast.name
        response_episodes.append(ep_response)

    return response_episodes


@router.get("/{episode_id}", response_model=EpisodeDetailResponse)
def get_episode(
    episode_id: int,
    include_transcript: bool = True,
    db: Session = Depends(get_db)
):
    """Get episode details with optional transcript"""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode with id {episode_id} not found"
        )

    response = EpisodeDetailResponse.model_validate(episode)
    response.podcast_name = episode.podcast.name

    if include_transcript:
        segments = db.query(TranscriptSegment).filter(
            TranscriptSegment.episode_id == episode_id
        ).order_by(TranscriptSegment.sequence_number).all()
        response.transcript_segments = segments

    return response


@router.put("/{episode_id}", response_model=EpisodeResponse)
def update_episode(
    episode_id: int,
    episode_update: EpisodeUpdate,
    db: Session = Depends(get_db)
):
    """Update episode metadata"""
    db_episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not db_episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode with id {episode_id} not found"
        )

    # Update fields
    update_data = episode_update.model_dump(exclude_unset=True)

    # Handle tags separately
    tag_names = update_data.pop('tag_names', None)

    for field, value in update_data.items():
        setattr(db_episode, field, value)

    # Update tags if provided
    if tag_names is not None:
        # Clear existing tags
        for tag in db_episode.tags:
            tag.usage_count = max(0, tag.usage_count - 1)
        db_episode.tags.clear()

        # Add new tags
        for tag_name in tag_names:
            tag_name = tag_name.lower().strip()
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                is_preset = tag_name in [t.lower() for t in ai_service.preset_tags]
                tag = Tag(name=tag_name, is_preset=is_preset, usage_count=0)
                db.add(tag)
                db.flush()

            db_episode.tags.append(tag)
            tag.usage_count += 1

    db.commit()
    db.refresh(db_episode)

    response = EpisodeResponse.model_validate(db_episode)
    response.podcast_name = db_episode.podcast.name
    return response


@router.delete("/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_episode(
    episode_id: int,
    db: Session = Depends(get_db)
):
    """Delete an episode"""
    db_episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not db_episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode with id {episode_id} not found"
        )

    # Delete audio file
    audio_service.delete_audio_file(db_episode.audio_file_path)

    # Update tag usage counts
    for tag in db_episode.tags:
        tag.usage_count = max(0, tag.usage_count - 1)

    # Delete episode (cascade will delete transcript segments)
    db.delete(db_episode)
    db.commit()
    return None


@router.get("/{episode_id}/audio")
def stream_audio(
    episode_id: int,
    db: Session = Depends(get_db)
):
    """Stream episode audio file"""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode with id {episode_id} not found"
        )

    return FileResponse(
        episode.audio_file_path,
        media_type=f"audio/{episode.audio_format}",
        filename=f"{episode.title}.{episode.audio_format}"
    )


@router.post("/{episode_id}/transcript", status_code=status.HTTP_201_CREATED)
async def upload_transcript(
    episode_id: int,
    transcript: TranscriptUpload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Upload or update transcript for an episode"""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode with id {episode_id} not found"
        )

    # Delete existing transcript segments
    transcript_service.delete_segments(db, episode_id)

    # Create new segments
    transcript_service.create_transcript_segments(
        db, episode_id, transcript.segments
    )

    # Trigger AI processing in background
    from app.database import SessionLocal
    background_tasks.add_task(
        process_episode_ai,
        episode_id,
        SessionLocal
    )

    return {"message": "Transcript uploaded successfully", "processing_started": True}


@router.post("/{episode_id}/regenerate-summary")
async def regenerate_summary(
    episode_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Regenerate AI summary for an episode"""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode with id {episode_id} not found"
        )

    # Check if transcript exists
    segment_count = db.query(TranscriptSegment).filter(
        TranscriptSegment.episode_id == episode_id
    ).count()

    if segment_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate summary without transcript"
        )

    # Trigger AI processing
    from app.database import SessionLocal
    background_tasks.add_task(
        process_episode_ai,
        episode_id,
        SessionLocal
    )

    return {"message": "Summary regeneration started"}
