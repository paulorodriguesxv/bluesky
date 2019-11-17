from decouple import config
from app import create_app

app = create_app(config('APP_ENV', 'dev'))
