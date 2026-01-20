# API Usage Examples

This document provides examples of how to use the Podcast API programmatically.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production, you should implement proper authentication.

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Examples

### 1. Create a Podcast

```bash
curl -X POST "http://localhost:8000/podcasts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Talk Daily",
    "description": "Daily discussions about technology and innovation",
    "author": "John Doe",
    "website": "https://techtalk.example.com"
  }'
```

### 2. List All Podcasts

```bash
curl -X GET "http://localhost:8000/podcasts/"
```

### 3. Upload an Episode

```bash
curl -X POST "http://localhost:8000/episodes/upload" \
  -F "podcast_id=1" \
  -F "title=Episode 5: AI and Creativity" \
  -F "description=Exploring how AI is changing creative work" \
  -F "episode_number=5" \
  -F "audio_file=@/path/to/episode.mp3" \
  -F "transcript_file=@/path/to/transcript.txt" \
  -F 'tag_names=["technology","ai","creativity"]'
```

### 4. Get Episode Details

```bash
curl -X GET "http://localhost:8000/episodes/1?include_transcript=true"
```

### 5. List Episodes with Filters

```bash
# By podcast
curl -X GET "http://localhost:8000/episodes/?podcast_id=1"

# By tag
curl -X GET "http://localhost:8000/episodes/?tag_id=3"

# With pagination
curl -X GET "http://localhost:8000/episodes/?skip=0&limit=20"
```

### 6. Search Transcripts

```bash
curl -X POST "http://localhost:8000/search/transcripts" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence",
    "limit": 50
  }'
```

### 7. Search by Keywords

```bash
curl -X GET "http://localhost:8000/search/keywords?keywords=AI,machine learning,neural networks&limit=30"
```

### 8. Get All Tags

```bash
# All tags sorted by usage
curl -X GET "http://localhost:8000/tags/?sort_by=usage"

# Preset tags only
curl -X GET "http://localhost:8000/tags/preset"

# Popular tags
curl -X GET "http://localhost:8000/tags/popular?limit=20"
```

### 9. Create a Custom Tag

```bash
curl -X POST "http://localhost:8000/tags/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "machine-learning",
    "description": "Episodes about machine learning",
    "is_preset": false
  }'
```

### 10. Discover Common Themes

```bash
curl -X POST "http://localhost:8000/search/discover-themes?limit=20"
```

### 11. Find Related Episodes

```bash
curl -X GET "http://localhost:8000/search/related-episodes/5?limit=10"
```

### 12. Get Segment Context

```bash
curl -X GET "http://localhost:8000/search/segment/123/context?context_seconds=30"
```

### 13. Regenerate Episode Summary

```bash
curl -X POST "http://localhost:8000/episodes/1/regenerate-summary"
```

### 14. Update Episode

```bash
curl -X PUT "http://localhost:8000/episodes/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "description": "Updated description",
    "tag_names": ["technology", "ai", "interviews"]
  }'
```

### 15. Delete Episode

```bash
curl -X DELETE "http://localhost:8000/episodes/1"
```

### 16. Get System Statistics

```bash
curl -X GET "http://localhost:8000/stats"
```

## Python Examples

### Using `requests` library

```python
import requests

API_URL = "http://localhost:8000"

# Create a podcast
response = requests.post(
    f"{API_URL}/podcasts/",
    json={
        "name": "My Podcast",
        "description": "A great podcast",
        "author": "John Doe"
    }
)
podcast = response.json()
print(f"Created podcast: {podcast['id']}")

# Upload an episode
with open("episode.mp3", "rb") as audio_file, \
     open("transcript.txt", "rb") as transcript_file:

    files = {
        "audio_file": audio_file,
        "transcript_file": transcript_file
    }

    data = {
        "podcast_id": podcast["id"],
        "title": "Episode 1",
        "description": "First episode",
        "tag_names": '["technology","education"]'
    }

    response = requests.post(
        f"{API_URL}/episodes/upload",
        files=files,
        data=data
    )

    result = response.json()
    episode_id = result["episode_id"]
    print(f"Uploaded episode: {episode_id}")

# Search transcripts
response = requests.post(
    f"{API_URL}/search/transcripts",
    json={
        "query": "machine learning",
        "limit": 10
    }
)

results = response.json()
print(f"Found {results['total_count']} results")

for result in results['results']:
    print(f"- {result['episode_title']} at {result['start_time']}s")
```

