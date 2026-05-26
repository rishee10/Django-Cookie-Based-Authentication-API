import random
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(user):
    code = generate_otp()
    OTP.objects.update_or_create(user=user, defaults={'code': code})
    send_mail(
        subject="Your OTP Code",
        message=f"Your OTP for registration is: {code}\n\nValid for 10 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
        recipient_list=[user.email],
        fail_silently=False,
    )

