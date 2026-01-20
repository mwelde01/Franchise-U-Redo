"""Initialize database and create preset tags"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db, SessionLocal
from app.models import Tag
from app.config import settings


def initialize_database():
    """Initialize database tables and preset tags"""
    print("Initializing database...")

    # Create tables
    init_db()
    print("✓ Database tables created")

    # Create preset tags
    db = SessionLocal()
    try:
        created_count = 0
        for tag_name in settings.preset_tags_list:
            tag_name = tag_name.lower().strip()

            # Check if already exists
            existing = db.query(Tag).filter(Tag.name == tag_name).first()
            if existing:
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
        print(f"✓ Created {created_count} preset tags")
        print(f"Total preset tags: {len(settings.preset_tags_list)}")

    except Exception as e:
        print(f"✗ Error creating preset tags: {e}")
        db.rollback()
    finally:
        db.close()

    print("\n✓ Database initialization complete!")
    print("\nPreset tags:")
    for tag in settings.preset_tags_list:
        print(f"  - {tag}")


if __name__ == "__main__":
    initialize_database()
