from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.db.enums import TextLength
from app.db.declarative_base import Base

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
        UniqueConstraint("provider", "model", "topic_id", "style_id", "version", name="uq_prompt_template"),
    )
