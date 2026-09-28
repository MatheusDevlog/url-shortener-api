from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from .models import Link
from .serializers import LinkSerializer


class LinkListCreateView(ListCreateAPIView):
    queryset = Link.objects.order_by("-created_at", "-pk")
    pagination_class = None
    serializer_class = LinkSerializer
    authentication_classes = []
    permission_classes = [AllowAny]


class LinkDetailView(RetrieveAPIView):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    lookup_field = "code"
    authentication_classes = []
    permission_classes = [AllowAny]


@csrf_exempt
@never_cache
@require_GET
def redirect_link(request, code):
    link = get_object_or_404(Link, code=code)
    Link.objects.filter(pk=link.pk).update(access_count=F("access_count") + 1)
    return HttpResponseRedirect(link.original_url)
