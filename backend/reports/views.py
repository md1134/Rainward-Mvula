import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from risk.models import Area
from whatsapp.bot import hash_phone
from .models import Report


@csrf_exempt
def create_report(request):
    """POST {kind, area, phone?} -> creates an unreviewed report. For integrations and tests."""
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    try:
        d = json.loads(request.body or "{}")
        area = Area.objects.get(name=d["area"])
        kind = d["kind"]
    except (KeyError, ValueError, Area.DoesNotExist):
        return JsonResponse({"error": "need valid 'kind' and 'area'"}, status=400)
    if kind not in Report.Kind.values:
        return JsonResponse({"error": "unknown kind"}, status=400)
    r = Report.objects.create(kind=kind, area=area.name, latitude=area.latitude, longitude=area.longitude,
                              submitter_phone_hash=hash_phone(str(d.get("phone", "api"))), method="api")
    return JsonResponse({"id": r.id, "review_status": r.review_status}, status=201)
