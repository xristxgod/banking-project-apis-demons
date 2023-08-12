from sqlalchemy.orm import relationship
from sqlalchemy import BIGINT, Column, ForeignKey, String, Text

from core.database import Base


class Phrase(Base):
    __tablename__ = 'languages__phrase'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    code = Column(String(length=255), nullable=True, default=None)
    text = Column(Text)
    language_id = Column(BIGINT, ForeignKey('languages__language.id', ondelete='CASCADE'))

    def __repr__(self):
        return self.code


class Language(Base):
    __tablename__ = 'languages__language'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    name = Column(String(length=255), nullable=True, default=None)
    dest = Column(String(length=10), nullable=True, default=None)
    phrases = relationship(Phrase, backref='language')

    def __repr__(self):
        return self.name
