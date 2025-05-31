from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.views import View
from django.urls import reverse_lazy
from .models import Post

# Create your views here.

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(status='published')
    
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    
    def get_queryset(self):
        return Post.objects.filter(status='published').order_by('-created_at')
    
class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'slug', 'content', 'image']
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post_list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
