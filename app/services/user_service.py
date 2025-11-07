from __future__ import annotations

from typing import Any, Dict, Optional

from platform_common.db.session import get_session
from platform_common.db.dal.datastore_dal import DatastoreDAL
from platform_common.models.datastore import Datastore
from platform_common.logging.logging import get_logger


class UserService:
    """
    Contains datastore-side reactions to user lifecycle events (e.g., verification).
    """

    def __init__(self):
        self.logger = get_logger("datastore_user_service")

    async def handle_user_verified(self, payload: Dict[str, Any]) -> None:
        """
        Called whenever we receive a user_verified event.
        Currently provisions a default datastore for the user if they don't
        already have one.
        """
        user_id: Optional[str] = payload.get("id")
        if not user_id:
            self.logger.warning(
                "[user_verified] Missing user id in payload: %s", payload
            )
            return

        username = payload.get("username") or payload.get("email") or user_id
        datastore_name = f"{username}'s Workspace"

        try:
            async for session in get_session():
                dal = DatastoreDAL(session)

                existing = await dal.get_by_user(user_id)
                if existing:
                    self.logger.info(
                        "[user_verified] User %s already has %s datastore(s); skipping provisioning",
                        user_id,
                        len(existing),
                    )
                    break

                datastore = Datastore(
                    name=datastore_name,
                    description="Default datastore provisioned after verification",
                    owner_id=user_id,
                    owner_type="user",
                    user_id=user_id,
                )

                await dal.save(datastore)
                self.logger.info(
                    "[user_verified] Provisioned datastore %s for user %s",
                    datastore.id,
                    user_id,
                )
                break
        except Exception:
            self.logger.exception(
                "[user_verified] Failed provisioning datastore for user %s", user_id
            )
