import numpy as np

def eval_polyclotho(x, coeffs):
  xT = x.T
  c0, c1, c2, c3 = coeffs
  yT = c3*(xT**3.0) + c2*(xT**2.0) + c1*xT + c0
  return yT.T

def fuse_lines_centerdrive(dx_l, dy_ll, viewrange_ll, dy_lr, viewrange_lr):
  n_meascycles, n_cols = dx_l.shape
  # simple fusion
  dy_lf = 0.5 * (dy_ll + dy_lr)  # TODO: include uncertainties
  viewrange_lf = np.max(np.vstack((viewrange_ll, viewrange_lr)), axis=0)
  # dy correction where info is incomplete
  for i in xrange(n_meascycles):
    dx_max = np.max(dx_l[i])
    if viewrange_ll[i] >= dx_max and viewrange_lr[i] >= dx_max:
      continue
    # find correction starting index
    i_laneends_l = np.nonzero(viewrange_ll[i] < dx_l[i])[0]
    i_laneend_l = i_laneends_l[0] if i_laneends_l.size > 0 else n_cols-1
    i_laneends_r = np.nonzero(viewrange_lr[i] < dx_l[i])[0]
    i_laneend_r = i_laneends_r[0] if i_laneends_r.size > 0 else n_cols-1
    if i_laneend_l > i_laneend_r:
      dy_long = dy_ll[i]
    else:
      dy_long = dy_lr[i]
    i_fusstart = min(i_laneend_l, i_laneend_r)
    # fused line is parallel to the longer line
    dy_lf[i, i_fusstart:] = (
      dy_long[i_fusstart:] - dy_long[i_fusstart] + dy_lf[i, i_fusstart]) 
  return dy_lf, viewrange_lf

def fuse_lines_paralleldrive(dx_l, dy_ll, viewrange_ll, dy_lr, viewrange_lr):
  dy_ll_offcomp = dy_ll - dy_ll[:, 0, np.newaxis]
  dy_lr_offcomp = dy_lr - dy_lr[:, 0, np.newaxis]
  dy_lf, viewrange_lf = fuse_lines_centerdrive(
    dx_l, dy_ll_offcomp, viewrange_ll, dy_lr_offcomp, viewrange_lr)
  return dy_lf, viewrange_lf

class LaneModel(object):
  def calc(self, lanes, dx_m, debug=None):
    raise NotImplementedError

class MultiClotho(LaneModel):
  def calc(self, lanes, dx_m, debug=None):
    ll = lanes.left_line
    lr = lanes.right_line
    dy_ll = eval_polyclotho(dx_m, ll.coeffs)
    dy_lr = eval_polyclotho(dx_m, lr.coeffs)
    dy_l, viewrange_l = fuse_lines_paralleldrive(
      dx_m, dy_ll, ll.view_range, dy_lr, lr.view_range)
    if debug is not None:
      debug.dy_l = dy_l
      debug.viewrange_l = viewrange_l
      debug.dy_ll = dy_ll
      debug.dy_lr = dy_lr
    return dy_l, viewrange_l
