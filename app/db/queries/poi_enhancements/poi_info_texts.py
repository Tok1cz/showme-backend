from typing import List, Optional

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.db.models.poi_enhancements import (
    InformationStyle,
    InformationTopic,
    POIInfoText,
)

# ---- Helper: Resolve topic/style name to ID ----


async def get_topic_id(
    session: AsyncSession, topic_name: Optional[str]
) -> Optional[int]:
    if not topic_name:
        return None
    result = await session.execute(
        select(InformationTopic).where(InformationTopic.name == topic_name)
    )
    topic = result.scalar_one_or_none()
    if not topic:
        raise ValueError(f"Unknown topic: {topic_name}")
    return topic.id


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
        raise ValueError(f"Unknown style: {style_name}")
    return style.id


# ---- Create ----
async def create_poi_info_text(
    session: AsyncSession,
    *,
    poi_id: int,
    info_text: str,
    prompt: Optional[str] = None,
    topic: Optional[str] = "general",
    style: Optional[str] = None,
    source: Optional[str] = None,
    status: Optional[str] = "active",
    task_id: Optional[str] = None,
) -> POIInfoText:
    topic_id = await get_topic_id(session, topic)
    style_id = await get_style_id(session, style)
    new_info = POIInfoText(
        poi_id=poi_id,
        info_text=info_text,
        prompt=prompt,
        topic_id=topic_id,
        style_id=style_id,
        source=source,
        status=status,
        task_id=task_id,
    )
    session.add(new_info)
    await session.commit()
    await session.refresh(new_info)
    return new_info


# ---- Read (get all for a POI) ----
async def get_poi_info_texts(
    session: AsyncSession,
    poi_id: int,
    topic: Optional[str] = None,
    style: Optional[str] = None,
) -> List[POIInfoText]:
    stmt = select(POIInfoText).where(POIInfoText.poi_id == poi_id)
    if topic:
        topic_id = await get_topic_id(session, topic)
        stmt = stmt.where(POIInfoText.topic_id == topic_id)
    if style:
        style_id = await get_style_id(session, style)
        stmt = stmt.where(POIInfoText.style_id == style_id)
    stmt = stmt.options(joinedload(POIInfoText.topic), joinedload(POIInfoText.style))
    result = await session.execute(stmt)
    return result.scalars().all()


# ---- Read by ID ----
async def get_poi_info_text_by_id(
    session: AsyncSession, info_id: int
) -> Optional[POIInfoText]:
    stmt = (
        select(POIInfoText)
        .options(joinedload(POIInfoText.topic), joinedload(POIInfoText.style))
        .where(POIInfoText.id == info_id)
    )
    result = await session.execute(stmt)
    return result.scalars().first()


# ---- Update ----
async def update_poi_info_text(
    session: AsyncSession, info_id: int, **kwargs
) -> Optional[POIInfoText]:
    # Convert topic/style from name to ID if present
    if "topic" in kwargs and kwargs["topic"] is not None:
        kwargs["topic_id"] = await get_topic_id(session, kwargs.pop("topic"))
    if "style" in kwargs and kwargs["style"] is not None:
        kwargs["style_id"] = await get_style_id(session, kwargs.pop("style"))
    stmt = (
        update(POIInfoText)
        .where(POIInfoText.id == info_id)
        .values(**kwargs)
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(stmt)
    await session.commit()
    return await get_poi_info_text_by_id(session, info_id)


# ---- Delete ----
async def delete_poi_info_text(session: AsyncSession, info_id: int) -> None:
    stmt = delete(POIInfoText).where(POIInfoText.id == info_id)
    await session.execute(stmt)
    await session.commit()
