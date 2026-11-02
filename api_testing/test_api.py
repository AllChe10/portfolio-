from unittest.mock import Mock, patch

import pytest
import requests

from api_client import get_user

@pytest.mark.integration
def test_get_user():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/users/1",
        timeout=10,
    )

    assert response.status_code == 200

    user = response.json()
    assert user["id"] == 1
    assert "name" in user

@pytest.mark.integration
def test_unknown_endpoint_returns_404():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/unknown-endpoint",
        timeout=10,
    )

    assert response.status_code == 404

@pytest.mark.integration
def test_user_has_expected_fields():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/users/1",
        timeout=10,
    )

    assert response.status_code == 200

    user = response.json()

    assert isinstance(user["id"], int)
    assert isinstance(user["name"], str)
    assert isinstance(user["email"], str)
    assert user["email"] != ""


def test_get_user_raises_error_on_server_error():
    with patch("api_client.requests.get") as mock_get:
        response = Mock()
        response.status_code = 500
        response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")

        mock_get.return_value = response

        with pytest.raises(requests.HTTPError):
            get_user(1)


def test_get_user_from_client():
    with patch("api_client.requests.get") as mock_get:
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
        }

        mock_get.return_value = response

        user = get_user(1)

        assert user["id"] == 1
        assert user["name"] == "Test User"
        assert user["email"] == "test@example.com"
        mock_get.assert_called_once_with(
            "https://jsonplaceholder.typicode.com/users/1",
            timeout=10,
        )
        response.raise_for_status.assert_called_once_with()


def test_get_user_raises_error_on_404():
    with patch("api_client.requests.get") as mock_get:
        response = Mock()
        response.status_code = 404

        response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

        mock_get.return_value = response

        with pytest.raises(requests.HTTPError):
            get_user(999)


def test_get_user_handles_timeout():
    with patch("api_client.requests.get") as mock_get:
        mock_get.side_effect = requests.Timeout("Request timed out")

        with pytest.raises(requests.Timeout):
            get_user(1)
        mock_get.assert_called_once_with(
            "https://jsonplaceholder.typicode.com/users/1",
            timeout=10,
        )


def test_get_user_from_client_wrong():
    with patch("api_client.requests.get") as mock_get:
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "id": 2,
            "name": "Test User",
            "email": "test@example.com",
        }

        mock_get.return_value = response

        user = get_user(1)

        assert user["id"] != 1


@pytest.mark.parametrize("status_code", [400, 404, 500])
def test_get_user_http_error(status_code):
    with patch("api_client.requests.get") as mock_get:
        response = Mock()
        response.status_code = status_code

        response.raise_for_status.side_effect = requests.HTTPError("HTTP error")
        mock_get.return_value = response

        with pytest.raises(requests.HTTPError):
            get_user(1)


def test_get_user_success():
    expected_user = {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
    }
    with patch("api_client.requests.get") as mock_get:
        response = Mock()
        response.status_code = 200
        response.json.return_value = expected_user
        mock_get.return_value = response

        user = get_user(1)

        assert user == expected_user
        mock_get.assert_called_once_with(
            "https://jsonplaceholder.typicode.com/users/1",
            timeout=10,
        )
        response.raise_for_status.assert_called_once_with()
