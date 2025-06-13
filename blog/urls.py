from django.urls import path, include
from .views import (
    PostDetailView, PostListView, PostCreateView, PostUpdateView, PostDeleteView,
    CategoryPostListView, SearchView, AddCommentView, AddReplyView,
    EditCommentView, DeleteCommentView, ModerateCommentView, check_new_comments,
    PostVoteView, PostVoteCountView, PostWatchTimeView, PostShareView,
    ProfileDetailView, ProfileEditView, AuthorDashboardView
)

urlpatterns = [
    path('', PostListView.as_view(), name = 'post_list'),
    path('post/<slug:slug>/',PostDetailView.as_view(),name='post_detail'),
    path('post/new', PostCreateView.as_view(), name='post_create'),

    path('post/<slug:slug>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('post/<slug:slug>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('post/<slug:slug>/comment/', AddCommentView.as_view(), name='add_comment'),
    path('post/<slug:slug>/comment/<int:comment_id>/reply/', AddReplyView.as_view(), name='add_reply'),
    path('post/<slug:slug>/comment/<int:comment_id>/edit/', EditCommentView.as_view(), name='edit_comment'),
    path('post/<slug:slug>/comment/<int:comment_id>/delete/', DeleteCommentView.as_view(), name='delete_comment'),
    path('post/<slug:slug>/comment/<int:comment_id>/moderate/', ModerateCommentView.as_view(), name='moderate_comment'),
    path('category/<slug:slug>/', CategoryPostListView.as_view(), name='category_posts'),
    path('search/', SearchView.as_view(), name='search_posts'),
    path('api/comments/check-new/', check_new_comments, name='check_new_comments'),

    path('post/<slug:slug>/vote/', PostVoteView.as_view(), name='post_vote'),
    path('post/<slug:slug>/votes/', PostVoteCountView.as_view(), name='post_vote_count'),
    path('post/<slug:slug>/watch-time/', PostWatchTimeView.as_view(), name='post_watch_time'),
    path('post/<slug:slug>/share/', PostShareView.as_view(), name='post_share'),

    path('profile/<str:username>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/<str:username>/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('dashboard/', AuthorDashboardView.as_view(), name='author_dashboard'),

]
