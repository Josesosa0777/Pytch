# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

"""
Show raw MBL79 detection information plots
"""

import interface
import datavis

def_param = interface.NullParam

class View(interface.iView):
  N_TARGETS = 100
  N_PRIMARY_TARGETS = 5
  
  def check(self):
    sg = {}
    for sig in ("CoGRange", "Azimuth", "PowerDB", "StdAzimuth", "CoGDoppler"):
      sg.update({"%s_%d" % (sig, i) : ("MB79_TARGET_DETECTION_%dB" % i, "%s_%d" % (sig, i)) for i in xrange(1, self.N_TARGETS+1)})
    sgs = [sg]
    group = self.source.selectLazySignalGroup(sgs)
    return group
  
  def view(self, param, group):
    kwargs1 = {'lw': 0, 'marker': '.'}
    kwargs2 = {'lw': 0}
    
    client00 = datavis.cPlotNavigator(title="")
    for sig in ("CoGRange", "Azimuth"):
      axis00 = client00.addAxis()
      for i in xrange(1, self.N_TARGETS+1):
        c_sig = "%s_%d" % (sig, i)
        if c_sig not in group: continue
        time00, value00, unit00 = group.get_signal_with_unit(c_sig)
        kwargs = kwargs1 if i <= self.N_PRIMARY_TARGETS else kwargs2
        client00.addSignal2Axis(axis00, c_sig, time00, value00, unit=unit00, **kwargs)
    self.sync.addClient(client00)
    
    client00 = datavis.cPlotNavigator(title="")
    for sig in ("PowerDB", "StdAzimuth", "CoGDoppler"):
      axis00 = client00.addAxis()
      for i in xrange(1, self.N_TARGETS+1):
        c_sig = "%s_%d" % (sig, i)
        if c_sig not in group: continue
        time00, value00, unit00 = group.get_signal_with_unit(c_sig)
        kwargs = kwargs1 if i <= self.N_PRIMARY_TARGETS else kwargs2
        client00.addSignal2Axis(axis00, c_sig, time00, value00, unit=unit00, **kwargs)
    self.sync.addClient(client00)
    
    return
