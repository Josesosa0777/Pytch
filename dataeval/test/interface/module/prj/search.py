# -*- dataeval: method -*-
from interface.Interfaces import iSearch
from interface.Parameter import iParameter

__version__ = '0.4.3' #test get_version

class Search(iSearch):
  def check(self):
    return 56

  def fill(self, egg):
    return egg + 4, egg - 4

  def search(self, param, spam, spamspam):
    self.egg = spam - spamspam + param.foo
    return

  def error(self, param):
    self.egg = param.foo + 9
  pass

class Parameter(iParameter):
  def __init__(self, foo):
    self.foo = foo
    self.genKeys()
    return
  

