import uuid

from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy.orm import relationship
from sqlalchemy import BIGINT, Boolean, Column, ForeignKey, String

from core.database import Base
from common.mixins import BaseModelWithDateTimeMixin

from apps.languages.models import Language


class UserConfig(Base):
    __tablename__ = 'users__user_config'

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey('telegram__telegramuser.id', ondelete='CASCADE'), unique=True)

    def __repr__(self):
        return self.user_id


class User(BaseModelWithDateTimeMixin, Base):
    __tablename__ = 'users__user'

    telegram_id = Column(BIGINT, unique=True, nullable=True)
    username = Column(String(length=255), nullable=True, default=None)
    first_name = Column(String(length=255), nullable=True, default=None)
    last_name = Column(String(length=255), nullable=True, default=None)

    is_admin = Column(Boolean, default=False)

    inviter_id = Column(GUID, ForeignKey('users__user.id', ondelete='CASCADE'))

    language_id = Column(BIGINT, ForeignKey('languages__language.id', ondelete='CASCADE'))
    language = relationship(Language, backref='users', uselist=False)

    config = relationship(UserConfig, backref='user', uselist=False, lazy='selectin')

    def __repr__(self):
        return self.username
