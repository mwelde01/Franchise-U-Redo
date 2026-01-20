# Podcast Storage & Summarization System

A comprehensive podcast management system with AI-powered summarization, theme extraction, and audio playback capabilities.

## Features

- **Audio Storage**: Upload and store podcast episode audio files
- **Transcript Management**: Store and sync transcripts with audio timestamps
- **AI Summarization**: Automatic episode summarization using Claude API
- **Theme Extraction**: Intelligent tag and theme identification across episodes
- **Pinpoint Search**: Find specific moments in recordings by content
- **Audio Playback**: Built-in web-based audio player with transcript synchronization
- **Tag System**: Preset tags + automatic theme discovery
- **Search & Filter**: Find episodes by tags, themes, or content

## Tech Stack

- **Backend**: Python FastAPI
- **Database**: PostgreSQL
- **AI**: Anthropic Claude API
- **Frontend**: React/Next.js
- **Audio Processing**: pydub, librosa

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Anthropic API key

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/podcast_db
   ANTHROPIC_API_KEY=your_api_key_here
   AUDIO_STORAGE_PATH=./audio_files
   MAX_UPLOAD_SIZE=500  # MB
   ```

5. Initialize the database:
   ```bash
   python -m app.init_db
   ```

6. Run the backend:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## API Documentation

Once the backend is running, visit:
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Utilities
│   │   └── main.py          # FastAPI app
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Next.js pages
│   │   ├── services/        # API clients
│   │   └── styles/          # CSS/styling
│   ├── public/
│   └── package.json
└── README.md
```

## Usage

### Uploading Episodes

1. Click "Upload Episode" in the UI
2. Provide episode details (title, podcast name, etc.)
3. Upload audio file and transcript (optional)
4. System will automatically:
   - Store the audio file
   - Generate a summary using Claude API
   - Extract themes and tags
   - Process transcript timestamps

### Finding Content

- **By Tags**: Filter episodes using preset or auto-discovered tags
- **By Theme**: View common themes across podcasts
- **By Content**: Search transcript text to find specific moments
- **By Timestamp**: Jump directly to specific parts of episodes

### Playback

- Click any episode to open the player
- Transcript is synced with audio playback
- Click transcript segments to jump to that moment
- Use keyboard shortcuts for playback control

## License

MIT
