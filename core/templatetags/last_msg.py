# myapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='filter_by_user')
def filter_by_user(dictionary_list, user):
    return [d for d in dictionary_list if d.get('user') == user]