import os
import django
import sys
from django.test import RequestFactory

# Setup Django environment
sys.path.append(r'c:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Carrier_Counsil.settings')
django.setup()

from django.contrib.auth.models import AnonymousUser
from CarrierApp.views import landing_view

def check_app_visibility():
    factory = RequestFactory()
    request = factory.get('/')
    request.user = AnonymousUser()
    
    try:
        response = landing_view(request)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            print(f"Content Length: {len(content)}")
            print("Title check:", "Future Pathways" in content)
            print("First 200 chars of content:")
            print(content[:200])
        else:
            print(f"Response Headers: {response.headers}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_app_visibility()
