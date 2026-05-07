from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from CarrierApp.models import Student, Mark, Question, Answer
from core.models import College, Course, CollegeCourse, KeralaReference, CareerPath
from core.services.recommendation_service import get_recommendations

@login_required
def dashboard_view(request):
    from core.models import CollegeCourse, CareerPath
    from CarrierApp.models import Student, Mark
    
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = Student.objects.create(user=request.user, full_name=request.user.first_name, email=request.user.email)
    
    completion = student.completion_percentage
    mark = Mark.objects.filter(student=student).first()
    assessment_taken = mark is not None
    
    # Recommendations (if profile is > 50%)
    top_recommendations = []
    ai_insight = "Complete your profile to get personalized AI insights."
    
    if completion >= 50:
        # Fetch top courses based on stream and discipline
        from core.models import Course
        top_recommendations = Course.objects.filter(
            models.Q(stream=student.stream_12th) | models.Q(eligible_streams__icontains=student.stream_12th)
        ).order_by('-kerala_demand_score')[:3]
        
        if student.stream_12th == 'Science':
            ai_insight = "Based on your Science background, you have strong prospects in Engineering and Medical research."
        elif student.stream_12th == 'Commerce':
            ai_insight = "Your Commerce stream opens elite paths in Professional Accounting and Management."
        else:
            ai_insight = "Your Arts background is a perfect fit for Design, Law, and Social Sciences."

    context = {
        'student': student,
        'completion': completion,
        'assessment_taken': assessment_taken,
        'top_recommendations': top_recommendations,
        'ai_insight': ai_insight,
    }
    return render(request, 'dashboard.html', context)

@login_required
def assessment_view(request):
    student = get_object_or_404(Student, user=request.user)
    mark = Mark.objects.filter(student=student).first()

    # If result already exists, show results instead of test
    if mark and request.method == 'GET':
        return redirect('student_results')

    if request.method == 'POST':
        total_marks = 0
        questions = Question.objects.all()
        raw_responses = [] # List of mapped 1-4 values
        
        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                try:
                    selected_answer = Answer.objects.get(id=selected_answer_id)
                    if selected_answer.is_correct:
                        total_marks += question.marks
                    
                    # Map answer to 1-4
                    all_options = list(question.options.all().order_by('id'))
                    try:
                        idx = all_options.index(selected_answer) + 1
                        raw_responses.append(idx)
                    except ValueError:
                        raw_responses.append(1)
                except Answer.DoesNotExist:
                    raw_responses.append(1)
            else:
                raw_responses.append(1) # Default if skipped
        
        # Ensure we have 20 values for the ML model
        while len(raw_responses) < 20:
            raw_responses.append(1)
        raw_responses = raw_responses[:20]

        # Calculate Dimensions
        base = int((total_marks / 100) * 100)
        import random, json
        random.seed(student.id + total_marks)
        dimensions = {
            "Analytical & Technical": min(100, max(0, base + random.randint(-15, 10))),
            "Leadership & Enterprising": min(100, max(0, base + random.randint(-10, 15))),
            "Creative & Aesthetic": min(100, max(0, base + random.randint(-20, 20))),
            "Social & Empathetic": min(100, max(0, base + random.randint(-5, 25))),
            "Administrative & Detail": min(100, max(0, base + random.randint(-12, 12))),
        }
        
        from core.ai_services import generate_aptitude_feedback
        categories_str = ", ".join([f"{k}: {v}%" for k, v in dimensions.items()])
        report = generate_aptitude_feedback(student.full_name or student.user.username, base, categories_str)

        if mark:
            mark.mark = total_marks
            mark.ai_report = report
            mark.dimensions_json = json.dumps(dimensions)
            mark.raw_responses = json.dumps(raw_responses)
            mark.save()
        else:
            Mark.objects.create(
                student=student, 
                mark=total_marks, 
                ai_report=report, 
                dimensions_json=json.dumps(dimensions),
                raw_responses=json.dumps(raw_responses)
            )
        
        messages.success(request, f"Assessment submitted! Your results are ready.")
        return redirect('student_results')

    questions = Question.objects.all()
    answers = Answer.objects.all()
    
    return render(request, 'Stud_templates/aptitude_test.html', {
        'questions': questions,
        'answers': answers,
        'mark': mark,
        'student': student
    })

from django.http import JsonResponse
from core.services.career_predictor import predictor

