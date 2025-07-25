from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate, UserLogin, UserResponse, AuthResponse, UserUpdate

router = APIRouter()

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split("Bearer ")[1]
    auth_service = AuthService(db)
    user = auth_service.get_user_by_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user

def get_current_admin_user(current_user = Depends(get_current_user)):
    """Get current authenticated admin user"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        auth_service = AuthService(db)
        user = auth_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.post("/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return token"""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(login_data)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    auth_response = auth_service.create_session(user)
    return auth_response

@router.post("/logout")
async def logout_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Logout current user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split("Bearer ")[1]
    auth_service = AuthService(db)
    success = auth_service.logout_user(token)
    
    if success:
        return {"message": "Logged out successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to logout")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.model_validate(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    auth_service = AuthService(db)
    updated_user = auth_service.update_user(
        current_user.id, 
        update_data.model_dump(exclude_unset=True)
    )
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_user

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    auth_service = AuthService(db)
    return auth_service.get_all_users()

@router.post("/users", response_model=UserResponse)
async def create_user_admin(
    user_data: UserCreate,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new user (admin only)"""
    try:
        auth_service = AuthService(db)
        user = auth_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: str,
    update_data: UserUpdate,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    auth_service = AuthService(db)
    updated_user = auth_service.update_user(
        user_id, 
        update_data.model_dump(exclude_unset=True)
    )
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_user

@router.delete("/users/{user_id}")
async def delete_user_admin(
    user_id: str,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    auth_service = AuthService(db)
    success = auth_service.delete_user(user_id)
    
    if success:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")