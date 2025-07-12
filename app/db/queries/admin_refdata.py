from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.db.models.poi_models import ImageStyle, InformationStyle, InformationTopic

# ---- Image Styles ----
async def add_image_style(session: AsyncSession, name: str) -> ImageStyle:
    style = ImageStyle(name=name)
    session.add(style)
    await session.commit()
    await session.refresh(style)
    return style

async def delete_image_style(session: AsyncSession, style_id: int) -> None:
    await session.execute(delete(ImageStyle).where(ImageStyle.id == style_id))
    await session.commit()

# ---- Information Styles ----
async def add_information_style(session: AsyncSession, name: str) -> InformationStyle:
    style = InformationStyle(name=name)
    session.add(style)
    await session.commit()
    await session.refresh(style)
    return style

async def delete_information_style(session: AsyncSession, style_id: int) -> None:
    await session.execute(delete(InformationStyle).where(InformationStyle.id == style_id))
    await session.commit()

# ---- Information Topics ----
async def add_information_topic(session: AsyncSession, name: str) -> InformationTopic:
    topic = InformationTopic(name=name)
    session.add(topic)
    await session.commit()
    await session.refresh(topic)
    return topic

async def delete_information_topic(session: AsyncSession, topic_id: int) -> None:
    await session.execute(delete(InformationTopic).where(InformationTopic.id == topic_id))
    await session.commit()

# --- InformationStyle by name ---
async def get_information_style_by_name(session: AsyncSession, name: str):
    stmt = select(InformationStyle).where(InformationStyle.name == name)
    result = await session.execute(stmt)
    return result.scalars().first()

# --- InformationTopic by name ---
async def get_information_topic_by_name(session: AsyncSession, name: str):
    stmt = select(InformationTopic).where(InformationTopic.name == name)
    result = await session.execute(stmt)
    return result.scalars().first()

# --- ImageStyle by name ---
async def get_image_style_by_name(session: AsyncSession, name: str):
    stmt = select(ImageStyle).where(ImageStyle.name == name)
    result = await session.execute(stmt)
    return result.scalars().first()