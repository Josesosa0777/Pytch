# -*- dataeval: init -*-

import numpy as np
from interface import iCalc
from primitives.bases import Primitive

signal_group = [
  {
    "x_pts": ("trajectory_generator_flx20_autobox", "tg_output_arbitrated_ref_traj_yx_ctrl_pts_10_5_1"),
    "y_pts": ("trajectory_generator_flx20_autobox", "tg_output_arbitrated_ref_traj_yx_ctrl_pts_10_5_2"),
    "yx_start": ("trajectory_generator_flx20_autobox", "tg_output_arbitrated_ref_traj_yx_start_pt"),
    "yx_num": ("trajectory_generator_flx20_autobox", "tg_output_arbitrated_ref_traj_yx_num_segments"),
    "st_coeffs": ("trajectory_generator_flx20_autobox", "tg_output_arbitrated_ref_traj_st_coeffs"),
    "st_bounds": ("trajectory_generator_flx20_autobox", "tg_output_arbitrated_ref_traj_st_bounds"),
    "st_num": ("trajectory_generator_flx20_autobox", "tg_output_arbitrated_ref_traj_st_num_segments"),
  },
  {
    "x_pts": ("XCP_Test", "tg_output_arbitrated_ref_traj_yx_ctrl_pts_10_5_1"),
    "y_pts": ("XCP_Test", "tg_output_arbitrated_ref_traj_yx_ctrl_pts_10_5_2"),
    "yx_start": ("XCP_Test", "tg_output_arbitrated_ref_traj_yx_start_pt"),
    "yx_num": ("XCP_Test", "tg_output_arbitrated_ref_traj_yx_num_segments"),
    "st_coeffs": ("XCP_Test", "tg_output_arbitrated_ref_traj_st_coeffs"),
    "st_bounds": ("XCP_Test", "tg_output_arbitrated_ref_traj_st_bounds"),
    "st_num": ("XCP_Test", "tg_output_arbitrated_ref_traj_st_num_segments"),
  },
]

def bezierTrajectoryGenerator(st_coeffs, st_bounds, st_num, x_pts, y_pts, yx_start, yx_num, lateral):
  # extract data
  st_coeffs = st_coeffs.data
  st_bounds = st_bounds.data

  x_pts = x_pts.data
  y_pts = y_pts.data
  yx_start = yx_start.data

  # calculate y(tau) and x(tau) points
  tau_step = 0.05
  xp = np.array([])
  yp = np.array([])
  # bezier coefficients
  p_coeff = (1, 5, 10, 10, 5, 1)

  # y(tau), x(tau) bezier calculator
  def b_calc(time, pts):
    return sum(pts[c_i] * np.power(1-time, 5-c_i)*np.power(time, c_i) * p_coeff[c_i] for c_i in range(6))

  first_pt = yx_start
  tau = np.linspace(0, 1, int(1 / tau_step))
  for yx_i in range(yx_num):
    b_pts = np.concatenate([first_pt[0], x_pts[:, yx_i]])
    xp = np.concatenate([xp, b_calc(tau, b_pts)])

    b_pts = np.concatenate([first_pt[1], y_pts[:, yx_i]])
    yp = np.concatenate([yp, b_calc(tau, b_pts)])

    first_pt = np.array([[x_pts[4, yx_i],], [y_pts[4, yx_i]],])

  if lateral:
    # plot only the bezier lateral trajectory
    return yp, xp
  else:

    # create time vector
    time_step = 0.2

    s = np.array([])

    # s(t) poly calculator
    def s_calc(time, coeffs):
      return sum(coeffs[c_i] * np.power(time, c_i) for c_i in range(6))

    # Due to sampling the last bound can change, the next section should start always from the last_bound + time_step
    last_bound = st_bounds[0]
    for st_i in range(st_num):
      t = np.arange(last_bound, st_bounds[st_i + 1], time_step)
      if len(t) > 0:
        # if this was a valid segment then calculate from
        last_bound = t[-1] + time_step
        s = np.concatenate([s, s_calc(t, st_coeffs[::-1, st_i])])

    # TODO decide if last is required
    # s = np.concatenate([s, s_calc(st_bounds[st_num], st_coeffs[:, st_num])])

    # calculate length of bezier segments
    def dist(x1,y1,x2,y2):
      return np.sqrt((y2 - y1) * (y2 - y1) + (x2 - x1) * (x2 - x1))

    # multiply with lower triangle and calculate bezier arc length in the function of yx_i
    yx_s_diff = dist(xp[1:], yp[1:], xp[:-1], yp[:-1])
    yx_s = np.concatenate([[0], np.dot(yx_s_diff, np.transpose(np.tri(len(yx_s_diff), len(yx_s_diff))))])

    # create x, y points based on s(t)
    x = np.zeros_like(s)
    y = np.zeros_like(s)

    if len(s):
      for s_i in range(0, len(s)):
        # find current slice of the bezier for the s(t) profile
        yx_i = 0

        if s[s_i] < 0:
          # It is behind the truck, then use y(x) = 0, x(t) = s(t)
          y[s_i] = 0
          x[s_i] = s[s_i]

        elif s[s_i] > yx_s[-1]:
          # if it is bigger then the bezier lateral trajectory then use y(x)=0, x(t) = s(t)
          y[s_i] = 0
          if len(xp) > 0:
            # if there was y(x) then measure from the end of the curve
            x[s_i] = s[s_i] - yx_s[-1] + xp[-1]
          else:
            x[s_i] = s[s_i]

        else:
          # otherwise search for the appropriate bezier segment
          while yx_i + 1 < len(yx_s) and yx_s[yx_i +1] < s[s_i]:
            yx_i += 1

          if yx_i + 1 >= len(yx_s):
            continue
          diff = s[s_i] - yx_s[yx_i]
          x[s_i] = xp[yx_i]
          y[s_i] = yp[yx_i]
          if np.abs(yx_s_diff[yx_i]) > 0.00001:
            # interpolate between two bezier steps
            x[s_i] += (xp[yx_i + 1] - xp[yx_i]) / yx_s_diff[yx_i] * diff
            y[s_i] += (yp[yx_i + 1] - yp[yx_i]) / yx_s_diff[yx_i] * diff
      return y, x
    else:
      return [], []


