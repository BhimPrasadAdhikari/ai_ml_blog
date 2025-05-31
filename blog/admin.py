from django.contrib import admin
from .models import Post, CustomUser, Category
from django.contrib.auth.admin import UserAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ('name','slug')
    list_filter = ('name',)
    search_fields = ('name','slug')
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    model=Post
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
    
    
    
    