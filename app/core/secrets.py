import os

from app.core.settings import settings


# Not sure if this is needed...
def get_secret(key: str) -> str:
    """
    Get a secret by key.
    - In dev/test: from settings/env.
    - In prod: (placeholder) from cloud secret manager.
    """
    app_env = getattr(settings, "APP_ENV", os.getenv("APP_ENV", "dev"))
    if app_env in ("dev", "test"):
        value = getattr(settings, key, None)
        if value is not None:
            return value
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
        raise RuntimeError(f"Secret '{key}' not found in settings or environment.")
    else:
        # for now (Raspi local deployment) prod is the same as dev/test
        # We cannot use the dev flag tho, as we want actual auth!
        value = getattr(settings, key, None)
        if value is not None:
            return value
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
        # raise NotImplementedError("Cloud secret manager integration for prod not implemented yet.")
