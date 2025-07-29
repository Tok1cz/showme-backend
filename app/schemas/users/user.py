from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from typing import Optional
from uuid import UUID

class UserRead(BaseUser[int]):
    id: int
    email: str
    role: str
    consent_given: bool

class UserCreate(BaseUserCreate):
    email: str
    password: str
    role: Optional[str] = "user"
    consent_given: Optional[bool] = False

class UserUpdate(BaseUserUpdate):
    role: Optional[str]
    consent_given: Optional[bool]