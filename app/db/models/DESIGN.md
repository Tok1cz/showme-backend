1. Purposefully not modelling POIs themselves 
    - as their logic is handled by the postgres osm import logic
    - adding the SQL models would probably
    - cause alembic to interfere with the osm imports.