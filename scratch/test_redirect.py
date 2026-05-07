import os
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
import sys

# Setup Django environment
sys.path.append(r'c:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Carrier_Counsil.settings')
django.setup()

from CarrierApp.views import landing_view

def test_landing_redirect():
    factory = RequestFactory()
    User = get_user_model()
    
    # Create a mock user
    user = User.objects.first() # Use an existing user from the DB
    if not user:
        user = User.objects.create_user(username='testuser', password='password')
    
    # Mock an authenticated request to the landing page
    request = factory.get('/')
    request.user = user
    
    response = landing_view(request)
    
    print(f"Status Code: {response.status_code}")
    if hasattr(response, 'url'):
        print(f"Redirect URL: {response.url}")
    else:
        print("No redirect URL found in response")

if __name__ == "__main__":
    test_landing_redirect()
