from django.shortcuts import render, redirect, get_object_or_404
import markdown
from django.utils.safestring import mark_safe
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import Http404, JsonResponse
from .models import Post, Category, Comment, PostInteraction, PostWatchTime, PostShare, UserProfile, EmailSubscription, Newsletter, PostBookmark, PostRating, Annotation, PostQnA
from django.db.models import Q, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .analytics import SearchAnalytics
from .forms import CommentForm, UserProfileForm, EmailSubscriptionForm, NewsletterForm, PostBookmarkForm, PostRatingForm
from django.db import models
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator

# Create your views here.

class LandingPageView(TemplateView):
    template_name = 'blog/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = Post.objects.filter(status='published').order_by('-published_at')[:6]
        context['categories'] = Category.objects.annotate(num_posts=models.Count('posts')).order_by('-num_posts')[:10]
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Post.objects.select_related('author')\
            .prefetch_related(
                'categories',
                models.Prefetch(
                    'comments',
                    queryset=Comment.objects.select_related('author', 'moderated_by')
                        .filter(parent__isnull=True)
                        .prefetch_related(
                            models.Prefetch(
                                'replies',
                                queryset=Comment.objects.select_related('author'),
                                to_attr='prefetched_replies'  # <-- use a unique name
                            )
                        )
                )
            )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        context['post_content_html'] = mark_safe(markdown.markdown(post.content, extensions=['extra','codehilite', 'toc','tables']))
        total_watch_time = PostWatchTime.objects.filter(
            post=post, 
            user=self.request.user
            ).aggregate(total=models.Sum('watch_time'))['total'] or 0
        context['total_watch_time_minutes'] = total_watch_time // 60
        
        # Get user's vote for this post
        if self.request.user.is_authenticated:
            bookmark = PostBookmark.objects.filter(post=post, user=self.request.user).first()
            context['user_bookmarked'] = post.bookmarks.filter(user=self.request.user).exists()
            context['bookmark_notes'] = bookmark.notes if bookmark else ''

            try:
                interaction = PostInteraction.objects.get(
                    post=post,
                    user=self.request.user
                )
                context['user_vote'] = interaction.vote_type
            except PostInteraction.DoesNotExist:
                context['user_vote'] = None
        else:
            context['user_vote'] = None
            context['bookmark_notes'] = ''
            context['user_bookmarked'] = False

        if self.request.user.is_authenticated:
            try:
                rating_obj = PostRating.objects.get(post=post, user=self.request.user)
                context['user_rating'] = rating_obj.rating
            except PostRating.DoesNotExist:
                context['user_rating'] = 0

        else:
            context['user_rating'] = 0

        

        
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
            
        # Add pagination for comments
        paginator = Paginator(comments, 10)
        page = self.request.GET.get('page')
        context['comments'] = paginator.get_page(page)
        
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
            context['user_interaction'] = PostInteraction.objects.filter(
                post=self.object,
                user=self.request.user
            ).first()
        
        # Get share counts for each platform
        share_counts = {}
        for platform, _ in PostShare.SHARE_PLATFORMS:
            share_counts[platform] = PostShare.objects.filter(
                post=post,
                platform=platform
            ).count()
        
        context['share_counts'] = share_counts

        # Related posts logic
        # Get categories and tags for the current post
        categories = post.categories.all()
        tags = post.get_tags_list()
        related_posts = Post.objects.filter(status='published').exclude(id=post.id)
        # Filter by categories
        if categories.exists():
            related_posts = related_posts.filter(categories__in=categories)
        # Filter by tags
        if tags:
            tag_query = Q()
            for tag in tags:
                tag_query |= Q(tags__icontains=tag)
            related_posts = related_posts.filter(tag_query)
        # Remove duplicates, order by published date, and limit
        related_posts = related_posts.distinct().order_by('-published_at')[:4]
        context['related_posts'] = related_posts

        return context
    
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Post.objects.select_related('author')\
            .prefetch_related('categories')\
            .filter(status='published')\
            .order_by('-published_at')
            
        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(summary__icontains=query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Get IDs of posts bookmarked by the user
            context['bookmarked_post_ids'] = set(
                self.request.user.bookmarked_posts.values_list('post_id', flat=True)
            )
        else:
            context['bookmarked_post_ids'] = set()
        # ... any other context ...
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
        try:
            post = get_object_or_404(Post, slug=self.kwargs['slug'])
            form.instance.author = self.request.user
            form.instance.post = post
            
            # Automatically approve comments from superusers and post authors
            if self.request.user.is_superuser or self.request.user == post.author:
                form.instance.status = 'approved'
                form.instance.moderated_at = timezone.now()
                form.instance.moderated_by = self.request.user
            
            response = super().form_valid(form)
            messages.success(self.request, 'Comment added successfully!')
            return response
        except Exception as e:
            messages.error(self.request, f'Error adding comment: {str(e)}')
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'slug': self.kwargs['slug']})

