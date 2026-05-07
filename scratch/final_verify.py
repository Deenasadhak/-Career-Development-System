from core.models import College, Course, CollegeCourse, CareerPath, KeralaReference
from core.services.recommendation_service import get_recommendations

print('--- COUNTS ---')
print(f'Colleges: {College.objects.count()}')
print(f'Courses: {Course.objects.count()}')
print(f'CC Links: {CollegeCourse.objects.count()}')
print(f'Career Paths: {CareerPath.objects.count()}')
print(f'Districts: {KeralaReference.objects.count()}')

print('\n--- SPOT CHECK 1: ERNAKULAM ---')
ernakulam_colleges = College.objects.filter(district='Ernakulam').order_by('name')
print(f'Count: {ernakulam_colleges.count()}')
for c in ernakulam_colleges:
    print(f'  - {c.name}')

print('\n--- SPOT CHECK 2: SCIENCE @ 390 ---')
# 97.5 / 150 * 600 = 390
recs = get_recommendations('Science', 80, 97.5)
for r in recs:
    print(f'  {r["college"].name[:30]} | {r["course"].name[:30]} | Cutoff: {r["cutoff_mark"]} | Eligible: {r["is_eligible"]}')
