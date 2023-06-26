import logging
import os.path

from fastapi import FastAPI
from loguru import logger
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from flightgear_bridge import api
from flightgear_bridge.config import config

PREFIX = "/api/v1"
HEALTHCHECK_ENDPOINT = f"{PREFIX}/healthcheck"


class EndpointFilter(logging.Filter):
    """Filter to remove some endpoints from access logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter the logs to remove healthcheck endpoint."""
        return record.getMessage().find(HEALTHCHECK_ENDPOINT) == -1


# Filter out healthcheck calls
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


def create_app(root_dir: str) -> FastAPI:
    """Create the FastAPI app."""

    app = FastAPI(
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            ),
        ],
    )

    app.include_router(api.router, prefix=PREFIX)
    app.mount(
        "/dashboard",
        StaticFiles(
            directory=os.path.join(root_dir, "ui"),
            html=True,
            follow_symlink=False,
        ),
        name="dashboard",
    )

    @app.on_event("startup")
    def startup_event():
        """Handle the app startup event."""
        logger.info(f"Ready @ http://{config.HTTP_HOST}:{config.HTTP_PORT}")

    @app.on_event("shutdown")
    def shutdown_event():
        """Handle the app shutdown event."""
        logger.info("Shutting down")

    @app.get("/")
    def redirect_to_dashboard():
        """Redirect to the dashboard."""
        return RedirectResponse(url="/dashboard")

    @app.get(HEALTHCHECK_ENDPOINT)
    async def healthcheck():
        """Check if api is up & running."""
        return {"status": "ok"}

    return app
