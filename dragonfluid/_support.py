"""
support functions - take from a personal library and included in dragonfluid
"""
import inspect

def _first_not_none(*args):
    for arg in args:
        if arg is not None:
            return arg
    return None


def _reduce_repeats(to_alter, to_reduce):
    parts = to_alter.split(to_reduce)
    parts = filter(None, parts)
    return to_reduce.join(parts)


def _reduce_spaces(to_alter):
    return _reduce_repeats(to_alter, " ")


def _rstrip_from(to_alter, strip_from):
    position = to_alter.find(strip_from)
    if position == -1:
        return to_alter
    else:
        return to_alter[:position]


def _safe_kwargs(function, *args, **kwargs):
    """
    Calls the given function, without passing items from kwargs that do not
    match expected named parameters.
    """
    validargs = inspect.getargspec(function).args
    removals = [key for key in kwargs.keys() if key not in validargs]
    for removal in removals:
        del kwargs[removal]
    return function(*args, **kwargs)

def _single_spaces_and_trimmed(some_string):
    words = some_string.split()
    return " ".join(words)
