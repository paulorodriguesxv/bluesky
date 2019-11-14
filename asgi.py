from decouple import config
from app import create_app
from app.main.controller import user_controller

app = create_app(config('APP_ENV', 'dev'))
app.include_router(user_controller.router)
