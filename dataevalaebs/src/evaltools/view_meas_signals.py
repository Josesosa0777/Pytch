# -*- dataeval: init -*-

"""
Prints the list of signals in the measurement
"""

import interface


class View(interface.iView):
  def fill(self):
    signals = self.source.querySignalNames((), (), (), (), False, False)
    return signals
  
  def view(self, signals):
    for dev, sig in signals:
      print "%s::%s" % (dev, sig)
    return
