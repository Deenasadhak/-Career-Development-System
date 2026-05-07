from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
import json

from core.models import TestSession, AptitudeQuestion, QuestionOption, TestAnswer
from core.models import StudentProfile
from core.services.assessment_service import AssessmentService

class StartTestView(LoginRequiredMixin, View):
    def post(self, request):
        test_type = request.POST.get('test_type', 'FULL')
        profile = get_object_or_404(StudentProfile, user=request.user)
        
        # Check for existing IN_PROGRESS session
        existing = TestSession.objects.filter(
            student=profile, 
            test_type=test_type, 
            status='IN_PROGRESS'
        ).first()
        
        if existing:
            if existing.is_expired:
                existing.status = 'EXPIRED'
                existing.save()
            else:
                messages.warning(request, f"You already have an active {test_type} test in progress.")
                return redirect('assessment:question', session_id=existing.id, n=existing.questions_answered + 1)

        try:
            session = AssessmentService.generate_test(profile, test_type)
            return redirect('assessment:question', session_id=session.id, n=1)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('Stud_home')

class QuestionView(LoginRequiredMixin, View):
    template_name = 'assessment/question_detail.html'

    def get(self, request, session_id, n):
        session = get_object_or_404(TestSession, id=session_id, student__user=request.user)
        
        if session.status != 'IN_PROGRESS':
            return redirect('assessment:result', session_id=session.id)

        # Get the nth question using session answers
        answers = session.answers.all().order_by('id')
        if n > answers.count() or n < 1:
            return redirect('assessment:question', session_id=session.id, n=1)
        
        answer = answers[n-1]
        question = answer.question
        
        context = {
            'session': session,
            'question': question,
            'answer': answer,
            'options': question.options.all(),
            'number': n,
            'total': session.total_questions,
            'progress': session.progress_percentage,
            'flagged_count': session.answers.filter(is_flagged=True).count(),
            'time_limit': question.time_limit_seconds,
        }
        return render(request, self.template_name, context)

    def post(self, request, session_id, n):
        session = get_object_or_404(TestSession, id=session_id, student__user=request.user)
        option_id = request.POST.get('option')
        time_taken = int(request.POST.get('time_taken', 0))
        question_id = request.POST.get('question_id')

        if not option_id:
            messages.error(request, "Please select an option.")
            return redirect('assessment:question', session_id=session.id, n=n)

        AssessmentService.submit_answer(session, question_id, option_id, time_taken)
        
        # Determine next question
        next_q = AssessmentService.get_next_unanswered_question(session)
        if next_q:
            # Find the index of the next question
            all_q_ids = list(session.answers.all().order_by('id').values_list('question_id', flat=True))
            next_n = all_q_ids.index(next_q.id) + 1
            return redirect('assessment:question', session_id=session.id, n=next_n)
        else:
            return redirect('assessment:submit', session_id=session.id)

class FlagQuestionView(LoginRequiredMixin, View):
    def post(self, request, session_id, question_id):
        session = get_object_or_404(TestSession, id=session_id, student__user=request.user)
        is_flagged = AssessmentService.flag_question(session, question_id)
        return JsonResponse({"flagged": is_flagged, "question_id": question_id})

class SubmitTestView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(TestSession, id=session_id, student__user=request.user)
        if session.status == 'IN_PROGRESS':
            AssessmentService.calculate_scores(session)
            # Update overall profile completion
            profile = session.student
            profile.calculate_completion()
        return redirect('assessment:result', session_id=session.id)

class ResultView(LoginRequiredMixin, View):
    template_name = 'assessment/result_detail.html'

    def get(self, request, session_id):
        session = get_object_or_404(TestSession, id=session_id, student__user=request.user)
        if session.status == 'IN_PROGRESS':
            return redirect('assessment:question', session_id=session.id, n=1)
            
        result_data = AssessmentService.get_result_summary(session)
        
        # Prepare RIASEC data for Chart.js
        riasec_json = json.dumps(session.riasec_scores)
        
        context = {
            'result': result_data,
            'riasec_json': riasec_json,
            'personality_json': json.dumps(session.personality_profile),
        }
        return render(request, self.template_name, context)

class TestHistoryView(LoginRequiredMixin, View):
    template_name = 'assessment/history.html'

    def get(self, request):
        profile = get_object_or_404(StudentProfile, user=request.user)
        sessions = TestSession.objects.filter(student=profile, status='COMPLETED').order_by('-completed_at')
        return render(request, self.template_name, {'sessions': sessions})
