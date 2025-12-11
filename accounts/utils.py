import uuid
from django.core.mail import send_mail

def generate_token():
    return str(uuid.uuid4())

def is_valid_uuid(value):
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False

def send_email(to, subject, body):
    send_mail(subject, body, None, [to], fail_silently=False)