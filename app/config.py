import os
from decouple import config
from json import JSONEncoder
import json
import logging
import jwt

logger = logging.getLogger(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))


def get_private_key():
    filename = config("ACCESS_TOKEN_PRIVATE_KEY", default=None)
    try:
        with open(filename) as f:
            key = f.read()
            logger.info('Private key loaded')

            return key
    except Exception as err:
        logger.error(f'Failed to load private key file: {str(err)}')


def get_public_key():
    filename = config("ACCESS_TOKEN_PUBLIC_KEY", default=None)
    try:
        with open(filename) as f:
            key = f.read()
            logger.info('Public key loaded')

            return key
    except Exception as err:
        logger.error(f'Failed to load public key file: {str(err)}')


class BaseConfig():
    API_PREFIX = '/api'
    TESTING = False
    DEBUG = False

    ACCESS_TOKEN_PRIVATE_KEY = get_private_key()
    ACCESS_TOKEN_PUBLIC_KEY = get_public_key()
    ACCESS_TOKEN_ALGORITHM = config("ACCESS_TOKEN_ALGORITHM", default="RS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES",
                                         default=30,
                                         cast=float)
    REFRESH_TOKEN_EXPIRE_MINUTES = config("REFRESH_TOKEN_EXPIRE_MINUTES",
                                          default=30,
                                          cast=float)

    SQLALCHEMY_DATABASE_URI = config("DATABASE_URI",
                                     default="sqlite:///" +
                                     os.path.join(basedir, "auth.db"))

    def init_app(self, app):
        app.config = self


class DevConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"


class AppConfig():
    def __init__(self, name):
        self._name = name
        self._config = dict(dev=DevConfig,
                            test=TestConfig,
                            prod=ProductionConfig)

    @property
    def config(self):
        return self._config[self._name]()


appConfig = AppConfig(config('APP_ENV', 'dev')).config


def get_config():
    yield appConfig