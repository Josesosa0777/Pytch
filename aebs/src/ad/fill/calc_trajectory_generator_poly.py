# -*- dataeval: init -*-

import numpy as np
from interface import iCalc
from primitives.bases import Primitive

signal_group = [
  {
  "b0": ("trajectory_generator_flx20_autobox", "tg_output_reference_traj_approx_b0"),
  "b1": ("trajectory_generator_flx20_autobox", "tg_output_reference_traj_approx_b1"),
  "b2": ("trajectory_generator_flx20_autobox", "tg_output_reference_traj_approx_b2"),
  "b3": ("trajectory_generator_flx20_autobox", "tg_output_reference_traj_approx_b3"),
  "c0": ("trajectory_generator_flx20_autobox", "tg_output_reference_traj_approx_c0"),
  "c1": ("trajectory_generator_flx20_autobox", "tg_output_reference_traj_approx_c1"),
  "c2": ("trajectory_generator_flx20_autobox", "tg_output_reference_traj_approx_c2"),
  "c3": ("trajectory_generator_flx20_autobox", "tg_output_reference_traj_approx_c3"),
  "valid_dist_max": ("trajectory_generator_flx20_autobox", "tg_output_reference_traj_approx_valid_dist_max"),
  "valid_dist_min": ("trajectory_generator_flx20_autobox", "tg_output_reference_traj_approx_valid_dist_min"),
  "valid_time_max": ("trajectory_generator_flx20_autobox", "tg_output_reference_traj_approx_valid_time_max"),
  "valid_time_min": ("trajectory_generator_flx20_autobox", "tg_output_reference_traj_approx_valid_time_min"),
  },
  {
    "b0": ("XCP_Test", "tg_output_reference_traj_approx_b0"),
    "b1": ("XCP_Test", "tg_output_reference_traj_approx_b1"),
    "b2": ("XCP_Test", "tg_output_reference_traj_approx_b2"),
    "b3": ("XCP_Test", "tg_output_reference_traj_approx_b3"),
    "c0": ("XCP_Test", "tg_output_reference_traj_approx_c0"),
    "c1": ("XCP_Test", "tg_output_reference_traj_approx_c1"),
    "c2": ("XCP_Test", "tg_output_reference_traj_approx_c2"),
    "c3": ("XCP_Test", "tg_output_reference_traj_approx_c3"),
    "valid_dist_max": ("XCP_Test", "tg_output_reference_traj_approx_valid_dist_max"),
    "valid_dist_min": ("XCP_Test", "tg_output_reference_traj_approx_valid_dist_min"),
    "valid_time_max": ("XCP_Test", "tg_output_reference_traj_approx_valid_time_max"),
    "valid_time_min": ("XCP_Test", "tg_output_reference_traj_approx_valid_time_min"),
  },
]

def polyTrajectoryGenerator(b0, b1, b2, b3, c0, c1, c2, c3, c4,
                            valid_dist_max, valid_dist_min, valid_time_max, valid_time_min, mask_s):
  time_step = 0.2

  t = np.arange(valid_time_min, valid_time_max + time_step, time_step)
  x = c4 * np.power(t, 4) + c3 * np.power(t, 3) + c2 * np.power(t, 2) + c1 * np.power(t, 1) + c0
  y = b3 * np.power(x, 3) + b2 * np.power(x, 2) + b1 * np.power(x, 1) + b0
  if mask_s:
    # This way only the actual Lat Lon trajectory is plotted
    mask = np.logical_and(x <= valid_dist_max, x >= valid_dist_min)
    return y[mask], x[mask]
  else:
    # This way the whole time box is plotted, where the lateral is invalid the y(x)=0
    mask = np.logical_or(x > valid_dist_max, x < valid_dist_min)
    y[mask] = 0
    return y, x

class Trajectory(Primitive):
  def __init__(self, time, b0, b1, b2, b3, c0, c1, c2, c3,
                     valid_dist_max, valid_dist_min, valid_time_max, valid_time_min, name,
                     group_type, mask_s=True):
    super(Trajectory, self).__init__(time)
    # b stands for y(x) coeffs
    self.b0 = b0
    self.b1 = b1
    self.b2 = b2
    self.b3 = b3

    # c stands for v(t) coeffs
    # create s(t)
    self.c0 = 0
    self.c1 = c0
    self.c2 = c1/2
    self.c3 = c2/3
    self.c4 = c3/4

    self.valid_dist_max = valid_dist_max
    self.valid_dist_min = valid_dist_min
    self.valid_time_max = valid_time_max
    self.valid_time_min = valid_time_min

    self.func = polyTrajectoryGenerator
    self.mask_s = mask_s

    self.group_type = group_type
    self.name = name
    return

class Calc(iCalc):
  def check(self):
    traj_group = self.source.selectSignalGroup(signal_group)
    return traj_group

  def fill(self, traj_group):
    time, b0 = traj_group.get_signal("b0")
    b1 = traj_group.get_value('b1', ScaleTime=time)
    b2 = traj_group.get_value('b2', ScaleTime=time)
    b3 = traj_group.get_value('b3', ScaleTime=time)

    c0 = traj_group.get_value('c0', ScaleTime=time)
    c1 = traj_group.get_value('c1', ScaleTime=time)
    c2 = traj_group.get_value('c2', ScaleTime=time)
    c3 = traj_group.get_value('c3', ScaleTime=time)

    valid_dist_max = traj_group.get_value('valid_dist_max', ScaleTime=time)
    valid_dist_min = traj_group.get_value('valid_dist_min', ScaleTime=time)
    valid_time_max = traj_group.get_value('valid_time_max', ScaleTime=time)
    valid_time_min = traj_group.get_value('valid_time_min', ScaleTime=time)

    obj1 = Trajectory(time, b0, b1, b2, b3, c0, c1, c2, c3,
                     valid_dist_max, valid_dist_min, valid_time_max, valid_time_min, 'Poly Trajectory',
                      'TRAJ_GEN_POLY')
    obj2 = Trajectory(time, b0, b1, b2, b3, c0, c1, c2, c3,
                     valid_dist_max, valid_dist_min, valid_time_max, valid_time_min, 'Poly Longitudinal Trajectory',
                      'TRAJ_GEN_POLY_VEL', mask_s=False)
    return [obj1, obj2]

if __name__ == '__main__':
    from config.Config import init_dataeval
    meas_path = r'\\file\Messdat\DAS\HWA\2017-07-18_Boxberg\TMC__20170718_132233.MF4'
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    obj = manager_modules.calc('calc_trajectory_generator_poly@ad.fill', manager)
    print obj.b0[1000], obj.b1[1000], obj.b2[1000], obj.b3[1000]
    print obj.c0[1000], obj.c1[1000], obj.c2[1000], obj.c3[1000]
    print obj.time[0:20]
