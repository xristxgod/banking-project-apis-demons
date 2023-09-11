from datetime import datetime

import sqlalchemy as fields
from sqlalchemy import Column


class DateTimeMixin:
    created_at = Column(fields.DateTime(), default=datetime.now())
    updated_at = Column(fields.DateTime(), onupdate=datetime.now())
