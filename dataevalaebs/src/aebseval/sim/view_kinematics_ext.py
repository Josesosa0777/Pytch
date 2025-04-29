# -*- dataeval: init -*-

import numpy as np
from scipy.signal import savgol_filter

from measparser.signalproc import backwardderiv
from aebseval.view_kinematics import View as BaseClass


kph2mps = lambda v: v/3.6

class ViewExt(BaseClass):
  sgs = [ { "MeanSpdFA" : ("EBC2_0B", "EBC2_MeanSpdFA_0B")} ]

  def check(self):
    group = self.source.selectSignalGroup(self.sgs)
    return group

  def fill(self, group):
    self.t, self.value, unit = group.get_signal_with_unit("MeanSpdFA")
    self.unit = unit or "kph"
    return

  def extend_speed_axis(self, pn, ax):
    pn.addSignal2Axis(ax, "ego speed (EBC2)", self.t, self.value, unit=self.unit)
    return

  def extend_accel_axis(self, pn, ax):
    value = kph2mps(self.value)
    accel_backwardderiv = backwardderiv(value, self.t, initialmode="copy_back")
    pn.addSignal2Axis(ax, "ego acceleration (EBC2 backwardderiv)", self.t, accel_backwardderiv, unit="m/s/s", ls="--", color='k')
    window_length = 11
    polyorder = 3
    dt = np.diff(self.t)
    accel_sg = savgol_filter(value, window_length, polyorder, deriv=1, delta=dt.mean())
    pn.addSignal2Axis(ax, "ego acceleration (EBC2 Savitzky-Golay)", self.t, accel_sg, unit="m/s/s", color='r')
    return
