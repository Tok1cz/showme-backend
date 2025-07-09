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
