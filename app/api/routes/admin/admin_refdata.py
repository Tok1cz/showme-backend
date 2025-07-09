from fastapi import APIRouter, Depends, HTTPException, status
from app.db.queries.admin_refdata import (
    add_image_style, delete_image_style,
    add_information_style, delete_information_style,
    add_information_topic, delete_information_topic,
)
from app.db.session import get_session
from app.schemas.admin_refdata import RefDataCreate, RefDataOut

router = APIRouter(prefix="/refdata", tags=["Admin: Reference Data"])

# ---- Image Styles ----
@router.post("/image-styles/", response_model=RefDataOut, status_code=201)
async def create_image_style(data: RefDataCreate, session=Depends(get_session)):
    return await add_image_style(session, data.name)

@router.delete("/image-styles/{style_id}", status_code=204)
async def remove_image_style(style_id: int, session=Depends(get_session)):
    await delete_image_style(session, style_id)
    return

# ---- Information Styles ----
@router.post("/information-styles/", response_model=RefDataOut, status_code=201)
async def create_information_style(data: RefDataCreate, session=Depends(get_session)):
    return await add_information_style(session, data.name)

@router.delete("/information-styles/{style_id}", status_code=204)
async def remove_information_style(style_id: int, session=Depends(get_session)):
    await delete_information_style(session, style_id)
    return

# ---- Information Topics ----
@router.post("/information-topics/", response_model=RefDataOut, status_code=201)
async def create_information_topic(data: RefDataCreate, session=Depends(get_session)):
    return await add_information_topic(session, data.name)

@router.delete("/information-topics/{topic_id}", status_code=204)
async def remove_information_topic(topic_id: int, session=Depends(get_session)):
    await delete_information_topic(session, topic_id)
    return
