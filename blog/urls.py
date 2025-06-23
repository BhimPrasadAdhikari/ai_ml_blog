from django.urls import path, include
from .views import (
    PostDetailView, PostListView, PostCreateView, PostUpdateView, PostDeleteView,
    CategoryPostListView, SearchView, AddCommentView, AddReplyView,
    EditCommentView, DeleteCommentView, ModerateCommentView, check_new_comments,
    PostVoteView, PostVoteCountView, PostWatchTimeView, PostShareView,
    ProfileDetailView, ProfileEditView, AuthorDashboardView, EmailSubscriptionView, EmailUnsubscribeView,
    CategoriesListView, NewsletterListView, NewsletterCreateView, NewsletterPreviewView, NewsletterUpdateView, NewsletterDeleteView
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
    path('categories/', CategoriesListView.as_view(), name='categories_list'),
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
    path('subscribe/', EmailSubscriptionView.as_view(), name='email_subscribe'),
    path('unsubscribe/', EmailUnsubscribeView.as_view(), name='email_unsubscribe'),
    path('newsletters/', NewsletterListView.as_view(), name='newsletter_list'),
    path('newsletters/create/', NewsletterCreateView.as_view(), name='newsletter_create'),
    path('newsletters/<int:newsletter_id>/preview/', NewsletterPreviewView.as_view(), name='newsletter_preview'),
    path('newsletters/<int:newsletter_id>/edit/', NewsletterUpdateView.as_view(), name='newsletter_edit'),
    path('newsletters/<int:newsletter_id>/delete/', NewsletterDeleteView.as_view(), name='newsletter_delete'),

]
