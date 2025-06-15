from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# SQLite database (simple, no extra setup needed)
DATABASE_URL = "sqlite:///./architectures.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class ProjectDB(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, index=True)
    project_name = Column(String, index=True)
    description = Column(Text)
    
    # Questionnaire data (stored as JSON)
    questionnaire_data = Column(JSON)
    
    # Generated architecture data (stored as JSON)
    architecture_data = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
