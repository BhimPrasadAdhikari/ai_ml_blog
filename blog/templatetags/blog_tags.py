from django import template

register = template.Library()
@register.filter
def split(value, delimiter=','):

    if value:
        return [item.strip() for item in value.split(delimiter) if item.strip()]
    return []


@register.filter
def trim(value):

    if value:
        return value.strip()
    return value