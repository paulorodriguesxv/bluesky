import os
from decouple import config
from json import JSONEncoder
import json

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfigEncoder(JSONEncoder):

    def default(self, object):

        if isinstance(object, BaseConfig):

            return object.__dict__

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object)

class BaseConfig():
    API_PREFIX = '/api'
    TESTING = False
    DEBUG = False

    SECRET_KEY = config('SECRET_KEY', 'my_precious_secret_key')
    SQLALCHEMY_DATABASE_URI = config("DATABASE_URI",
                                     default="sqlite:///" +
                                     os.path.join(basedir, "auth.db"))


class DevConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config_by_name = dict(dev=DevConfig, test=TestConfig, prod=ProductionConfig)

secret_key = config_by_name[config('APP_ENV', 'dev')].SECRET_KEY
