from fastapi import Depends, HTTPException, status, Request
from app.services.auth.oauth import fastapi_users
from app.services.auth.api_key_auth import get_user_by_api_key
from app.db.models.user.user import User
from app.core.settings import settings  # Make sure this imports your settings
from app.db.enums import UserRole

class DummyUser(User):
    def __init__(self):
        super().__init__(
            id=0,
            email="dev@example.com",
            role=UserRole.admin
        )


async def get_current_user(
    request: Request,
    user_oauth: User = Depends(fastapi_users.current_user(optional=True)),
    user_api_key: User = Depends(get_user_by_api_key),
) -> User:
    if getattr(settings, "DEBUG", False):  # or settings.ENV == "dev"
        return DummyUser()
    if user_oauth:
        return user_oauth
    if user_api_key:
        return user_api_key
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")