import types

def is_pub_method(f):
  return isinstance(f, types.FunctionType) and not f.__name__.startswith('_')

class cached_attribute(object):
  """ Non-data descriptor that takes a function and caches its result on the
  instance under the name of the function. If `name` is given, the funcion
  is called with it and the result is cached under `name` attribute. When
  prefix is also given, caching is done under prefixed `name` attribute. """
  def __init__(self, func, name=None, prefix=None):
    self.func = func
    self.name = name
    self.prefix = prefix
    return

  def __get__(self, instance, cls):
    if self.name is None:
      res = self.func(instance)
      name = self.func.__name__
    else:
      res = self.func(instance, self.name)
      name = self.name if self.prefix is None else self.prefix + self.name
    setattr(instance, name, res)
    return res
