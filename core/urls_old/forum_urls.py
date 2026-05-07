from django.urls import path
from core.views.forum_views import (
    ForumHomeView, CreatePostView, ForumCategoryView,
    ForumPostDetailView, UpvotePostView, UpvoteReplyView, MarkAnswerView
)

app_name = 'forum'

urlpatterns = [
    # Static paths BEFORE dynamic
    path('',
         ForumHomeView.as_view(),
         name='home'),
    path('new/',
         CreatePostView.as_view(),
         name='create'),
    path('category/<slug:slug>/',
         ForumCategoryView.as_view(),
         name='category'),
    path('post/<int:pk>/<slug:slug>/',
         ForumPostDetailView.as_view(),
         name='post_detail'),
    path('post/<int:pk>/upvote/',
         UpvotePostView.as_view(),
         name='upvote_post'),
    path('reply/<int:pk>/upvote/',
         UpvoteReplyView.as_view(),
         name='upvote_reply'),
    path('reply/<int:pk>/mark-answer/',
         MarkAnswerView.as_view(),
         name='mark_answer'),
]
