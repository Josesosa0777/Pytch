# -*- dataeval: init -*-

from interface.Interfaces import Interface

class Bunny(Interface):
  dep = 'error-spam@prj',
  def init(self, foo):
    return

