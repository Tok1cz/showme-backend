# app/db/queries/prompt_templates.py

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.prompt_template import PromptTemplate

async def get_prompt_template(
    session: AsyncSession,
    provider: str,
    model: str,
    topic_id: int,
    style_id: int,
    version: Optional[int] = None
):
    stmt = select(PromptTemplate).where(
        PromptTemplate.provider == provider,
        PromptTemplate.model == model,
        PromptTemplate.topic_id == topic_id,
        PromptTemplate.style_id == style_id
    )
    if version:
        stmt = stmt.where(PromptTemplate.version == version)
    else:
        # get the latest version
        stmt = stmt.order_by(PromptTemplate.version.desc())
    result = await session.execute(stmt)
    return result.scalars().first()
