"""API routes for podcast management"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Podcast, Episode
from app.schemas import PodcastCreate, PodcastUpdate, PodcastResponse

router = APIRouter(prefix="/podcasts", tags=["podcasts"])


@router.post("/", response_model=PodcastResponse, status_code=status.HTTP_201_CREATED)
def create_podcast(
    podcast: PodcastCreate,
    db: Session = Depends(get_db)
):
    """Create a new podcast"""
    db_podcast = Podcast(**podcast.model_dump())
    db.add(db_podcast)
    db.commit()
    db.refresh(db_podcast)

    # Add episode count
    response = PodcastResponse.model_validate(db_podcast)
    response.episode_count = 0
    return response


@router.get("/", response_model=List[PodcastResponse])
def list_podcasts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all podcasts"""
    podcasts = db.query(Podcast).offset(skip).limit(limit).all()

    # Add episode counts
    response_podcasts = []
    for podcast in podcasts:
        response = PodcastResponse.model_validate(podcast)
        response.episode_count = db.query(Episode).filter(
            Episode.podcast_id == podcast.id
        ).count()
        response_podcasts.append(response)

    return response_podcasts


@router.get("/{podcast_id}", response_model=PodcastResponse)
def get_podcast(
    podcast_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific podcast by ID"""
    podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Podcast with id {podcast_id} not found"
        )

    response = PodcastResponse.model_validate(podcast)
    response.episode_count = db.query(Episode).filter(
        Episode.podcast_id == podcast.id
    ).count()
    return response


@router.put("/{podcast_id}", response_model=PodcastResponse)
def update_podcast(
    podcast_id: int,
    podcast_update: PodcastUpdate,
    db: Session = Depends(get_db)
):
    """Update a podcast"""
    db_podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not db_podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Podcast with id {podcast_id} not found"
        )

    # Update fields
    update_data = podcast_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_podcast, field, value)

    db.commit()
    db.refresh(db_podcast)

    response = PodcastResponse.model_validate(db_podcast)
    response.episode_count = db.query(Episode).filter(
        Episode.podcast_id == db_podcast.id
    ).count()
    return response


@router.delete("/{podcast_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_podcast(
    podcast_id: int,
    db: Session = Depends(get_db)
):
    """Delete a podcast and all its episodes"""
    db_podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not db_podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Podcast with id {podcast_id} not found"
        )

    db.delete(db_podcast)
    db.commit()
    return None


@router.get("/{podcast_id}/episodes", response_model=List[dict])
def get_podcast_episodes(
    podcast_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all episodes for a specific podcast"""
    podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not podcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Podcast with id {podcast_id} not found"
        )

    episodes = db.query(Episode).filter(
        Episode.podcast_id == podcast_id
    ).offset(skip).limit(limit).all()

    # Format response
    from app.schemas import EpisodeResponse
    response_episodes = []
    for episode in episodes:
        ep_response = EpisodeResponse.model_validate(episode)
        ep_response.podcast_name = podcast.name
        response_episodes.append(ep_response)

    return response_episodes