class Trajectory(Primitive):
  def __init__(self, time, st_coeffs, st_bounds, st_num, x_pts, y_pts, yx_start, yx_num, name, group_type, lateral=True):
    super(Trajectory, self).__init__(time)
    self.x_pts = np.array([BezierData(p) for p in x_pts])
    self.y_pts = np.array([BezierData(p) for p in y_pts])
    self.yx_start = np.array([BezierData(p) for p in yx_start])
    self.yx_num = yx_num

    self.st_coeffs = np.array([BezierData(p) for p in st_coeffs])
    self.st_bounds = np.array([BezierData(p) for p in st_bounds])
    self.st_num = st_num

    self.func = bezierTrajectoryGenerator
    self.lateral = lateral

    self.group_type = group_type
    self.name = name
    return

class BezierData(object):
  def __init__(self, data):
    self.data = data

class Calc(iCalc):
  def check(self):
    traj_group = self.source.selectSignalGroup(signal_group)
    return traj_group

  def fill(self, traj_group):
    time, x_pts = traj_group.get_signal("x_pts")
    y_pts = traj_group.get_value('y_pts', ScaleTime=time)
    yx_start = traj_group.get_value('yx_start', ScaleTime=time)
    yx_num = traj_group.get_value('yx_num', ScaleTime=time)

    st_coeffs = traj_group.get_value('st_coeffs', ScaleTime=time)
    st_bounds = traj_group.get_value('st_bounds', ScaleTime=time)
    st_num = traj_group.get_value('st_num', ScaleTime=time)

    obj1 = Trajectory(time, st_coeffs, st_bounds, st_num, x_pts, y_pts, yx_start, yx_num, 'Bezier Trajectory',
                     'TRAJ_GEN_BEZIER')
    obj2 = Trajectory(time, st_coeffs, st_bounds, st_num, x_pts, y_pts, yx_start, yx_num,
                     'Bezier Longitudinal Trajectory', 'TRAJ_GEN_BEZIER_VEL', lateral=False)
    return [obj1, obj2]

if __name__ == '__main__':
    from config.Config import init_dataeval
    meas_path = r'\\file\Messdat\DAS\HWA\2017-07-18_Boxberg\TMC__20170718_132233.MF4'
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    obj = manager_modules.calc('calc_trajectory_generator_bezier@ad.fill', manager)
    print obj.x_pts[100, :, 1]
    print obj.x_pts[100, :, 2]


