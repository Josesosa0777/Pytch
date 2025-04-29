# -*- dataeval: init -*-

from interface.Interfaces import Interface

class Bear(Interface):
  optdep = 'fill-bar@prj', 'error-spam@prj'
