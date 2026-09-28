import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from links.models import Link

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient(enforce_csrf_checks=True)


def test_list_returns_empty_array_when_no_links_exist(client):
    response = client.get(reverse("links:list-create"))

    assert response.status_code == 200
    assert response.data == []
    assert not Link.objects.exists()


def test_list_returns_links_newest_first_without_incrementing_counters(client):
    older = Link.objects.create(
        original_url="https://example.com/older", code="Codigo01", access_count=3
    )
    newer = Link.objects.create(
        original_url="https://example.com/newer", code="Codigo02", access_count=7
    )

    response = client.get(reverse("links:list-create"))

    assert response.status_code == 200
    assert [item["code"] for item in response.data] == [newer.code, older.code]
    for item, link in zip(response.data, [newer, older]):
        assert item == {
            "id": link.id,
            "original_url": link.original_url,
            "code": link.code,
            "short_url": f"http://testserver/{link.code}/",
            "access_count": link.access_count,
            "created_at": link.created_at.isoformat().replace("+00:00", "Z"),
        }
        previous_count = link.access_count
        link.refresh_from_db()
        assert link.access_count == previous_count
    assert Link.objects.count() == 2


def test_detail_finds_link_by_code_without_incrementing_counter(client):
    link = Link.objects.create(
        original_url="https://example.com/page", code="Codigo01", access_count=5
    )
    Link.objects.create(original_url="https://example.com/other", code="Codigo02")

    response = client.get(reverse("links:detail", kwargs={"code": link.code}))

    assert response.status_code == 200
    assert response.data == {
        "id": link.id,
        "original_url": link.original_url,
        "code": link.code,
        "short_url": f"http://testserver/{link.code}/",
        "access_count": 5,
        "created_at": link.created_at.isoformat().replace("+00:00", "Z"),
    }
    link.refresh_from_db()
    assert link.access_count == 5
    assert Link.objects.count() == 2


def test_unknown_code_returns_404_without_changing_data(client):
    link = Link.objects.create(
        original_url="https://example.com", code="Codigo01", access_count=2
    )

    response = client.get(reverse("links:detail", kwargs={"code": "Ausente1"}))

    assert response.status_code == 404
    assert "detail" in response.data
    link.refresh_from_db()
    assert link.access_count == 2
    assert Link.objects.count() == 1


@pytest.mark.parametrize("method", ["post", "put", "patch"])
def test_detail_rejects_unsupported_writes_without_modifying_link(client, method):
    link = Link.objects.create(
        original_url="https://example.com/original", code="Codigo01", access_count=4
    )
    url = reverse("links:detail", kwargs={"code": link.code})

    response = getattr(client, method)(
        url, {"original_url": "https://example.com/changed"}, format="json"
    )

    assert response.status_code == 405
    link.refresh_from_db()
    assert link.original_url == "https://example.com/original"
    assert link.access_count == 4
    assert Link.objects.count() == 1


def test_detail_shows_counter_updated_by_redirect(client):
    link = Link.objects.create(original_url="https://example.com", code="Codigo01")
    redirect_url = reverse("redirect-link", kwargs={"code": link.code})
    detail_url = reverse("links:detail", kwargs={"code": link.code})

    assert client.get(redirect_url).status_code == 302
    assert client.get(redirect_url).status_code == 302
    first = client.get(detail_url)
    second = client.get(detail_url)

    assert first.status_code == second.status_code == 200
    assert first.data["access_count"] == second.data["access_count"] == 2
    link.refresh_from_db()
    assert link.access_count == 2
