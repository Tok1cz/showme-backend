from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.prompt_templates import (
    AudioPromptTemplate,
    ImagePromptTemplate,
    TextPromptTemplate,
)


# Existing function (Text)
async def get_text_prompt_template(
    session: AsyncSession,
    provider: str,
    model: str,
    topic_id: int,
    style_id: int,
    version: Optional[int] = None,
):
    stmt = select(TextPromptTemplate).where(
        TextPromptTemplate.provider == provider,
        TextPromptTemplate.model == model,
        TextPromptTemplate.topic_id == topic_id,
        TextPromptTemplate.style_id == style_id,
    )
    if version:
        stmt = stmt.where(TextPromptTemplate.version == version)
    else:
        stmt = stmt.order_by(TextPromptTemplate.version.desc())
    result = await session.execute(stmt)
    return result.scalars().first()


# New: Image prompt template
async def get_image_prompt_template(
    session: AsyncSession,
    provider: str,
    model: str,
    style_id: int,
    aspect_id: Optional[int] = None,
    version: Optional[int] = None,
):
    stmt = select(ImagePromptTemplate).where(
        ImagePromptTemplate.provider == provider,
        ImagePromptTemplate.model == model,
        ImagePromptTemplate.style_id == style_id,
    )
    if aspect_id:
        stmt = stmt.where(ImagePromptTemplate.aspect_id == aspect_id)
    if version:
        stmt = stmt.where(ImagePromptTemplate.version == version)
    else:
        stmt = stmt.order_by(ImagePromptTemplate.version.desc())
    result = await session.execute(stmt)
    return result.scalars().first()


# New: Audio prompt template
async def get_audio_prompt_template(
    session: AsyncSession,
    provider: str,
    model: str,
    voice_id: int,
    version: Optional[int] = None,
):
    stmt = select(AudioPromptTemplate).where(
        AudioPromptTemplate.provider == provider,
        AudioPromptTemplate.model == model,
        AudioPromptTemplate.voice_id == voice_id,
    )
    if version:
        stmt = stmt.where(AudioPromptTemplate.version == version)
    else:
        stmt = stmt.order_by(AudioPromptTemplate.version.desc())
    result = await session.execute(stmt)
    return result.scalars().first()
