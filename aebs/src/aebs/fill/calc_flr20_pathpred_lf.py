# -*- dataeval: init -*-

import numpy as np

import interface
from primitives.lane import PolyClothoid
from aebs.fill import calc_flr20_egomotion

class Calc(interface.iCalc):
  dep = ('calc_flr20_common_time',)

  def check(self):
    sgs = [
      {
        "heading_angle": ("General_radar_status", "LF_heading_angle"),
        "curvature": ("General_radar_status", "LF_curvature"),
        "curvature_rate": ("General_radar_status", "LF_curvature_rate"),
      },
    ]
    group = self.get_source().selectSignalGroup(sgs)
    return group

  def fill(self, group):
    time = self.get_modules().fill('calc_flr20_common_time')
    rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
    left_is_positive = calc_flr20_egomotion.is_left_positive(self.get_source())
    dir_corr = 1.0 if left_is_positive else -1.0
    # line
    a0 = np.zeros_like(time)
    a1 = dir_corr * group.get_value('heading_angle', **rescale_kwargs)
    a2 = dir_corr * group.get_value('curvature', **rescale_kwargs)
    a3 = dir_corr * group.get_value('curvature_rate', **rescale_kwargs)
    line = PolyClothoid.from_physical_coeffs(time, a0, a1, a2, a3)
    return line
