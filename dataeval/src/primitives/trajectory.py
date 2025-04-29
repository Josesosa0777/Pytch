import copy

import numpy as np

from measparser.signalproc import isSameTime, smooth
from primitives.bases import Primitive

class SlicedTrajectory(list):
  def __init__(self, time, trajectories):
    assert time.ndim == 1
    list.__init__(self, trajectories)
    self.time = time
    return
  
  def calc_rms_errors(self, other):
    assert isSameTime(self.time, other.time), "different time domains"
    rmss = np.empty_like(self.time)
    for i, (self_traj, other_traj) in enumerate(zip(self, other)):
      rmss[i] = self_traj.calc_rms_error(other_traj)
    return rmss
  
  def rescale(self, time_scale, **kwargs):
    raise NotImplementedError
  
  def rescale_slices(self, dt, **kwargs):
    newobj = copy.copy(self)
    for i, traj in enumerate(self):
      if traj.time.size > 1:
        time_scale = np.arange(traj.time[0], traj.time[-1], dt)
        newtraj = traj.rescale(time_scale, **kwargs)
      else:
        newtraj = copy.copy(traj)
      newobj[i] = newtraj
    return newobj

class Trajectory(Primitive):
  SLICED_CLASS = SlicedTrajectory
  
  def slice(self, n_pre, n_post):
    n_meascycles = self.time.size
    states = self.get_states()
    def _extend_arr(base):
      ext_shape = list(base.shape)
      ext_shape[0] += n_pre+n_post
      arr = np.empty(ext_shape)
      arr.fill(np.NaN)
      arr[n_pre : n_pre+n_meascycles, ...] = base
      return arr
    # create NaN-extended arrays for easy indexing
    ext_states = _extend_arr(states)
    ext_time = _extend_arr(self.time)
    # create sliced trajectories
    traj_parts = []
    for i in xrange(n_meascycles):
      extind1, extind2 = i, i+n_pre+n_post+1
      traj_part = self.from_states(
        ext_time[extind1:extind2,...], ext_states[extind1:extind2,...])
      traj_part = traj_part.transform(-states[i,...])
      traj_parts.append(traj_part)
    straj = self.SLICED_CLASS(self.time, traj_parts)
    return straj
  
  def transform(self, state_offset):
    return copy.copy(self)  # default = no transform
  
  def calc_rms_error(self, other, state_idx=None):
    # TODO: weight parameter
    self_states = self.get_states()
    other_states = other.get_states()
    if np.all(~np.isnan(self.time)) and np.all(~np.isnan(other.time)):
      assert isSameTime(self.time, other.time), "different time domains"
    else:
      assert self.time.size == other.time.size, "different size of times"
    assert self_states.shape == other_states.shape, \
      "different shape of trajectories"
    if state_idx is None:
      # TODO: vectorize the whole calc in this case
      state_idx = xrange(self_states.shape[1])  # all states
    elif np.isscalar(state_idx):
      state_idx = [state_idx]
    errors = np.zeros_like(self.time)
    for i_col in state_idx:
      errors += (self_states[:,i_col,...] - other_states[:,i_col,...]) ** 2.0
    rms = np.sqrt(np.mean(errors))
    return rms


class SlicedPath(SlicedTrajectory):
  def calc_rms_pos_errors(self, other):
    assert isSameTime(self.time, other.time), "different time domains"
    rmss = np.empty_like(self.time)
    for i, (self_traj, other_traj) in enumerate(zip(self, other)):
      rmss[i] = self_traj.calc_rms_pos_error(other_traj)
    return rmss
  
  def _get_attribute(self, attr_name):
    attr_value = [getattr(path, attr_name) for path in self]
    attr_value = np.array(attr_value)
    return attr_value
  
  def get_dxs(self):
    return self._get_attribute('dx')
  
  def get_dys(self):
    return self._get_attribute('dy')
  
  def get_headings(self):
    return self._get_attribute('heading')
  
  def get_times(self):
    return self._get_attribute('time')

class Path(Trajectory):
  SLICED_CLASS = SlicedPath
  
  def __init__(self, time, dx, dy, heading=None):
    Trajectory.__init__(self, time)
    self.dx = dx
    self.dy = dy
    if heading is None:
      heading = np.arctan2(np.gradient(dy), np.gradient(dx))
    self.heading = heading
    return
  
  def transform(self, state_offset):
    state_indices = self.get_statenames2indices()
    Ddx = state_offset[state_indices['dx']]
    Ddy = state_offset[state_indices['dy']]
    Dpsi = state_offset[state_indices['heading']]
    # translate
    dx_t = self.dx + Ddx
    dy_t = self.dy + Ddy
    # ... then rotate
    dx_t_r = dx_t*np.cos(Dpsi) - dy_t*np.sin(Dpsi)
    dy_t_r = dx_t*np.sin(Dpsi) + dy_t*np.cos(Dpsi)
    heading_r = self.heading + Dpsi
    # result
    newobj = copy.copy(self)
    newobj.dx = dx_t_r
    newobj.dy = dy_t_r
    newobj.heading = heading_r
    return newobj
  
  def calc_rms_pos_error(self, other):
    state_indices = self.get_statenames2indices()
    pos_states = (state_indices['dx'], state_indices['dy'])
    rms = self.calc_rms_error(other, state_idx=pos_states)
    return rms
  
  def calc_rms_dy_error(self, other):
    raise NotImplementedError  # TODO: impl
  
  def _smooth(self, w_cutoff=5.0):
    newobj = copy.copy(self)
    valid_mask = ~np.isnan(self.heading)
    heading = np.interp(self.time, self.time[valid_mask], self.heading[valid_mask])
    smoothed_heading = smooth(heading, self.time, w_cutoff=w_cutoff)
    smoothed_heading[~valid_mask] = np.NaN
    newobj.heading = smoothed_heading
    return newobj
