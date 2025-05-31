from django.urls import path, include
from .views import PostDetailView, PostListView, PostCreateView
urlpatterns = [
    path('', PostListView.as_view(), name = 'post_list'),
    path('post/<slug:slug>/',PostDetailView.as_view(),name='post_detail'),
    path('post/new', PostCreateView.as_view(), name='post_create'),
    
]
