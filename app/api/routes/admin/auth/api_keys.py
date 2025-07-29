from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
from datetime import datetime, timedelta
import hashlib

from app.db.session import get_session
from app.db.models.auth.api_key import APIKey
from app.db.models.user.user import User
from app.services.auth.dependencies import get_current_user
from app.core.settings import settings

router = APIRouter(prefix="/api-keys", )

@router.get("/", response_model=list[str])
async def list_api_keys(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(APIKey).where(APIKey.user_id == user.id, APIKey.revoked == False)
    )
    keys = result.scalars().all()
    # For security, only return masked keys or key IDs, not the full hash
    return [f"key_{k.id}" for k in keys]

@router.post("/", response_model=str)
async def create_api_key(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if getattr(settings, "DEBUG", False):
        raise HTTPException(status_code=400, detail="API keys cannot be created in debug mode.")
    if user.id == 0:
        raise HTTPException(status_code=400, detail="API keys cannot be created for dummy users.")
    # Generate a new API key
    raw_key = str(uuid4())
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest() 
    api_key = APIKey(
        user_id=user.id,
        key_hash=key_hash,
        revoked=False,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=90),
    )
    session.add(api_key)
    await session.commit()
    await session.refresh(api_key)
    return raw_key  # Show the user the raw key ONCE

@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(APIKey).where(APIKey.id == key_id, APIKey.user_id == user.id)
    )
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    api_key.revoked = True
    await session.commit()