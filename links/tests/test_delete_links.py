import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from links.models import Link

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient(enforce_csrf_checks=True)


def test_delete_removes_link_from_database_and_all_read_endpoints(client):
    link = Link.objects.create(
        original_url="https://example.com/campaign", code="Codigo01", access_count=5
    )
    other = Link.objects.create(
        original_url="https://example.com/other", code="Codigo02", access_count=7
    )
    detail_url = reverse("links:detail", kwargs={"code": link.code})
    redirect_url = reverse("redirect-link", kwargs={"code": link.code})

    response = client.delete(detail_url)

    assert response.status_code == 204
    assert response.content == b""
    assert not Link.objects.filter(pk=link.pk).exists()
    assert client.get(detail_url).status_code == 404
    assert client.get(redirect_url).status_code == 404
    listing = client.get(reverse("links:list-create"))
    assert listing.status_code == 200
    assert [item["code"] for item in listing.data] == [other.code]
    assert client.get(reverse("links:detail", kwargs={"code": other.code})).status_code == 200
    other.refresh_from_db()
    assert other.original_url == "https://example.com/other"
    assert other.access_count == 7


def test_delete_unknown_code_returns_404_without_removing_existing_link(client):
    link = Link.objects.create(
        original_url="https://example.com", code="Codigo01", access_count=3
    )

    response = client.delete(reverse("links:detail", kwargs={"code": "Ausente1"}))

    assert response.status_code == 404
    assert "detail" in response.data
    link.refresh_from_db()
    assert link.access_count == 3
    assert Link.objects.count() == 1


def test_deleting_same_link_again_returns_404(client):
    link = Link.objects.create(original_url="https://example.com", code="Codigo01")
    url = reverse("links:detail", kwargs={"code": link.code})

    assert client.delete(url).status_code == 204
    assert client.delete(url).status_code == 404
    assert not Link.objects.exists()


def test_delete_collection_is_not_allowed_and_preserves_links(client):
    link = Link.objects.create(
        original_url="https://example.com", code="Codigo01", access_count=2
    )

    response = client.delete(reverse("links:list-create"))

    assert response.status_code == 405
    link.refresh_from_db()
    assert link.access_count == 2
    assert Link.objects.count() == 1
