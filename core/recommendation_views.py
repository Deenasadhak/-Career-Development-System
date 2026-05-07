import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.db.models import Sum

from core.models import StudentProfile
from core.models import StudentRecommendation
from core.models import TestSession
from core.services.recommendation_service import RecommendationEngine

class RecommendationListView(LoginRequiredMixin, ListView):
    template_name = 'core/recommendations/list.html'
    context_object_name = 'recommendations'

    def get_queryset(self):
        student = get_object_or_404(StudentProfile, user=self.request.user)
        recs = StudentRecommendation.objects.filter(student=student).select_related(
            'college_course__college', 
            'college_course__course__discipline__field__stream'
        )
        
        if not recs.exists():
            engine = RecommendationEngine()
            recs = engine.get_recommendations(student)
            
        return recs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recs = self.get_queryset()
        student = StudentProfile.objects.get(user=self.request.user)
        
        # Group by stream
        grouped = {}
        for rec in recs:
            stream = rec.college_course.course.discipline.field.stream.name if rec.college_course.course.discipline and rec.college_course.course.discipline.field and rec.college_course.course.discipline.field.stream else "Other"
            if stream not in grouped:
                grouped[stream] = []
            grouped[stream].append(rec)
            
        context['grouped_recommendations'] = grouped
        context['total_count'] = recs.count()
        context['eligible_count'] = recs.filter(eligibility_status='ELIGIBLE').count()
        context['shortlisted_count'] = recs.filter(is_shortlisted=True).count()
        
        last_rec = recs.order_by('-generated_at').first()
        context['last_generated_at'] = last_rec.generated_at if last_rec else None
        
        context['has_completed_test'] = TestSession.objects.filter(student=student, status='COMPLETED').exists()
        context['profile_complete'] = student.is_profile_complete
        
        return context

class RecommendationDetailView(LoginRequiredMixin, DetailView):
    model = StudentRecommendation
    template_name = 'core/recommendations/detail.html'
    context_object_name = 'recommendation'

    def get_queryset(self):
        return StudentRecommendation.objects.filter(student__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rec = self.object
        engine = RecommendationEngine()
        
        # Prepare chart data
        context['score_breakdown_json'] = json.dumps(rec.score_breakdown)
        
        # Similar alternatives
        context['alternatives'] = engine.get_similar_alternatives(rec)
        
        # Yearly cutoff history
        context['cutoff_history'] = rec.college_course.yearly_cutoffs.all().order_by('-year')
        
        # TODO: Phase 5 Scholarship eligibility check
        context['scholarships'] = [] 
        
        return context

class GenerateRecommendationsView(LoginRequiredMixin, View):
    def post(self, request):
        student = get_object_or_404(StudentProfile, user=request.user)
        
        if not student.is_profile_complete:
            messages.error(request, "Please complete your profile before generating recommendations.")
            return redirect('recommendations:list')
            
        # Rate limit: 24 hours
        last_rec = StudentRecommendation.objects.filter(student=student).order_by('-generated_at').first()
        if last_rec:
            diff = timezone.now() - last_rec.generated_at
            if diff.total_seconds() < 86400:
                hours_left = int((86400 - diff.total_seconds()) // 3600)
                messages.warning(request, f"Recommendations were generated recently. Next refresh available in {hours_left} hours.")
                return redirect('recommendations:list')

        engine = RecommendationEngine()
        recs = engine.get_recommendations(student)
        messages.success(request, f"Generated {len(recs)} personalized recommendations for you.")
        return redirect('recommendations:list')

class ToggleShortlistView(LoginRequiredMixin, View):
    def post(self, request, pk):
        student = get_object_or_404(StudentProfile, user=request.user)
        engine = RecommendationEngine()
        try:
            result = engine.toggle_shortlist(student, pk)
            return JsonResponse(result)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception:
            return JsonResponse({"error": "Failed to update shortlist"}, status=500)

class ShortlistView(LoginRequiredMixin, ListView):
    template_name = 'core/recommendations/shortlist.html'
    context_object_name = 'shortlisted_items'

    def get_queryset(self):
        student = get_object_or_404(StudentProfile, user=self.request.user)
        engine = RecommendationEngine()
        return engine.get_shortlisted(student)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.get_queryset()
        
        # Group by college
        grouped_by_college = {}
        total_fee = 0
        for item in items:
            college = item.college_course.college
            if college not in grouped_by_college:
                grouped_by_college[college] = []
            grouped_by_college[college].append(item)
            total_fee += (item.college_course.tuition_fee or 0)
            
        context['grouped_items'] = grouped_by_college
        context['total_estimated_fee'] = total_fee
        
        return context
