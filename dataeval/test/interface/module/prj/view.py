# -*- dataeval: init -*-
from interface.Interfaces import Interface

__version__ = '0.4.2' #test get_version

class View(Interface):
  def init(self, spam):
    self.spam = spam
    return

  def check(self):
    return self.spam + 1, self.spam + 2
  
  def fill(self, egg, eggegg):
    return egg + 5

  def run(self, egg):
    self.spam = egg
    return

  def error(self):
    self.spam = 33
  pass


