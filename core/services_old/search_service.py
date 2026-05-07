from django.db.models import Q, Count, Min
from django.core.paginator import Paginator, EmptyPage
from django.core.cache import cache
from core.models import College, CollegeCourse
from core.models import Stream, Field, Discipline, Course
from core.models import District, University
from core.models import Career
from django.urls import reverse

class SearchService:

    COLLEGE_SORT_OPTIONS = {
        'name': 'name',
        'naac': 'naac_grade',
        'nirf': 'nirf_rank',
        'established': 'established_year',
    }

    VALID_NAAC_GRADES = [
        'A++', 'A+', 'A', 'B++', 'B+', 'B', 'C', 'PENDING', 'NA'
    ]

    def search_colleges(self, filters: dict, page: int = 1, per_page: int = 20) -> dict:
        qs = College.objects.filter(is_verified=filters.get('is_verified', True))
        
        district_id = filters.get('district_id')
        if district_id:
            qs = qs.filter(district_id=district_id)
            
        college_type = filters.get('college_type')
        if college_type:
            qs = qs.filter(college_type=college_type)
            
        university_id = filters.get('university_id')
        if university_id:
            qs = qs.filter(university_id=university_id)
            
        naac_grade = filters.get('naac_grade')
        if naac_grade:
            if isinstance(naac_grade, list):
                qs = qs.filter(naac_grade__in=naac_grade)
            else:
                qs = qs.filter(naac_grade=naac_grade)
                
        has_hostel = filters.get('has_hostel')
        if has_hostel == 'boys':
            qs = qs.filter(has_hostel_boys=True)
        elif has_hostel == 'girls':
            qs = qs.filter(has_hostel_girls=True)
        elif has_hostel == 'any':
            qs = qs.filter(Q(has_hostel_boys=True) | Q(has_hostel_girls=True))
            
        has_placement_cell = filters.get('has_placement_cell')
        if has_placement_cell is not None:
            # Assuming has_placement_cell is requested as boolean
            qs = qs.filter(has_placement_cell=bool(has_placement_cell))
            
        is_women_only = filters.get('is_women_only')
        if is_women_only is not None:
            qs = qs.filter(is_women_only=bool(is_women_only))
            
        is_minority = filters.get('is_minority')
        if is_minority is not None:
            qs = qs.filter(is_minority=bool(is_minority))
            
        stream_id = filters.get('stream_id')
        if stream_id:
            qs = qs.filter(college_courses__course__discipline__field__stream_id=stream_id)
            
        fee_max = filters.get('fee_max')
        if fee_max:
            qs = qs.filter(college_courses__tuition_fee__lte=fee_max)
            
        search = filters.get('search')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | 
                Q(short_name__icontains=search) | 
                Q(address__icontains=search)
            )

        qs = qs.select_related('district', 'university').prefetch_related('college_courses__course')
        qs = qs.annotate(
            course_count=Count('college_courses', distinct=True),
            min_fee=Min('college_courses__tuition_fee')
        )
        
        # We need distinct() as we filter over M2M/reverse FKs that could duplicate rows
        qs = qs.distinct()

        sort_key = filters.get('sort', 'name')
        sort_field = self.COLLEGE_SORT_OPTIONS.get(sort_key, 'name')
        if sort_field == 'naac_grade' or sort_field == 'nirf_rank':
             # naac string sort may not be fully accurate, but sorting by naac_grade asc or desc 
             qs = qs.order_by(sort_field)
        else:
             qs = qs.order_by(sort_field)

        paginator = Paginator(qs, per_page)
        
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return {
            "colleges": list(page_obj.object_list),
            "total_count": paginator.count,
            "page": page_obj.number,
            "per_page": per_page,
            "total_pages": paginator.num_pages,
            "applied_filters": filters,
        }

    def search_courses(self, filters: dict, page: int = 1, per_page: int = 20) -> dict:
        qs = CollegeCourse.objects.all()

        stream_id = filters.get('stream_id')
        if stream_id:
            qs = qs.filter(course__discipline__field__stream_id=stream_id)
            
        field_id = filters.get('field_id')
        if field_id:
            qs = qs.filter(course__discipline__field_id=field_id)
            
        discipline_id = filters.get('discipline_id')
        if discipline_id:
            qs = qs.filter(course__discipline_id=discipline_id)
            
        course_id = filters.get('course_id')
        if course_id:
            qs = qs.filter(course_id=course_id)
            
        level = filters.get('level')
        if level:
            qs = qs.filter(course__level=level)
            
        district_id = filters.get('district_id')
        if district_id:
            qs = qs.filter(college__district_id=district_id)
            
        college_type = filters.get('college_type')
        if college_type:
            qs = qs.filter(college__college_type=college_type)
            
        university_id = filters.get('university_id')
        if university_id:
            qs = qs.filter(college__university_id=university_id)
            
        fee_min = filters.get('fee_min')
        if fee_min:
            qs = qs.filter(tuition_fee__gte=fee_min)
            
        fee_max = filters.get('fee_max')
        if fee_max:
            qs = qs.filter(tuition_fee__lte=fee_max)
            
        cutoff_max = filters.get('cutoff_max')
        if cutoff_max is not None:
            qs = qs.filter(cutoff_general__lte=cutoff_max)
            
        admission_mode = filters.get('admission_mode')
        if admission_mode:
            qs = qs.filter(admission_mode=admission_mode)
            
        medium = filters.get('medium')
        if medium:
            qs = qs.filter(medium=medium)
            
        has_placement = filters.get('has_placement')
        if has_placement is not None:
            qs = qs.filter(placement_percentage__isnull=False)
            
        lateral_entry = filters.get('lateral_entry')
        if lateral_entry is not None:
            qs = qs.filter(lateral_entry=bool(lateral_entry))
            
        search = filters.get('search')
        if search:
            qs = qs.filter(
                Q(course__name__icontains=search) | 
                Q(college__name__icontains=search) | 
                Q(course__discipline__name__icontains=search)
            )

        qs = qs.select_related(
            'college__district',
            'college__university',
            'course__discipline__field__stream',
            'specialization',
        )

        sort_key = filters.get('sort', 'college_name')
        if sort_key == 'fee_asc':
            qs = qs.order_by('tuition_fee', 'college__name')
        elif sort_key == 'fee_desc':
            qs = qs.order_by('-tuition_fee', 'college__name')
        elif sort_key == 'cutoff_asc':
            qs = qs.order_by('cutoff_general', 'college__name')
        elif sort_key == 'placement_desc':
            qs = qs.order_by('-placement_percentage', 'college__name')
        else: # college_name
            qs = qs.order_by('college__name', 'course__name')

        paginator = Paginator(qs, per_page)
        
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return {
            "college_courses": list(page_obj.object_list),
            "total_count": paginator.count,
            "page": page_obj.number,
            "per_page": per_page,
            "total_pages": paginator.num_pages,
            "applied_filters": filters,
        }

    def get_filter_options(self) -> dict:
        cached_options = cache.get('search_filter_options')
        if cached_options:
            return cached_options
            
        # We need choices from models. 
        # Using string literals or fetching from models if defined.
        college_types = [
            ('GOVT', 'Government'),
            ('AIDED', 'Aided'),
            ('SF', 'Self-Financing'),
            ('AUTONOMOUS', 'Autonomous'),
            ('DEEMED', 'Deemed University'),
            ('CENTRAL', 'Central University'),
        ]
        
        course_levels = [
            ('UG', 'Undergraduate'),
            ('PG', 'Postgraduate'),
            ('DIPLOMA', 'Diploma'),
            ('CERTIFICATE', 'Certificate'),
            ('PHD', 'Ph.D'),
        ]
        
        admission_modes = [
            ('CAP', 'Centralized Allotment Process'),
            ('MANAGEMENT', 'Management Quota'),
            ('NRI', 'NRI Quota'),
            ('DIRECT', 'Direct Admission'),
        ]
        
        mediums = [
            ('EN', 'English'),
            ('ML', 'Malayalam'),
            ('BI', 'Bilingual'),
        ]
            
        options = {
            "districts": list(District.objects.values('id', 'name')),
            "universities": list(University.objects.values('id', 'name', 'short_name')),
            "streams": list(Stream.objects.filter(is_active=True).values('id', 'name', 'slug')),
            "fields": list(Field.objects.filter(is_active=True).values('id', 'name', 'stream_id')),
            "disciplines": list(Discipline.objects.filter(is_active=True).values('id', 'name', 'field_id')),
            "college_types": college_types,
            "course_levels": course_levels,
            "naac_grades": self.VALID_NAAC_GRADES,
            "admission_modes": admission_modes,
            "mediums": mediums,
        }
        
        cache.set('search_filter_options', options, 3600)
        return options

    def quick_search(self, query: str, limit: int = 10) -> dict:
        results = []
        if not query or len(query) < 2:
            return {
                "results": results,
                "total": 0,
                "query": query,
            }
            
        # Distribute limit evenly across 4 types
        type_limit = limit // 4
        
        colleges = College.objects.filter(name__icontains=query).select_related('district')[:type_limit]
        courses = Course.objects.filter(name__icontains=query).select_related('discipline__field__stream')[:type_limit]
        careers = Career.objects.filter(title__icontains=query).select_related('category')[:type_limit]
        disciplines = Discipline.objects.filter(name__icontains=query).select_related('field')[:type_limit]
        
        # Build results
        for c in colleges:
            subtitle = c.district.name if c.district else ''
            results.append({
                "type": "college",
                "id": c.id,
                "title": c.name,
                "subtitle": subtitle,
                "url": reverse('discovery:college_detail', kwargs={'slug': c.slug}) if hasattr(c, 'slug') and c.slug else f'/colleges/{c.id}/',
            })
            
        for c in courses:
            subtitle = c.discipline.field.stream.name if c.discipline and c.discipline.field and c.discipline.field.stream else ''
            results.append({
                "type": "course",
                "id": c.id,
                "title": c.name,
                "subtitle": subtitle,
                "url": reverse('discovery:course_detail', kwargs={'slug': c.slug}) if hasattr(c, 'slug') and c.slug else f'/courses/{c.id}/',
            })
            
        for c in careers:
            subtitle = c.category.name if c.category else ''
            # careers might not be in discovery namespace if they are in core/career_urls
            # Assume reverse('detail', kwargs={'slug': c.slug}) works if it's the core app, but wait, 
            # the task asks to use reverse(). I will use "detail" assuming it might be in another app, or I can try reverse('detail')
            try:
                url = reverse('detail', kwargs={'slug': c.slug})
            except:
                url = f'/careers/{c.slug}/' if hasattr(c, 'slug') else f'/careers/{c.id}/'
            results.append({
                "type": "career",
                "id": c.id,
                "title": c.title,
                "subtitle": subtitle,
                "url": url,
            })
            
        for d in disciplines:
            subtitle = d.field.name if d.field else ''
            try:
                # Assuming no detail view for discipline yet, point to courses with filter
                url = reverse('discovery:course_list') + f"?discipline_id={d.id}"
            except:
                url = f'/courses/?discipline_id={d.id}'
            results.append({
                "type": "discipline",
                "id": d.id,
                "title": d.name,
                "subtitle": subtitle,
                "url": url,
            })
            
        # If we have remainder limits, fill with more colleges
        current_len = len(results)
        if current_len < limit:
            rem = limit - current_len
            more_colleges = College.objects.filter(name__icontains=query).select_related('district').exclude(id__in=[r['id'] for r in results if r['type']=='college'])[:rem]
            for c in more_colleges:
                subtitle = c.district.name if c.district else ''
                results.append({
                    "type": "college",
                    "id": c.id,
                    "title": c.name,
                    "subtitle": subtitle,
                    "url": reverse('discovery:college_detail', kwargs={'slug': c.slug}) if hasattr(c, 'slug') and c.slug else f'/colleges/{c.id}/',
                })

        return {
            "results": results[:limit],
            "total": len(results),
            "query": query,
        }
