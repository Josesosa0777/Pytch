# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import types

import numpy as np

import interface
import datavis

sgs = [
{
  "tr0_range": ("Tracks", "tr0_range"),
  "CCVS_WheelbasedVehSpd_00": ("CCVS1_00", "CCVS_WheelbasedVehSpd_00"),
},
]

# initial time domain to consider
tstart, tend = -np.Inf, np.Inf

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def view(self, group):
    t_dx, dx_all, unit_dx       = group.get_signal_with_unit("tr0_range")
    t_vego, vego_all, unit_vego = group.get_signal_with_unit("CCVS_WheelbasedVehSpd_00", ScaleTime=t_dx)
    unit_vego = unit_vego or 'kph'

    client00 = datavis.cPlotNavigator(title="Ego speed vs. target distance")
    axis00 = client00.addAxis(xlabel='dx [%s]'%unit_dx, ylabel='vEgo [%s]'%unit_vego)
    axis00.invert_xaxis()
    def clip_data(start, end):
      st,end = t_dx.searchsorted( [start, end] )
      dx = dx_all[st:end]
      vego = vego_all[st:end]
      return st, end, dx, vego
    st, end, dx, vego = clip_data(tstart, tend)
    client00.addSignal2Axis(axis00, "CCVS_WheelbasedVehSpd", dx, vego, unit=unit_vego)
    # workaround to flip x axis (xlim is set in start() that is called after us)
    client00.ax = axis00
    start_orig = client00.start
    def start_hack(selfie):
      start_orig() # already a bound method
      selfie.ax.set_xlim(dx.max(), dx.min())
    client00.start = types.MethodType(start_hack, client00) # bound method only to this instance (don't monkeypatch whole class)
    # workaround to set bounds with ROI
    setROI_orig = client00.setROI
    def setROI_hack(selfie, client, pstart, pend, color):
      st, end, dx, vego = clip_data(pstart, pend)
      selfie.ax.lines[1].set_xdata(dx)
      selfie.ax.lines[1].set_ydata(vego)
      selfie.ax.set_xlim(dx.max(), dx.min())
      client00.canvas.draw()
      # setROI_orig()
    client00.setROI = types.MethodType(setROI_hack, client00) # bound method only to this instance (don't monkeypatch whole class)
    # add special time synchronization function
    self.sync.addClient(client00, timesyncfunc=(t_dx[st:end],dx))
    return
