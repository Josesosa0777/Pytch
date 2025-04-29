import sys

import numpy as np

from primitives.lane import PolyClothoid, FiniteLineProp
from primitives.trajectory import Path, SlicedTrajectory

class FusedPath(PolyClothoid, FiniteLineProp):
  def __init__(self, time, c0, c1, c2, c3, view_range):
    PolyClothoid.__init__(self, time, c0, c1, c2, c3)
    FiniteLineProp.__init__(self, time, view_range)
    return

def create_lin_weighter(length, start=None, end=None):
  if start is None:
    start = 0
  if end is None:
    end = length
  assert end-start > 1, 'allowed interval length minimum is 2'
  w = np.zeros(length)
  ww = (np.arange(0, min(end,length)-max(start,0), dtype=float) +
        max(-start,0)) / (end-start-1)
  w[max(start,0):end] = ww
  w[end:] = 1.0
  return w

def fuse_path(time, dt, dx_m, dy_m, dy_l, viewrange_l, fusrange, debug=None):
  n_meascycles, n_cols = dy_m.shape
  n_predsteps = n_cols - 1
  fusstart, fusend = fusrange
  w = create_lin_weighter(n_predsteps, start=fusstart, end=fusend)
  w = np.insert(w, 0, 0.0)  # j=0 contains non-predicted (but factual) data
  fusend_sat = min(fusend+1, n_cols-1)  # saturated for indexing; +1 for j=0
  dy_f = np.empty_like(dy_l)
  viewrange_f = np.empty_like(viewrange_l)
  fused_paths = SlicedTrajectory(time, [None]*time.size)
  for i in xrange(n_meascycles):
    # lane info quality (view range) based weight update
    if dx_m[i, fusend_sat] > 0.0:
      ww = w * min(viewrange_l[i]/dx_m[i, fusend_sat], 1.0)
    else:
      ww = w  # no sense for modification if dx is 0
    # fusion
    dy_f[i] = (1.0-ww)*dy_m[i] + ww*dy_l[i]
    viewrange_f[i] = min(viewrange_l[i], dx_m[i, -1])
    # fused path as Path
    path_time = time[i] + dt*np.arange(n_predsteps+1)
    fused_paths[i] = Path(path_time, dx_m[i], dy_f[i])
  if debug is not None:
    debug.dy_f = dy_f
    debug.viewrange_f = viewrange_f
    debug.sliced_fused_path = fused_paths
  return dy_f, viewrange_f

def filter_polyclotho(t, dx_pred, dy_pred, motion, debug=None):
  # TODO: model re-implementation
  n_meascycles = t.size
  coeffs = np.empty((n_meascycles, 4))
  if n_meascycles < 1:
    return coeffs
  n_predsteps = dx_pred.shape[1] - 1
  dx_pred_T = dx_pred
  dy_pred_T = dy_pred
  vx = motion.vx
  # init
  A_k = np.zeros((3, 3))  # todo: check
  Q_k = np.eye(3) * 0.01  # todo: check
  S_k = np.eye(3) * 0.01  # todo: check
  xhat_k = np.matrix(np.zeros((3, 1)))
  coeffs[0] = np.zeros(4)  # todo: from xhat_k
  warn_already = False
  for k in xrange(1, n_meascycles):
    # copy previous quantities
    A_k1 = A_k
    Q_k1 = Q_k
    S_k1 = S_k
    xhat_k1 = xhat_k
    
    # calculate current quantities
    Ddx_k = dx_pred_T[k][0] - dx_pred_T[k-1][0]  # ego movement
    # state transition
    A_k = np.array(((    1.0,            Ddx_k,      0.0),
                    (    0.0,             1.0,       0.0),
                    (Ddx_k**2.0/2.0, Ddx_k**3.0/6.0, 1.0)))
    Dt_k = t[k] - t[k-1]
    El_k = vx[k-1] * Dt_k  # todo: improve
    sc2_k = 0.01  # todo: from measurement
    s02_k = 0.01  # todo: from measurement
    # process noise
    Q_k = np.array(((El_k**2.0 * sc2_k,     0.0,        0.0),
                    (       0.0,           sc2_k,       0.0),
                    (       0.0,            0.0,       s02_k)))
    if debug is not None and not warn_already:
      try:
        from numpy.linalg.linalg import cholesky
        cholesky(Q_k)
      except:
        print >> sys.stderr, \
          "Warning: definiteness violated during clothoid filtering"
        warn_already = True
    # measurement noise
    R_k = np.eye(n_predsteps+1) * 1.0  # todo: from measurement
    dx_pred_k = dx_pred_T[k][np.newaxis].T
    # measurement projection
    C_k = np.hstack((dx_pred_k**2.0/2.0,
                     dx_pred_k**3.0/6.0,
                     np.ones_like(dx_pred_k)))
    # "measurement"
    y_k = dy_pred_T[k][np.newaxis].T
    
    # create matrices from arrays
    A_k1 = np.matrix(A_k1)
    S_k1 = np.matrix(S_k1)
    Q_k1 = np.matrix(Q_k1)
    C_k  = np.matrix(C_k)
    R_k  = np.matrix(R_k)
    # 1. prediction
    M_k = A_k1*S_k1*A_k1.T + Q_k1
    G_k = M_k*C_k.T * (C_k*M_k*C_k.T + R_k).I
    S_k = M_k - G_k*C_k*M_k
    xbar_k = A_k1*xhat_k1
    # 2. update
    xhat_k = xbar_k + G_k*(y_k - C_k*xbar_k)
    
    coeffs[k] = np.array((xhat_k[2], 0.0, xhat_k[0], xhat_k[1]), dtype=float)
  return coeffs

class PathFusion(object):
  def calc(self, time, motion, dx_m, dy_m, dy_l, viewrange_l, debug=None):
    raise NotImplementedError

class LinWeight(PathFusion):
  def __init__(self, fusrange):
    self._fusrange = fusrange
    return
  
  def calc(self, time, motion, dt, dx_m, dy_m, dy_l, viewrange_l, debug=None):
    dy_f, viewrange_f = fuse_path(
      time, dt, dx_m, dy_m, dy_l, viewrange_l, self._fusrange, debug)
    coeffs = filter_polyclotho(time, dx_m, dy_f, motion, debug)
    line_f = FusedPath(time, *([None]*5))
    line_f.physical_coeffs = coeffs.T
    line_f.viewrange = viewrange_f
    return line_f
