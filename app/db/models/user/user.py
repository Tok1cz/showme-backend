# app/db/models/user/user.py
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.declarative_base import Base
from app.db.enums.user_role import UserRole


class User(SQLAlchemyBaseUserTable, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False, default=UserRole.user.value
    )
    consent_given: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
