from collections import namedtuple

def enum(*args, **kwargs):
  """
  Represents enum in python, returns named tuple instance with fields in increasing enumeration order.
  Integers are assigned to positional arguments in range after the largest enumeration value or from zero if no
  keyword argument is provided.
  
  Examples
  --------
  >>> FRUIT = enum(APPLE=0, PEAR=1, PEACH=2)
  >>> FRUIT.PEACH
  2
  
  >>> FRUIT = enum("APPLE", "PEAR", "PEACH")
  >>> FRUIT.PEACH
  2
  
  >>> FRUIT = enum("APPLE", PEAR=15, PEACH=8)
  >>> FRUIT
  Enum(PEACH=8, PEAR=15, APPLE=16)
  """
  i = max(kwargs.itervalues())+1 if kwargs else 0
  for arg in args:
    assert arg not in kwargs, "multiple occurrences: %s" % arg
    kwargs[arg] = i
    i += 1
  fields_in_enum_order = sorted(kwargs.keys(), key=lambda field: kwargs[field])
  return namedtuple('Enum', fields_in_enum_order)(**kwargs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
