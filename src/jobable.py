class Jobable():
    """ Base class for Job classes. """
    editor = []


def jobFactory(pattern):
    """ Dynamically load and instantiate Job params. """
    from importlib import import_module

    lm = import_module('jobs.%s' % pattern)
    return lm.Jober()
