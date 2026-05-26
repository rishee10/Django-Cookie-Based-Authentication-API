from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from django.conf import settings


class CookieTokenAuthentication(BaseAuthentication):
    """
    Reads auth_token from HTTP-only cookie instead of Authorization header.
    """

    def authenticate(self, request):
        token_key = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
        if not token_key:
            return None  # no credentials — let permission class handle it

        try:
            token = Token.objects.select_related('user').get(key=token_key)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Invalid or expired auth token.")

        if not token.user.is_active:
            raise AuthenticationFailed("User account is inactive.")

        return (token.user, token)