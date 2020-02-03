import pytest
from alembic.command import upgrade
from alembic.config import Config
from starlette.testclient import TestClient
from app import create_app
from app.database import db
from http import HTTPStatus
from .base_test import BaseTest, database_config


def get_token(username, password):
    response = BaseTest.client.post("/auth/token",
                                    data={
                                        'grant_type': 'password',
                                        'username': 'user@example.com',
                                        'password': 'mypassword'
                                    })

    token = response.json()['access_token']

    return token


class TestUserController(BaseTest):
    def test_create_user(self, database_config):
        """ Test if a user can be successfully created """

        response = BaseTest.client.post("/users/",
                                        json={
                                            "name": "John Paul",
                                            "picture": "http://my_picture_url",
                                            "email": "user@example.com",
                                            "password": "mypassword"
                                        })

        assert response.status_code == HTTPStatus.OK

        data = response.json()
        del data['updated_at']

        assert data == {
            "name": "John Paul",
            "picture": "http://my_picture_url",
            "is_active": True,
            "id": 1,
            "email": "user@example.com",
        }

    def test_create_user_already_registred(self, database_config):
        """ Test if a user create operation 
            fail if already registered """

        response = BaseTest.client.post("/users/",
                                        json={
                                            "name": "John Paul",
                                            "picture": "http://my_picture_url",
                                            "email": "user@example.com",
                                            "password": "mypassword"
                                        })

        assert response.status_code == HTTPStatus.BAD_REQUEST

        assert response.json() == {"detail": "Email already registered"}

    def test_create_user_with_missing_data(self, database_config):
        """ Test if a user create operation
            fail if created with missing data"""

        response = BaseTest.client.post("/users/",
                                        json={
                                            "name": "",
                                            "picture": "http://my_picture_url",
                                            "email": "newuser@example.com",
                                            "password": ""
                                        })

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_read_users(self, database_config):
        """ Read all users from database """

        response = BaseTest.client.post("/users/",
                                        json={
                                            "name": "John Paul 2",
                                            "picture": "http://my_picture_url",
                                            "email": "user2@example.com",
                                            "password": "mypassword"
                                        })

        token = get_token('user@example.com', 'mypassword')

        headers = {"Authorization": f"bearer {token}"}

        response = BaseTest.client.get("/users/", headers=headers)

        assert response.status_code == HTTPStatus.OK

        assert len(response.json()) == 2

    def test_read_user_me(self, database_config):
        """ Read logged user info from database """

        token = get_token('user@example.com', 'mypassword')

        headers = {"Authorization": f"bearer {token}"}

        response = BaseTest.client.get("/users/me", headers=headers)

        assert response.status_code == HTTPStatus.OK

        assert response.json()['email'] == 'user@example.com'