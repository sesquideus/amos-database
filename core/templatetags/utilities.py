import functools


def mdash(function):
    @functools.wraps(function)
    def wrapper(arg):
        if arg == None:
            return mark_safe("&mdash;")
        else:
            return function(arg)

    return wrapper


def empty_on_error(*exceptions):
    def protected(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except exceptions as e:
                print(f"Caught exception {e.__class__.__name__} ({e}) and returning '' for {function.__name__}")
                return None
        return wrapper

    return protected


def graceful():
    @functools.wraps(function)
    def wrapper(function):
        return register.filter(mdash(empty_on_error(function)))

    return wrapper
