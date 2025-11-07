import asyncio

from platform_common.logging.logging import get_logger
from platform_common.pubsub.event import PubSubEvent
from platform_common.pubsub.factory import get_subscriber

from app.services.user_service import UserService

logger = get_logger("datastore_user_changes_subscriber")
CHANNEL = "user:changes"

user_service = UserService()


async def _handle_user_verified(event: PubSubEvent) -> None:
    await user_service.handle_user_verified(event.payload or {})


async def _handle_fallback(event: PubSubEvent) -> None:
    logger.debug(
        "[user_changes] Ignoring event type=%s payload=%s",
        event.event_type,
        event.payload,
    )


async def start_user_changes_subscriber() -> None:
    """
    Blocks forever (until cancelled) while listening to user changes from Redis.
    """
    subscriber = get_subscriber()
    logger.info("Datastore subscriber listening on channel '%s'", CHANNEL)
    try:
        await subscriber.subscribe(
            {
                CHANNEL: {
                    "user_verified": _handle_user_verified,
                    "*": _handle_fallback,
                }
            }
        )
    except asyncio.CancelledError:
        logger.info("Datastore user_changes subscriber cancelled.")
        raise
    except Exception:
        logger.exception("Datastore user_changes subscriber crashed.")
        raise
