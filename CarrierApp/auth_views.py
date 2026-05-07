from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from CarrierApp.models import Login, Student
import json

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role', 'STUDENT')
        
        if Login.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username exists'}, status=400)
            
        user = Login.objects.create_user(
            username=username, 
            password=password, 
            email=email,
            role=role,
            is_student=(role == 'STUDENT')
        )
        return JsonResponse({'message': 'User registered successfully'}, status=201)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({'message': 'Logged in successfully'})
        return JsonResponse({'error': 'Invalid credentials'}, status=401)

@method_decorator(csrf_exempt, name='dispatch')
class OTPLoginView(View):
    def post(self, request):
        # Placeholder logic for generating OTP
        return JsonResponse({'message': 'OTP sent to mobile'})

@method_decorator(csrf_exempt, name='dispatch')
class VerifyOTPView(View):
    def post(self, request):
        # Placeholder logic for verifying OTP
        return JsonResponse({'message': 'OTP verified'})

class LogoutView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({'message': 'Logged out successfully'})

@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetView(View):
    def post(self, request):
        return JsonResponse({'message': 'Reset link sent'})

class VerifyEmailView(View):
    def get(self, request, token):
        return JsonResponse({'message': 'Email verified'})

@method_decorator(csrf_exempt, name='dispatch')
class StudentProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        try:
            profile = Student.objects.get(user=request.user)
            return JsonResponse({'name': profile.full_name, 'completion': 100})
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Profile not found'}, status=404)

    def put(self, request):
        # logic for updating profile
        return JsonResponse({'message': 'Profile updated'})

class ProfileCompletionView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        profile, _ = Student.objects.get_or_create(user=request.user)
        return JsonResponse({'completion_pct': 100, 'is_complete': True})
