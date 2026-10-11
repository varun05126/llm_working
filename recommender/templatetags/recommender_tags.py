from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter(name='render_md')
def render_md(value):
    from recommender.services.markdown_render import render_markdown
    from django.utils.safestring import mark_safe
    if not value:
        return ""
    return mark_safe(render_markdown(str(value)))

