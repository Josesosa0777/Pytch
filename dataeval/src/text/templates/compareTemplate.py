# -*- dataeval: method -*-

import interface

Parameter = interface.NullParam

SignalGroups = [{},]

class cCompare(interface.iCompare):
  SignalGroups = SignalGroups
  channels = 'main', 'compare'

