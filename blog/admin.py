from django.contrib import admin
from .models import Post, CustomUser, Category, Comment, PostInteraction, UserProfile, EmailSubscription, Newsletter
from django.contrib.auth.admin import UserAdmin
from .forms import PostAdminForm
from .analytics import SearchAnalytics

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ('name','slug')
    list_filter = ('name',)
    search_fields = ('name','slug')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('title','slug','summary','content','image','tags','status','created_at','updated_at','published_at')
    list_filter = ('status',)  # removed 'slug'
    search_fields =('title','slug','author__username')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    model= CustomUser
    list_display=['email', 'username', 'phone_number', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields':('phone_number',)}),
    )

@admin.register(SearchAnalytics)
class SearchAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('query', 'timestamp', 'results_count', 'user', 'ip_address')
    list_filter = ('timestamp',)
    search_fields = ('query', 'user__username')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'content', 'created_at', 'is_reply', 'is_edited')
    list_filter = ('is_edited',)  # removed 'created_at', 'parent'
    search_fields = ('author__username', 'post__title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    # removed date_hierarchy

    def is_reply(self, obj):
        return obj.is_reply
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'

@admin.register(PostInteraction)
class PostInteractionAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'vote_type', 'watch_time', 'created_at')
    list_filter = ('vote_type', 'created_at')
    search_fields = ('post__title', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'location')
    list_filter = ('created_at', 'updated_at')

@admin.register(EmailSubscription)
class EmailSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'first_name', 'last_name')
    actions = ('activate_subscriptions', 'deactivate_subscriptions')

    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
    activate_subscriptions.short_description = 'Activate selected subscriptions'

    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_subscriptions.short_description = 'Deactivate selected subscriptions'
    
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sent_at', 'is_sent', 'sent_count')
    list_filter = ('is_sent', 'created_at')
    search_fields = ('subject', 'content')
    readonly_fields = ('sent_at', 'sent_count')