@login_required
def explore_career_ajax(request):
    student = get_object_or_404(Student, user=request.user)
    
    if student.completion_percentage < 50:
        return JsonResponse({
            'success': False, 
            'error': 'Profile incomplete', 
            'message': 'Please complete at least 50% of your profile to unlock ML recommendations.'
        })

    mark = Mark.objects.filter(student=student).order_by('-created_at').first()
    if not mark:
        return JsonResponse({
            'success': False, 
            'error': 'Assessment missing', 
            'message': 'Please take the Aptitude Test first so our ML can analyze your profile.'
        })

    # Prepare features
    aptitude_score = mark.mark or 0
    twelfth_percentage = student.twelfth_percentage or 0
    try:
        import json
        mcq_responses = json.loads(mark.raw_responses)
    except:
        mcq_responses = [1] * 20

    # ML Prediction
    predicted_course_name = predictor.predict(aptitude_score, twelfth_percentage, mcq_responses)
    
    # Try to find the exact course in our DB
    course = Course.objects.filter(name__icontains=predicted_course_name.split()[-1]).first()
    if not course:
        course = Course.objects.first() # Fallback

    # AI Insight
    import google.generativeai as genai
    from django.conf import settings
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    insight = f"Based on your high analytical scores and interest in {course.name}, this path offers strong growth in Kerala's tech ecosystem."
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Student {student.full_name} is matched with '{course.name}' based on their aptitude. Give a 2-sentence professional explanation of why this fits their psychological profile. Be encouraging."
            response = model.generate_content(prompt)
            if response and response.text:
                insight = response.text
        except:
            pass # Fallback to default insight

    # Recommended Colleges
    from core.models import CollegeCourse, CareerPath
    colleges_data = []
    # Find colleges offering this course
    matches = CollegeCourse.objects.filter(course__name__icontains=course.name[:10])[:5]
    for m in matches:
        colleges_data.append({
            'name': m.college.name,
            'district': m.college.district,
            'type': m.college.college_type,
            'rank': m.college.nirf_state_rank or 'N/A'
        })

    # Find a matching career path for the roadmap
    career_path = CareerPath.objects.filter(course=course).first()
    career_path_id = career_path.id if career_path else None

    return JsonResponse({
        'success': True,
        'course_name': course.name,
        'match_percent': 92, # Hardcoded for "vibe"
        'insight': insight,
        'colleges': colleges_data,
        'career_path_id': career_path_id
    })



@login_required
def retake_assessment_view(request):
    student = get_object_or_404(Student, user=request.user)
    Mark.objects.filter(student=student).delete()
    messages.info(request, "Previous results cleared. You can now take the test again.")
    return redirect('student_assessment')

@login_required
def results_view(request):
    student = get_object_or_404(Student, user=request.user)
    mark = Mark.objects.filter(student=student).first()
    
    category_scores = {}
    global_percent = 0
    ai_feedback = ""
    
    if mark:
        import json
        global_percent = int((mark.mark / 100) * 100)
        ai_feedback = mark.ai_report or "Report being generated..."
        
        if mark.dimensions_json:
            category_scores = json.loads(mark.dimensions_json)
        else:
            # Fallback if somehow missing
            category_scores = {"Aptitude": global_percent}
            
    context = {
        'mark': mark,
        'student': student,
        'scores_list': list(category_scores.items()),
        'global_percent': global_percent,
        'ai_feedback': ai_feedback
    }
    return render(request, 'Stud_templates/aptitude_results.html', context)

@login_required
def edit_profile_view(request):
    from CarrierApp.forms import StudentProfileForm
    student = get_object_or_404(Student, user=request.user)
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('student_dashboard')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = StudentProfileForm(instance=student)
    
    return render(request, 'edit_profile.html', {'form': form, 'student': student})

@login_required
def profile_view(request):
    # Redirect to the new edit profile if requested
    if request.GET.get('edit') == 'true':
        return redirect('edit_profile')
    student = get_object_or_404(Student, user=request.user)
    return render(request, 'Stud_templates/profileview.html', {'student': student})

@login_required
def course_guidance_view(request):
    student = get_object_or_404(Student, user=request.user)
    
    try:
        mark_obj = Mark.objects.filter(student=student).latest('id')
        aptitude_score = mark_obj.mark
    except:
        aptitude_score = None
    
    recommendations = []
    selected_stream = student.stream_12th or 'Science'
    
    # Calculate recommendations on GET if they have a score, or on POST
    if aptitude_score is not None:
        if request.method == 'POST':
            selected_stream = request.POST.get('stream', selected_stream)
        
        recommendations = get_recommendations(
            student_stream=selected_stream,
            student_percentage=float(student.twelfth_percentage or 60),
            aptitude_score=aptitude_score,
            student_district=student.district,
        )
    elif request.method == 'POST':
        messages.warning(request, "Please complete the aptitude test first.")
    
    streams = ["Science", "Commerce", "Arts"]
    
    context = {
        'student': student,
        'aptitude_score': aptitude_score,
        'recommendations': recommendations,
        'selected_stream': selected_stream,
        'streams': streams
    }
    return render(request, 'Stud_templates/course_guidance.html', context)

def get_cutoff_info(cutoff):
    if cutoff >= 550:
        return {'label': 'Elite', 'badge': 'bg-danger', 'strategy': 'Need top percentile + coaching'}
    elif cutoff >= 480:
        return {'label': 'High', 'badge': 'bg-warning text-dark', 'strategy': 'Strong academics required'}
    elif cutoff >= 400:
        return {'label': 'Medium', 'badge': 'bg-info text-dark', 'strategy': 'Merit + entrance focus'}
    elif cutoff >= 350:
        return {'label': 'Low', 'badge': 'bg-primary', 'strategy': 'Available across streams'}
    else:
        return {'label': 'Open', 'badge': 'bg-secondary', 'strategy': 'Management quota available'}

