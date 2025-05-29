from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    model=BlogPost
    list_display = ('title','slug','image','content','created_at','updated_at','is_published')
    list_filter = ('slug',)
    search_fields =('title','slug')
    
    
    