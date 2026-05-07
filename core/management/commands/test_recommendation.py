from django.core.management.base import BaseCommand
from core.models import StudentProfile
from core.models import TestSession
from core.models import StudentRecommendation
from core.services.recommendation_service import RecommendationEngine
from django.utils import timezone

class Command(BaseCommand):
    help = 'Tests the Enhanced Recommendation Engine with a sample student'

    def handle(self, *args, **options):
        self.stdout.write("==========================================")
        self.stdout.write("RECOMMENDATION TEST REPORT")
        
        student = StudentProfile.objects.first()
        if not student:
            self.stdout.write(self.style.ERROR("No StudentProfile found. Please create one first."))
            return

        self.stdout.write(f"Student: {student.user.email if student.user else student.email}")
        self.stdout.write(f"Profile complete: {'Yes' if student.is_profile_complete else 'No'}")
        
        session = TestSession.objects.filter(student=student, status='COMPLETED').order_by('-completed_at').first()
        self.stdout.write(f"Test session used: {session.id if session else 'None'}")
        self.stdout.write("==========================================")

        engine = RecommendationEngine()
        recs = engine.get_recommendations(student, test_session=session, top_n=5)
        
        total = StudentRecommendation.objects.filter(student=student).count()
        eligible = StudentRecommendation.objects.filter(student=student, eligibility_status='ELIGIBLE').count()
        borderline = StudentRecommendation.objects.filter(student=student, eligibility_status='BORDERLINE').count()
        ineligible = StudentRecommendation.objects.filter(student=student, eligibility_status='INELIGIBLE').count()
        
        high = StudentRecommendation.objects.filter(student=student, admission_chance='HIGH').count()
        medium = StudentRecommendation.objects.filter(student=student, admission_chance='MEDIUM').count()
        low = StudentRecommendation.objects.filter(student=student, admission_chance='LOW').count()

        self.stdout.write(f"Total generated: {total}")
        self.stdout.write(f"Eligible: {eligible} | Borderline: {borderline} | Ineligible: {ineligible}")
        self.stdout.write(f"HIGH chance: {high} | MEDIUM: {medium} | LOW: {low}")
        self.stdout.write("------------------------------------------")
        self.stdout.write("TOP 5 RECOMMENDATIONS:")

        for i, rec in enumerate(recs, 1):
            self.stdout.write(f"{i}. [{rec.college_course.college.name}] - [{rec.college_course.course.name}]")
            self.stdout.write(f"   Score: {rec.total_score:.1f} | Eligibility: {rec.eligibility_status}")
            bk = rec.score_breakdown
            self.stdout.write(f"   Aptitude: {bk.get('aptitude', 0):.0f} | Interest: {bk.get('interest', 0):.0f} | "
                             f"Academic: {bk.get('academic', 0):.0f} | Personality: {bk.get('personality', 0):.0f} | "
                             f"Values: {bk.get('values', 0):.0f}")
            self.stdout.write(f"   Why: {rec.why_recommended}")
            self.stdout.write("------------------------------------------")

        # Test toggle_shortlist
        if recs:
            self.stdout.write(f"Testing toggle_shortlist on Rec #{recs[0].id}...")
            res = engine.toggle_shortlist(student, recs[0].id)
            self.stdout.write(f"Result: {res['message']} (Total shortlisted: {res['total_shortlisted']})")
            
            # Test alternatives
            self.stdout.write(f"Testing get_similar_alternatives for Rec #{recs[0].id}...")
            alts = engine.get_similar_alternatives(recs[0])
            for alt in alts:
                self.stdout.write(f"   Alternative: {alt.college_course.college.name} - {alt.college_course.course.name} (Score: {alt.total_score:.1f})")

        self.stdout.write("==========================================")
        self.stdout.write(self.style.SUCCESS("Phase 4 Recommendation Engine Test Completed."))
