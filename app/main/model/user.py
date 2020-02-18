import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy_utils import PasswordType, force_auto_coercion
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from app.database import db

force_auto_coercion()

BLUESKY_PROVIDER = 'bluesky'


class User(db.Model):
    """ user Model for storing keys related details """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    password = Column(PasswordType(schemes=['bcrypt']), nullable=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    picture = Column(String(), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    updated_at = Column(DateTime,
                        nullable=False,
                        default=datetime.datetime.utcnow)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