class AddReplyView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/post_detail.html'

    def form_valid(self, form):
        try:
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
            
            response = super().form_valid(form)
            messages.success(self.request, 'Reply added successfully')
            return response
        except Exception as e:
            messages.error(self.request, f'Error adding reply: {str(e)}')
            return self.form_invalid(form)
    
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

class PostVoteView(LoginRequiredMixin, View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        vote_type = request.POST.get('vote_type')
        
        if vote_type not in ['up', 'down']:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid vote type'
            }, status=400)

        # Get or create interaction
        interaction, created = PostInteraction.objects.get_or_create(
            post=post,
            user=request.user
        )

        # If the same vote type is clicked again, remove the vote
        if interaction.vote_type == vote_type:
            interaction.vote_type = None
            interaction.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Vote removed',
                'vote_count': post.get_vote_count()
            })

        # Update vote
        interaction.vote_type = vote_type
        interaction.save()

        return JsonResponse({
            'status': 'success',
            'message': f'Vote {vote_type} recorded',
            'vote_count': post.get_vote_count()
        })

class PostVoteCountView(View):
    """
    View to get post vote count
    """
    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        upvotes = post.interactions.filter(vote_type='up').count()
        downvotes = post.interactions.filter(vote_type='down').count()
        
        return JsonResponse({
            'upvotes': upvotes,
            'downvotes': downvotes,
            'total': upvotes - downvotes
        })

@method_decorator(ensure_csrf_cookie, name='dispatch')
class PostWatchTimeView(LoginRequiredMixin, View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        
        # Debug logging
        print(f"Watch time update request from user: {request.user.username}")
        print(f"Is superuser: {request.user.is_superuser}")
        print(f"Is author: {request.user == post.author}")
        
        # Don't track watch time for superusers or post authors
        if request.user.is_superuser or request.user == post.author:
            return JsonResponse({
                'status': 'success',
                'message': 'Watch time not tracked for superusers or post authors'
            })
            
        # Get or create watch time record
        watch_time, created = PostWatchTime.objects.get_or_create(
            post=post,
            user=request.user,
            defaults={'watch_time': 0}
        )
        
        # Update watch time (assuming 30-second intervals)
        watch_time.watch_time += 30
        watch_time.save()
        
        print(f"Updated watch time for user {request.user.username}: {watch_time.watch_time} seconds")
        
        return JsonResponse({
            'status': 'success',
            'watch_time': watch_time.watch_time
        })

class PostShareView(View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        platform = request.POST.get('platform')
        
        if platform not in dict(PostShare.SHARE_PLATFORMS).keys():
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid platform'
            }, status=400)
            
        # Create share record
        PostShare.objects.create(
            post=post,
            platform=platform,
            shared_by=request.user if request.user.is_authenticated else None
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Share recorded for {platform}'
        })

