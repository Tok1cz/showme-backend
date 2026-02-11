from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

from app.db.declarative_base import Base
from app.db.enums import TextLength


class TextPromptTemplate(Base):
    __tablename__ = "text_prompt_templates"

    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    topic_id = Column(Integer, nullable=False)
    style_id = Column(Integer, nullable=False)
    version = Column(Integer, nullable=False)
    template = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    text_length = Column(Enum(TextLength, name="text_length"), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "model",
            "topic_id",
            "style_id",
            "version",
            name="uq_prompt_template",
        ),
    )
