import sys

import numpy as np

import motionmodel
import lanemodel
import pathfusion
from measparser.signalproc import isSameTime
from primitives.lane import FiniteLineProp, PolyClothoid, LaneData
from primitives.egomotion import EgoMotion

class PathPredictor(object):
  def __init__(self, motion_model=None, lane_model=None, path_fusion=None,
               debug_active=False):
    # process input
    if motion_model is None:
      cycletime = 0.08
      n_predsteps = 50
      mm = motionmodel.CtrModel(cycletime, n_predsteps)
    if lane_model is None:
      lm = lanemodel.MultiClotho()
    if path_fusion is None:
      fusrange = (0, 40)
      pf = pathfusion.LinWeight(fusrange)
    # store values
    self._motionmodel = mm
    self._lanemodel = lm
    self._pathfusion = pf
    self.debug_active = debug_active
    return
  
  def predict(self, motion, lanes):
    assert isSameTime(motion.time, lanes.time), "multiple time domains"
    time = motion.time
    debug = PpDebug() if self.debug_active else None
    dx_m, dy_m = self._motionmodel.calc(motion, debug=debug)
    dy_l, viewrange_l = self._lanemodel.calc(lanes, dx_m, debug=debug)
    line_f = self._pathfusion.calc(time, motion,
      self._motionmodel._dt, dx_m, dy_m, dy_l, viewrange_l, debug=debug)
    return line_f, debug

class PpDebug(object):
  def __init__(self):
    # motion
    self.dx_m = None
    self.dy_m = None
    self.vx_m = None
    self.ax_m = None
    # lane
    self.dy_l = None
    self.viewrange_l = None
    self.dy_ll = None
    self.dy_lr = None
    # fusion
    self.dy_f = None
    self.viewrange_f = None
    self.sliced_fused_path = None
    return

if __name__ == '__main__':
  def get_signals(n_meascycles):
    n = n_meascycles
    t  =  np.arange(n, dtype=float)
    vx =  np.random.random(n) * 100.0
    ax =  np.random.random(n) * 5.0
    w  = (np.random.random(n) - 0.5) * 10.0
    a0l = np.random.random(n) + 2.0
    a1l = np.random.random(n)
    a2l = np.random.random(n)
    a3l = np.random.random(n)
    coeffsl = (a0l, a1l, a2l, a3l)
    viewrangel = np.random.random(n) * 100.0
    a0r = np.random.random(n) - 2.0
    a1r = np.random.random(n)
    a2r = np.random.random(n)
    a3r = np.random.random(n)
    coeffsr = (a0r, a1r, a2r, a3r)
    viewranger = np.random.random(n) * 100.0
    return t, vx, ax, w, coeffsl, viewrangel, coeffsr, viewranger
  
  class VideoLine(PolyClothoid, FiniteLineProp):
    def __init__(self, time, c0, c1, c2, c3, view_range):
      PolyClothoid.__init__(self, time, c0, c1, c2, c3)
      FiniteLineProp.__init__(self, time, view_range)
      return
  
  t, vx, ax, w, coeffsl, viewrangel, coeffsr, viewranger = get_signals(100)
  motion = EgoMotion(t, vx, ax, w)
  linel = VideoLine(t, *([None]*5))
  linel.physical_coeffs = coeffsl
  linel.view_range = viewrangel
  liner = VideoLine(t, *([None]*5))
  liner.physical_coeffs = coeffsr
  liner.view_range = viewranger
  lanes = LaneData(linel, liner)
  pp = PathPredictor(debug_active=True)
  line_f, debug = pp.predict(motion, lanes)
  print >> sys.stderr, 'Calculation finished.'
