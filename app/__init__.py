from fastapi import FastAPI
from app.database import db
from app.main.controller import user_controller, auth_controller

PROJECT_VERSION = '0.1.0'
PROJECT_NAME = 'BlueSky'
PROJECT_DESCRIPTION = 'Experimental OAuth2 server forged with the powerful FastAPI'


def create_app(config_name):
    app = FastAPI(
        title=PROJECT_NAME,
        description=PROJECT_DESCRIPTION,
        version=PROJECT_VERSION,
    )

    db.init_app(app)

    app.include_router(user_controller.router, prefix='/users', tags=['users'])

    app.include_router(auth_controller.router, prefix='/auth', tags=['auth'])

    return app
