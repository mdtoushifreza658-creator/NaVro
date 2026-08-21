"""
Dev-only helper: creates a Project so you have an API key to call the
endpoints with. There's no POST /projects endpoint yet (that's an M5
dashboard concern) — this script is the stand-in until then.

Usage:
    python scripts/seed_project.py "My Project"
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.db import Base, engine, SessionLocal
from app.models import Project

Base.metadata.create_all(bind=engine)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "Dev Project"
    db = SessionLocal()
    try:
        project = Project(name=name)
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"Created project '{project.name}'")
        print(f"  id:      {project.id}")
        print(f"  api_key: {project.api_key}")
        print()
        print("Use it like:")
        print(f'  curl -H "X-Navro-Api-Key: {project.api_key}" ...')
    finally:
        db.close()


if __name__ == "__main__":
    main()
