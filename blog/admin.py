from django.contrib import admin
from .models import BlogPost, CustomUser
from django.contrib.auth.admin import UserAdmin
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    model=BlogPost
    list_display = ('title','slug','image','content','created_at','updated_at','is_published')
    list_filter = ('slug',)
    search_fields =('title','slug')
    
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    model= CustomUser
    list_display=['email', 'username', 'phone_number', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields':('phone_number',)}),
    )
    
    
    
    