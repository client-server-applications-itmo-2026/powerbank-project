import base64
from http import HTTPStatus
from typing import final

import pytest
from django.test import Client

from server.apps.users.models import UserModel


def _auth_header(email: str, password: str) -> str:
    token = base64.b64encode(f"{email}:{password}".encode()).decode()
    return f"Basic {token}"


@pytest.fixture
def user(db) -> UserModel:
    return UserModel.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@final
@pytest.mark.django_db
class TestRegisterUser:
    def test_register_success(self, client: Client) -> None:
        response = client.post(
            "/api/register",
            data={
                "email": "new@example.com",
                "password": "secret123",
                "re_password": "secret123",
                "first_name": "John",
                "last_name": "Doe",
                "patronymic_name": None,
                "phone_number": None,
            },
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["email"] == "new@example.com"

    def test_register_password_mismatch(self, client: Client) -> None:
        response = client.post(
            "/api/register",
            data={
                "email": "new@example.com",
                "password": "secret123",
                "re_password": "different",
                "first_name": "John",
                "last_name": "Doe",
                "patronymic_name": None,
                "phone_number": None,
            },
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.CONFLICT

    def test_register_duplicate_email(self, client: Client, user: UserModel) -> None:
        response = client.post(
            "/api/register",
            data={
                "email": user.email,
                "password": "secret123",
                "re_password": "secret123",
                "first_name": "John",
                "last_name": "Doe",
                "patronymic_name": None,
                "phone_number": None,
            },
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.CONFLICT

    def test_register_duplicate_phone(self, client: Client, db) -> None:
        UserModel.objects.create_user(
            email="existing@example.com",
            password="pass",
            first_name="X",
            last_name="Y",
            phone_number="+71234567890",
        )
        response = client.post(
            "/api/register",
            data={
                "email": "newemail@example.com",
                "password": "secret123",
                "re_password": "secret123",
                "first_name": "John",
                "last_name": "Doe",
                "patronymic_name": None,
                "phone_number": "+71234567890",
            },
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.CONFLICT


@final
@pytest.mark.django_db
class TestGetMe:
    def test_authenticated(self, client: Client, user: UserModel) -> None:
        response = client.get(
            "/api/me",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["email"] == user.email

    def test_unauthenticated(self, client: Client) -> None:
        response = client.get("/api/me")
        assert response.status_code == HTTPStatus.UNAUTHORIZED


@final
@pytest.mark.django_db
class TestUpdateMe:
    def test_update_first_name(self, client: Client, user: UserModel) -> None:
        response = client.patch(
            "/api/me",
            data={"first_name": "Updated"},
            content_type="application/json",
            HTTP_AUTHORIZATION=_auth_header(user.email, "testpass123"),
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["first_name"] == "Updated"

    def test_unauthenticated(self, client: Client) -> None:
        response = client.patch(
            "/api/me",
            data={"first_name": "X"},
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
