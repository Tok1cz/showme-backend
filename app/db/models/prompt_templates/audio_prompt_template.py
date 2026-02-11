from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.db.declarative_base import Base


class AudioPromptTemplate(Base):
    __tablename__ = "audio_prompt_templates"

    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    voice_id = Column(Integer, ForeignKey("audio_voices.id"))
    version = Column(Integer, nullable=False)
    template = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
