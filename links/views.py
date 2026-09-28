from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .serializers import LinkSerializer


class LinkCreateView(CreateAPIView):
    serializer_class = LinkSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
