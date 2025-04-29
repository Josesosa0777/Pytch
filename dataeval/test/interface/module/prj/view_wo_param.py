# -*- dataeval: method -*-

from interface.Interfaces import Interface

class View(Interface):
  def check(self):
    return 1, 2
  
  def fill(self, egg, eggegg):
    return egg + 5

  def run(self, egg):
    self.spam = egg
    return

  def error(self):
    self.spam = 33
    return
  pass

