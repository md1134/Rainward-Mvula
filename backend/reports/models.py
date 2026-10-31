from django.db import models


class Report(models.Model):
    """A community observation. Always stored with provenance; never treated as a measurement."""

    class Kind(models.TextChoices):
        DRY_TAP = "dry_tap", "Dry tap"
        BURST_PIPE = "burst_pipe", "Burst pipe"
        BLOCKED_DRAIN = "blocked_drain", "Blocked drain"
        FLOODING = "flooding", "Flooding"
        SOIL_MOISTURE = "soil_moisture", "Soil moisture"
        CROP_CONDITION = "crop_condition", "Crop condition"

    class Review(models.TextChoices):
        UNREVIEWED = "unreviewed", "Unreviewed"
        CONFIRMED = "confirmed", "Confirmed"
        REJECTED = "rejected", "Rejected"

    kind = models.CharField(max_length=32, choices=Kind.choices)
    value = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to="reports/", blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    area = models.CharField(max_length=120, blank=True)
    submitter_phone_hash = models.CharField(max_length=64)  # hashed, never the raw number
    method = models.CharField(max_length=32, default="whatsapp")
    created_at = models.DateTimeField(auto_now_add=True)
    review_status = models.CharField(max_length=16, choices=Review.choices, default=Review.UNREVIEWED)

    def __str__(self):
        return f"{self.kind} @ {self.area or 'unknown'} ({self.review_status})"
