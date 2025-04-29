# -*- dataeval: init -*-

"""
Plots the signals of the given device
"""

from collections import OrderedDict

import datavis
import interface

init_params = {
  "default": dict(dev_name="device_name"),
}

class View(interface.iView):
  def init(self, dev_name):
    self.dev_name = dev_name
    return
  
  def check(self):
    signals = self.source.querySignalNames((self.dev_name,), (), (), (), False, False)
    sgs = [OrderedDict( (sig, (dev, sig)) for (dev, sig) in signals )]
    group = self.source.selectSignalGroup(sgs)
    return group
  
  def view(self, group):
    title = "Signals of '%s' device" % self.dev_name
    pn = datavis.cPlotNavigator(title=title)
    for alias in group:
      ax = pn.addAxis()
      time, value, unit = group.get_signal_with_unit(alias)
      pn.addSignal2Axis(ax, alias, time, value, unit=unit)
    self.sync.addClient(pn)
    return
