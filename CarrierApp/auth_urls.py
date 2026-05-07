from django.urls import path
from CarrierApp import auth_views

urlpatterns = [
    path('register/', auth_views.RegisterView.as_view(), name='api_register'),
    path('login/', auth_views.LoginView.as_view(), name='api_login'),
    path('otp-login/', auth_views.OTPLoginView.as_view(), name='api_otp_login'),
    path('verify-otp/', auth_views.VerifyOTPView.as_view(), name='api_verify_otp'),
    path('logout/', auth_views.LogoutView.as_view(), name='api_logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='api_password_reset'),
    path('verify-email/<str:token>/', auth_views.VerifyEmailView.as_view(), name='api_verify_email'),
    path('student/profile/', auth_views.StudentProfileView.as_view(), name='api_student_profile'),
    path('student/profile/completion/', auth_views.ProfileCompletionView.as_view(), name='api_profile_completion'),
]
