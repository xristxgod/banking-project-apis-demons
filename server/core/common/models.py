import sqlalchemy as fields
from sqlalchemy import Column

from config.database import Base


class Model(Base):
    __abstract__ = True
    __tablename__ = NotImplementedError

    id = Column(fields.Integer, primary_key=True, autoincrement=True)

    @property
    def pk(self) -> int:
        return self.id

    def __repr__(self):
        return f'{self.id}'
