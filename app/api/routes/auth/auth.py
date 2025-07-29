from fastapi import APIRouter
from app.services.auth.oauth import fastapi_users, google_oauth_client, oauth_backend
from app.core.settings import settings
# TODO:
# Actually register with Oauth Provider
router = APIRouter(prefix="/auth")

router.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        oauth_backend,
        state_secret=settings.JWT_SECRET,
        redirect_url="http://localhost:8000/auth/google/callback",
    ),
    prefix="/google",
)