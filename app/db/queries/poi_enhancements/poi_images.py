from typing import List, Optional

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.db.enums import ImageResolution
from app.db.models.poi_enhancements import ImageAspect, ImageStyle, POIImage

# ---- Helper: Resolve style name to ID ----


async def get_style_id(
    session: AsyncSession, style_name: Optional[str]
) -> Optional[int]:
    if not style_name:
        return None
    result = await session.execute(
        select(ImageStyle).where(ImageStyle.name == style_name)
    )
    style = result.scalar_one_or_none()
    if not style:
        raise ValueError(f"Unknown image style: {style_name}")
    return style.id


# ---- Helper: Resolve aspect name to ID ----


async def get_aspect_id(
    session: AsyncSession, aspect_name: Optional[str]
) -> Optional[int]:
    if not aspect_name:
        return None
    result = await session.execute(
        select(ImageAspect).where(ImageAspect.name == aspect_name)
    )
    aspect = result.scalar_one_or_none()
    if not aspect:
        raise ValueError(f"Unknown image aspect: {aspect_name}")
    return aspect.id


# ---- Create ----
async def create_poi_image(
    session: AsyncSession,
    *,
    poi_id: int,
    filename: str,
    image_url: str,
    resolution: ImageResolution,
    style: Optional[str] = None,
    aspect: Optional[str] = None,
    prompt: Optional[str] = None,
    source: Optional[str] = None,
    status: str = "active",
    task_id: Optional[str] = None,
) -> POIImage:
    style_id = await get_style_id(session, style)
    aspect_id = await get_aspect_id(session, aspect) if aspect else None
    new_image = POIImage(
        poi_id=poi_id,
        filename=filename,
        image_url=image_url,
        prompt=prompt,
        source=source,
        style_id=style_id,
        aspect_id=aspect_id,
        resolution=resolution,
        status=status,
        task_id=task_id,
    )
    session.add(new_image)
    await session.commit()
    await session.refresh(new_image)
    return new_image


# ---- Read (get all for a POI) ----
async def get_poi_images(
    session: AsyncSession,
    poi_id: int,
    resolution: Optional[ImageResolution] = None,
    style: Optional[str] = None,
    aspect: Optional[str] = None,
) -> List[POIImage]:
    stmt = select(POIImage).where(POIImage.poi_id == poi_id)
    if resolution:
        stmt = stmt.where(POIImage.resolution == resolution)
    if style:
        style_id = await get_style_id(session, style)
        stmt = stmt.where(POIImage.style_id == style_id)
    if aspect:
        aspect_id = await get_aspect_id(session, aspect)
        stmt = stmt.where(POIImage.aspect_id == aspect_id)
    stmt = stmt.options(joinedload(POIImage.style), joinedload(POIImage.aspect))
    result = await session.execute(stmt)
    return result.scalars().all()


# ---- Read (get by image id) ----
async def get_poi_image_by_id(
    session: AsyncSession, image_id: int
) -> Optional[POIImage]:
    stmt = (
        select(POIImage)
        .options(joinedload(POIImage.style), joinedload(POIImage.aspect))
        .where(POIImage.id == image_id)
    )
    result = await session.execute(stmt)
    return result.scalars().first()


# ---- Update ----
async def update_poi_image(
    session: AsyncSession, image_id: int, **kwargs
) -> Optional[POIImage]:
    # If "style" present in kwargs, resolve to style_id
    if "style" in kwargs and kwargs["style"] is not None:
        kwargs["style_id"] = await get_style_id(session, kwargs.pop("style"))
    if "aspect" in kwargs and kwargs["aspect"] is not None:
        kwargs["aspect_id"] = await get_aspect_id(session, kwargs.pop("aspect"))
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
async def get_images_for_poi_ids(
    session: AsyncSession, ids: list[int]
) -> list[POIImage]:
    stmt = (
        select(POIImage)
        .where(POIImage.poi_id.in_(ids))
        .options(joinedload(POIImage.style), joinedload(POIImage.aspect))
    )
    result = await session.execute(stmt)
    return result.scalars().all()
