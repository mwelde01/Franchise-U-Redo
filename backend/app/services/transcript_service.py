"""Transcript Service for processing and searching transcripts"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.models import TranscriptSegment, Episode, Podcast
from app.schemas import TranscriptSegmentCreate, TranscriptSearchResult
import re


class TranscriptService:
    """Service for transcript operations"""

    @staticmethod
    def create_transcript_segments(
        db: Session,
        episode_id: int,
        segments: List[TranscriptSegmentCreate]
    ) -> List[TranscriptSegment]:
        """
        Create transcript segments for an episode

        Args:
            db: Database session
            episode_id: Episode ID
            segments: List of transcript segments to create

        Returns:
            List of created TranscriptSegment objects
        """
        db_segments = []

        for segment_data in segments:
            db_segment = TranscriptSegment(
                episode_id=episode_id,
                start_time=segment_data.start_time,
                end_time=segment_data.end_time,
                text=segment_data.text,
                speaker=segment_data.speaker,
                sequence_number=segment_data.sequence_number,
                confidence=segment_data.confidence
            )
            db.add(db_segment)
            db_segments.append(db_segment)

        db.commit()
        return db_segments

    @staticmethod
    def get_transcript_segments(
        db: Session,
        episode_id: int,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[TranscriptSegment]:
        """
        Get transcript segments for an episode, optionally filtered by time range

        Args:
            db: Database session
            episode_id: Episode ID
            start_time: Optional start time filter
            end_time: Optional end time filter

        Returns:
            List of TranscriptSegment objects
        """
        query = db.query(TranscriptSegment).filter(
            TranscriptSegment.episode_id == episode_id
        )

        if start_time is not None:
            query = query.filter(TranscriptSegment.start_time >= start_time)
        if end_time is not None:
            query = query.filter(TranscriptSegment.end_time <= end_time)

        return query.order_by(TranscriptSegment.sequence_number).all()

    @staticmethod
    def search_transcripts(
        db: Session,
        query: str,
        podcast_ids: Optional[List[int]] = None,
        tag_ids: Optional[List[int]] = None,
        limit: int = 50
    ) -> Tuple[List[TranscriptSearchResult], int]:
        """
        Search through transcripts for matching text

        Args:
            db: Database session
            query: Search query string
            podcast_ids: Optional list of podcast IDs to filter
            tag_ids: Optional list of tag IDs to filter
            limit: Maximum number of results

        Returns:
            Tuple of (list of search results, total count)
        """
        # Build base query
        base_query = db.query(
            TranscriptSegment,
            Episode,
            Podcast
        ).join(
            Episode,
            TranscriptSegment.episode_id == Episode.id
        ).join(
            Podcast,
            Episode.podcast_id == Podcast.id
        )

        # Apply filters
        if podcast_ids:
            base_query = base_query.filter(Episode.podcast_id.in_(podcast_ids))

        if tag_ids:
            from app.models import episode_tags
            base_query = base_query.filter(
                Episode.id.in_(
                    db.query(episode_tags.c.episode_id).filter(
                        episode_tags.c.tag_id.in_(tag_ids)
                    )
                )
            )

        # Search in transcript text (case-insensitive)
        search_pattern = f"%{query}%"
        base_query = base_query.filter(
            TranscriptSegment.text.ilike(search_pattern)
        )

        # Get total count
        total_count = base_query.count()

        # Get results with limit
        results = base_query.order_by(
            Episode.created_at.desc(),
            TranscriptSegment.start_time
        ).limit(limit).all()

        # Format results
        search_results = []
        for segment, episode, podcast in results:
            search_results.append(TranscriptSearchResult(
                episode_id=episode.id,
                episode_title=episode.title,
                podcast_name=podcast.name,
                segment_id=segment.id,
                start_time=segment.start_time,
                end_time=segment.end_time,
                text=segment.text,
                speaker=segment.speaker
            ))

        return search_results, total_count

    @staticmethod
    def find_by_keywords(
        db: Session,
        keywords: List[str],
        episode_id: Optional[int] = None,
        limit: int = 50
    ) -> List[TranscriptSegment]:
        """
        Find transcript segments containing specific keywords

        Args:
            db: Database session
            keywords: List of keywords to search for
            episode_id: Optional episode ID to limit search
            limit: Maximum number of results

        Returns:
            List of matching TranscriptSegment objects
        """
        query = db.query(TranscriptSegment)

        if episode_id:
            query = query.filter(TranscriptSegment.episode_id == episode_id)

        # Build OR conditions for each keyword
        conditions = []
        for keyword in keywords:
            conditions.append(
                TranscriptSegment.text.ilike(f"%{keyword}%")
            )

        if conditions:
            query = query.filter(or_(*conditions))

        return query.order_by(
            TranscriptSegment.episode_id,
            TranscriptSegment.start_time
        ).limit(limit).all()

    @staticmethod
    def get_context_around_segment(
        db: Session,
        segment_id: int,
        context_seconds: float = 30.0
    ) -> List[TranscriptSegment]:
        """
        Get transcript segments around a specific segment (for context)

        Args:
            db: Database session
            segment_id: Target segment ID
            context_seconds: Seconds of context before and after

        Returns:
            List of TranscriptSegment objects including context
        """
        # Get the target segment
        segment = db.query(TranscriptSegment).filter(
            TranscriptSegment.id == segment_id
        ).first()

        if not segment:
            return []

        # Calculate time range
        start_time = max(0, segment.start_time - context_seconds)
        end_time = segment.end_time + context_seconds

        # Get segments in range
        return db.query(TranscriptSegment).filter(
            and_(
                TranscriptSegment.episode_id == segment.episode_id,
                TranscriptSegment.start_time >= start_time,
                TranscriptSegment.end_time <= end_time
            )
        ).order_by(TranscriptSegment.sequence_number).all()

    @staticmethod
    def get_full_transcript_text(
        db: Session,
        episode_id: int,
        include_timestamps: bool = False,
        include_speakers: bool = False
    ) -> str:
        """
        Get full transcript as formatted text

        Args:
            db: Database session
            episode_id: Episode ID
            include_timestamps: Whether to include timestamps
            include_speakers: Whether to include speaker names

        Returns:
            Formatted transcript text
        """
        segments = db.query(TranscriptSegment).filter(
            TranscriptSegment.episode_id == episode_id
        ).order_by(TranscriptSegment.sequence_number).all()

        lines = []
        for segment in segments:
            parts = []

            if include_timestamps:
                timestamp = TranscriptService._format_timestamp(segment.start_time)
                parts.append(f"[{timestamp}]")

            if include_speakers and segment.speaker:
                parts.append(f"{segment.speaker}:")

            parts.append(segment.text)

            lines.append(" ".join(parts))

        return "\n\n".join(lines)

    @staticmethod
    def parse_transcript_file(
        file_content: str,
        auto_detect_format: bool = True
    ) -> List[TranscriptSegmentCreate]:
        """
        Parse transcript file and extract segments with timestamps

        Supports formats like:
        - [00:12:34] Speaker: Text
        - [12:34] Text
        - 00:12:34 - Text
        - Plain text (generates segments every 30 seconds)

        Args:
            file_content: Content of transcript file
            auto_detect_format: Try to auto-detect timestamp format

        Returns:
            List of TranscriptSegmentCreate objects
        """
        segments = []
        lines = file_content.strip().split('\n')

        # Timestamp patterns
        timestamp_patterns = [
            r'\[(\d{1,2}):(\d{2}):(\d{2})\]',  # [HH:MM:SS]
            r'\[(\d{1,2}):(\d{2})\]',  # [MM:SS]
            r'(\d{1,2}):(\d{2}):(\d{2})',  # HH:MM:SS
            r'(\d{1,2}):(\d{2})',  # MM:SS
        ]

        sequence = 0
        current_time = 0.0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            timestamp = None
            speaker = None
            text = line

            # Try to extract timestamp
            for pattern in timestamp_patterns:
                match = re.search(pattern, line)
                if match:
                    groups = match.groups()
                    if len(groups) == 3:  # HH:MM:SS
                        timestamp = int(groups[0]) * 3600 + int(groups[1]) * 60 + int(groups[2])
                    elif len(groups) == 2:  # MM:SS
                        timestamp = int(groups[0]) * 60 + int(groups[1])

                    # Remove timestamp from text
                    text = re.sub(pattern, '', line).strip()
                    break

            # Try to extract speaker
            speaker_match = re.match(r'^([^:]+):\s*(.+)$', text)
            if speaker_match:
                speaker = speaker_match.group(1).strip()
                text = speaker_match.group(2).strip()

            # Use detected timestamp or estimate
            if timestamp is not None:
                start_time = float(timestamp)
            else:
                start_time = current_time

            # Estimate end time (will be updated by next segment or set to start + 30s)
            end_time = start_time + 30.0

            if segments:
                # Update previous segment's end time
                segments[-1].end_time = start_time

            segments.append(TranscriptSegmentCreate(
                start_time=start_time,
                end_time=end_time,
                text=text,
                speaker=speaker,
                sequence_number=sequence,
                confidence=None
            ))

            current_time = end_time
            sequence += 1

        return segments

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format seconds to HH:MM:SS or MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def update_segment(
        db: Session,
        segment_id: int,
        text: Optional[str] = None,
        speaker: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Optional[TranscriptSegment]:
        """
        Update a transcript segment

        Args:
            db: Database session
            segment_id: Segment ID to update
            text: New text (if provided)
            speaker: New speaker (if provided)
            start_time: New start time (if provided)
            end_time: New end time (if provided)

        Returns:
            Updated TranscriptSegment or None if not found
        """
        segment = db.query(TranscriptSegment).filter(
            TranscriptSegment.id == segment_id
        ).first()

        if not segment:
            return None

        if text is not None:
            segment.text = text
        if speaker is not None:
            segment.speaker = speaker
        if start_time is not None:
            segment.start_time = start_time
        if end_time is not None:
            segment.end_time = end_time

        db.commit()
        db.refresh(segment)
        return segment

    @staticmethod
    def delete_segments(
        db: Session,
        episode_id: int
    ) -> int:
        """
        Delete all transcript segments for an episode

        Args:
            db: Database session
            episode_id: Episode ID

        Returns:
            Number of segments deleted
        """
        count = db.query(TranscriptSegment).filter(
            TranscriptSegment.episode_id == episode_id
        ).delete()
        db.commit()
        return count
