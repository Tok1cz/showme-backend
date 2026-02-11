from fastapi_users_db_sqlalchemy import SQLAlchemyBaseOAuthAccountTable
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.declarative_base import Base


class OAuthAccount(SQLAlchemyBaseOAuthAccountTable, Base):
    __tablename__ = "oauth_accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
