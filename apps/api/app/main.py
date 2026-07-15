from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(
    title="推薦業務支援システム API",
    version="0.1.0",
    description="推薦業務を支援するためのREST API。AIは業務判断を行わない。",
)

app.include_router(health_router)
