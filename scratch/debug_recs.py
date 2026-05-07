import os
import django

import sys
project_path = r'c:\Users\deena\Documents\Deenasadhak\LPU\SEM 6\Placement Preparation class\r\Career-development-project'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Carrier_Counsil.settings')
django.setup()

from core.services.recommendation_service import get_recommendations
recs = get_recommendations('Science', 80, 97.5)
print('--- RESULTS ---')
for r in recs:
    print(f'{r["college"].name} | {r["course"].name} | {r["cutoff_mark"]} | {r["is_eligible"]}')
