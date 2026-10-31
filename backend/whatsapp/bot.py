"""Conversation logic, independent of the transport (Meta webhook or the browser demo)."""
import hashlib

from django.conf import settings

from alerts.models import Subscriber
from reports.models import Report
from risk.engine import score_area
from risk.models import Area

REPORT_OPTIONS = {"2": ("flooding", "flooding"), "3": ("dry_tap", "a dry tap"),
                  "4": ("burst_pipe", "a burst pipe"), "5": ("blocked_drain", "a blocked drain")}

MENU = ("Reply:\n1 - Status for your area\n2 - Report flooding\n3 - Report dry tap\n"
        "4 - Report burst pipe\n5 - Report blocked drain\n6 - Change area\nSTOP - Delete my data")


def hash_phone(phone):
    return hashlib.sha256((settings.PHONE_HASH_SALT + phone).encode()).hexdigest()


def _areas():
    return list(Area.objects.order_by("name"))


def _welcome():
    lines = "\n".join(f"{i} - {a.name}" for i, a in enumerate(_areas(), 1))
    return ("Welcome to Mvula. I warn you about water shortages and floods.\n"
            f"Which area are you in? Reply with a number:\n{lines}\n"
            "By choosing, you agree we store your area and reports. Reply STOP any time to delete them.")


ACTIONS = {"HIGH": "Move valuables up, keep children away from water, boil drinking water.",
           "MEDIUM": "Stay alert, clear drains near your home, store clean water.",
           "LOW": "No action needed right now."}


def status_text(area_name):
    area = Area.objects.get(name=area_name)
    s = score_area(area)
    out = [f"Mvula ({area.name})", f"Flood risk: {s['flood']} (about {s['rain_mm']} mm rain expected in 24h).",
           ACTIONS[s["flood"]], f"Water shortage risk: {s['water']}."]
    for sc in s["schedules"]:
        out.append(f"{'Water supply' if sc['kind'] == 'water' else 'Power cuts'}: {sc['window']} (check official notice).")
    if s["rain_source"] == "unavailable":
        out.append("Note: rain forecast is unavailable right now.")
    return "\n".join(out)


def handle_message(phone, text):
    text = (text or "").strip()
    low = text.lower()
    if low == "stop":
        Subscriber.objects.filter(phone_hash=hash_phone(phone)).delete()
        Report.objects.filter(submitter_phone_hash=hash_phone(phone)).update(submitter_phone_hash="deleted")
        return "Your data has been deleted. Send HI to start again."

    sub, _ = Subscriber.objects.get_or_create(phone_hash=hash_phone(phone))
    areas = _areas()

    if sub.state == "choose_area" or low in ("6", "change"):
        if low not in ("6", "change") and text.isdigit() and 1 <= int(text) <= len(areas):
            sub.area = areas[int(text) - 1].name
            sub.state, sub.consent_given = "ready", True
            sub.save()
            return f"Thank you. You are subscribed to {sub.area}.\n\n{status_text(sub.area)}\n\n{MENU}"
        sub.state = "choose_area"
        sub.save()
        return _welcome()

    if text == "1":
        return status_text(sub.area)
    if text in REPORT_OPTIONS:
        kind, label = REPORT_OPTIONS[text]
        Report.objects.create(kind=kind, area=sub.area, submitter_phone_hash=sub.phone_hash, method="whatsapp",
                              latitude=Area.objects.get(name=sub.area).latitude,
                              longitude=Area.objects.get(name=sub.area).longitude)
        return (f"Thank you. We recorded {label} in {sub.area}. It is unverified until cross-checked with other "
                "reports. The map has been updated.")
    return MENU
