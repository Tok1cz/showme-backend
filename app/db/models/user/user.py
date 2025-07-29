# app/db/models/user.py
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from app.db.declarative_base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Integer, Enum

from app.db.enums.user_role import UserRole


class User(SQLAlchemyBaseUserTable, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False, default=UserRole.user.value
    )
    consent_given: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

