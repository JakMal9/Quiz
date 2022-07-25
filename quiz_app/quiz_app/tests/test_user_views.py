import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
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


def test_register_when_logged_in(authenticated_client: Client) -> None:
    res = authenticated_client.get("/auth/register/")
    assert res.status_code == 200
    content = res.content.decode("utf-8")
    assert "You are logged in" in content
    assert "Sign up" not in content


@pytest.mark.django_db
def test_register_valid_data(client: Client) -> None:
    payload = {
        "username": "test2",
        "password1": "testpassword",
        "password2": "testpassword",
    }
    res = client.post("/auth/register/", payload)
    assert res.status_code == 302
    assert res.url == "/auth/login/"
    message = get_messages(res.wsgi_request)._queued_messages[0].message
    assert "Successfully created new user" in message
    assert User.objects.filter(username=payload["username"]).count() == 1


@pytest.mark.django_db
def test_register_the_same_user(client: Client, registered_user: User) -> None:
    payload = {
        "username": registered_user.username,
        "password1": "testpassword",
        "password2": "testpassword",
    }
    res = client.post("/auth/register/", payload)
    assert res.status_code == 200
    assert "A user with that username already exists" in res.content.decode("utf-8")


@pytest.mark.django_db
def test_register_invalid_data(client: Client) -> None:
    payload = {"username": "test2", "password1": "t", "password2": "t"}
    res = client.post("/auth/register/", payload)
    assert res.status_code == 200
    assert "This password is too short" in res.content.decode("utf-8")
