from django.http import JsonResponse
from django.shortcuts import render

from reports.models import Report
from .engine import score_all


def map_page(request):
    return render(request, "risk/map.html")


def map_data(request):
    data = score_all()
    counts = {}
    for r in Report.objects.exclude(review_status="rejected").order_by("-created_at")[:200]:
        counts.setdefault(r.area, {}).setdefault(r.kind, 0)
        counts[r.area][r.kind] += 1
    for a in data:
        a["reports"] = counts.get(a["name"], {})
    recent = [{"kind": r.get_kind_display(), "area": r.area, "at": r.created_at.strftime("%H:%M"),
               "status": r.review_status} for r in Report.objects.order_by("-created_at")[:8]]
    return JsonResponse({"areas": data, "recent": recent})
