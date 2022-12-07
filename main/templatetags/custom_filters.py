from django import template

from typing import Iterable

register = template.Library()

@register.filter(name='zip')
def zip_filter(a: Iterable, b: Iterable):
    return zip(a, b)