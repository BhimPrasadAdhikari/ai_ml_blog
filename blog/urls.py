from django.urls import path, include
from .views import PostDetailView, PostListView, PostCreateView, PostUpdateView, PostDeleteView,CategoryPostListView
urlpatterns = [
    path('', PostListView.as_view(), name = 'post_list'),
    path('post/<slug:slug>/',PostDetailView.as_view(),name='post_detail'),
    path('post/new', PostCreateView.as_view(), name='post_create'),

    path('post/<slug:slug>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('post/<slug:slug>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('category/<slug:slug>/', CategoryPostListView.as_view(), name='category_posts'),
    
]
