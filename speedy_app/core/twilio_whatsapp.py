from django.conf import settings
from twilio.rest import Client
import json


def _get_client():
    sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    if not sid or not token:
        raise RuntimeError('Twilio credentials not configured in settings')
    return Client(sid, token)


def send_whatsapp_message(to_number: str, body: str = None, from_number: str = None):
    """Send a plain WhatsApp message using Twilio."""
    client = _get_client()
    from_num = from_number or getattr(settings, 'TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
    # Twilio expects 'whatsapp:+<number>' format
    return client.messages.create(
        from_=from_num,
        body=body or '',
        to=to_number,
    )


def send_whatsapp_template(to_number: str, content_sid: str, content_variables: dict | str, from_number: str = None):
    """Send a WhatsApp message using Twilio Content API (templates)."""
    client = _get_client()
    from_num = from_number or getattr(settings, 'TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
    # content_variables can be a dict or JSON string
    if isinstance(content_variables, dict):
        content_vars = json.dumps(content_variables)
    else:
        content_vars = str(content_variables)

    return client.messages.create(
        from_=from_num,
        to=to_number,
        content_sid=content_sid,
        content_variables=content_vars,
    )
