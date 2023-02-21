from django import template

from typing import Iterable

register = template.Library()

@register.filter(name='zip')
def zip_filter(a: Iterable, b: Iterable):
    return zip(a, b)

# It is possible to optimize it, checking bunch of questions at once before rendering (in view)
@register.filter(name='is_saved_by_user')
def is_saved_by_user(question, user):
    return question.is_saved(user)