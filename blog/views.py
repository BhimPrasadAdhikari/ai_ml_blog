from django.shortcuts import render, redirect
import markdown
from django.utils.safestring import mark_safe
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import Http404
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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        context['post_content_html'] = mark_safe(markdown.markdown(post.content, extensions=['extra','codehilite', 'toc','tables']))
        return context 
    
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    
    def get_queryset(self):
        return Post.objects.filter(status='published').order_by('-created_at')
    
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'slug', 'summary', 'content', 'image', 'categories', 'tags', 'status']
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post_list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create New Post'
        context['form_subtitle'] = 'Share your AI/ML knowledge with the world'
        context['submit_text'] = 'Create Post'
        return context
    
class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'slug', 'summary', 'content', 'image', 'categories', 'tags', 'status']
    template_name = 'blog/post_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        """
        Ensure that only the author can update the post.
        """
        post = self.get_object()
        return self.request.user == post.author


    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        else:
            messages.error(self.request, 'You do not have permission to edit this post.')
            return redirect('post_detail', slug=self.kwargs['slug'])
    
    def form_valid(self, form):
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Post: {self.object.title}'
        context['form_subtitle'] = 'Edit your AI/ML post'
        context['submit_text'] = 'Update Post'
        context['is_edit'] = True
        return context
    
    
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        """
        Ensure that only the author can delete the post.
        """
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        else:
             messages.error(self.request, 'You do not have permission to delete this post.')
             return redirect('post_detail', slug=self.kwargs['slug'])

    def delete(self, request, *args, **kwargs):
        post_title = self.get_object().title
        messages.success(request, f'Post "{post_title}" deleted successfully!')
        return super().delete(request, *args, **kwargs)

