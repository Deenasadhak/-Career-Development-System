from django.views.generic import View, DetailView
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import PSCDepartment, PSCPost, GulfCountry
from core.services.kerala_service import KeralaService

class CAPGuidanceView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'student_profile'):
            return redirect('login')
        
        profile = request.user.student_profile
        from core.models import StudentRecommendation
        if not StudentRecommendation.objects.filter(student=profile).exists():
            from django.contrib import messages
            messages.info(request, "Please generate your recommendations first to get CAP guidance.")
            return redirect('recommendations:generate')
            
        kerala_svc = KeralaService()
        guidance = kerala_svc.get_cap_guidance(profile)
        
        current_round = None
        if guidance['cap_rounds']:
            current_round = guidance['cap_rounds'][-1]
            for r in guidance['cap_rounds']:
                if r.is_active:
                    current_round = r
                    break
                    
        context = {
            'guidance': guidance,
            'current_round': current_round,
            'has_keam': profile.keam_rank is not None,
            'has_neet': profile.neet_score is not None,
        }
        return render(request, 'core/kerala/cap_guidance.html', context)


class PSCOpportunitiesView(View):
    def get(self, request, *args, **kwargs):
        dept_slug = request.GET.get('department')
        search_q = request.GET.get('search')
        
        qs = PSCPost.objects.filter(is_active=True).select_related('department')
        
        if dept_slug:
            qs = qs.filter(department__slug=dept_slug)
        if search_q:
            qs = qs.filter(title__icontains=search_q)
            
        paginator = Paginator(qs, 15)
        page = request.GET.get('page', 1)
        posts = paginator.get_page(page)
        
        departments = PSCDepartment.objects.all()
        
        context = {
            'posts': posts,
            'departments': departments,
            'selected_department': dept_slug,
        }
        
        if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
            kerala_svc = KeralaService()
            context['personalized_posts'] = kerala_svc.get_psc_opportunities(request.user.student_profile)
            
        return render(request, 'core/kerala/psc_list.html', context)


class PSCPostDetailView(DetailView):
    model = PSCPost
    template_name = 'core/kerala/psc_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return PSCPost.objects.select_related('department').prefetch_related(
            'related_careers', 'required_courses'
        )


class GulfOpportunitiesView(View):
    def get(self, request, *args, **kwargs):
        profile = request.user.student_profile if (request.user.is_authenticated and hasattr(request.user, 'student_profile')) else None
        
        kerala_svc = KeralaService()
        gulf_data = kerala_svc.get_gulf_opportunities(profile)
        
        countries = GulfCountry.objects.filter(is_active=True).order_by('-kerala_workers_estimate')
        top_careers = sorted([c.career for c in gulf_data['top_opportunities']], key=lambda x: x.title)[:5]
        
        context = {
            'gulf_data': gulf_data,
            'countries': countries,
            'top_careers': top_careers,
        }
        return render(request, 'core/kerala/gulf_list.html', context)


class GulfCountryDetailView(DetailView):
    model = GulfCountry
    template_name = 'core/kerala/gulf_country.html'
    context_object_name = 'country'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        country = self.object
        
        opps = country.career_opportunities.filter(is_active=True).select_related('career')
        
        opportunities_by_demand = {
            'HIGH': [],
            'MEDIUM': [],
            'LOW': [],
        }
        
        for opp in opps:
            opportunities_by_demand[opp.demand_level].append(opp)
            
        context['opportunities_by_demand'] = opportunities_by_demand
        context['total_opportunities'] = opps.count()
        return context


class AyurvedaPathwaysView(View):
    def get(self, request, *args, **kwargs):
        kerala_svc = KeralaService()
        context = {'pathway_data': kerala_svc.get_ayurveda_pathways()}
        return render(request, 'core/kerala/ayurveda.html', context)


class TourismPathwaysView(View):
    def get(self, request, *args, **kwargs):
        kerala_svc = KeralaService()
        context = {'pathway_data': kerala_svc.get_tourism_pathways()}
        return render(request, 'core/kerala/tourism.html', context)
