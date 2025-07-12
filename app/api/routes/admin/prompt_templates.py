from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.models.prompt_template import PromptTemplate
from app.schemas.prompt_template import PromptTemplateOut, PromptTemplateCreate, PromptTemplateUpdate
from app.db.session import get_session

router = APIRouter(prefix="/prompt-templates", )

# --- LIST ALL ---
@router.get("/", response_model=List[PromptTemplateOut])
async def list_prompt_templates(db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(PromptTemplate).order_by(PromptTemplate.created_at.desc())
    )
    return result.scalars().all()

# --- GET BY ID ---
@router.get("/{template_id}", response_model=PromptTemplateOut)
async def get_prompt_template(template_id: int, db: AsyncSession = Depends(get_session)):
    template = await db.get(PromptTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return template

# --- CREATE ---
@router.post("/", response_model=PromptTemplateOut, status_code=status.HTTP_201_CREATED)
async def create_prompt_template(data: PromptTemplateCreate, db: AsyncSession = Depends(get_session)):
    tmpl = PromptTemplate(**data.dict())
    db.add(tmpl)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    await db.refresh(tmpl)
    return tmpl

# --- UPDATE ---
@router.patch("/{template_id}", response_model=PromptTemplateOut)
async def update_prompt_template(template_id: int, data: PromptTemplateUpdate, db: AsyncSession = Depends(get_session)):
    tmpl = await db.get(PromptTemplate, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(tmpl, field, value)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    await db.refresh(tmpl)
    return tmpl

# --- DELETE ---
@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt_template(template_id: int, db: AsyncSession = Depends(get_session)):
    tmpl = await db.get(PromptTemplate, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    await db.delete(tmpl)
    await db.commit()
