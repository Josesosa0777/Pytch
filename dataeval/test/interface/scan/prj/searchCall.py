# -*- dataeval: call -*-

from interface.Interfaces import iSearch
from interface.Parameter import iParameter

class Parameter(iParameter):
  def __init__(self, foo):
    self.foo = foo
    self.genKeys()
    return

call_params = {
  'spam': dict(foo=9),
  'egg':  dict(foo=0),
}

class Search(iSearch):
  pass
