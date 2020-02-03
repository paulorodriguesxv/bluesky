import pytest
from alembic.command import upgrade
from alembic.config import Config
from starlette.testclient import TestClient
from app import create_app
from app.database import db
from http import HTTPStatus
from .base_test import BaseTest, database_config
from app.main.services.social_login_service import SocialLoginService
from app.main.services import user_service


def create_user():
    response = BaseTest.client.post("/users/",
                                    json={
                                        "name": "John Paul",
                                        "picture": "http://my_picture_url",
                                        "email": "user@example.com",
                                        "password": "mypassword"
                                    })


def get_token(username, password):
    response = BaseTest.client.post("/auth/token",
                                    data={
                                        'grant_type': 'password',
                                        'username': 'user@example.com',
                                        'password': 'mypassword'
                                    })

    token = response.json()

    return token


class TestAuthController(BaseTest):
    def test_get_token(self, database_config):
        """ Test get token """
        create_user()
        response = BaseTest.client.post("/auth/token",
                                        data={
                                            'grant_type': 'password',
                                            'username': 'user@example.com',
                                            'password': 'mypassword'
                                        })

        assert response.status_code == HTTPStatus.OK

        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_get_jwks(self, database_config):
        response = BaseTest.client.get("/auth/.well-known/jwks.json",
                                       data={
                                           'grant_type': 'password',
                                           'username': 'user@example.com',
                                           'password': 'mypassword'
                                       })

        assert response.status_code == HTTPStatus.OK

        data = response.json()
        assert 'keys' in data

    def test_get_refresh_token(self, database_config):
        token = get_token('user@example.com', 'mypassword')
        response = BaseTest.client.post("/auth/refresh-token",
                                        json={
                                            'refresh_token':
                                            token['refresh_token'],
                                        })

        assert response.status_code == HTTPStatus.OK

        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_swap_token(self, database_config):
        class SocialLoginServiceFake():
            def __init__(self):
                pass

            async def get_user(self, db, social_token):
                return user_service.get_user(db, email='user@example.com')

        BaseTest.app.dependency_overrides[
            SocialLoginService] = SocialLoginServiceFake

        response = BaseTest.client.post("/auth/swap-social-token",
                                        json={
                                            'token': 'any_token',
                                            'provider': 'facebook'
                                        })

        assert response.status_code == HTTPStatus.OK
