from fastapi import FastAPI
from app.database import db
from app.main.controller import user_controller


def create_app(config_name):
    app = FastAPI()

    db.init_app(app)

    app.include_router(user_controller.router)

    return app
