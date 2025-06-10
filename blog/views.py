from django.shortcuts import render, redirect, get_object_or_404
import markdown
from django.utils.safestring import mark_safe
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import Http404, JsonResponse
from .models import Post, Category, Comment
from django.db.models import Q, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .analytics import SearchAnalytics
from .forms import CommentForm
from django.db import models

# Create your views here.

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_arg = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(status='published')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        context['post_content_html'] = mark_safe(markdown.markdown(post.content, extensions=['extra','codehilite', 'toc','tables']))
        
        # Get sort parameter
        sort = self.request.GET.get('sort', 'newest')
        
        # Base queryset for comments
        comments = post.comments.filter(parent=None)
        
        # Apply sorting
        if sort == 'oldest':
            comments = comments.order_by('created_at')
        elif sort == 'most_replies':
            comments = comments.annotate(
                reply_count=models.Count('replies')
            ).order_by('-reply_count', '-created_at')
        else:  # newest is default
            comments = comments.order_by('-created_at')
            
        # Filter comments based on user permissions
        if not self.request.user.is_authenticated:
            # Anonymous users can only see approved comments
            comments = comments.filter(status='approved')
        elif self.request.user.is_superuser or self.request.user == post.author:
            # Superusers and post authors can see all comments
            pass
        else:
            # Regular users can only see approved comments
            comments = comments.filter(status='approved')
            
        context['comments'] = comments
        context['comment_sort'] = sort
        return context
    
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    
    def get_queryset(self):
        return Post.objects.filter(status='published').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
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

class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    
    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        return Post.objects.filter(
            status='published',
            categories__slug=category_slug
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('slug')
        category = Category.objects.get(slug=category_slug)
        context['category'] = category
        context['hero_title'] = f'Posts in {category.name}'
        context['hero_subtitle'] = f'Explore our collection of {category.name} articles'
        return context

class SearchView(ListView):
    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = Post.objects.filter(status='published')
        query = self.request.GET.get('q', '').strip()
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__icontains=query)
            )

        # Apply category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(categories__slug=category)

        # Apply author filter
        author = self.request.GET.get('author')
        if author:
            queryset = queryset.filter(author_id=author)

        # Apply date filter
        date_filter = self.request.GET.get('date')
        if date_filter:
            now = timezone.now()
            if date_filter == 'day':
                queryset = queryset.filter(created_at__gte=now - timedelta(days=1))
            elif date_filter == 'week':
                queryset = queryset.filter(created_at__gte=now - timedelta(weeks=1))
            elif date_filter == 'month':
                queryset = queryset.filter(created_at__gte=now - timedelta(days=30))
            elif date_filter == 'year':
                queryset = queryset.filter(created_at__gte=now - timedelta(days=365))

        # Apply sorting
        sort = self.request.GET.get('sort', 'relevance')
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        else:  # 'relevance' is default
            if query:
                title_matches = queryset.filter(title__icontains=query)
                content_matches = queryset.filter(content__icontains=query)
                tag_matches = queryset.filter(tags__icontains=query)
                queryset = (title_matches | content_matches | tag_matches).distinct()
            queryset = queryset.order_by('-created_at')

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['categories'] = Category.objects.all()
        
        # Modified author query to get all authors who have published posts
        context['authors'] = get_user_model().objects.filter(
            posts__status='published'
        ).distinct().order_by('username')
        
        # Add selected filters to context
        context['selected_category'] = self.request.GET.get('category')
        context['selected_author'] = self.request.GET.get('author')
        context['selected_date'] = self.request.GET.get('date')
        context['selected_sort'] = self.request.GET.get('sort', 'relevance')
        context['request'] = self.request
        
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        # Log search for analytics
        query = request.GET.get('q', '').strip()
        if query:
            filters = {
                'category': request.GET.get('category'),
                'author': request.GET.get('author'),
                'date': request.GET.get('date'),
                'sort': request.GET.get('sort')
            }
            SearchAnalytics.log_search(
                request=request,
                query=query,
                results_count=self.get_queryset().count(),
                filters=filters
            )
        
        return response

class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/post_detail.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        form.instance.author = self.request.user
        form.instance.post = post
        
        # Automatically approve comments from superusers and post authors
        if self.request.user.is_superuser or self.request.user == post.author:
            form.instance.status = 'approved'
            form.instance.moderated_at = timezone.now()
            form.instance.moderated_by = self.request.user
        
        messages.success(self.request, 'Comment added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'slug': self.kwargs['slug']})

class AddReplyView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/post_detail.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        parent_comment = get_object_or_404(Comment, id=self.kwargs['comment_id'], post=post)
        form.instance.author = self.request.user
        form.instance.post = post
        form.instance.parent = parent_comment
        
        # Automatically approve replies from superusers and post authors
        if self.request.user.is_superuser or self.request.user == post.author:
            form.instance.status = 'approved'
            form.instance.moderated_at = timezone.now()
            form.instance.moderated_by = self.request.user
        
        messages.success(self.request, 'Reply added successfully')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'slug': self.kwargs['slug']})

class EditCommentView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/post_detail.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        else:
            messages.error(self.request, 'You do not have permission to edit this comment.')
            return redirect('post_detail', slug=self.kwargs['slug'])

    def form_valid(self, form):
        form.instance.is_edited = True
        messages.success(self.request, 'Comment updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'slug': self.kwargs['slug']})

class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/post_detail.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        else:
            messages.error(self.request, 'You do not have permission to delete this comment.')
            return redirect('post_detail', slug=self.kwargs['slug'])

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Comment deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'slug': self.kwargs['slug']})

class ModerateCommentView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        comment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        # Allow superusers and post authors to moderate
        return self.request.user.is_superuser or self.request.user == comment.post.author

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        else:
            messages.error(self.request, 'You do not have permission to moderate this comment.')
            return redirect('post_detail', slug=self.kwargs['slug'])
    
    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=kwargs['comment_id'])
        action = request.POST.get('action')
        
        if action == 'approve':
            comment.status = 'approved'
        elif action == 'reject':
            comment.status = 'rejected'
            
        comment.moderated_at = timezone.now()
        comment.moderated_by = request.user
        comment.save()
        
        messages.success(request, f'Comment {action}d successfully!')
        return redirect('post_detail', slug=comment.post.slug)

def check_new_comments(request):
    post_id = request.GET.get('post_id')
    last_id = request.GET.get('last_id', '0')
    
    try:
        last_id = int(last_id)
    except (ValueError, TypeError):
        last_id = 0
    
    has_new = Comment.objects.filter(
        post_id=post_id,
        id__gt=last_id,
        status='approved'
    ).exists()
    
    return JsonResponse({'has_new_comments': has_new})

        


