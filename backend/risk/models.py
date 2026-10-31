from django.db import models


class Area(models.Model):
    """A ward, compound or farm that receives a risk score."""

    name = models.CharField(max_length=120, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class RiskScore(models.Model):
    class Hazard(models.TextChoices):
        FLOOD = "flood", "Flood"
        WATER = "water", "Water shortage"
        DRY_SPELL = "dry_spell", "Dry spell"

    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="scores")
    hazard = models.CharField(max_length=16, choices=Hazard.choices)
    level = models.CharField(max_length=8)  # LOW / MEDIUM / HIGH
    rationale = models.TextField()  # sources used, so every alert is explainable
    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-computed_at"]
