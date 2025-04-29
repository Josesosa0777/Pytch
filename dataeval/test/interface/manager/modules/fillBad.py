# -*- dataeval: init -*-
from interface.Interfaces import iFill
from measparser.signalgroup import SignalGroupError

class Fill(iFill):
  def check(self):
    raise SignalGroupError

