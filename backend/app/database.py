from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
import hashlib
import secrets

# SQLite database (simple, no extra setup needed)
DATABASE_URL = "sqlite:///./architectures.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    projects = relationship("ProjectDB", back_populates="user")
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return hashlib.sha256(password.encode()).hexdigest() == self.password_hash
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()

class SessionDB(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
class ProjectDB(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, index=True)
    project_name = Column(String, index=True)
    description = Column(Text)
    user_id = Column(String, ForeignKey("users.id"))
    
    # Questionnaire data (stored as JSON)
    questionnaire_data = Column(JSON)
    
    # Generated architecture data (stored as JSON)
    architecture_data = Column(JSON)
    
    # User custom preferences (stored as JSON)
    user_preferences = Column(JSON, default=lambda: {})
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserDB", back_populates="projects")

class AWSAccountDB(Base):
    __tablename__ = "aws_accounts"
    
    id = Column(String, primary_key=True, index=True)
    account_name = Column(String, index=True)
    aws_region = Column(String, default="us-west-2")
    description = Column(Text)
    
    # Encrypted credentials (stored securely)
    encrypted_access_key = Column(Text)
    encrypted_secret_key = Column(Text) 
    encrypted_session_token = Column(Text)
    
    # Account status
    is_active = Column(Boolean, default=True)
    last_validated = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DeploymentDB(Base):
    __tablename__ = "deployments"
    
    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    aws_account_id = Column(String, index=True)
    template_type = Column(String)  # terraform or cloudformation
    status = Column(String)  # pending, running, success, failed
    dry_run = Column(Boolean, default=True)
    
    # Deployment results
    output = Column(Text)
    error = Column(Text)
    
    # Deployment state tracking
    stack_name = Column(String)  # For CloudFormation stack name
    terraform_state_path = Column(String)  # For Terraform state file path
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables and demo user
def create_tables():
    Base.metadata.create_all(bind=engine)
    create_demo_user()

def create_demo_user():
    """Create demo user if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if demo user exists
        demo_user = db.query(UserDB).filter(UserDB.username == "demo").first()
        if not demo_user:
            import uuid
            demo_user = UserDB(
                id=str(uuid.uuid4()),
                username="demo",
                password_hash=UserDB.hash_password("demo"),
                full_name="Demo User",
                email="demo@example.com",
                is_active=True,
                is_admin=True
            )
            db.add(demo_user)
            db.commit()
            print("Demo user created: username=demo, password=demo")
    except Exception as e:
        print(f"Error creating demo user: {e}")
        db.rollback()
    finally:
        db.close()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
