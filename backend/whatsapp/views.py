import json

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .bot import handle_message
from .transport import send_text


@csrf_exempt
def webhook(request):
    """Meta WhatsApp Cloud API webhook: GET verifies, POST receives messages."""
    if request.method == "GET":
        if (request.GET.get("hub.mode") == "subscribe" and settings.WHATSAPP_VERIFY_TOKEN
                and request.GET.get("hub.verify_token") == settings.WHATSAPP_VERIFY_TOKEN):
            return HttpResponse(request.GET.get("hub.challenge", ""))
        return HttpResponse("forbidden", status=403)
    try:
        payload = json.loads(request.body or "{}")
    except ValueError:
        return HttpResponse(status=400)
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for m in change.get("value", {}).get("messages", []):
                if m.get("type") == "text":
                    send_text(m["from"], handle_message(m["from"], m["text"]["body"]))
                else:
                    send_text(m["from"], "Please reply with text for now. Photo reports are coming soon.")
    return HttpResponse("ok")


def demo_page(request):
    return render(request, "whatsapp/demo.html")


@csrf_exempt
def demo_message(request):
    """Browser simulator endpoint, for demos without a WhatsApp number."""
    if request.method != "POST":
        return HttpResponse(status=405)
    data = json.loads(request.body or "{}")
    phone = str(data.get("phone", ""))[:40] or "demo"
    return JsonResponse({"reply": handle_message("demo:" + phone, data.get("text", ""))})
