from django.contrib import admin
from .models import College, Course, CollegeCourse, CareerPath, KeralaReference

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'college_type', 'naac_grade', 'nirf_state_rank')
    list_filter = ('district', 'college_type', 'naac_grade')
    search_fields = ('name', 'college_id', 'city')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'stream', 'degree_type', 'duration_years', 'kerala_demand_score')
    list_filter = ('stream', 'degree_type', 'cap_applicable')
    search_fields = ('name', 'course_id')

@admin.register(CollegeCourse)
class CollegeCourseAdmin(admin.ModelAdmin):
    list_display = ('college', 'course', 'cutoff_general', 'total_intake', 'fee_per_year')
    list_filter = ('college__district', 'course__stream')
    search_fields = ('college__name', 'course__name')

@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = ('career_path_name', 'course', 'demand_score', 'gulf_opportunity')
    list_filter = ('gulf_opportunity', 'course__stream')
    search_fields = ('career_path_name', 'course__name')

@admin.register(KeralaReference)
class KeralaReferenceAdmin(admin.ModelAdmin):
    list_display = ('district', 'region', 'university_affiliation')
    list_filter = ('region',)
    search_fields = ('district',)
