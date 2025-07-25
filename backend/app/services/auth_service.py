from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import secrets
from typing import Optional

from app.database import UserDB, SessionDB
from app.schemas.auth import UserCreate, UserLogin, UserResponse, AuthResponse

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        # Check if username already exists
        existing_user = self.db.query(UserDB).filter(UserDB.username == user_data.username).first()
        if existing_user:
            raise ValueError("Username already exists")
        
        # Check if email already exists (if provided)
        if user_data.email:
            existing_email = self.db.query(UserDB).filter(UserDB.email == user_data.email).first()
            if existing_email:
                raise ValueError("Email already exists")
        
        # Create new user
        user = UserDB(
            id=str(uuid.uuid4()),
            username=user_data.username,
            password_hash=UserDB.hash_password(user_data.password),
            email=user_data.email,
            full_name=user_data.full_name,
            is_active=True,
            is_admin=False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return UserResponse.model_validate(user)

    def authenticate_user(self, login_data: UserLogin) -> Optional[UserDB]:
        """Authenticate user with username and password"""
        user = self.db.query(UserDB).filter(
            UserDB.username == login_data.username.lower(),
            UserDB.is_active == True
        ).first()
        
        if user and user.verify_password(login_data.password):
            # Update last login
            user.last_login = datetime.utcnow()
            self.db.commit()
            return user
        
        return None

    def create_session(self, user: UserDB) -> AuthResponse:
        """Create a new session for authenticated user"""
        # Generate session token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days expiry
        
        # Create session record
        session = SessionDB(
            id=str(uuid.uuid4()),
            user_id=user.id,
            token=token,
            expires_at=expires_at,
            is_active=True
        )
        
        self.db.add(session)
        self.db.commit()
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            token=token,
            expires_at=expires_at
        )

    def get_user_by_token(self, token: str) -> Optional[UserDB]:
        """Get user by session token"""
        session = self.db.query(SessionDB).filter(
            SessionDB.token == token,
            SessionDB.is_active == True,
            SessionDB.expires_at > datetime.utcnow()
        ).first()
        
        if session:
            user = self.db.query(UserDB).filter(
                UserDB.id == session.user_id,
                UserDB.is_active == True
            ).first()
            return user
        
        return None

    def logout_user(self, token: str) -> bool:
        """Logout user by deactivating session"""
        session = self.db.query(SessionDB).filter(
            SessionDB.token == token,
            SessionDB.is_active == True
        ).first()
        
        if session:
            session.is_active = False
            self.db.commit()
            return True
        
        return False

    def get_all_users(self) -> list[UserResponse]:
        """Get all users (admin only)"""
        users = self.db.query(UserDB).all()
        return [UserResponse.model_validate(user) for user in users]

    def update_user(self, user_id: str, update_data: dict) -> Optional[UserResponse]:
        """Update user information"""
        user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            return None
        
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                if field == 'password':
                    user.password_hash = UserDB.hash_password(value)
                else:
                    setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        return UserResponse.model_validate(user)

    def delete_user(self, user_id: str) -> bool:
        """Deactivate user"""
        user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if user:
            user.is_active = False
            self.db.commit()
            return True
        return False