# myapp/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='remove_chars')
def remove_chars(value):
    if value:
        # Remove quotes, commas, and square brackets using str.replace
        cleaned_value = value.replace('"', '').replace(',', '').replace('[', '').replace(']', '').replace("'", '')
        return cleaned_value
    else:
        return value
