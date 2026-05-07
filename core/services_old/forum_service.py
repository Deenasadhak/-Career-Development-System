from django.utils.text import slugify
from django.db.models import F, Prefetch, Count
from django.core.paginator import Paginator
from core.models import ForumPost, ForumReply, ForumUpvote, ForumCategory
from core.models import Notification
from .notification_service import NotificationService

class ForumService:
    def create_post(
            self,
            author,
            title: str,
            body: str,
            category_id: int,
            tags: list = None,
            related_college_id: int = None,
            related_course_id: int = None,
            related_stream_id: int = None) -> ForumPost:
        
        if not (10 <= len(title) <= 300):
            raise ValueError("Title must be between 10 and 300 characters.")
        if len(body) < 20:
            raise ValueError("Body must be at least 20 characters.")

        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while ForumPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return ForumPost.objects.create(
            author=author,
            title=title,
            slug=slug,
            body=body,
            category_id=category_id,
            tags=tags or [],
            related_college_id=related_college_id,
            related_course_id=related_course_id,
            related_stream_id=related_stream_id
        )

    def create_reply(
            self,
            author,
            post_id: int,
            body: str,
            parent_reply_id: int = None) -> ForumReply:
        
        try:
            post = ForumPost.objects.get(pk=post_id)
        except ForumPost.DoesNotExist:
            raise ValueError("Post not found.")

        if post.is_closed:
            raise ValueError("This thread is closed for new replies.")
        
        if len(body) < 5:
            raise ValueError("Reply must be at least 5 characters.")

        parent_reply = None
        if parent_reply_id:
            try:
                parent_reply = ForumReply.objects.get(pk=parent_reply_id, post_id=post_id)
                if parent_reply.parent_reply_id is not None:
                    raise ValueError("Cannot nest replies deeper than one level.")
            except ForumReply.DoesNotExist:
                raise ValueError("Parent reply not found in this post.")

        reply = ForumReply.objects.create(
            post=post,
            author=author,
            body=body,
            parent_reply=parent_reply
        )

        ForumPost.objects.filter(pk=post_id).update(reply_count=F('reply_count') + 1)

        if author != post.author:
            svc = NotificationService()
            svc.create_notification(
                recipient=post.author,
                notification_type='RECOMMENDATION_READY',
                title="New reply on your post",
                message=f"{author.email} replied to '{post.title[:50]}'",
                link=f"/forum/post/{post_id}/{post.slug}/"
            )
        
        return reply

    def toggle_upvote_post(
            self,
            user,
            post_id: int) -> dict:
        upvote, created = ForumUpvote.objects.get_or_create(user=user, post_id=post_id)
        if created:
            ForumPost.objects.filter(pk=post_id).update(upvotes=F('upvotes') + 1)
        else:
            upvote.delete()
            ForumPost.objects.filter(pk=post_id).update(upvotes=F('upvotes') - 1)
        
        post = ForumPost.objects.get(pk=post_id)
        return {"upvoted": created, "total_upvotes": post.upvotes}

    def toggle_upvote_reply(
            self,
            user,
            reply_id: int) -> dict:
        upvote, created = ForumUpvote.objects.get_or_create(user=user, reply_id=reply_id)
        if created:
            ForumReply.objects.filter(pk=reply_id).update(upvotes=F('upvotes') + 1)
        else:
            upvote.delete()
            ForumReply.objects.filter(pk=reply_id).update(upvotes=F('upvotes') - 1)
        
        reply = ForumReply.objects.get(pk=reply_id)
        return {"upvoted": created, "total_upvotes": reply.upvotes}

    def mark_verified_answer(
            self,
            user,
            reply_id: int) -> bool:
        try:
            reply = ForumReply.objects.select_related('post').get(pk=reply_id)
        except ForumReply.DoesNotExist:
            return False

        post = reply.post
        if not (user == post.author or getattr(user, 'role', '') == 'SUPER_ADMIN'):
            raise PermissionError("Only post author or Super Admin can mark verified answers.")

        ForumReply.objects.filter(post=post, is_verified_answer=True).update(is_verified_answer=False)
        
        reply.is_verified_answer = True
        reply.save(update_fields=['is_verified_answer'])
        
        post.is_answered = True
        post.save(update_fields=['is_answered'])
        return True

    def increment_view_count(
            self,
            post_id: int) -> None:
        ForumPost.objects.filter(pk=post_id).update(view_count=F('view_count') + 1)

    def get_feed(
            self,
            user=None,
            category_id: int = None,
            tag: str = None,
            search: str = None,
            sort: str = 'latest',
            page: int = 1,
            per_page: int = 20) -> dict:
        
        qs = ForumPost.objects.filter(is_active=True).select_related(
            'author', 'category', 'related_college', 'related_course', 'related_stream'
        )

        if category_id:
            qs = qs.filter(category_id=category_id)
        
        if tag:
            qs = qs.filter(tags__contains=tag)
            
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(body__icontains=search))

        if sort == 'latest':
            qs = qs.order_by('-is_pinned', '-created_at')
        elif sort == 'popular':
            qs = qs.order_by('-upvotes', '-created_at')
        elif sort == 'unanswered':
            qs = qs.filter(is_answered=False).order_by('-created_at')
        elif sort == 'most_viewed':
            qs = qs.order_by('-view_count', '-created_at')

        unanswered_count = qs.filter(is_answered=False).count()

        paginator = Paginator(qs, per_page)
        p_obj = paginator.get_page(page)

        if user and user.is_authenticated:
            # Efficiently check upvotes
            post_ids = [p.id for p in p_obj]
            upvoted_ids = set(ForumUpvote.objects.filter(user=user, post_id__in=post_ids).values_list('post_id', flat=True))
            for p in p_obj:
                p.user_has_upvoted = p.id in upvoted_ids
        else:
            for p in p_obj:
                p.user_has_upvoted = False

        return {
            "posts": p_obj,
            "total_count": paginator.count,
            "page": p_obj.number,
            "total_pages": paginator.num_pages,
            "unanswered_count": unanswered_count
        }

    def get_post_detail(
            self,
            post_id: int,
            user=None) -> dict:
        
        try:
            post = ForumPost.objects.select_related(
                'author', 'category', 'related_college', 'related_course'
            ).prefetch_related(
                Prefetch('replies',
                    queryset=ForumReply.objects.filter(
                        is_active=True,
                        parent_reply__isnull=True,
                    ).select_related('author')
                    .prefetch_related(
                        Prefetch('child_replies',
                            queryset=ForumReply.objects.filter(is_active=True).select_related('author')
                        )
                    )
                )
            ).get(pk=post_id, is_active=True)
        except ForumPost.DoesNotExist:
            return None

        user_has_upvoted_post = False
        user_upvoted_replies = set()
        
        if user and user.is_authenticated:
            user_has_upvoted_post = ForumUpvote.objects.filter(user=user, post=post).exists()
            user_upvoted_replies = set(ForumUpvote.objects.filter(
                user=user, reply__post=post
            ).values_list('reply_id', flat=True))

        return {
            "post": post,
            "top_level_replies": list(post.replies.all()),
            "total_replies": post.reply_count,
            "user_has_upvoted_post": user_has_upvoted_post,
            "user_upvoted_replies": user_upvoted_replies
        }
