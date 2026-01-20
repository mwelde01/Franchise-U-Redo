"""AI Service for summarization and theme extraction using Claude API"""

import anthropic
from typing import List, Tuple, Dict
from app.config import settings
from sqlalchemy.orm import Session
from app.models import Episode, TranscriptSegment, Tag
import json


class AIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.preset_tags = settings.preset_tags_list

    async def generate_summary_and_tags(
        self,
        episode: Episode,
        transcript_segments: List[TranscriptSegment],
        db: Session
    ) -> Tuple[str, List[str]]:
        """
        Generate episode summary and extract tags using Claude API

        Returns:
            Tuple of (summary, list of tags)
        """
        # Combine transcript segments into full text
        full_transcript = "\n\n".join([
            f"[{self._format_timestamp(seg.start_time)}] {seg.speaker or 'Speaker'}: {seg.text}"
            for seg in sorted(transcript_segments, key=lambda x: x.sequence_number)
        ])

        # Build prompt for Claude
        prompt = self._build_summary_prompt(
            title=episode.title,
            description=episode.description,
            transcript=full_transcript,
            preset_tags=self.preset_tags
        )

        try:
            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = message.content[0].text
            summary, tags = self._parse_summary_response(response_text)

            return summary, tags

        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")

    async def discover_themes(
        self,
        episodes: List[Episode],
        db: Session
    ) -> Dict:
        """
        Analyze multiple episodes to discover common themes and relationships

        Returns:
            Dictionary with discovered themes and relationships
        """
        # Collect summaries and existing tags from episodes
        episode_data = []
        for ep in episodes[:20]:  # Limit to 20 episodes for API constraints
            tags = [tag.name for tag in ep.tags]
            episode_data.append({
                "title": ep.title,
                "summary": ep.summary or "No summary available",
                "tags": tags
            })

        prompt = self._build_theme_discovery_prompt(episode_data, self.preset_tags)

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.8,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text
            return self._parse_theme_response(response_text)

        except Exception as e:
            raise Exception(f"Failed to discover themes: {str(e)}")

    async def extract_tags_from_text(
        self,
        text: str,
        context: str = ""
    ) -> List[str]:
        """
        Extract relevant tags from a piece of text

        Args:
            text: The text to analyze
            context: Optional context (e.g., title, description)

        Returns:
            List of relevant tags
        """
        prompt = f"""Analyze the following text and extract relevant tags/themes.
Consider these preset tags: {', '.join(self.preset_tags)}

Use preset tags when applicable, but also suggest new relevant tags if needed.

{f'Context: {context}' if context else ''}

Text to analyze:
{text}

Return ONLY a JSON array of tags, like: ["tag1", "tag2", "tag3"]
Limit to 5-8 most relevant tags."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text
            # Extract JSON array from response
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start != -1 and end > start:
                tags = json.loads(response_text[start:end])
                return [tag.lower() for tag in tags if isinstance(tag, str)]
            return []

        except Exception as e:
            print(f"Warning: Failed to extract tags: {str(e)}")
            return []

    def _build_summary_prompt(
        self,
        title: str,
        description: str,
        transcript: str,
        preset_tags: List[str]
    ) -> str:
        """Build prompt for episode summarization"""
        return f"""You are analyzing a podcast episode. Please provide:
1. A concise summary (2-3 paragraphs) capturing the main topics, key insights, and important takeaways
2. Relevant tags/themes from the episode

Episode Title: {title}
{f'Description: {description}' if description else ''}

Preset Tags (use when relevant): {', '.join(preset_tags)}

Transcript:
{transcript[:15000]}  # Limit transcript length

Please respond in this format:

SUMMARY:
[Your 2-3 paragraph summary here]

TAGS:
[Comma-separated list of 5-8 relevant tags. Use preset tags when applicable, but also add new specific tags that capture unique themes from this episode]"""

    def _build_theme_discovery_prompt(
        self,
        episode_data: List[Dict],
        preset_tags: List[str]
    ) -> str:
        """Build prompt for theme discovery across episodes"""
        episodes_text = "\n\n".join([
            f"Episode: {ep['title']}\nSummary: {ep['summary']}\nTags: {', '.join(ep['tags'])}"
            for ep in episode_data
        ])

        return f"""Analyze these podcast episodes and identify:
1. Common themes that appear across multiple episodes
2. Emerging topics or trends
3. Tag relationships (which tags frequently appear together)
4. Suggested new tags that capture recurring themes

Current Preset Tags: {', '.join(preset_tags)}

Episodes:
{episodes_text}

Provide your analysis in this JSON format:
{{
    "common_themes": [
        {{"theme": "theme name", "frequency": "how often it appears", "description": "brief description"}}
    ],
    "new_tag_suggestions": ["tag1", "tag2"],
    "tag_relationships": {{"tag1": ["related_tag1", "related_tag2"]}},
    "insights": "Brief overview of patterns you discovered"
}}"""

    def _parse_summary_response(self, response: str) -> Tuple[str, List[str]]:
        """Parse Claude's response to extract summary and tags"""
        summary = ""
        tags = []

        # Split by SUMMARY: and TAGS: markers
        if "SUMMARY:" in response and "TAGS:" in response:
            parts = response.split("TAGS:")
            summary = parts[0].replace("SUMMARY:", "").strip()
            tags_text = parts[1].strip()

            # Parse tags (comma-separated)
            tags = [tag.strip().lower() for tag in tags_text.split(",")]
            tags = [tag for tag in tags if tag and len(tag) > 1]
        else:
            # Fallback: use entire response as summary
            summary = response.strip()

        return summary, tags

    def _parse_theme_response(self, response: str) -> Dict:
        """Parse theme discovery response"""
        try:
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass

        # Fallback response
        return {
            "common_themes": [],
            "new_tag_suggestions": [],
            "tag_relationships": {},
            "insights": "Unable to parse theme analysis"
        }

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format seconds to MM:SS or HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
