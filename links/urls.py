from django.urls import path

from .views import LinkCreateView

app_name = "links"

urlpatterns = [
    path("", LinkCreateView.as_view(), name="create"),
]
