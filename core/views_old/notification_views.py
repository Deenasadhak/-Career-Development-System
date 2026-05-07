from django.views.generic import ListView, TemplateView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms
from core.models import Notification, NotificationPreference
from core.services.notification_service import NotificationService
from django.utils import timezone

class NotificationListView(LoginRequiredMixin, ListView):
    template_name = 'core/notifications/list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        svc = NotificationService()
        return svc.get_notifications(self.request.user, include_read=True, limit=50)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        svc = NotificationService()
        context['unread_count'] = svc.get_unread_count(self.request.user)
        
        # Group notifications
        now = timezone.now()
        today = now.date()
        week_ago = today - timezone.timedelta(days=7)
        
        grouped = {
            'today': [],
            'this_week': [],
            'older': []
        }
        
        for n in context['notifications']:
            dt = n.created_at.date()
            if dt == today:
                grouped['today'].append(n)
            elif dt >= week_ago:
                grouped['this_week'].append(n)
            else:
                grouped['older'].append(n)
                
        context['grouped_notifications'] = grouped
        context['preferences'], _ = NotificationPreference.objects.get_or_create(user=self.request.user)
        return context

class MarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        svc = NotificationService()
        success = svc.mark_read(request.user, pk)
        unread_count = svc.get_unread_count(request.user)
        return JsonResponse({"success": success, "unread_count": unread_count})

class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        svc = NotificationService()
        updated = svc.mark_all_read(request.user)
        return JsonResponse({"updated": updated, "unread_count": 0})

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        exclude = ['user']

class NotificationPreferenceView(LoginRequiredMixin, View):
    template_name = 'core/notifications/preferences.html'

    def get(self, request):
        pref, _ = NotificationPreference.objects.get_or_create(user=request.user)
        form = NotificationPreferenceForm(instance=pref)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        pref, _ = NotificationPreference.objects.get_or_create(user=request.user)
        form = NotificationPreferenceForm(request.POST, instance=pref)
        if form.is_valid():
            form.save()
            messages.success(request, "Notification preferences updated successfully.")
            return redirect('notifications:preferences')
        return render(request, self.template_name, {'form': form})

class NotificationCountView(LoginRequiredMixin, View):
    def get(self, request):
        svc = NotificationService()
        return JsonResponse({"unread_count": svc.get_unread_count(request.user)})
