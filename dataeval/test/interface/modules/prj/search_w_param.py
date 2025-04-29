# -*- dataeval: method -*-

from interface.Interfaces import iSearch
from interface.Parameter import iParameter
from measparser.signalgroup import SignalGroupError

class Parameter(iParameter):
  def __init__(self, egg):
    self.egg = egg
    self.genKeys()
    return


class cSearch(iSearch):
  def check(self):
    raise SignalGroupError()

  def error(self, param):
    self.egg = param.egg


