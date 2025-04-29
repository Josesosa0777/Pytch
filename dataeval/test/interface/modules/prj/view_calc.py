# -*- dataeval: method -*-

from interface.Interfaces import iView
from interface.Parameter import iParameter

class Parameter(iParameter):
  def __init__(self, egg):
    self.egg = egg
    return

class cView(iView):
  def check(self):
    return 6

  def fill(self, egg):
    return egg * 2, egg / 2

  def view(self, param, egg, eggegg):
    self.egg = param.egg - (egg + eggegg)
    return


