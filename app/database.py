import warnings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import appConfig


class SQLAlchemy():
    def __init__(self):
        self.Model = declarative_base()
        self.config = appConfig

    def init_app(self, app):
        """
        if ('SQLALCHEMY_DATABASE_URI' not in app.config
                and 'SQLALCHEMY_BINDS' not in app.config):
            warnings.warn(
                'Neither SQLALCHEMY_DATABASE_URI nor SQLALCHEMY_BINDS is set. '
                'Defaulting SQLALCHEMY_DATABASE_URI to "sqlite:///:memory:".')
        """

        SQLALCHEMY_DATABASE_URI = self.config.SQLALCHEMY_DATABASE_URI

        #connect_args={"check_same_thread": False}
        self.engine = create_engine(SQLALCHEMY_DATABASE_URI)
        self.session = sessionmaker(autocommit=False,
                                    autoflush=False,
                                    bind=self.engine)


db = SQLAlchemy()


# Dependency
def get_db():
    try:
        x = db.session()
        yield x
    finally:
        x.close()