### Using `httpx` (async)

```python
import httpx
import asyncio

API_URL = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # Get all episodes
        response = await client.get(f"{API_URL}/episodes/")
        episodes = response.json()

        for episode in episodes:
            print(f"Episode: {episode['title']}")

            # Get full details with transcript
            detail_response = await client.get(
                f"{API_URL}/episodes/{episode['id']}",
                params={"include_transcript": True}
            )
            details = detail_response.json()

            print(f"  Duration: {details['duration']}s")
            print(f"  Segments: {len(details['transcript_segments'])}")

asyncio.run(main())
```

## JavaScript/TypeScript Examples

### Using `fetch`

```javascript
const API_URL = 'http://localhost:8000';

// Search transcripts
async function searchTranscripts(query) {
  const response = await fetch(`${API_URL}/search/transcripts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      limit: 50
    })
  });

  const data = await response.json();
  return data;
}

// Upload episode
async function uploadEpisode(podcastId, title, audioFile, transcriptFile) {
  const formData = new FormData();
  formData.append('podcast_id', podcastId);
  formData.append('title', title);
  formData.append('audio_file', audioFile);
  if (transcriptFile) {
    formData.append('transcript_file', transcriptFile);
  }
  formData.append('tag_names', JSON.stringify(['technology', 'podcast']));

  const response = await fetch(`${API_URL}/episodes/upload`, {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  return data;
}

// Get episode with transcript
async function getEpisode(episodeId) {
  const response = await fetch(
    `${API_URL}/episodes/${episodeId}?include_transcript=true`
  );

  const data = await response.json();
  return data;
}
```

### Using `axios`

```javascript
import axios from 'axios';

const API_URL = 'http://localhost:8000';

// List episodes by podcast
async function getEpisodesByPodcast(podcastId) {
  const response = await axios.get(`${API_URL}/episodes/`, {
    params: { podcast_id: podcastId }
  });
  return response.data;
}

// Discover themes
async function discoverThemes() {
  const response = await axios.post(
    `${API_URL}/search/discover-themes`,
    null,
    { params: { limit: 20 } }
  );
  return response.data;
}
```

## Response Examples

### Episode Detail Response

```json
{
  "id": 1,
  "podcast_id": 1,
  "title": "AI and Creativity",
  "description": "Exploring how AI impacts creative work",
  "audio_file_path": "/path/to/audio.mp3",
  "audio_file_size": 15728640,
  "duration": 300.5,
  "audio_format": "mp3",
  "episode_number": 5,
  "season_number": 1,
  "publish_date": "2024-01-15T10:00:00Z",
  "summary": "In this episode, we explore...",
  "summary_generated_at": "2024-01-15T11:00:00Z",
  "is_processed": true,
  "processing_error": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "tags": [
    {
      "id": 1,
      "name": "technology",
      "description": null,
      "is_preset": true,
      "usage_count": 15,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "podcast_name": "Tech Talk Daily",
  "transcript_segments": [
    {
      "id": 1,
      "episode_id": 1,
      "start_time": 0.0,
      "end_time": 5.5,
      "text": "Welcome to the show!",
      "speaker": "Host",
      "sequence_number": 0,
      "confidence": 0.95,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Search Results Response

```json
{
  "results": [
    {
      "episode_id": 1,
      "episode_title": "AI and Creativity",
      "podcast_name": "Tech Talk Daily",
      "segment_id": 15,
      "start_time": 125.5,
      "end_time": 132.0,
      "text": "Machine learning models are transforming how we create content",
      "speaker": "Guest"
    }
  ],
  "total_count": 1
}
```

## Error Handling

All errors return a JSON response with a `detail` field:

```json
{
  "detail": "Episode with id 999 not found"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `204`: No Content (successful deletion)
- `400`: Bad Request
- `404`: Not Found
- `409`: Conflict (e.g., duplicate tag)
- `500`: Internal Server Error

## Rate Limiting

Currently, there is no rate limiting. For production, implement rate limiting to prevent abuse.

## Best Practices

1. Always check response status codes
2. Handle errors gracefully
3. Use pagination for large result sets
4. Cache frequently accessed data
5. Validate file sizes before uploading
6. Use appropriate timeouts for long-running operations
7. Implement retry logic for transient failures
