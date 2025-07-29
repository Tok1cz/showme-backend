from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.models.poi_enhancements import InformationStyle, InformationTopic, ImageStyle
from app.db.session import get_session
from app.schemas.refdata import RefDataOut

router = APIRouter(prefix="/refdata",)

@router.get("/information-styles/", response_model=List[RefDataOut])
async def list_information_styles(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(InformationStyle))
    return result.scalars().all()

@router.get("/information-topics/", response_model=List[RefDataOut])
async def list_information_topics(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(InformationTopic))
    return result.scalars().all()

@router.get("/image-styles/", response_model=List[RefDataOut])
async def list_image_styles(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(ImageStyle))
    return result.scalars().all()
