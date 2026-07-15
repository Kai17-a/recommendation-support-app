from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.members import router as members_router
from app.api.routes.projects import router as projects_router
from app.core.errors import ApiError, api_error_handler

app = FastAPI(
    title="推薦業務支援システム API",
    version="0.1.0",
    description="推薦業務を支援するためのREST API。AIは業務判断を行わない。",
)

app.add_exception_handler(ApiError, api_error_handler)
app.include_router(health_router)
app.include_router(members_router)
app.include_router(projects_router)
