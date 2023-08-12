import uuid

from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func


class BaseModelWithDateTimeMixin:
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __mapper_args__ = {'always_refresh': True}
