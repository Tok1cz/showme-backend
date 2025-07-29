def serialize_poi_image(img, base_image_url=None):
    return {
        "id": img.id,
        "poi_id": img.poi_id,
        "filename": img.filename,
        "resolution": img.resolution,
        "style": {
            "id": img.style.id,
            "name": img.style.name,
        } if img.style else None,
        "image_url": (img.image_url if img.image_url else (base_image_url + img.filename) if base_image_url else None),
        "prompt": img.prompt,
        "source": img.source,
        "status": img.status,
        "created_at": img.created_at,
        "updated_at": img.updated_at,
    }


def serialize_poi_info_text(info):
    return {
        "id": info.id,
        "poi_id": info.poi_id,
        "info_text": info.info_text,
        "prompt": info.prompt,
        "topic": {
            "id": info.topic.id,
            "name": info.topic.name,
        } if info.topic else None,
        "style": {
            "id": info.style.id,
            "name": info.style.name,
        } if info.style else None,
        "source": info.source,
        "status": info.status,
        "created_at": info.created_at,
        "updated_at": info.updated_at,
    }