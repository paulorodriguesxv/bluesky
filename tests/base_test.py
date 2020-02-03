import pytest
from alembic.command import upgrade
from alembic.config import Config
from starlette.testclient import TestClient
from app import create_app
from app.database import db
from http import HTTPStatus

app = create_app('test')
client = TestClient(app)


def upgrade_database():
    config = Config()
    config.set_main_option("script_location", "migrations")
    config.set_main_option('sqlalchemy.url', 'sqlite:///test.db')

    print("\nRunning database migration to HEAD...")
    upgrade(config, 'head')


def clean_database():
    print("\nCleaning database...")
    for tbl in reversed(db.Model.metadata.sorted_tables):
        db.engine.execute(tbl.delete())


@pytest.fixture(scope="module")
def database_config(request):
    upgrade_database()

    def teardown():
        clean_database()

    request.addfinalizer(teardown)


class BaseTest():
    app = create_app('test')
    client = TestClient(app)
