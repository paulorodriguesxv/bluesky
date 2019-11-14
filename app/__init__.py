from fastapi import FastAPI
from .config import config_by_name

from app.database import db


def create_app(config_name):    
    app = FastAPI()

    app.config = config_by_name[config_name]

    db.init_app(app)

    return app
