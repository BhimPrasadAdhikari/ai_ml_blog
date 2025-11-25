from django.db import models
from django.utils.text import slugify
from PIL import Image
from .constants import MAX_IMAGE_SIZE, MAX_IMAGE_DIMENSION

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SlugMixin(models.Model):
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class ImageProcessingMixin:
    class Meta:
        abstract = True
    
    def process_image(self, image_field, max_size=MAX_IMAGE_SIZE, max_dimension=MAX_IMAGE_DIMENSION):
        if image_field:
            img = Image.open(image_field)

            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize the image if it exceeds max dimensions
            if img.width > max_dimension or img.height > max_dimension:
                output_size = (max_dimension, max_dimension)
                img.thumbnail(output_size, Image.LANCZOS)

            # Save the image with optimized settings
            img.save(image_field.path, 'JPEG', quality=85, optimize=True)

