# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

"""
Show raw MBL2 target and track information plots
"""

import interface
import datavis

def_param = interface.NullParam

class View(interface.iView):
  N_TARGETS = 24
  N_PRIMARY_TARGETS = 3
  N_TRACKS = 3
  
  def check(self):
    sg = {}
    for sig in ("Range", "Azimuth", "Power", "BeamNumber", "Velocity"):
      sg.update({"%s_%02d_r" % (sig, i) : ("MBM_TARGET_DETECTION_%02d_r" % i, "%s_%02d_r" % (sig, i)) for i in xrange(1, self.N_TARGETS+1)})
    for sig in ("sixPos", "siyPos"):
      sg.update({"Track%d_%s" % (i, sig) : ("MBM_TRACKS_XY_%02d_r" % i, "Track%d_%s" % (i, sig)) for i in xrange(1, self.N_TRACKS+1)})
    sg["AMBM_Fatal_Error3_r"] = ("MBM_DIAG3_r", "AMBM_Fatal_Error3_r")
    sgs = [sg]
    group = self.source.selectLazySignalGroup(sgs)
    return group
  
  def view(self, param, group):
    kwargs1 = {'lw': 0, 'marker': '.'}
    kwargs2 = {'lw': 0}
    
    client00 = datavis.cPlotNavigator(title="")
    for sig in ("Range", "Azimuth"):
      axis00 = client00.addAxis()
      for i in xrange(1, self.N_TARGETS+1):
        c_sig = "%s_%02d_r" % (sig, i)
        if c_sig not in group: continue
        time00, value00, unit00 = group.get_signal_with_unit(c_sig)
        kwargs = kwargs1 if i <= self.N_PRIMARY_TARGETS else kwargs2
        client00.addSignal2Axis(axis00, c_sig, time00, value00, unit=unit00, **kwargs)
    self.sync.addClient(client00)
    
    client00 = datavis.cPlotNavigator(title="")
    for sig in ("Power", "BeamNumber", "Velocity"):
      axis00 = client00.addAxis()
      for i in xrange(1, self.N_TARGETS+1):
        c_sig = "%s_%02d_r" % (sig, i)
        if c_sig not in group: continue
        time00, value00, unit00 = group.get_signal_with_unit(c_sig)
        kwargs = kwargs1 if i <= self.N_PRIMARY_TARGETS else kwargs2
        client00.addSignal2Axis(axis00, c_sig, time00, value00, unit=unit00, **kwargs)
    self.sync.addClient(client00)
    
    client00 = datavis.cPlotNavigator(title="")
    for sig in ("sixPos", "siyPos"):
      axis00 = client00.addAxis()
      for i in xrange(1, self.N_TRACKS+1):
        c_sig = "Track%d_%s" % (i, sig)
        if c_sig not in group: continue
        time00, value00, unit00 = group.get_signal_with_unit(c_sig)
        client00.addSignal2Axis(axis00, c_sig, time00, value00, unit=unit00)
    self.sync.addClient(client00)
    
    c_sig = "AMBM_Fatal_Error3_r"
    if c_sig in group:
      client02 = datavis.cListNavigator(title="")
      time54, value54 = self.source.getSignalFromSignalGroup(group, c_sig)
      client02.addsignal(c_sig, (time54, value54), groupname="Default")
      self.sync.addClient(client02)
    
    return
