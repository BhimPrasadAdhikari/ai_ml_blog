from django import template
from django.utils.html import mark_safe
import re
from blog.models import EmailSubscription, Post
register = template.Library()

@register.filter
def highlight(text, query):
    if not query:
        return text
    
    # Escape special characters in the query
    query = re.escape(query)
    
    # Create the highlight pattern
    pattern = re.compile(f'({query})', re.IGNORECASE)
    
    # Replace matches with highlighted version
    highlighted = pattern.sub(r'<span class="highlight">\1</span>', text)
    
    return mark_safe(highlighted)

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return the URL parameters that are in the current request's GET data,
    except any parameters whose names are in the kwargs dict.
    """
    # Get the request from the context
    request = context['request']
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return updated.urlencode() 


@register.simple_tag
def get_subscriber_count():
    """
    Get the number of active subscribers
    """
    return EmailSubscription.objects.filter(is_active=True).count()

@register.simple_tag
def get_user_bookmarks(user, limit=5):
    """
    Get the user's bookmarked posts, limited to the specified number.
    """
    if user.is_authenticated:
        return Post.objects.filter(
            bookmarks__user=user,
            status='published'
            ).order_by('-bookmarks__created_at')[:limit]
    return []
    
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
