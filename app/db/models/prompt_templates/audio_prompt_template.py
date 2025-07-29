from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from app.db.base import Base

class AudioPromptTemplate(Base):
    __tablename__ = "audio_prompt_templates"

    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    voice_id = Column(Integer, ForeignKey("audio_voices.id"))
    version = Column(Integer, nullable=False)
    template = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