class ProfileDetailView(DetailView):
    model = UserProfile
    template_name = 'blog/profile_detail.html'
    context_object_name = 'profile'
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        user = get_object_or_404(get_user_model(), username=username)
        try:
            return user.profile
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            return UserProfile.objects.create(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object.user
        context['user_posts'] = user.posts.filter(status='published')[:5]
        context['user_comments'] = user.comments.filter(status='approved')[:5]
        context['stats'] = {
            'total_posts': self.object.total_posts,
            'total_comments': self.object.total_comments,
            'total_upvotes': self.object.total_upvotes_received,
            'total_watch_time': PostWatchTime.objects.filter(
                user=user
            ).aggregate(total=models.Sum('watch_time'))['total'] or 0,
            'total_shares': self.object.total_shares,
        }
        return context

class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'blog/profile_edit.html'

    def test_func(self):
        """Ensure users can only edit their own profile"""
        username = self.kwargs.get('username')
        return self.request.user.username == username

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        user = get_object_or_404(get_user_model(), username=username)
        return user.profile

    def get_success_url(self):
        return reverse('profile_detail', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class AuthorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/author_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get recent posts
        context['recent_posts'] = user.posts.filter(status='published')[:5]
        
        # Get post statistics
        context['post_stats'] = {
            'total_posts': user.profile.total_posts,
            'total_views': PostWatchTime.objects.filter(
                post__author=user
            ).count(),
            'total_upvotes': user.profile.total_upvotes_received,
            'total_shares': user.profile.total_shares,
        }
        
        # Get recent comments
        context['recent_comments'] = user.comments.filter(status='approved')[:5]
        
        # Get watch time statistics
        context['watch_time_stats'] = PostWatchTime.objects.filter(
            post__author=user
        ).aggregate(
            total_minutes=models.Sum('watch_time') / 60
        )
        
        return context

class EmailSubscriptionView(View):
    def post(self, request):
        form = EmailSubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            existing_subscription = EmailSubscription.objects.filter(email=email).first()

            if existing_subscription:
                if existing_subscription.is_active:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'You are already subscribed to our newsletter.'
                    }, status=400)
                else:
                    existing_subscription.is_active = True
                    existing_subscription.unsubscribed_at = None
                    existing_subscription.save()
                    messages.success(request, 'You have been re-subscribed to our newsletter.')
                    return JsonResponse({
                        'status': 'success',
                        'message': 'You have been re-subscribed to our newsletter.'
                    })
            else:
                subscription = form.save()
                messages.success(request, 'You have been subscribed to our newsletter!')
                return JsonResponse({
                'status': 'success',
                'message': 'Subscription successful'

            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid email address'
            }, status=400)

    def get(self, request):

        email = request.GET.get('email')
        if email:
            try:
                subscription = EmailSubscription.objects.get(email=email)
                return JsonResponse({
                    'is_subscribed': subscription is not None
                })
            except EmailSubscription.DoesNotExist:
                return JsonResponse({
                    'is_subscribed': False
                })
        return JsonResponse({
            'is_subscribed': False
        })


class EmailUnsubscribeView(View):
    def post(self, request):
        email = request.POST.get('email')
        if email:
            try:
                subscription = EmailSubscription.objects.get(email=email)
                subscription.unsubscribe()
                messages.success(request, 'You have been unsubscribed from our newsletter.')
                return JsonResponse({
                    'status': 'success',
                    'message': 'Unsubscribed successfully'
                })
            except EmailSubscription.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email not found in our subscription list.'
                }, status=404)
        return JsonResponse({
            'status': 'error',
            'message': 'Email is required'
        }, status=400)
      
class CategoriesListView(TemplateView):
    template_name = 'blog/categories_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.annotate(
            post_count=models.Count('posts', filter=models.Q(posts__status='published')),
            total_watch_time=models.Sum('posts__watch_times__watch_time'),
            total_likes=models.Count(
                'posts__interactions',
                filter=models.Q(posts__interactions__vote_type='up')
            ),
            total_shares=models.Count('posts__shares'),
            total_comments=models.Count(
                'posts__comments',
                filter=models.Q(posts__comments__status='approved')
            )
        )
        context['categories'] = categories
        return context

