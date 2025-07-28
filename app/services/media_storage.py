from app.core.settings import settings

def upload_to_cdn(filename: str, data: bytes) -> str:
    # Upload to S3, GCS, etc.
    # Return the CDN/public URL for the uploaded file.
    raise NotImplementedError("CDN uploading not implemented yet")


class MediaStorage:
    @staticmethod
    def save_audio(filename: str, audio_bytes: bytes) -> str:
        if settings.MEDIA_STORAGE_BACKEND == "local":
            path = f"./audio/{filename}"
            with open(path, "wb") as f:
                f.write(audio_bytes)
            return f"/audio/{filename}"
        elif settings.MEDIA_STORAGE_BACKEND == "cdn":
            # Replace with actual CDN/bucket logic
            # Example: upload to S3/GCS, then return public URL
            url = upload_to_cdn(filename, audio_bytes)
            return url
        else:
            raise ValueError("Invalid MEDIA_STORAGE_BACKEND setting.")

    @staticmethod
    def save_image(filename: str, image_bytes: bytes) -> str:
        if settings.MEDIA_STORAGE_BACKEND == "local":
            path = f"./images/{filename}"
            with open(path, "wb") as f:
                f.write(image_bytes)
            return f"/images/{filename}"
        elif settings.MEDIA_STORAGE_BACKEND == "cdn":
            url = upload_to_cdn(filename, image_bytes)
            return url
        else:
            raise ValueError("Invalid MEDIA_STORAGE_BACKEND setting.")
