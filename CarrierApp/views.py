from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View

from core.models import College, Course, CareerPath

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    return render(request, 'landing.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('explore')
    
    if request.method == 'POST':
        # Read form data
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not full_name:
            errors.append("Full name is required.")
        if not username:
            errors.append("Username is required.")
        if len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not email:
            errors.append("Email is required.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        
        # Check if username exists
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            errors.append("Username already taken. Choose another.")
        if User.objects.filter(email=email).exists():
            errors.append("Email already registered.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'register.html', {
                'form_data': request.POST
            })
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            # Set role
            user.first_name = full_name
            user.role = 'STUDENT'
            user.save()
            
            # Create profile
            from CarrierApp.models import Student
            Student.objects.get_or_create(user=user, defaults={'full_name': full_name, 'email': email})
            
            # Auto login after registration
            login(request, user)
            messages.success(request, 
                f"Welcome to Future Pathways, {full_name}! "
                "Explore our career recommendations.")
            
            return redirect('explore')
                
        except Exception as e:
            messages.error(request, 
                f"Registration failed: {str(e)}")
            return render(request, 'register.html', {
                'form_data': request.POST
            })
    
    return render(request, 'register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('explore')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, "Both fields are required.")
            return render(request, 'login.html')
        
        user = authenticate(request, username=username, 
                           password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 
                f"Welcome back, {user.first_name or user.username}!")
            
            # Redirect to explore or next param
            next_url = request.GET.get('next', '')
            if next_url:
                # Sanitize next_url: if it points to legacy student/college apps, redirect to explore instead
                if next_url.startswith('/student/') or next_url.startswith('/college/'):
                    return redirect('explore')
                return redirect(next_url)
            
            return redirect('explore')
        else:
            messages.error(request, 
                "Invalid username or password. Please try again.")
            return render(request, 'login.html',
                        {'username': username})
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('landing')

@login_required
def explore_view(request):
    query = request.GET.get('q', '')
    district = request.GET.get('district', '')
    
    from django.db.models import Count
    colleges = College.objects.all().annotate(course_count=Count('college_courses')).prefetch_related('college_courses__course').order_by('nirf_state_rank')
    
    if query:
        colleges = colleges.filter(name__icontains=query)
    if district:
        colleges = colleges.filter(district=district)
        
    districts = College.objects.exclude(district__isnull=True).exclude(district='').values_list('district', flat=True).distinct().order_by('district')
    
    return render(request, 'explore.html', {
        'colleges': colleges,
        'districts': districts,
        'query': query,
        'selected_district': district
    })

@login_required
def recommend_view(request):
    from CarrierApp.models import Student
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = Student.objects.create(user=request.user, full_name=request.user.first_name, email=request.user.email)
    
    if student.completion_percentage < 50:
        messages.warning(request, "Help us get to know you! Complete your profile (at least 50%) to see personalized course matches.")
        return redirect('edit_profile')

    from core.models import Course, College, CollegeCourse
    from django.db.models import Q
    
    # Get dynamic options
    streams = Course.objects.exclude(stream='').values_list('stream', flat=True).distinct().order_by('stream')
    districts = College.objects.exclude(district='').exclude(district__icontains='(').values_list('district', flat=True).distinct().order_by('district')
    # Use disciplines as interest areas
    interest_areas = Course.objects.exclude(discipline='').values_list('discipline', flat=True).distinct().order_by('discipline')
    
    recommendations = None
    if request.method == 'POST':
        stream = request.POST.get('stream')
        interest = request.POST.get('interest')
        percentage = request.POST.get('percentage', 0)
        district = request.POST.get('district')
        
        try:
            percentage = int(percentage)
        except ValueError:
            percentage = 0
            
        # Recommendation logic
        # 1. Start with courses matching the interest area
        courses = Course.objects.filter(discipline__iexact=interest)
        
        # 2. Filter by percentage eligibility
        courses = courses.filter(min_percentage__lte=percentage)
        
        # 3. Filter by stream (allow some flexibility)
        courses = courses.filter(Q(eligible_streams__icontains=stream) | Q(stream=stream))
        
        # 4. Get available colleges for these courses
        colleges_courses = CollegeCourse.objects.filter(course__in=courses).select_related('college', 'course')
        
        if district and district != 'All Kerala':
            colleges_courses = colleges_courses.filter(college__district=district)
            
        # 5. Order by demand and fee (if available)
        colleges_courses = colleges_courses.order_by('-course__kerala_demand_score')[:10]
        
        recommendations = colleges_courses
        
        if not recommendations:
            messages.info(request, "We couldn't find exact matches. Try broadening your criteria.")

    return render(request, 'recommend.html', {
        'streams': streams,
        'districts': districts,
        'interest_areas': interest_areas,
        'recommendations': recommendations,
        'form_data': request.POST if request.method == 'POST' else {}
    })

@login_required
def careers_view(request):
    career_paths = CareerPath.objects.all().select_related('course')
    return render(request, 'careers.html', {
        'career_paths': career_paths
    })

@login_required
def generate_roadmap_view(request, career_id):
    from core.models import CareerPath
    from core.ai_services import generate_career_roadmap
    from django.http import JsonResponse
    
    try:
        path = CareerPath.objects.get(id=career_id)
        result = generate_career_roadmap(path.career_path_name, path.course.name)
        return JsonResponse(result)
    except CareerPath.DoesNotExist:
        return JsonResponse({"error": "Career path not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
