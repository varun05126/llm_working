from django import template
from django.utils.safestring import mark_safe
from recommender.services.markdown_render import render_markdown

register = template.Library()

@register.filter(name='render_md')
def render_md(value):
    if not value:
        return ""
    return mark_safe(render_markdown(str(value)))
