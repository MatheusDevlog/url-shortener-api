from django.db import models


class Link(models.Model):
    original_url = models.URLField(max_length=2048)
    code = models.CharField(max_length=8, unique=True)
    access_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
