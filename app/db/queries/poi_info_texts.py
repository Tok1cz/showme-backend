from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.db.models import POIInfoText

# ---- Create ----
async def create_poi_info_text(
    session: AsyncSession,
    *,
    poi_id: int,
    geometry_type: str,
    info_text: str,
    prompt: Optional[str] = None,
    topic: Optional[str] = "general",
    style: Optional[str] = None,
    source: Optional[str] = None,
    status: Optional[str] = "ready",
) -> POIInfoText:
    new_info = POIInfoText(
        poi_id=poi_id,
        geometry_type=geometry_type,
        info_text=info_text,
        prompt=prompt,
        topic=topic,
        style=style,
        source=source,
        status=status,
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
        stmt = stmt.where(POIInfoText.topic == topic)
    if style:
        stmt = stmt.where(POIInfoText.style == style)
    result = await session.execute(stmt)
    return result.scalars().all()

# ---- Read by ID ----
async def get_poi_info_text_by_id(session: AsyncSession, info_id: int) -> Optional[POIInfoText]:
    stmt = select(POIInfoText).where(POIInfoText.id == info_id)
    result = await session.execute(stmt)
    return result.scalars().first()

# ---- Update ----
async def update_poi_info_text(
    session: AsyncSession,
    info_id: int,
    **kwargs
) -> Optional[POIInfoText]:
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
