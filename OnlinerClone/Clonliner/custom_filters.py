from django import template
from datetime import datetime

register = template.Library()


@register.filter
def set_variable(value):
    return value
