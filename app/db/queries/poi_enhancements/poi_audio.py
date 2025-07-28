from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.orm import joinedload

from app.db.models.poi_enhancements import POIAudio, AudioVoice
from app.db.enums import AudioQuality, AudioLength

# ---- Helper: Resolve style name to ID ----
async def get_style_id(session: AsyncSession, voice_name: Optional[str]) -> Optional[int]:
    if not voice_name:
        return None
    result = await session.execute(
        select(AudioVoice).where(AudioVoice.name == voice_name)
    )
    audio_voice = result.scalar_one_or_none()
    if not audio_voice:
        raise ValueError(f"Unknown audio voice: {voice_name}")
    return audio_voice.id

# ---- Create ----
async def create_poi_audio(
    session: AsyncSession,
    *,
    poi_id: int,
    filename: str,
    audio_url: str,
    quality: AudioQuality,
    length: AudioLength,
    style: Optional[str] = None,
    prompt: Optional[str] = None,
    source: Optional[str] = None,
    status: str = "active",
) -> POIAudio:
    style_id = await get_style_id(session, style)
    new_audio = POIAudio(
        poi_id=poi_id,
        filename=filename,
        audio_url=audio_url,
        prompt=prompt,
        source=source,
        quality=quality,
        length=length,
        style_id=style_id,
        status=status,
    )
    session.add(new_audio)
    await session.commit()
    await session.refresh(new_audio)
    return new_audio

# ---- Read (get all for a POI) ----
async def get_poi_audio(
    session: AsyncSession,
    poi_id: int,
    quality: Optional[AudioQuality] = None,
    length: Optional[AudioLength] = None,
    style: Optional[str] = None,
) -> List[POIAudio]:
    stmt = select(POIAudio).where(POIAudio.poi_id == poi_id)
    if quality:
        stmt = stmt.where(POIAudio.quality == quality)
    if length:
        stmt = stmt.where(POIAudio.length == length)
    if style:
        style_id = await get_style_id(session, style)
        stmt = stmt.where(POIAudio.style_id == style_id)
    stmt = stmt.options(joinedload(POIAudio.style))
    result = await session.execute(stmt)
    return result.scalars().all()

# ---- Read (get by audio id) ----
async def get_poi_audio_by_id(session: AsyncSession, audio_id: int) -> Optional[POIAudio]:
    stmt = (
        select(POIAudio)
        .options(joinedload(POIAudio.style))
        .where(POIAudio.id == audio_id)
    )
    result = await session.execute(stmt)
    return result.scalars().first()

# ---- Update ----
async def update_poi_audio(
    session: AsyncSession,
    audio_id: int,
    **kwargs
) -> Optional[POIAudio]:
    # If "style" present in kwargs, resolve to style_id
    if "style" in kwargs and kwargs["style"] is not None:
        kwargs["style_id"] = await get_style_id(session, kwargs.pop("style"))
    stmt = (
        update(POIAudio)
        .where(POIAudio.id == audio_id)
        .values(**kwargs)
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(stmt)
    await session.commit()
    return await get_poi_audio_by_id(session, audio_id)

# ---- Delete ----
async def delete_poi_audio(session: AsyncSession, audio_id: int) -> None:
    stmt = delete(POIAudio).where(POIAudio.id == audio_id)
    await session.execute(stmt)
    await session.commit()

# ---- Bulk get for list of POI IDs ----
async def get_audio_for_poi_ids(session: AsyncSession, ids: list[int]) -> list[POIAudio]:
    stmt = select(POIAudio).where(POIAudio.poi_id.in_(ids)).options(joinedload(POIAudio.style))
    result = await session.execute(stmt)
    return result.scalars().all()
