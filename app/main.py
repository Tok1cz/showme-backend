from fastapi import FastAPI
from app.api.routes import pois, health

app = FastAPI()

app.include_router(pois.router, prefix="/pois", tags=["POIs"])
app.include_router(health.router)