from django.core.validators import URLValidator
from django.db import IntegrityError, transaction
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import Link


class LinkSerializer(serializers.ModelSerializer):
    original_url = serializers.URLField(
        max_length=2048,
        validators=[URLValidator(schemes=["http", "https"])],
    )
    short_url = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = ["id", "original_url", "code", "short_url", "access_count", "created_at"]
        read_only_fields = ["id", "code", "access_count", "created_at"]

    def create(self, validated_data):
        for _ in range(5):
            code = get_random_string(length=8)
            try:
                with transaction.atomic():
                    return Link.objects.create(code=code, **validated_data)
            except IntegrityError:
                if not Link.objects.filter(code=code).exists():
                    raise

        raise APIException("Não foi possível gerar um código único. Tente novamente.")

    def get_short_url(self, obj):
        return self.context["request"].build_absolute_uri(f"/{obj.code}/")
