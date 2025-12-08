from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.health import router as health_router
from app.routes.telemetry import router as telemetry_router

from prometheus_fastapi_instrumentator import Instrumentator

def create_app() -> FastAPI:
    app = FastAPI(
        title="Ground Data Platform API Gateway",
        version="0.1.0",
    )

    # Allow local frontend dev
    origins = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # if you ever use that
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(health_router, prefix="/health", tags=["Health"])
    app.include_router(telemetry_router, prefix="/telemetry", tags=["Telemetry"])

    Instrumentator().instrument(app).expose(app)

    return app


app = create_app()
