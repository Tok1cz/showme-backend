from app.db.declarative_base import Base
from app.db.models.auth.api_key import APIKey
from app.db.models.auth.oauth_account import OAuthAccount
from app.db.models.generation_jobs.audio_generation_job import AudioGenerationJob
from app.db.models.generation_jobs.image_generation_job import ImageGenerationJob
from app.db.models.generation_jobs.text_generation_job import TextGenerationJob
from app.db.models.log_models import OSMImportLog
from app.db.models.poi_enhancements.generation_sources import GenerationSource
from app.db.models.poi_enhancements.poi_audio import POIAudio
from app.db.models.poi_enhancements.poi_image import POIImage
from app.db.models.poi_enhancements.poi_info_text import (
    InformationStyle,
    InformationTopic,
    POIInfoText,
)
from app.db.models.prompt_templates.audio_prompt_template import AudioPromptTemplate
from app.db.models.prompt_templates.image_prompt_template import ImagePromptTemplate
from app.db.models.prompt_templates.text_prompt_template import TextPromptTemplate
from app.db.models.user.audit_log import AuditLog

# Import all models so Alembic can detect them for migrations
from app.db.models.user.user import User

# Add any additional models as needed
