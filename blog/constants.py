from django.db import models

# Post status choices
class PostStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'

# Comment status choices
class CommentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'

# Vote types
class VoteType(models.TextChoices):
    UP = 'up', 'Upvote'
    DOWN = 'down', 'Downvote'

# Share platforms
class SharePlatform(models.TextChoices):
    TWITTER = 'twitter', 'Twitter'
    FACEBOOK = 'facebook', 'Facebook'
    LINKEDIN = 'linkedin', 'LinkedIn'
    WHATSAPP = 'whatsapp', 'WhatsApp'
    TELEGRAM = 'telegram', 'Telegram'

# Post interaction types
class PostInteractionType(models.TextChoices):
    UPVOTE = 'upvote', 'Upvote'
    DOWNVOTE = 'downvote', 'Downvote'
    WATCH = 'watch', 'Watch'
    SHARE = 'share', 'Share'
    COMMENT = 'comment', 'Comment'
    REPLY = 'reply', 'Reply'
    EDIT = 'edit', 'Edit'
    DELETE = 'delete', 'Delete'


# File sizes
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_PROFILE_PICTURE_SIZE = 5 * 1024 * 1024  # 5MB

# Image dimensions
MAX_IMAGE_DIMENSION = 4000
MAX_THUMBNAIL_DIMENSION = 1200

# File extensions
VALID_IMAGE_EXTENSIONS= ['.jpg', '.jpeg', '.png', '.gif', '.webp']
VALID_VIDEO_EXTENSIONS= ['.mp4', '.mov', '.avi', '.mkv', '.webm']
VALID_AUDIO_EXTENSIONS= ['.mp3', '.wav', '.ogg', '.m4a', '.aac']
VALID_DOCUMENT_EXTENSIONS= ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx']
VALID_ARCHIVE_EXTENSIONS= ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
VALID_CODE_EXTENSIONS= ['.py', '.js', '.html', '.css', '.php', '.java', '.cpp', '.c', '.h', '.hpp', '.hxx']
VALID_TEXT_EXTENSIONS= ['.txt', '.md', '.csv', '.tsv', '.log', '.ini', '.conf', '.cfg', '.json', '.xml', '.yaml', '.yml']

class NewsletterStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SCHEDULED = 'scheduled', 'Scheduled'
    SENT = 'sent', 'Sent'







