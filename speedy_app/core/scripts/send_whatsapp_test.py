import os
from twilio.rest import Client

# Read credentials from environment
sid = os.environ.get('TWILIO_ACCOUNT_SID')
token = os.environ.get('TWILIO_AUTH_TOKEN')
from_number = os.environ.get('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

def main():
    to = 'whatsapp:+5213221924866'
    body = 'Your booking is confirmed on 12/1 at 3pm'

    if not sid or not token:
        print('Missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN in environment')
        return

    try:
        client = Client(sid, token)
        msg = client.messages.create(from_=from_number, body=body, to=to)
        print('Message sent. SID:', getattr(msg, 'sid', None))
        print('Full response:', msg)
    except Exception as e:
        print('Error sending message:', e)

if __name__ == '__main__':
    main()
