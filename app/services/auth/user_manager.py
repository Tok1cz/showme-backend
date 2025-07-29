from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.manager import BaseUserManager
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from app.db.models.user.user import User
from app.db.models.auth.oauth_account import OAuthAccount
from app.core.settings import settings
from app.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)

class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET

    # Add custom logic here (optional)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


