import random
import json
from datetime import datetime
from django.utils import timezone
from django.db.models import Count, Sum, Q, Avg
from django.apps import apps
from django.db import transaction
from typing import Optional, Dict, List
from core.models import (
    AptitudeCategory, AptitudeQuestion, QuestionOption,
    TestSession, TestAnswer
)
from core.models import Stream

class AssessmentService:

    TEST_CONFIG = {
        'FULL':        {'per_category': 12, 'categories':
                        ['LOGICAL','QUANTITATIVE','VERBAL',
                         'TECHNICAL','ARTS']},
        'QUICK':       {'per_category': 5,  'categories':
                        ['LOGICAL','QUANTITATIVE','VERBAL',
                         'TECHNICAL','ARTS']},
        'PERSONALITY': {'total': 40, 'categories':
                        ['PERSONALITY']},
        'INTEREST':    {'total': 30, 'categories':
                        ['INTEREST']},
        'VALUES':      {'total': 20, 'categories':
                        ['VALUES']},
    }

    STREAM_SCORE_WEIGHTS = {
        # stream_slug: {category_code: weight}
        'science-technology': {
            'TECHNICAL': 0.35, 'QUANTITATIVE': 0.35,
            'LOGICAL': 0.30
        },
        'engineering': {
            'TECHNICAL': 0.35, 'QUANTITATIVE': 0.35,
            'LOGICAL': 0.30
        },
        'medical-sciences': {
            'LOGICAL': 0.30, 'QUANTITATIVE': 0.30,
            'VERBAL': 0.20, 'TECHNICAL': 0.20
        },
        'commerce-management': {
            'QUANTITATIVE': 0.40, 'VERBAL': 0.30,
            'LOGICAL': 0.30
        },
        'arts-humanities': {
            'ARTS': 0.50, 'VERBAL': 0.30,
            'LOGICAL': 0.20
        },
        'law': {
            'VERBAL': 0.45, 'LOGICAL': 0.35,
            'QUANTITATIVE': 0.20
        },
    }

    @staticmethod
    def generate_test(student_profile, test_type='FULL') -> TestSession:
        """
        Generates a new test session based on the specified type.
        """
        config = AssessmentService.TEST_CONFIG.get(test_type)
        if not config:
            raise ValueError(f"Invalid test type: {test_type}")

        selected_questions = []
        categories = config.get('categories', [])
        
        # 30 days exclusion
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        past_question_ids = TestAnswer.objects.filter(
            session__student=student_profile,
            session__started_at__gt=cutoff_date
        ).values_list('question_id', flat=True)

        for cat_code in categories:
            try:
                category = AptitudeCategory.objects.get(code=cat_code)
            except AptitudeCategory.DoesNotExist:
                continue

            # Base queryset
            qs = AptitudeQuestion.objects.filter(
                category=category,
                is_active=True
            ).exclude(id__in=past_question_ids)

            per_cat = config.get('per_category') or (config.get('total') // len(categories))
            
            # Difficulty bands: Easy 30%, Medium 50%, Hard 20%
            counts = {
                'E': int(per_cat * 0.3),
                'M': int(per_cat * 0.5),
                'H': per_cat - int(per_cat * 0.3) - int(per_cat * 0.5)
            }

            cat_questions = []
            for diff, count in counts.items():
                diff_qs = list(qs.filter(difficulty=diff).order_by('?')[:count])
                cat_questions.extend(diff_qs)
            
            # If still short, pick random from category
            if len(cat_questions) < per_cat:
                remaining_needed = per_cat - len(cat_questions)
                extra_qs = qs.exclude(id__in=[q.id for q in cat_questions]).order_by('?')[:remaining_needed]
                cat_questions.extend(list(extra_qs))

            if len(cat_questions) < 3 and test_type not in ['PERSONALITY', 'INTEREST', 'VALUES']:
                raise ValueError(f"Insufficient questions in category {cat_code}")
            
            selected_questions.extend(cat_questions)

        if not selected_questions:
            raise ValueError("No questions found for the selected test type.")

        with transaction.atomic():
            session = TestSession.objects.create(
                student=student_profile,
                test_type=test_type,
                total_questions=len(selected_questions),
                status='IN_PROGRESS'
            )
            
            # Create TestAnswer stubs
            answers = [
                TestAnswer(session=session, question=q)
                for q in selected_questions
            ]
            TestAnswer.objects.bulk_create(answers)

        return session

    @staticmethod
    def get_next_unanswered_question(session: TestSession) -> Optional[AptitudeQuestion]:
        """
        Return the next question in session that has selected_option=None.
        Prioritizes unflagged questions.
        """
        unanswered = TestAnswer.objects.filter(session=session, selected_option__isnull=True).order_by('is_flagged', 'id')
        if unanswered.exists():
            return unanswered.first().question
        return None

    @staticmethod
    def submit_answer(session: TestSession, question_id: int, option_id: int, time_taken: int = 0) -> dict:
        """
        Submits an answer for a question in a session.
        """
        with transaction.atomic():
            answer = TestAnswer.objects.get(session=session, question_id=question_id)
            option = QuestionOption.objects.get(id=option_id)
            
            if answer.selected_option is None:
                session.questions_answered += 1
            
            answer.selected_option = option
            answer.is_correct = option.is_correct
            answer.time_taken_seconds = time_taken
            answer.save()
            
            # Question Stats
            question = answer.question
            question.times_used += 1
            if answer.is_correct:
                question.correct_count += 1
            question.save()
            
            session.save()
            
        return {
            "is_correct": answer.is_correct,
            "explanation": answer.question.explanation,
            "progress": session.progress_percentage
        }

    @staticmethod
    def flag_question(session: TestSession, question_id: int) -> bool:
        """Toggles flagged state."""
        answer = TestAnswer.objects.get(session=session, question_id=question_id)
        answer.is_flagged = not answer.is_flagged
        answer.save()
        return answer.is_flagged

    @staticmethod
    def calculate_scores(session: TestSession) -> TestSession:
        """
        Calculates and saves scores for the session.
        """
        answers = TestAnswer.objects.filter(session=session).select_related('question', 'question__category', 'selected_option')
        
        # Aptitude Scores
        cat_scores = {}
        for ans in answers:
            code = ans.question.category.code
            if code not in cat_scores:
                cat_scores[code] = {'raw': 0, 'max': 0}
            cat_scores[code]['max'] += ans.question.marks
            if ans.is_correct:
                cat_scores[code]['raw'] += ans.question.marks

        for code, scores in cat_scores.items():
            normalized = (scores['raw'] / scores['max'] * 100) if scores['max'] > 0 else 0
            if code == 'LOGICAL': session.logical_score = normalized
            elif code == 'QUANTITATIVE': session.quantitative_score = normalized
            elif code == 'VERBAL': session.verbal_score = normalized
            elif code == 'TECHNICAL': session.technical_score = normalized
            elif code == 'ARTS': session.arts_score = normalized

        # Personality (Big Five)
        if session.test_type == 'PERSONALITY':
            traits = {"openness": [], "conscientiousness": [], "extraversion": [], "agreeableness": [], "neuroticism": []}
            for ans in answers:
                if ans.selected_option:
                    trait = ans.question.topic_tag.lower()
                    if trait in traits:
                        # Map order 1-5 to score
                        traits[trait].append(ans.selected_option.order)
            
            session.personality_profile = {
                trait: round(sum(scores)/len(scores)*20, 2) if scores else 0
                for trait, scores in traits.items()
            }

        # Interest (RIASEC)
        if session.test_type == 'INTEREST':
            riasec = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
            total_interest = 0
            for ans in answers:
                if ans.selected_option and ans.selected_option.riasec_code:
                    riasec[ans.selected_option.riasec_code] += 1
                    total_interest += 1
            
            session.riasec_scores = {
                code: round(count/total_interest*100, 2) if total_interest > 0 else 0
                for code, count in riasec.items()
            }

        # Values
        if session.test_type == 'VALUES':
            v_scores = {}
            for ans in answers:
                if ans.selected_option:
                    tag = ans.question.topic_tag
                    if tag not in v_scores: v_scores[tag] = []
                    v_scores[tag].append(ans.selected_option.order)
            
            session.values_scores = {
                tag: round(sum(scores)/len(scores)*20, 2) if scores else 0
                for tag, scores in v_scores.items()
            }

        AssessmentService.get_stream_recommendation(session)
        
        # Percentile calculation
        same_type_count = TestSession.objects.filter(
            test_type=session.test_type, 
            status='COMPLETED',
            started_at__gt=timezone.now() - timezone.timedelta(days=90)
        ).count()
        
        if same_type_count > 0:
            # Simple approximation for demo
            session.percentile = 75.0 + (random.random() * 20) # Mock percentile
        else:
            session.percentile = 100.0

        session.status = 'COMPLETED'
        session.completed_at = timezone.now()
        
        # Calculate total time
        total_sec = answers.aggregate(Sum('time_taken_seconds'))['time_taken_seconds__sum'] or 0
        session.total_time_seconds = total_sec
        
        session.save()
        return session

    @staticmethod
    def get_stream_recommendation(session: TestSession) -> Stream:
        """
        Suggests a stream based on weighted scores.
        """
        scores = {
            'LOGICAL': session.logical_score,
            'QUANTITATIVE': session.quantitative_score,
            'VERBAL': session.verbal_score,
            'TECHNICAL': session.technical_score,
            'ARTS': session.arts_score
        }
        
        best_stream = None
        highest_weighted = -1
        
        for slug, weights in AssessmentService.STREAM_SCORE_WEIGHTS.items():
            weighted_score = sum(scores.get(cat, 0) * weight for cat, weight in weights.items())
            if weighted_score > highest_weighted:
                highest_weighted = weighted_score
                try:
                    best_stream = Stream.objects.get(slug=slug)
                except Stream.DoesNotExist:
                    continue

        if not best_stream:
            # Fallback to most popular or first active stream
            best_stream = Stream.objects.filter(is_active=True).first()

        session.recommended_stream = best_stream
        session.save()
        return best_stream

    @staticmethod
    def get_result_summary(session: TestSession) -> dict:
        """
        Returns a rich summary of test results.
        """
        answers = TestAnswer.objects.filter(session=session).select_related('question', 'selected_option')
        
        scores = {
            "logical": session.logical_score,
            "quantitative": session.quantitative_score,
            "verbal": session.verbal_score,
            "technical": session.technical_score,
            "arts": session.arts_score,
        }
        
        # Strengths: > 70, Improvement: < 40
        strengths = [cat for cat, score in scores.items() if score > 70]
        improvements = [cat for cat, score in scores.items() if score < 40]
        
        review = []
        for ans in answers:
            correct_opt = ans.question.options.filter(is_correct=True).first()
            review.append({
                "question": ans.question.question_text,
                "your_answer": ans.selected_option.option_text if ans.selected_option else "Not Answered",
                "correct_answer": correct_opt.option_text if correct_opt else "N/A",
                "is_correct": ans.is_correct,
                "explanation": ans.question.explanation,
                "time_taken_seconds": ans.time_taken_seconds or 0,
            })

        dominant = max(scores, key=scores.get)

        return {
            "session_id": session.id,
            "test_type": session.get_test_type_display(),
            "completed_at": session.completed_at,
            "total_time_minutes": round((session.total_time_seconds or 0) / 60, 1),
            "scores": scores,
            "personality_profile": session.personality_profile,
            "riasec_scores": session.riasec_scores,
            "values_scores": session.values_scores,
            "dominant_aptitude": dominant.capitalize(),
            "recommended_stream": {
                "name": session.recommended_stream.name if session.recommended_stream else "None",
                "slug": session.recommended_stream.slug if session.recommended_stream else "",
                "description": session.recommended_stream.description if session.recommended_stream else "",
                "suitable_for": session.recommended_stream.suitable_for if session.recommended_stream else "",
            },
            "percentile": session.percentile,
            "strengths": strengths,
            "improvement_areas": improvements,
            "career_directions": session.recommended_stream.suitable_for.split('\n') if session.recommended_stream else [],
            "answers_review": review
        }
