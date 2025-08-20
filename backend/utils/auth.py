from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
import os
from typing import Optional

from models.user import User
from database import get_db

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current authenticated user"""
    
    if not credentials:
        return None
    
    try:
        # Decode JWT token (simplified - in production use proper JWT validation)
        payload = jwt.decode(
            credentials.credentials,
            os.getenv("JWT_SECRET", "dev-secret"),
            algorithms=["HS256"]
        )
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
        
    except jwt.InvalidTokenError:
        return None

def require_auth(current_user: Optional[User] = Depends(get_current_user)) -> User:
    """Require authentication"""
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return current_user

def require_admin(current_user: User = Depends(require_auth)) -> User:
    """Require admin role"""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user

def require_credits(user: User, credits_needed: int) -> bool:
    """Check if user has sufficient credits"""
    
    if not user:
        return True  # Allow anonymous users for demo
    
    return user.credits_remaining >= credits_needed
