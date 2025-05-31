from django.urls import path, include
from .views import PostDetailView, PostView
urlpatterns = [
    path('posts', PostView.as_view(), name = 'posts'),
    path('post_deatil/<slug:slug>/',PostDetailView.as_view(),name='post_detail'),
]
