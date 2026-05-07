from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Q, UniqueConstraint
from .institution import College
from .taxonomy import Course, Stream

class ForumCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color_code = models.CharField(max_length=7, default='#6366F1')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Forum Category"
        verbose_name_plural = "Forum Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class ForumPost(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forum_posts'
    )
    category = models.ForeignKey(
        ForumCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts'
    )
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    tags = models.JSONField(default=list)
    related_college = models.ForeignKey(
        College,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    related_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    related_stream = models.ForeignKey(
        Stream,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    upvotes = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)
    is_answered = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['is_answered', 'is_active']),
        ]

    def __str__(self):
        return self.title[:60] + "..." if len(self.title) > 60 else self.title

    @property
    def short_body(self):
        if len(self.body) > 200:
            return self.body[:200] + "..."
        return self.body

class ForumReply(models.Model):
    post = models.ForeignKey(
        ForumPost,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forum_replies'
    )
    body = models.TextField()
    parent_reply = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_replies'
    )
    upvotes = models.PositiveIntegerField(default=0)
    is_verified_answer = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Forum Reply"
        verbose_name_plural = "Forum Replies"
        ordering = ['-is_verified_answer', 'created_at']
        indexes = [
            models.Index(fields=['post', 'is_active']),
        ]

    def __str__(self):
        return f"Reply by {self.author.email} on {self.post.title[:30]}"

class ForumUpvote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        ForumPost,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    reply = models.ForeignKey(
        ForumReply,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'post'],
                condition=Q(post__isnull=False),
                name='unique_user_post_upvote'
            ),
            UniqueConstraint(
                fields=['user', 'reply'],
                condition=Q(reply__isnull=False),
                name='unique_user_reply_upvote'
            ),
        ]
