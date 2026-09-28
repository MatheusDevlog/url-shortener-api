from django.urls import include, path

from links.views import redirect_link

urlpatterns = [
    path("api/links/", include("links.urls")),
    path("<str:code>/", redirect_link, name="redirect-link"),
]
