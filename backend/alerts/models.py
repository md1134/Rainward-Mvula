from django.db import models


class Subscriber(models.Model):
    phone_hash = models.CharField(max_length=64, unique=True)  # hashed WhatsApp number, never the raw one
    area = models.CharField(max_length=120, blank=True)
    language = models.CharField(max_length=8, default="en")
    state = models.CharField(max_length=16, default="choose_area")
    consent_given = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