class NewsletterCreateView(LoginRequiredMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'blog/newsletter_form.html'
    success_url = reverse_lazy('newsletter_list')

    def form_valid(self, form):
        messages.success(self.request, 'Newsletter created successfully!')
        return super().form_valid(form)

class NewsletterListView(LoginRequiredMixin, ListView):
    model = Newsletter
    template_name = 'blog/newsletter_list.html'
    context_object_name = 'newsletters'
    paginate_by = 10
    
    def get_queryset(self):
        return Newsletter.objects.filter(is_sent=True).order_by('-sent_at')


class NewsletterPreviewView(LoginRequiredMixin, DetailView):
    model = Newsletter
    template_name = 'blog/newsletter_preview.html'
    context_object_name = 'newsletter'
    pk_url_kwarg = 'newsletter_id'
    

class NewsletterUpdateView(LoginRequiredMixin, UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'blog/newsletter_form.html'
    pk_url_kwarg = 'newsletter_id'
    success_url = reverse_lazy('newsletter_list')

    def form_valid(self, form):
        messages.success(self.request, 'Newsletter updated successfully!')
        return super().form_valid(form)


class NewsletterDeleteView(LoginRequiredMixin, DeleteView):
    model = Newsletter
    success_url = reverse_lazy('newsletter_list')
    pk_url_kwarg = 'newsletter_id'

    def delete(self, request, *args, **kwargs):
        newsletter = self.get_object()
        if newsletter.is_sent:
            return JsonResponse({
                'status': 'error',
                'message': 'Cannot delete a sent newsletter.'
            }, status=400)
        
        newsletter.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Newsletter deleted successfully'
        })

class PostBookmarkView(LoginRequiredMixin, View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        action = request.POST.get('action')
        notes = request.POST.get('notes', '').strip()

        if action == 'add':
            bookmark, created = PostBookmark.objects.get_or_create(
                post=post,
                user=request.user
            )
            message = 'Post bookmarked successfully'
        elif action == 'remove':
            try:
                bookmark = PostBookmark.objects.get(post=post, user=request.user)
                bookmark.delete()
                message = 'Bookmark removed successfully'
            except PostBookmark.DoesNotExist:
                message = 'Bookmark not found'
        elif action == 'update_notes':
            try:
                bookmark = PostBookmark.objects.get(post=post, user=request.user)
                bookmark.notes = notes
                bookmark.save()
                message = 'Notes updated successfully'
            except PostBookmark.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Bookmark not found'
                }, status=404)

        
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid action'
            }, status=400)
        
        return JsonResponse({
            'status': 'success',
            'message': message
        })

class UserBookmarksView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/user_bookmarks.html'
    context_object_name = 'bookmarked_posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            bookmarks__user=self.request.user,
            status = 'published'
        ).order_by('-bookmarks__created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bookmarks = self.request.user.bookmarked_posts.filter(
            post__in=context['bookmarked_posts']

        ).select_related('post')

        context['bookmarks_map'] = {
            bookmark.post.id: bookmark for bookmark in bookmarks
        
        }
        return context

class PostRatingView(LoginRequiredMixin, View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        rating = request.POST.get('rating')

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
                
        except (ValueError, TypeError):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid rating value'
            }, status=400)

        try:
            rating_obj, created = PostRating.objects.get_or_create(
                post=post,
                user=request.user,
                defaults={'rating': rating}
            )

            if not created:
                rating_obj.rating = rating
                rating_obj.save()
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to save rating'
            }, status=500)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Rating saved successfully',
            'average_rating': post.get_average_rating(),
            'rating_count': post.get_rating_count(),
        })


