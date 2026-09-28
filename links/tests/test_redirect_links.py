import pytest
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient

from links.models import Link

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "original_url",
    ["http://example.com/page", "https://example.com/search?q=django&lang=pt"],
)
def test_redirect_to_original_url(client, original_url):
    link = Link.objects.create(original_url=original_url, code="Codigo01")

    response = client.get(reverse("redirect-link", kwargs={"code": link.code}))

    assert response.status_code == 302
    assert response["Location"] == original_url
    assert "no-store" in response["Cache-Control"]
    link.refresh_from_db()
    assert link.access_count == 1


def test_each_redirect_increments_only_requested_link(client):
    link = Link.objects.create(
        original_url="https://example.com/page", code="Codigo01", access_count=5
    )
    other = Link.objects.create(
        original_url="https://example.com/other", code="Codigo02", access_count=2
    )
    url = reverse("redirect-link", kwargs={"code": link.code})

    for _ in range(3):
        response = client.get(url)
        assert response.status_code == 302

    link.refresh_from_db()
    other.refresh_from_db()
    assert link.access_count == 8
    assert other.access_count == 2


def test_unknown_code_returns_404_without_changing_existing_link(client):
    link = Link.objects.create(
        original_url="https://example.com", code="Codigo01", access_count=3
    )

    response = client.get(reverse("redirect-link", kwargs={"code": "Ausente1"}))

    assert response.status_code == 404
    assert "Location" not in response
    link.refresh_from_db()
    assert link.access_count == 3
    assert Link.objects.count() == 1


@pytest.mark.parametrize("method", ["post", "head"])
def test_non_get_requests_do_not_increment_counter(method):
    client = Client(enforce_csrf_checks=True)
    link = Link.objects.create(original_url="https://example.com", code="Codigo01")

    response = getattr(client, method)(
        reverse("redirect-link", kwargs={"code": link.code})
    )

    assert response.status_code == 405
    link.refresh_from_db()
    assert link.access_count == 0


def test_short_url_returned_by_creation_can_be_used_to_redirect():
    client = APIClient()
    original_url = "https://example.com/page"
    created = client.post(
        reverse("links:create"), {"original_url": original_url}, format="json"
    )
    assert created.status_code == 201

    response = client.get(created.data["short_url"])

    assert response.status_code == 302
    assert response["Location"] == original_url
    link = Link.objects.get(pk=created.data["id"])
    assert link.access_count == 1
