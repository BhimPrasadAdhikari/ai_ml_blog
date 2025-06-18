import os
from django.core.exceptions import ValidationError
from .constants import MAX_IMAGE_SIZE, VALID_IMAGE_EXTENSIONS, MAX_IMAGE_DIMENSION


def validate_image_size(image):
    if image.size > MAX_IMAGE_SIZE:
        raise ValidationError(f"Image size must be less than {MAX_IMAGE_SIZE} bytes")
    
def validate_image_dimensions(image):
    if image.width > MAX_IMAGE_DIMENSION or image.height > MAX_IMAGE_DIMENSION:
        raise ValidationError(f"Image dimensions must be less than {MAX_IMAGE_DIMENSION} pixels")
    
def validate_image_extension(image):
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in VALID_IMAGE_EXTENSIONS:
        raise ValidationError(f"Invalid image extension. Allowed extensions are: {', '.join(VALID_IMAGE_EXTENSIONS)}")

    