class AnnotationListCreateView(LoginRequiredMixin, View):

    def get(self, request, slug):
        post = Post.objects.filter(slug=slug, status='published').first()

        annotations = Annotation.objects.filter(post=post).filter(
            Q(user=request.user) | Q(is_public=True)
        ).order_by('-created_at')
        data = [
            {
                "id": ann.id,
                "user": ann.user.username if ann.user else None,
                "selected_text": ann.selected_text,
                "content": ann.content,
                "is_public": ann.is_public,
                "status": ann.status,
                "created_at": ann.created_at.isoformat(),
                
            }
            for ann in annotations
        ]

        return JsonResponse({"annotations": data})

    def post(self, request, slug):
        post = Post.objects.filter(slug=slug, status='published').first()
        selected_text = request.POST.get('selected_text', '').strip()
        content = request.POST.get('content', '').strip()
        is_public = request.POST.get('is_public', 'false').lower() == 'true'

        if not selected_text or not content:
            return JsonResponse({
                'status': 'error',
                'message': 'Selected text and content are required'
            }, status=400)

        if Annotation.objects.filter(
            post=post,
            user=request.user,
            selected_text=selected_text
        ).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Annotation for this text already exists'
            }, status=400)

        annotation = Annotation.objects.create(
            post=post,
            user=request.user,
            selected_text=selected_text,
            content=content,
            is_public=is_public,
            status='open',
        )

        return JsonResponse({
            'id': annotation.id,
            'user': annotation.user.username if annotation.user else None,
            'selected_text': annotation.selected_text,
            'content': annotation.content,
            'is_public': annotation.is_public,
            'status': annotation.status,
            'created_at': annotation.created_at.isoformat(),
            'status': 'success',
        }, status=201)

class AnnotationResolveView(LoginRequiredMixin, View):

    def post(self, request, slug, pk):
        annotation = Annotation.objects.filter(id=pk).first()
        if not annotation:
            return JsonResponse({
                'status': 'error',
                'message': 'Annotation not found'
            }, status=404)
        if request.user != annotation.user and request.user!=annotation.post.author and not request.user.is_superuser:
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to resolve this annotation'
            }, status=403)

        annotation.status = 'resolved'
        annotation.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Annotation resolved successfully',
            'annotation_id': annotation.id
        })
        
    
class PostQnAListCreateView(LoginRequiredMixin, View):
    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug, status='published')
        qnas = PostQnA.objects.filter(post=post).order_by('-created_at')
        data = [
            {
                "id": qna.id,
                "user": qna.user.username if qna.user else None,
                "question": qna.question,
                "answer": qna.ansewer,
                "is_answered": qna.is_answered,
                "created_at": qna.created_at.isoformat(),
                "answered_at": qna.answered_at.isoformat() if qna.answered_at else None,
            }
            for qna in qnas
        ]
        return JsonResponse({"qnas": data}, status=200)

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug, status='published')
        question = request.POST.get('question', '').strip()
        if not question:
            return JsonResponse({
                'status': 'error',
                'message': 'Question is required'
            }, status=400)
        qna = PostQnA.objects.create(
            post = post,
            user = request.user, 
            question = question
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Question submitted successfully',
            'user': qna.user.username if qna.user else None,
            'question': qna.question,
            'created_at': qna.created_at.isoformat(),
            'id': qna.id, 
        }, status=201)

class PostQnAAnswerView(LoginRequiredMixin, View):
    def post(self, request, slug, pk):
        post = get_object_or_404(Post, slug=slug, status='published')
        qna = get_object_or_404(PostQnA, id=pk, post=post)
        if request.user != qna.post.author and not request.user.is_superuser:
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to answer this question'
            }, status=403)

        answer = request.POST.get('answer', '').strip()
        if not answer:
            return JsonResponse({
                'status': 'error',
                'message': 'Answer is required'
            }, status=400)

        qna.answer = answer
        qna.is_answered = True
        qna.answered_at = timezone.now()
        qna.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Answer submitted successfully',
            'id': qna.id,
            'answer': qna.answer,
            'answered_at': qna.answered_at.isoformat(),
        }, status=200)
