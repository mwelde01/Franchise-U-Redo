"""API routes for tag management"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Tag, Episode, episode_tags
from app.schemas import TagCreate, TagResponse

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[TagResponse])
def list_tags(
    skip: int = 0,
    limit: int = 200,
    preset_only: bool = False,
    sort_by: str = "usage",  # usage, name, date
    db: Session = Depends(get_db)
):
    """
    List all tags

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        preset_only: If True, only return preset tags
        sort_by: Sort order (usage, name, date)
    """
    query = db.query(Tag)

    if preset_only:
        query = query.filter(Tag.is_preset == True)

    # Apply sorting
    if sort_by == "usage":
        query = query.order_by(Tag.usage_count.desc())
    elif sort_by == "name":
        query = query.order_by(Tag.name)
    else:  # date
        query = query.order_by(Tag.created_at.desc())

    tags = query.offset(skip).limit(limit).all()
    return tags


@router.get("/preset", response_model=List[TagResponse])
def get_preset_tags(db: Session = Depends(get_db)):
    """Get all preset tags"""
    tags = db.query(Tag).filter(Tag.is_preset == True).order_by(Tag.name).all()
    return tags


@router.get("/popular", response_model=List[TagResponse])
def get_popular_tags(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get most popular tags by usage"""
    tags = db.query(Tag).filter(
        Tag.usage_count > 0
    ).order_by(
        Tag.usage_count.desc()
    ).limit(limit).all()
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific tag by ID"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found"
        )
    return tag


@router.get("/{tag_id}/episodes")
def get_tag_episodes(
    tag_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all episodes with a specific tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found"
        )

    episodes = db.query(Episode).filter(
        Episode.id.in_(
            db.query(episode_tags.c.episode_id).filter(
                episode_tags.c.tag_id == tag_id
            )
        )
    ).order_by(Episode.created_at.desc()).offset(skip).limit(limit).all()

    from app.schemas import EpisodeResponse
    response_episodes = []
    for episode in episodes:
        ep_response = EpisodeResponse.model_validate(episode)
        ep_response.podcast_name = episode.podcast.name
        response_episodes.append(ep_response)

    return response_episodes


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db)
):
    """Create a new tag"""
    # Check if tag already exists
    existing_tag = db.query(Tag).filter(
        Tag.name == tag.name.lower()
    ).first()

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag '{tag.name}' already exists"
        )

    db_tag = Tag(
        name=tag.name.lower(),
        description=tag.description,
        is_preset=tag.is_preset,
        usage_count=0
    )
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_update: TagCreate,
    db: Session = Depends(get_db)
):
    """Update a tag"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found"
        )

    # Check if new name conflicts with existing tag
    if tag_update.name.lower() != db_tag.name:
        existing = db.query(Tag).filter(
            Tag.name == tag_update.name.lower()
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tag '{tag_update.name}' already exists"
            )

    db_tag.name = tag_update.name.lower()
    if tag_update.description is not None:
        db_tag.description = tag_update.description

    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    force: bool = False,
    db: Session = Depends(get_db)
):
    """
    Delete a tag

    Args:
        tag_id: Tag ID to delete
        force: If True, delete even if tag is in use
    """
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found"
        )

    # Check if tag is in use
    if db_tag.usage_count > 0 and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag is used by {db_tag.usage_count} episodes. Use force=true to delete anyway."
        )

    db.delete(db_tag)
    db.commit()
    return None


@router.post("/initialize-presets", response_model=dict)
def initialize_preset_tags(db: Session = Depends(get_db)):
    """Initialize preset tags from configuration"""
    from app.config import settings

    created_count = 0
    skipped_count = 0

    for tag_name in settings.preset_tags_list:
        tag_name = tag_name.lower().strip()

        # Check if already exists
        existing = db.query(Tag).filter(Tag.name == tag_name).first()
        if existing:
            # Ensure it's marked as preset
            if not existing.is_preset:
                existing.is_preset = True
                db.commit()
            skipped_count += 1
            continue

        # Create new preset tag
        tag = Tag(
            name=tag_name,
            is_preset=True,
            usage_count=0
        )
        db.add(tag)
        created_count += 1

    db.commit()

    return {
        "message": "Preset tags initialized",
        "created": created_count,
        "skipped": skipped_count,
        "total": len(settings.preset_tags_list)
    }
