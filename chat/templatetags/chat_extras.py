# chat/templatetags/chat_extras.py

from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dict_obj, key):
    try:
        if isinstance(dict_obj, dict):
            return dict_obj.get(key, 0)
        return 0
    except Exception:
        return 0

