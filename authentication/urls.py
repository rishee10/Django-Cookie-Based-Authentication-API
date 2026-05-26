from django.urls import path
from .views import RegisterView, VerifyOTPView, LoginView, MeView, LogoutView

urlpatterns = [
    path('register/',        RegisterView.as_view(),   name='register'),
    path('register/verify',  VerifyOTPView.as_view(),  name='verify-otp'),
    path('login/',           LoginView.as_view(),      name='login'),
    path('me/',              MeView.as_view(),          name='me'),
    path('logout/',          LogoutView.as_view(),      name='logout'),
]