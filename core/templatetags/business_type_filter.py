# myapp/custom_filters.py
from django import template
import ast

register = template.Library()

@register.filter(name='remove_chars')
def remove_chars(value):
    if value:
        # Remove quotes, commas, and square brackets using str.replace
        list = ast.literal_eval(value)
        return list
    else:
        return value
    
@register.filter(name='remove_session', takes_context=True)
def remove_session(request, value):
    if value:
        del request.session[value]
    else:
        return value