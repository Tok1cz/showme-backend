import hashlib
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.settings import settings
from app.db.models.auth.api_key import APIKey
from app.db.models.user.user import User
from app.db.session import get_session


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


async def get_user_by_api_key(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> User | None:
    if getattr(settings, "DEBUG", False):
        return None  # Allow OAuth to be used in debug mode, don't raise
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None  # Don't raise, just return None so OAuth can be used
    key_hash = hash_api_key(api_key)  # <-- hash the incoming key!
    result = await session.execute(
        select(APIKey).where(APIKey.key_hash == key_hash, APIKey.revoked == False)
    )
    api_key_obj = result.scalar_one_or_none()
    if not api_key_obj or (
        api_key_obj.expires_at and api_key_obj.expires_at < datetime.now(timezone.utc)
    ):
        return None
    user_result = await session.execute(
        select(User).where(User.id == api_key_obj.user_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        return None
    return user
