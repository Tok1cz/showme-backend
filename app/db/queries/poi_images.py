# app/db/queries.py

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.db.models import POIImage

# ---- Create ----
async def create_poi_image(
    session: AsyncSession,
    *,
    poi_id: int,
    geometry_type: str,
    filename: str,
    image_url: Optional[str] = None,
    prompt: Optional[str] = None,
    source: Optional[str] = None,
    style: Optional[str] = None,
    resolution: str = "medium",
    status: str = "ready",
) -> POIImage:
    """
    Create and persist a new POI image record.
    """
    new_image = POIImage(
        poi_id=poi_id,
        geometry_type=geometry_type,
        filename=filename,
        image_url=image_url,
        prompt=prompt,
        source=source,
        style=style,
        resolution=resolution,
        status=status,
    )
    session.add(new_image)
    await session.commit()
    await session.refresh(new_image)
    return new_image

# ---- Read (get all for a POI) ----
async def get_poi_images(
    session: AsyncSession,
    poi_id: int,
    geometry_type: Optional[str] = None,
    resolution: Optional[str] = None,
) -> List[POIImage]:
    """
    Get all images for a POI, optionally filtered by geometry_type and/or resolution.
    """
    stmt = select(POIImage).where(POIImage.poi_id == poi_id)
    if geometry_type:
        stmt = stmt.where(POIImage.geometry_type == geometry_type)
    if resolution:
        stmt = stmt.where(POIImage.resolution == resolution)
    result = await session.execute(stmt)
    return result.scalars().all()

# ---- Read (get by image id) ----
async def get_poi_image_by_id(session: AsyncSession, image_id: int) -> Optional[POIImage]:
    stmt = select(POIImage).where(POIImage.id == image_id)
    result = await session.execute(stmt)
    return result.scalars().first()

# ---- Update ----
async def update_poi_image(
    session: AsyncSession,
    image_id: int,
    **kwargs
) -> Optional[POIImage]:
    """
    Update fields on a POIImage by id. kwargs can include any POIImage column.
    """
    stmt = (
        update(POIImage)
        .where(POIImage.id == image_id)
        .values(**kwargs)
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(stmt)
    await session.commit()
    return await get_poi_image_by_id(session, image_id)

# ---- Delete ----
async def delete_poi_image(session: AsyncSession, image_id: int) -> None:
    stmt = delete(POIImage).where(POIImage.id == image_id)
    await session.execute(stmt)
    await session.commit()
