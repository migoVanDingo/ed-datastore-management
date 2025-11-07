from fastapi import Request, Depends
from platform_common.models.datastore import Datastore
from platform_common.db.dal.datastore_dal import DatastoreDAL
from platform_common.db.dependencies.get_dal import get_dal
from platform_common.utils.service_response import ServiceResponse
from platform_common.logging.logging import get_logger
from platform_common.errors.base import (
    BadRequestError,
)
from app.api.interface.abstract_handler import AbstractHandler

logger = get_logger("create_datastore_handler")


class CreateDatastoreHandler(AbstractHandler):
    """
    Handler for creating a datastore.
    """

    def __init__(
        self,
        datastore_dal: DatastoreDAL = Depends(get_dal(DatastoreDAL)),
    ):
        super().__init__()
        self.datastore_dal = datastore_dal

    async def do_process(self, request: Request) -> ServiceResponse:
        """
        Handle the request to create a datastore.
        """
        try:
            payload = await request.json()
            datastore = Datastore(**payload)

        except TypeError as e:
            logger.error(f"Error creating datastore: {e}")
            raise BadRequestError(
                message="Invalid datastore data", code="INVALID_PAYLOAD"
            )

        created_datastore = await self.datastore_dal.create(datastore)
        logger.info(f"Datastore created: {created_datastore.id}")
        return ServiceResponse(
            message="Datastore created successfully",
            status_code=201,
            data=created_datastore.dict(),
        )
