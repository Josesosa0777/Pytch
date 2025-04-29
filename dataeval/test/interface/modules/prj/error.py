# -*- dataeval: init -*-

from interface.Interfaces import Interface
from measparser.signalgroup import SignalGroupError


class Error(Interface):
  def init(self, foo):
    return

  def check(self):
    raise SignalGroupError('foo')

  def error(self):
    self.spam = 42


