import re
from django import template

register = template.Library()


@register.simple_tag
def is_active_nav(request, match):
    if re.search(match, request.path):
        return "is-active"
    return ""


@register.simple_tag
def is_active_item(left, right):
    return "is-active" if left == right else ""