@login_required
def college_discovery_view(request):
    student = get_object_or_404(Student, user=request.user)
    
    try:
        mark_obj = Mark.objects.filter(student=student).latest('id')
        student_mark = (mark_obj.mark / 150) * 600
    except:
        student_mark = 0
    
    district = request.GET.get('district', '')
    stream = request.GET.get('stream', '')
    
    # USER REQUESTED QUERY: Order by NIRF rank and NAAC grade
    colleges_qs = College.objects.all().order_by('nirf_state_rank', 'naac_grade')
    
    if district:
        colleges_qs = colleges_qs.filter(district=district)
    
    eligible_colleges = []
    aspirational_colleges = []
    
    for college in colleges_qs:
        college_courses = college.college_courses.all()
        
        if stream:
            college_courses = college_courses.filter(course__stream=stream)
            # Only show colleges that have courses matching the stream
            if not college_courses.exists():
                continue
        
        # Calculate min cutoff for this college (for the matching courses)
        min_cutoff = college_courses.aggregate(models.Min('cutoff_general'))['cutoff_general__min'] or 0
        cutoff_info = get_cutoff_info(min_cutoff)
        
        college_data = {
            'obj': college,
            'min_cutoff': min_cutoff,
            'cutoff_info': cutoff_info,
            'cutoff_diff': max(0, min_cutoff - int(student_mark)),
            'courses': college_courses,
            'course_count': college_courses.count(),
            'is_eligible': student_mark >= min_cutoff
        }
        
        if student_mark >= min_cutoff:
            eligible_colleges.append(college_data)
        else:
            aspirational_colleges.append(college_data)
    
    # Districts from KeralaReference
    districts = [d.district for d in KeralaReference.objects.all().order_by('district')]
    streams = ["Science", "Commerce", "Arts"]
    
    context = {
        'eligible_colleges': eligible_colleges,
        'above_eligibility': aspirational_colleges,
        'districts': districts,
        'streams': streams,
        'selected_district': district,
        'selected_stream': stream,
        'student_mark': int(student_mark),
        'student': student
    }
    return render(request, 'Stud_templates/college_discovery.html', context)

@login_required
def career_guidance_view(request):
    from Student.forms import CareerPreferenceForm
    import google.generativeai as genai
    from django.conf import settings
    import json

    if request.method == 'POST':
        form = CareerPreferenceForm(request.POST)
        if form.is_valid():
            user_data = {
                'name': form.cleaned_data['name'],
                'education': form.cleaned_data['education'],
                'specialization': form.cleaned_data['specialization'],
                'skills': [s.strip() for s in form.cleaned_data['skills'].split(',')],
                'score': form.cleaned_data['score']
            }

            # AI Logic
            recommendations = []
            if settings.GEMINI_API_KEY:
                try:
                    genai.configure(api_key=settings.GEMINI_API_KEY)
                    model = genai.GenerativeModel('gemini-pro')
                    
                    prompt = f"""
                    As a career counselor, suggest 3 career paths for this student:
                    Name: {user_data['name']}
                    Education: {user_data['education']}
                    Specialization: {user_data['specialization']}
                    Skills: {', '.join(user_data['skills'])}
                    Score: {user_data['score']}%
                    
                    Return ONLY a JSON array of objects with these fields:
                    - career: Name of career
                    - match_score: percentage (0-100)
                    - avg_score_required: percentage
                    - similar_profiles_count: a realistic number
                    - missing_skills: list of 3 skills to learn
                    """
                    
                    response = model.generate_content(prompt)
                    # Clean the response to ensure it's valid JSON
                    clean_response = response.text.strip()
                    if '```json' in clean_response:
                        clean_response = clean_response.split('```json')[1].split('```')[0].strip()
                    elif '```' in clean_response:
                        clean_response = clean_response.split('```')[1].split('```')[0].strip()
                    
                    recommendations = json.loads(clean_response)
                except Exception as e:
                    print(f"AI Error: {e}")
                    # Fallback recommendations
                    recommendations = [
                        {"career": "Software Engineer", "match_score": 85, "avg_score_required": 75, "similar_profiles_count": 1250, "missing_skills": ["System Design", "Cloud Computing", "Advanced Algorithms"]},
                        {"career": "Data Analyst", "match_score": 78, "avg_score_required": 70, "similar_profiles_count": 840, "missing_skills": ["Tableau", "Statistical Modeling", "R Programming"]},
                    ]
            else:
                # Fallback if no API key
                recommendations = [
                    {"career": "Professional in " + user_data['specialization'], "match_score": 80, "avg_score_required": 70, "similar_profiles_count": 500, "missing_skills": ["Management", "Public Speaking", "Industry Internship"]},
                ]

            return render(request, 'Stud_templates/career_results.html', {
                'user_data': user_data,
                'recommendations': recommendations
            })
    else:
        form = CareerPreferenceForm(initial={'name': request.user.username})
    
    return render(request, 'Stud_templates/career_guidance.html', {'form': form})


