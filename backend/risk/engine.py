from datetime import timedelta

from django.utils import timezone

from reports.models import Report
from .models import Area, RiskScore
from .weather import rain_next_24h

LEVELS = ["LOW", "MEDIUM", "HIGH"]


def _bump(level, steps=1):
    return LEVELS[min(LEVELS.index(level) + steps, 2)]


def flood_risk(area):
    mm, source = rain_next_24h(area.latitude, area.longitude)
    level = "HIGH" if mm >= 40 else "MEDIUM" if mm >= 20 else "LOW"
    why = [f"forecast rain {mm} mm in 24h ({source})"]
    if area.flood_prone and level != "LOW":
        level = _bump(level)
        why.append("low-lying area with poor drainage")
    since = timezone.now() - timedelta(hours=6)
    n = Report.objects.filter(area=area.name, kind="flooding", created_at__gte=since).exclude(review_status="rejected").count()
    if n >= 2:
        level = _bump(level)
        why.append(f"{n} flood reports in the last 6h")
    elif n == 1:
        why.append("1 flood report in the last 6h")
    return level, "; ".join(why), mm, source


def water_risk(area):
    since = timezone.now() - timedelta(hours=24)
    n = Report.objects.filter(area=area.name, kind__in=["dry_tap", "burst_pipe"], created_at__gte=since).exclude(review_status="rejected").count()
    level = "HIGH" if n >= 3 else "MEDIUM" if n >= 1 else "LOW"
    why = [f"{n} dry-tap or burst-pipe reports in 24h"]
    sched = list(area.schedules.all())
    if sched:
        why.append("published schedule: " + ", ".join(f"{s.get_kind_display()} {s.window}" for s in sched))
    return level, "; ".join(why)


def score_area(area):
    f_level, f_why, mm, source = flood_risk(area)
    w_level, w_why = water_risk(area)
    for hazard, level, why in (("flood", f_level, f_why), ("water", w_level, w_why)):
        last = area.scores.filter(hazard=hazard).first()
        if not last or last.level != level or last.rationale != why:
            RiskScore.objects.create(area=area, hazard=hazard, level=level, rationale=why)
    return {"id": area.id, "name": area.name, "lat": area.latitude, "lng": area.longitude,
            "flood": f_level, "flood_why": f_why, "water": w_level, "water_why": w_why,
            "rain_mm": mm, "rain_source": source,
            "schedules": [{"kind": s.kind, "window": s.window} for s in area.schedules.all()]}


def score_all():
    return [score_area(a) for a in Area.objects.prefetch_related("schedules").order_by("name")]
