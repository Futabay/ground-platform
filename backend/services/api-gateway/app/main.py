from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.telemetry import router as telemetry_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Ground Data Platform API Gateway",
        version="0.1.0",
    )

    # Include routes
    app.include_router(health_router, prefix="/health", tags=["Health"])
    app.include_router(telemetry_router, prefix="/telemetry", tags=["Telemetry"])

    return app


app = create_app()
