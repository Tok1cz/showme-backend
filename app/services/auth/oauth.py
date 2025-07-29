from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from httpx_oauth.clients.google import GoogleOAuth2

from app.db.session import get_session
from app.db.models.user.user import User
from app.db.models.auth.oauth_account import OAuthAccount
from app.core.settings import settings
from app.services.auth.user_manager import get_user_manager

cookie_transport = CookieTransport(cookie_name="auth", cookie_max_age=3600)

oauth_backend = AuthenticationBackend(
    name="google",
    transport=cookie_transport,
    get_strategy=None,  # For OAuth, you can set this to None
)

google_oauth_client = GoogleOAuth2(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [],
)

