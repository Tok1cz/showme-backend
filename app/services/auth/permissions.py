from fastapi import Depends, HTTPException, status
from app.services.auth.dependencies import get_current_user
from app.db.models.user.user import User
from app.db.enums import UserRole

def admin_required(user: User = Depends(get_current_user)) -> User:
    if getattr(user, "role", None) != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user

def premium_required(user: User = Depends(get_current_user)) -> User:
    if getattr(user, "role", None) not in [UserRole.admin, UserRole.premium]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium privileges required",
        )
    return user