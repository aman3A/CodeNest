from django import template
from django.utils.safestring import mark_safe

from apps.posts.models import clean_rich_text

register = template.Library()


@register.filter(is_safe=True)
def safe_rich_text(value):
    return mark_safe(clean_rich_text(value))
