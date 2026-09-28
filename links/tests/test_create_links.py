from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from links.models import Link

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.parametrize(
    "original_url", ["http://example.com/page", "https://example.com/page"]
)
def test_create_link(client, original_url):
    response = client.post(
        reverse("links:create"), {"original_url": original_url}, format="json"
    )

    assert response.status_code == 201
    link = Link.objects.get()
    assert link.original_url == original_url
    assert len(link.code) == 8
    assert link.code.isalnum()
    assert link.access_count == 0
    assert response.data == {
        "id": link.id,
        "original_url": original_url,
        "code": link.code,
        "short_url": f"http://testserver/{link.code}/",
        "access_count": 0,
        "created_at": link.created_at.isoformat().replace("+00:00", "Z"),
    }


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"original_url": ""},
        {"original_url": "not-a-url"},
        {"original_url": "ftp://example.com/file"},
        {"original_url": "javascript:alert(1)"},
        {"original_url": None},
        {"original_url": "https://example.com/" + "a" * 2048},
    ],
)
def test_reject_invalid_url(client, payload):
    response = client.post(reverse("links:create"), payload, format="json")

    assert response.status_code == 400
    assert "original_url" in response.data
    assert not Link.objects.exists()


def test_server_controls_code_and_access_count(client):
    with patch("links.serializers.get_random_string", return_value="Novo1234"):
        response = client.post(
            reverse("links:create"),
            {"original_url": "https://example.com", "code": "Escolhido", "access_count": 99},
            format="json",
        )

    assert response.status_code == 201
    link = Link.objects.get()
    assert link.code == "Novo1234"
    assert link.access_count == 0


def test_same_url_can_have_different_codes(client):
    with patch(
        "links.serializers.get_random_string", side_effect=["Codigo01", "Codigo02"]
    ):
        first = client.post(
            reverse("links:create"), {"original_url": "https://example.com"}, format="json"
        )
        second = client.post(
            reverse("links:create"), {"original_url": "https://example.com"}, format="json"
        )

    assert first.status_code == second.status_code == 201
    assert first.data["code"] != second.data["code"]
    assert Link.objects.count() == 2


def test_retry_when_code_already_exists(client):
    existing = Link.objects.create(
        original_url="https://example.com/existing", code="Usado123"
    )

    with patch(
        "links.serializers.get_random_string", side_effect=["Usado123", "Novo1234"]
    ):
        response = client.post(
            reverse("links:create"),
            {"original_url": "https://example.com/new"},
            format="json",
        )

    assert response.status_code == 201
    assert response.data["code"] == "Novo1234"
    assert Link.objects.count() == 2
    existing.refresh_from_db()
    assert existing.original_url == "https://example.com/existing"


def test_return_error_after_repeated_collisions(client):
    Link.objects.create(original_url="https://example.com/existing", code="Usado123")

    with patch(
        "links.serializers.get_random_string", return_value="Usado123"
    ) as generate_code:
        response = client.post(
            reverse("links:create"),
            {"original_url": "https://example.com/new"},
            format="json",
        )

    assert response.status_code == 500
    assert "detail" in response.data
    assert generate_code.call_count == 5
    assert Link.objects.count() == 1


def test_creation_endpoint_does_not_allow_listing(client):
    response = client.get(reverse("links:create"))

    assert response.status_code == 405
    assert not Link.objects.exists()
