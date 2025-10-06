from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from .api.routes import agents, orchestrate, health

def create_app() -> FastAPI:
    app = FastAPI(
        title="Interflow Agent Orchestration API",
        description="Async backend coordinating specialized agents and workflows.",
        version="0.1.0"
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict in prod!
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handling
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error": str(exc)},
        )

    # Include routers
    app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
    app.include_router(orchestrate.router, prefix="/api/orchestrate", tags=["Orchestration"])
    app.include_router(health.router, prefix="/api/health", tags=["Health"])

    return app

app = create_app()
