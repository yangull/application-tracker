# database.py — sets up the SQLAlchemy connection to PostgreSQL

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

# Load variables from the .env file into the environment
load_dotenv()

# Read the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

# The engine is the low-level connection to PostgreSQL
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory — each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all SQLAlchemy models will inherit from
class Base(DeclarativeBase):
    pass

# Dependency used in FastAPI routes — yields a DB session and closes it after the request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()