from django.contrib import admin
from .models import Post, CustomUser, Category
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
    list_filter = ('slug','status')
    search_fields =('title','slug','author')
    
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
    
    
    
    