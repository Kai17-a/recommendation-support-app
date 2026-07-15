from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.routes.admin import router as admin_router
from app.api.routes.ai import router as ai_router
from app.api.routes.evaluations import router as evaluations_router
from app.api.routes.health import router as health_router
from app.api.routes.markdown_imports import router as markdown_imports_router
from app.api.routes.members import router as members_router
from app.api.routes.projects import router as projects_router
from app.api.routes.recommendations import (
    router as recommendation_router,
)
from app.api.routes.recommendations import (
    version_router as recommendation_version_router,
)
from app.api.routes.reports import router as reports_router
from app.api.routes.skills import router as skills_router
from app.core.errors import ApiError, api_error_handler, validation_error_handler
from app.core.observability import RequestContextMiddleware, configure_logging

configure_logging()

app = FastAPI(
    title="推薦業務支援システム API",
    version="0.1.0",
    description="推薦業務を支援するためのREST API。AIは業務判断を行わない。",
)

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_middleware(RequestContextMiddleware)
app.include_router(health_router)
app.include_router(admin_router)
app.include_router(ai_router)
app.include_router(evaluations_router)
app.include_router(members_router)
app.include_router(markdown_imports_router)
app.include_router(projects_router)
app.include_router(reports_router)
app.include_router(skills_router)
app.include_router(recommendation_router)
app.include_router(recommendation_version_router)
