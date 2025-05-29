from django.db import models

from django.db.models import CharField, ImageField, DateTimeField,BooleanField, TextField

class BlogPost(models.Model):
    """
    Model to store blog posts for the AI/ML blog.
    """
    title = CharField(max_length=50)
    slug = CharField(max_length=255, unique=True, blank=True)
    content = TextField()
    image = ImageField(upload_to='blog_images/')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    is_published = BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class meta: 
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-created_at']
        
        
        
        
    
