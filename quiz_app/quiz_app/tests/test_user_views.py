import pytest
from django.contrib.auth.models import User
from django.test import Client


@pytest.mark.django_db
def test_login_view_correct_data(client: Client, registered_user: User) -> None:
    user = registered_user
    res = client.post(
        "/auth/login/", data={"username": user.username, "password": "test"}
    )
    assert res.status_code == 302
    assert res.url == "/questions/"
    assert client.session._SessionBase__session_key is not None


@pytest.mark.django_db
def test_login_view_incorrect_data(client: Client, registered_user: User) -> None:
    user = registered_user
    res = client.post(
        "/auth/login/", data={"username": user.username, "password": "wrong"}
    )
    assert res.status_code == 200
    assert "Please enter a correct username and password" in res.content.decode("utf-8")


def test_logout(authenticated_client: Client) -> None:
    res = authenticated_client.get("/auth/logout/")
    assert res.status_code == 302
    assert res.url == "/auth/login/"
    assert authenticated_client.session._SessionBase__session_key is None
