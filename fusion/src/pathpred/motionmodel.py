import numpy as np

def rotate(dx, dy, phi):
  dx_t = dx*np.cos(phi) - dy*np.sin(phi)
  dy_t = dx*np.sin(phi) + dy*np.cos(phi)
  return dx_t, dy_t

def translate(dx, dy, dx_offset, dy_offset):
  return dx+dx_offset, dy+dy_offset

def rm_backwards(dx_m, dy_m=None, vx_m=None, vy_m=None, ax_m=None):
  n_meascycles = dx_m.shape[0]
  for i in xrange(n_meascycles):
    ind = np.nonzero(np.diff(dx_m[i]) < 0.0)[0]
    if ind.size > 0:
      j = ind[0]
      dx_m[i, j:] = dx_m[i, j]
      if dy_m is not None:
        dy_m[i, j:] = dy_m[i, j]
      if vx_m is not None:
        vx_m[i, j:] = 0.0
      if vy_m is not None:
        vy_m[i, j:] = 0.0
      if ax_m is not None:
        ax_m[i, j:] = 0.0
  return

def calc_ca_step(dt, dx, dy, vx, vy, ax, ay):
  dx_kp1 = dx + vx*dt + 0.5*ax*dt**2.0
  dy_kp1 = dy + vy*dt + 0.5*ay*dt**2.0
  vx_kp1 = vx + ax*dt
  vy_kp1 = vy + ay*dt
  return dx_kp1, dy_kp1, vx_kp1, vy_kp1

def calc_ctr_step(dt, dx, dy, vx, vy, w):
  phi = w*dt
  with np.errstate(divide='ignore', invalid='ignore'):
    sw = np.where(phi, np.sin(phi)/phi, 1.0)
    cw = np.where(phi, (1.0-np.cos(phi))/phi, 0.0)
  dx_kp1 = dx + dt * (sw*vx - cw*vy)
  dy_kp1 = dy + dt * (cw*vx + sw*vy)
  vx_kp1 = vx*np.cos(phi) - vy*np.sin(phi)
  vy_kp1 = vx*np.sin(phi) + vy*np.cos(phi)
  return dx_kp1, dy_kp1, vx_kp1, vy_kp1

class MotionModel(object):
  def __init__(self, cycletime, n_predsteps):
    self._dt = cycletime
    self._n_predsteps = n_predsteps
    return
  
  def calc(self, motion, debug=None):
    raise NotImplementedError

class CaModel(MotionModel):
  def calc(self, motion, debug=None):
    n_rows = self._n_predsteps + 1
    vx = motion.vx
    ax = motion.ax
    ay = vx * motion.yaw_rate
    dx_pred = np.empty((n_rows, vx.size))
    dy_pred = np.empty((n_rows, vx.size))
    vx_pred = np.empty((n_rows, vx.size))
    vy_pred = np.empty((n_rows, vx.size))
    dx_pred[0] = np.zeros_like(vx)
    dy_pred[0] = np.zeros_like(vx)
    vx_pred[0] = vx[:]
    vy_pred[0] = np.zeros_like(vx)
    for k in xrange(self._n_predsteps):
      dx_pred[k+1], dy_pred[k+1], vx_pred[k+1], vy_pred[k+1] = calc_ca_step(
        self._dt, dx_pred[k], dy_pred[k], vx_pred[k], vy_pred[k], ax, ay)
    dx_m = dx_pred.T
    dy_m = dy_pred.T
    rm_backwards(dx_m, dy_m)
    if debug is not None:
      debug.dx_m = dx_m
      debug.dy_m = dy_m
    return dx_m, dy_m

class CtrModel(MotionModel):
  def calc(self, motion, debug=None):
    n_rows = self._n_predsteps + 1
    vx = motion.vx
    w = motion.yaw_rate
    dx_pred = np.empty((n_rows, vx.size))
    dy_pred = np.empty((n_rows, vx.size))
    vx_pred = np.empty((n_rows, vx.size))
    vy_pred = np.empty((n_rows, vx.size))
    dx_pred[0] = np.zeros_like(vx)
    dy_pred[0] = np.zeros_like(vx)
    vx_pred[0] = vx[:]
    vy_pred[0] = np.zeros_like(vx)
    for k in xrange(self._n_predsteps):
      dx_pred[k+1], dy_pred[k+1], vx_pred[k+1], vy_pred[k+1] = calc_ctr_step(
        self._dt, dx_pred[k], dy_pred[k], vx_pred[k], vy_pred[k], w)
    dx_m = dx_pred.T
    dy_m = dy_pred.T
    rm_backwards(dx_m, dy_m)
    if debug is not None:
      debug.dx_m = dx_m
      debug.dy_m = dy_m
    return dx_m, dy_m

class CtraModel(MotionModel):
  def calc(self, motion, debug=None):
    # TODO
    raise NotImplementedError
