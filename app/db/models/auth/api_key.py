from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from app.db.declarative_base import Base

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    key_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True))
    revoked = Column(Boolean, nullable=False, default=False)