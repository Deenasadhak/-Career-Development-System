from django.views.generic import TemplateView, DetailView, View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.db.models import Count
from core.models import ForumPost, ForumCategory, ForumReply, ForumUpvote
from core.models import Stream
from core.services.forum_service import ForumService

class ForumHomeView(TemplateView):
    template_name = 'core/forum/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        svc = ForumService()
        user = self.request.user if self.request.user.is_authenticated else None
        
        sort = self.request.GET.get('sort', 'latest')
        page = self.request.GET.get('page', 1)
        
        feed = svc.get_feed(user=user, sort=sort, page=int(page))
        context['feed'] = feed
        context['categories'] = ForumCategory.objects.filter(is_active=True)
        
        # popular tags - flatten and count
        all_tags = ForumPost.objects.filter(is_active=True).values_list('tags', flat=True)
        tag_counts = {}
        for tags in all_tags:
            for t in tags:
                tag_counts[t] = tag_counts.get(t, 0) + 1
        
        context['popular_tags'] = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        context['unanswered_count'] = feed['unanswered_count']
        
        if user:
            context['recent_by_user'] = ForumPost.objects.filter(author=user, is_active=True).order_by('-created_at')[:3]
            
        return context

class ForumCategoryView(ForumHomeView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(ForumCategory, slug=self.kwargs['slug'], is_active=True)
        svc = ForumService()
        user = self.request.user if self.request.user.is_authenticated else None
        
        sort = self.request.GET.get('sort', 'latest')
        page = self.request.GET.get('page', 1)
        
        feed = svc.get_feed(user=user, category_id=category.id, sort=sort, page=int(page))
        context['feed'] = feed
        context['selected_category'] = category
        return context

class ForumPostDetailView(View):
    template_name = 'core/forum/post_detail.html'

    def get(self, request, pk, slug):
        svc = ForumService()
        svc.increment_view_count(pk)
        detail = svc.get_post_detail(pk, request.user)
        if not detail:
            return redirect('forum:home')
            
        return render(request, self.template_name, detail)

    def post(self, request, pk, slug):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to reply.")
            
        body = request.POST.get('body')
        parent_id = request.POST.get('parent_reply_id')
        
        svc = ForumService()
        try:
            reply = svc.create_reply(
                author=request.user,
                post_id=pk,
                body=body,
                parent_reply_id=parent_id if parent_id else None
            )
            return redirect(f"{request.path}#reply-{reply.pk}")
        except ValueError as e:
            messages.error(request, str(e))
            detail = svc.get_post_detail(pk, request.user)
            return render(request, self.template_name, detail)

class CreatePostView(LoginRequiredMixin, View):
    template_name = 'core/forum/create_post.html'

    def get(self, request):
        categories = ForumCategory.objects.filter(is_active=True)
        streams = Stream.objects.all()
        return render(request, self.template_name, {'categories': categories, 'streams': streams})

    def post(self, request):
        title = request.POST.get('title')
        body = request.POST.get('body')
        category_id = request.POST.get('category')
        tags_raw = request.POST.get('tags', '')
        tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
        
        svc = ForumService()
        try:
            post = svc.create_post(
                author=request.user,
                title=title,
                body=body,
                category_id=category_id,
                tags=tags,
                related_stream_id=request.POST.get('related_stream')
            )
            return redirect('forum:post_detail', pk=post.pk, slug=post.slug)
        except ValueError as e:
            messages.error(request, str(e))
            categories = ForumCategory.objects.filter(is_active=True)
            streams = Stream.objects.all()
            return render(request, self.template_name, {'categories': categories, 'streams': streams})

class UpvotePostView(LoginRequiredMixin, View):
    def post(self, request, pk):
        svc = ForumService()
        res = svc.toggle_upvote_post(request.user, pk)
        return JsonResponse(res)

class UpvoteReplyView(LoginRequiredMixin, View):
    def post(self, request, pk):
        svc = ForumService()
        res = svc.toggle_upvote_reply(request.user, pk)
        return JsonResponse(res)

class MarkAnswerView(LoginRequiredMixin, View):
    def post(self, request, pk):
        svc = ForumService()
        try:
            success = svc.mark_verified_answer(request.user, pk)
            return JsonResponse({"success": success})
        except PermissionError:
            return JsonResponse({"success": False, "error": "Permission denied"}, status=403)
