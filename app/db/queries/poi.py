# app/db/queries.py
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional


# N nearest attractions to a given lat/lon, with optional tag filtering
async def get_n_nearest_attractions(
    session: AsyncSession,
    lat: float,
    lon: float,
    n: int = 10,
    skip: int = 0,
    extra_where: str = "",
):
    sql = f"""
        SELECT
            osm_id AS id,
            name,
            tags,
            tags->'description' AS description,
            way AS geometry,
            GeometryType(way) as structure_type,
            ST_X(ST_Centroid(way)) AS lon,
            ST_Y(ST_Centroid(way)) AS lat,
            ST_Distance(
                way::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            ) AS distance_m
        FROM (
            SELECT osm_id, name, tags, tags->'description' AS description, way FROM planet_osm_point WHERE name IS NOT NULL {extra_where}
            UNION ALL
            SELECT osm_id, name, tags, tags->'description' AS description, way FROM planet_osm_polygon WHERE name IS NOT NULL {extra_where}
            UNION ALL
            SELECT osm_id, name, tags, tags->'description' AS description, way FROM planet_osm_line WHERE name IS NOT NULL {extra_where}
        ) AS all_attractions
        ORDER BY distance_m ASC
        LIMIT :n OFFSET :skip
        """
    result = await session.execute(
        text(sql), {"lat": lat, "lon": lon, "n": n, "skip": skip}
    )
    rows = result.mappings().all()
    return rows



async def get_poi_by_id(session, poi_id: int):
    sql = """
        SELECT
            osm_id AS id,
            name,
            tags,
            tags->'description' AS description,
            way AS geometry,
            GeometryType(way) as structure_type,
            ST_X(ST_Centroid(way)) AS lon,
            ST_Y(ST_Centroid(way)) AS lat
        FROM (
            SELECT osm_id, name, tags, tags->'description' AS description, way FROM planet_osm_point WHERE osm_id = :poi_id
            UNION ALL
            SELECT osm_id, name, tags, tags->'description' AS description, way FROM planet_osm_polygon WHERE osm_id = :poi_id
            UNION ALL
            SELECT osm_id, name, tags, tags->'description' AS description, way FROM planet_osm_line WHERE osm_id = :poi_id
        ) AS all_pois
        LIMIT 1
    """
    result = await session.execute(text(sql), {"poi_id": poi_id})
    row = result.mappings().first()
    return row
