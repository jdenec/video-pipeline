"""
Video Pipeline — Database Connection

This file handles connecting to SQLite and creating sessions.
Every other module that needs the database imports from here.

Why SQLite? It's a single file, requires zero setup, and is perfect
for a single-user tool like this. The database file (pipeline.db) will
appear in your project folder automatically.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# The database file lives right in the project folder
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pipeline.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy setup:
# - engine: the thing that actually talks to the database file
# - Base: a template that all our models inherit from
# - SessionLocal: a factory that creates database sessions

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """
    Create all tables if they don't exist yet.
    
    Call this once when the application starts (from the API, worker, or CLI).
    It's safe to call multiple times — SQLAlchemy checks "if not exists" internally.
    """
    from db.models import Job  # noqa: F401 — import so Base knows about Job
    Base.metadata.create_all(bind=engine)
    print(f"📦 Database ready: {DB_PATH}")


def get_session():
    """
    Create a new database session.
    
    Always close it when you're done:
        session = get_session()
        # ... do stuff ...
        session.close()
    
    Or use it as a context manager (advanced Python):
        with get_session() as session:
            # ... do stuff ...
    """
    return SessionLocal()