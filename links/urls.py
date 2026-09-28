from django.urls import path

from .views import LinkDetailView, LinkListCreateView

app_name = "links"

urlpatterns = [
    path("", LinkListCreateView.as_view(), name="list-create"),
    path("<str:code>/", LinkDetailView.as_view(), name="detail"),
]
