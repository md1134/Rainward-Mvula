import json
import logging
import urllib.request

from django.conf import settings

log = logging.getLogger(__name__)


def send_text(to, body):
    """Send a WhatsApp message through the Cloud API. Logs instead when credentials are not set."""
    if not (settings.WHATSAPP_TOKEN and settings.WHATSAPP_PHONE_NUMBER_ID):
        log.info("[whatsapp not configured] to=%s body=%s", to, body)
        return False
    req = urllib.request.Request(
        f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages",
        data=json.dumps({"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}}).encode(),
        headers={"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}", "Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception:
        log.exception("WhatsApp send failed")
        return False
