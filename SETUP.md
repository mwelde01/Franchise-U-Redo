# Quick Start Guide

This guide will help you get the Podcast Storage & Summarization System up and running.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/)
- **Anthropic API Key** - [Get one here](https://console.anthropic.com/)

## Step 1: Database Setup

1. Install PostgreSQL if you haven't already

2. Create a new database:
   ```bash
   createdb podcast_db
   ```

3. Or using psql:
   ```sql
   CREATE DATABASE podcast_db;
   ```

4. Note your database credentials (username, password, host, port)

## Step 2: Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - **Linux/Mac**: `source venv/bin/activate`
   - **Windows**: `venv\Scripts\activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

6. Edit `.env` with your settings:
   ```env
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/podcast_db
   ANTHROPIC_API_KEY=your_api_key_here
   AUDIO_STORAGE_PATH=./audio_files
   MAX_UPLOAD_SIZE=500
   ```

7. Initialize the database:
   ```bash
   python -m app.init_db
   ```

8. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

9. Verify it's running by visiting: http://localhost:8000/docs

## Step 3: Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file:
   ```bash
   cp .env.local.example .env.local
   ```

4. Edit `.env.local` if needed (default should work):
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

5. Start the development server:
   ```bash
   npm run dev
   ```

6. Open your browser and visit: http://localhost:3000

## Step 4: Upload Your First Episode

1. Click the **"Upload"** button in the navigation bar

2. Create a podcast first, or select an existing one

3. Fill in the episode details:
   - Title (required)
   - Description (optional)
   - Episode/Season numbers (optional)
   - Select tags

4. Upload files:
   - **Audio file** (required) - Supports MP3, WAV, OGG, M4A, FLAC
   - **Transcript file** (optional) - Plain text with timestamps

5. Click **"Upload Episode"**

6. The system will:
   - Store the audio file
   - Process the transcript
   - Generate an AI summary
   - Extract themes and tags
   - Enable searchable content

## Transcript Format

The system supports various transcript formats:

### Format 1: With timestamps and speakers
```
[00:00:12] John: Welcome to the show!
[00:00:15] Jane: Thanks for having me.
```

### Format 2: Simple timestamps
```
[00:12] This is the introduction
[01:30] Now we're discussing the main topic
```

### Format 3: Plain text
```
Welcome to the show. Today we'll be discussing...
```

If no timestamps are provided, the system will estimate them based on text length.

## Using the System

### Browse Episodes
- Visit the home page to see all episodes
- Filter by tags
- Click an episode card to view details

### Play Episodes
- Episode detail page includes an audio player
- See real-time transcript synchronization
- Click transcript segments to jump to that moment

### Search Transcripts
- Use the Search page to find specific content
- Search across all episodes
- Jump directly to the moment in the audio

### Manage Tags
- Preset tags are automatically available
- Add custom tags when uploading
- System can auto-discover new relevant tags

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `pg_isready`
- Verify database credentials in `.env`
- Ensure virtual environment is activated
- Check for port conflicts (default: 8000)

### Frontend won't start
- Ensure Node.js version is 18+: `node --version`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check for port conflicts (default: 3000)

### Audio won't play
- Check browser console for errors
- Verify audio file path in database
- Ensure `AUDIO_STORAGE_PATH` directory exists and is writable

### AI summarization not working
- Verify `ANTHROPIC_API_KEY` in `.env`
- Check API key is valid at https://console.anthropic.com/
- Ensure transcript was uploaded with the episode
- Check backend logs for errors

### Database connection errors
- Verify PostgreSQL is running
- Check `DATABASE_URL` format in `.env`
- Ensure database exists: `psql -l | grep podcast_db`
- Check PostgreSQL logs for connection issues

## Advanced Configuration

### Changing Preset Tags

Edit `backend/.env`:
```env
PRESET_TAGS=tag1,tag2,tag3,custom-tag,another-tag
```

Then reinitialize:
```bash
python -m app.init_db
```

### Adjusting Upload Size Limit

Edit `backend/.env`:
```env
MAX_UPLOAD_SIZE=1000  # MB
```

### CORS Configuration

Edit `backend/.env`:
```env
CORS_ORIGINS=["http://localhost:3000","https://your-domain.com"]
```

## Production Deployment

### Backend
1. Set `DEBUG=False` in `.env`
2. Use a production WSGI server (e.g., Gunicorn)
3. Set up SSL/HTTPS
4. Configure firewall rules
5. Use environment-specific database

### Frontend
1. Build the production version:
   ```bash
   npm run build
   ```
2. Start production server:
   ```bash
   npm start
   ```
3. Or deploy to Vercel, Netlify, etc.

### Database
1. Use managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)
2. Enable automated backups
3. Set up monitoring and alerts
4. Configure connection pooling

## Support

For issues and questions:
- Check the main [README.md](./README.md)
- Review API documentation at `/docs`
- Check backend logs for errors
- Inspect browser console for frontend issues

## Next Steps

- Explore the API documentation at http://localhost:8000/docs
- Try the theme discovery feature
- Set up automated backups
- Configure additional preset tags
- Integrate with podcast RSS feeds (custom development)
