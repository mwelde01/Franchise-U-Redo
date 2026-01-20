"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base
from app.routes import podcasts, episodes, tags, search

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Podcast Storage & Summarization API",
    description="API for managing podcast episodes with AI-powered summarization and theme extraction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(podcasts.router)
app.include_router(episodes.router)
app.include_router(tags.router)
app.include_router(search.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Podcast Storage & Summarization API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }


@app.get("/stats")
def get_stats(db=None):
    """Get system statistics"""
    from app.database import SessionLocal
    from app.models import Podcast, Episode, Tag, TranscriptSegment

    db = SessionLocal()
    try:
        stats = {
            "podcasts": db.query(Podcast).count(),
            "episodes": db.query(Episode).count(),
            "tags": db.query(Tag).count(),
            "transcript_segments": db.query(TranscriptSegment).count(),
            "processed_episodes": db.query(Episode).filter(
                Episode.is_processed == True
            ).count()
        }
        return stats
    finally:
        db.close()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
