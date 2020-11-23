import functools
import django

from django.utils.safestring import mark_safe

register = django.template.Library()


def default_string(function, replacement="&mdash;"):
    @functools.wraps(function)
    def wrapper(arg):
        return mark_safe(replacement) if arg is None else function(arg)

    return wrapper


def empty_on_error(*exceptions):
    def protected(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except exceptions as e:
                print(f"Caught exception {e.__class__.__name__} ({e}), returning None for {function.__name__}")
                return None
        return wrapper

    return protected


def graceful(function, replacement="&mdash;"):
    return default_string(empty_on_error(TypeError, ValueError)(function), replacement)
