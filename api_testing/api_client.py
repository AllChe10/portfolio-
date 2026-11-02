import requests

BASE_URL = "https://jsonplaceholder.typicode.com"


def get_user(user_id):
    response = requests.get(
        f"{BASE_URL}/users/{user_id}",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()
