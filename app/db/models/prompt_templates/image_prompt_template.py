from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from app.db.declarative_base import Base

class ImagePromptTemplate(Base):
    __tablename__ = "image_prompt_templates"

    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    style_id = Column(Integer, ForeignKey("image_styles.id"))
    aspect_id = Column(Integer, ForeignKey("image_aspects.id"))
    version = Column(Integer, nullable=False)
    template = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
