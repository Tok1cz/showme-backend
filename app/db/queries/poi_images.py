# app/db/queries/poi_images.py

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.orm import joinedload

from app.db.models.poi_models import POIImage, ImageStyle
from app.db.enums import GeometryType, Resolution

# ---- Helper: Resolve style name to ID ----

async def get_style_id(session: AsyncSession, style_name: Optional[str]) -> Optional[int]:
    if not style_name:
        return None
    result = await session.execute(
        select(ImageStyle).where(ImageStyle.name == style_name)
    )
    style = result.scalar_one_or_none()
    if not style:
        raise ValueError(f"Unknown image style: {style_name}")
    return style.id

# ---- Create ----
async def create_poi_image(
    session: AsyncSession,
    *,
    poi_id: int,
    geometry_type: GeometryType,
    filename: str,
    resolution: Resolution,
    style: Optional[str] = None,
    image_url: Optional[str] = None,
    prompt: Optional[str] = None,
    source: Optional[str] = None,
    status: str = "ready",
) -> POIImage:
    style_id = await get_style_id(session, style)
    new_image = POIImage(
        poi_id=poi_id,
        geometry_type=geometry_type,
        filename=filename,
        image_url=image_url,
        prompt=prompt,
        source=source,
        style_id=style_id,
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
    geometry_type: Optional[GeometryType] = None,
    resolution: Optional[Resolution] = None,
    style: Optional[str] = None,
) -> List[POIImage]:
    stmt = select(POIImage).where(POIImage.poi_id == poi_id)
    if geometry_type:
        stmt = stmt.where(POIImage.geometry_type == geometry_type)
    if resolution:
        stmt = stmt.where(POIImage.resolution == resolution)
    if style:
        style_id = await get_style_id(session, style)
        stmt = stmt.where(POIImage.style_id == style_id)
    stmt = stmt.options(joinedload(POIImage.style))
    result = await session.execute(stmt)
    return result.scalars().all()

# ---- Read (get by image id) ----
async def get_poi_image_by_id(session: AsyncSession, image_id: int) -> Optional[POIImage]:
    stmt = (
        select(POIImage)
        .options(joinedload(POIImage.style))
        .where(POIImage.id == image_id)
    )
    result = await session.execute(stmt)
    return result.scalars().first()

# ---- Update ----
async def update_poi_image(
    session: AsyncSession,
    image_id: int,
    **kwargs
) -> Optional[POIImage]:
    # If "style" present in kwargs, resolve to style_id
    if "style" in kwargs and kwargs["style"] is not None:
        kwargs["style_id"] = await get_style_id(session, kwargs.pop("style"))
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

# ---- Bulk get for list of POI IDs ----
async def get_images_for_poi_ids(session: AsyncSession, ids: list[int]) -> list[POIImage]:
    stmt = select(POIImage).where(POIImage.poi_id.in_(ids)).options(joinedload(POIImage.style))
    result = await session.execute(stmt)
    return result.scalars().all()
