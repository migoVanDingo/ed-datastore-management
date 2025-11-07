import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.controller.health_check import router as health_router
from app.listeners.user_changes_subscriber import start_user_changes_subscriber
from platform_common.logging.logging import get_logger

logger = get_logger("datastore_lifespan")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Datastore service starting user_changes subscriber…")
    task = asyncio.create_task(start_user_changes_subscriber())
    app.state.user_changes_task = task
    try:
        yield
    finally:
        logger.info("Datastore service shutting down user_changes subscriber…")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info("User_changes subscriber cancelled cleanly.")


app = FastAPI(title="Core Service", lifespan=lifespan)

# REST endpoints
app.include_router(health_router, prefix="/health", tags=["Health"])
