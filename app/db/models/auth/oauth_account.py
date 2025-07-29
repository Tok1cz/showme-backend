from fastapi_users_db_sqlalchemy import SQLAlchemyBaseOAuthAccountTable
from app.db.declarative_base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer

class OAuthAccount(SQLAlchemyBaseOAuthAccountTable, Base):
    __tablename__ = "oauth_accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

