"""API routes for search and theme discovery"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Episode
from app.schemas import SearchRequest, SearchResponse, ThemeDiscoveryResponse
from app.services.transcript_service import TranscriptService
from app.services.ai_service import AIService

router = APIRouter(prefix="/search", tags=["search"])
transcript_service = TranscriptService()
ai_service = AIService()


@router.post("/transcripts", response_model=SearchResponse)
def search_transcripts(
    search: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search through transcript content

    Find specific moments in podcast episodes by searching transcript text.
    Returns segments with timestamps that match the search query.
    """
    results, total_count = transcript_service.search_transcripts(
        db=db,
        query=search.query,
        podcast_ids=search.podcast_ids,
        tag_ids=search.tag_ids,
        limit=search.limit
    )

    return SearchResponse(
        results=results,
        total_count=total_count
    )


@router.get("/keywords")
def search_by_keywords(
    keywords: str,  # Comma-separated list
    episode_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Search for transcript segments containing specific keywords

    Args:
        keywords: Comma-separated list of keywords
        episode_id: Optional episode ID to limit search
        limit: Maximum results to return
    """
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]

    if not keyword_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one keyword is required"
        )

    segments = transcript_service.find_by_keywords(
        db=db,
        keywords=keyword_list,
        episode_id=episode_id,
        limit=limit
    )

    # Format response
    from app.schemas import TranscriptSearchResult
    results = []
    for segment in segments:
        results.append(TranscriptSearchResult(
            episode_id=segment.episode_id,
            episode_title=segment.episode.title,
            podcast_name=segment.episode.podcast.name,
            segment_id=segment.id,
            start_time=segment.start_time,
            end_time=segment.end_time,
            text=segment.text,
            speaker=segment.speaker
        ))

    return {
        "results": results,
        "total_count": len(results),
        "keywords": keyword_list
    }


@router.get("/segment/{segment_id}/context")
def get_segment_context(
    segment_id: int,
    context_seconds: float = 30.0,
    db: Session = Depends(get_db)
):
    """
    Get context around a specific transcript segment

    Useful for understanding the conversation around a search result.

    Args:
        segment_id: ID of the target segment
        context_seconds: Seconds of context before and after (default: 30)
    """
    segments = transcript_service.get_context_around_segment(
        db=db,
        segment_id=segment_id,
        context_seconds=context_seconds
    )

    if not segments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Segment with id {segment_id} not found"
        )

    from app.schemas import TranscriptSegmentResponse
    return {
        "target_segment_id": segment_id,
        "context_seconds": context_seconds,
        "segments": [TranscriptSegmentResponse.model_validate(s) for s in segments]
    }


@router.get("/episodes")
def search_episodes(
    query: str,
    podcast_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Search episodes by title, description, or summary

    Args:
        query: Search query
        podcast_id: Optional podcast ID filter
        skip: Number of results to skip
        limit: Maximum results to return
    """
    from app.models import Podcast
    from sqlalchemy import or_

    q = db.query(Episode).join(Podcast)

    # Apply podcast filter
    if podcast_id:
        q = q.filter(Episode.podcast_id == podcast_id)

    # Search in multiple fields
    search_pattern = f"%{query}%"
    q = q.filter(
        or_(
            Episode.title.ilike(search_pattern),
            Episode.description.ilike(search_pattern),
            Episode.summary.ilike(search_pattern),
            Podcast.name.ilike(search_pattern)
        )
    )

    total_count = q.count()
    episodes = q.order_by(Episode.created_at.desc()).offset(skip).limit(limit).all()

    from app.schemas import EpisodeResponse
    response_episodes = []
    for episode in episodes:
        ep_response = EpisodeResponse.model_validate(episode)
        ep_response.podcast_name = episode.podcast.name
        response_episodes.append(ep_response)

    return {
        "results": response_episodes,
        "total_count": total_count,
        "query": query
    }


@router.post("/discover-themes", response_model=ThemeDiscoveryResponse)
async def discover_themes(
    podcast_ids: Optional[List[int]] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Discover common themes across podcast episodes using AI

    Analyzes multiple episodes to find:
    - Common themes across episodes
    - Tag relationships (which tags appear together)
    - Emerging topics
    - Suggestions for new tags

    Args:
        podcast_ids: Optional list of podcast IDs to analyze (default: all)
        limit: Maximum number of episodes to analyze (default: 20, max: 50)
    """
    if limit > 50:
        limit = 50

    # Get episodes
    query = db.query(Episode).filter(Episode.summary.isnot(None))

    if podcast_ids:
        query = query.filter(Episode.podcast_id.in_(podcast_ids))

    episodes = query.order_by(Episode.created_at.desc()).limit(limit).all()

    if not episodes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No episodes with summaries found for analysis"
        )

    # Discover themes using AI
    try:
        result = await ai_service.discover_themes(episodes, db)

        return ThemeDiscoveryResponse(
            discovered_tags=result.get('new_tag_suggestions', []),
            common_themes=result.get('common_themes', []),
            tag_relationships=result.get('tag_relationships', {})
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Theme discovery failed: {str(e)}"
        )


@router.get("/related-episodes/{episode_id}")
def find_related_episodes(
    episode_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Find episodes related to a specific episode based on shared tags

    Args:
        episode_id: Target episode ID
        limit: Maximum number of related episodes to return
    """
    # Get target episode
    target_episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not target_episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode with id {episode_id} not found"
        )

    if not target_episode.tags:
        return {
            "episode_id": episode_id,
            "related_episodes": [],
            "message": "No tags available for finding related episodes"
        }

    # Get tag IDs from target episode
    tag_ids = [tag.id for tag in target_episode.tags]

    # Find episodes with overlapping tags
    from app.models import episode_tags
    from sqlalchemy import func

    related_episodes = db.query(
        Episode,
        func.count(episode_tags.c.tag_id).label('shared_tags')
    ).join(
        episode_tags,
        Episode.id == episode_tags.c.episode_id
    ).filter(
        episode_tags.c.tag_id.in_(tag_ids),
        Episode.id != episode_id  # Exclude the target episode itself
    ).group_by(
        Episode.id
    ).order_by(
        func.count(episode_tags.c.tag_id).desc(),
        Episode.created_at.desc()
    ).limit(limit).all()

    # Format response
    from app.schemas import EpisodeResponse
    results = []
    for episode, shared_count in related_episodes:
        ep_response = EpisodeResponse.model_validate(episode)
        ep_response.podcast_name = episode.podcast.name
        results.append({
            "episode": ep_response,
            "shared_tags_count": shared_count
        })

    return {
        "episode_id": episode_id,
        "target_episode_title": target_episode.title,
        "related_episodes": results,
        "total_found": len(results)
    }
