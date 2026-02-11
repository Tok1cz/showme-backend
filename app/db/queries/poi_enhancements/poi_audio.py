from typing import List, Optional

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.db.enums import AudioLength, AudioQuality
from app.db.models.poi_enhancements import AudioVoice, InformationStyle, POIAudio


# ---- Helper: Resolve style name to ID ----
async def get_style_id(
    session: AsyncSession, style_name: Optional[str]
) -> Optional[int]:
    if not style_name:
        return None
    result = await session.execute(
        select(InformationStyle).where(InformationStyle.name == style_name)
    )
    style = result.scalar_one_or_none()
    if not style:
        raise ValueError(f"Unknown audio style: {style_name}")
    return style.id


# ---- Helper: Resolve voice name to ID ----
async def get_voice_id(
    session: AsyncSession, voice_name: Optional[str]
) -> Optional[int]:
    if not voice_name:
        return None
    result = await session.execute(
        select(AudioVoice).where(AudioVoice.name == voice_name)
    )
    voice = result.scalar_one_or_none()
    if not voice:
        raise ValueError(f"Unknown audio voice: {voice_name}")
    return voice.id


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
    voice: Optional[str] = None,  # for future voice support
    prompt: Optional[str] = None,
    source: Optional[str] = None,
    status: str = "active",
    task_id: Optional[str] = None,
) -> POIAudio:
    style_id = await get_style_id(session, style)
    voice_id = await get_voice_id(session, voice) if voice else None
    new_audio = POIAudio(
        poi_id=poi_id,
        filename=filename,
        audio_url=audio_url,
        prompt=prompt,
        source=source,
        quality=quality,
        length=length,
        style_id=style_id,
        # Add voice_id if your model/table supports it
        status=status,
        task_id=task_id,
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
    voice: Optional[str] = None,
) -> List[POIAudio]:
    stmt = select(POIAudio).where(POIAudio.poi_id == poi_id)
    if quality:
        stmt = stmt.where(POIAudio.quality == quality)
    if length:
        stmt = stmt.where(POIAudio.length == length)
    if style:
        style_id = await get_style_id(session, style)
        stmt = stmt.where(POIAudio.style_id == style_id)
    # If you add voice filtering, add here
    stmt = stmt.options(joinedload(POIAudio.style))
    result = await session.execute(stmt)
    return result.scalars().all()


# ---- Read (get by audio id) ----
async def get_poi_audio_by_id(
    session: AsyncSession, audio_id: int
) -> Optional[POIAudio]:
    stmt = (
        select(POIAudio)
        .options(joinedload(POIAudio.style))
        .where(POIAudio.id == audio_id)
    )
    result = await session.execute(stmt)
    return result.scalars().first()


# ---- Update ----
async def update_poi_audio(
    session: AsyncSession, audio_id: int, **kwargs
) -> Optional[POIAudio]:
    if "style" in kwargs and kwargs["style"] is not None:
        kwargs["style_id"] = await get_style_id(session, kwargs.pop("style"))
    # If you want to support updating voice by name
    if "voice" in kwargs and kwargs["voice"] is not None:
        kwargs["voice_id"] = await get_voice_id(session, kwargs.pop("voice"))
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
async def get_audio_for_poi_ids(
    session: AsyncSession, ids: list[int]
) -> list[POIAudio]:
    stmt = (
        select(POIAudio)
        .where(POIAudio.poi_id.in_(ids))
        .options(joinedload(POIAudio.style))
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_voice_by_id(
    session: AsyncSession, voice_id: Optional[int]
) -> Optional[AudioVoice]:
    if not voice_id:
        return None
    result = await session.execute(select(AudioVoice).where(AudioVoice.id == voice_id))
    return result.scalar_one_or_none()
