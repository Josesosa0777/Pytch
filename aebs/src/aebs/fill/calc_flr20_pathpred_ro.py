# -*- dataeval: init -*-

import interface
from primitives.lane import Circle
from aebs.fill import calc_flr20_egomotion

class Calc(interface.iCalc):
  dep = ('calc_flr20_common_time',)

  def check(self):
    sgs = [{
      # misleading signal name '...curvature' in the actual protocol
      # TODO: handle old protocol, where 'curvature' is really curvature
      "radius": ("General_radar_status", "estimated_road_curvature"),
    }]
    group = self.get_source().selectSignalGroup(sgs)
    return group

  def fill(self, group):
    time = self.get_modules().fill('calc_flr20_common_time')
    rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
    left_is_positive = calc_flr20_egomotion.is_left_positive(self.get_source())
    dir_corr = 1.0 if left_is_positive else -1.0
    # line
    radius = dir_corr * group.get_value('radius', **rescale_kwargs)
    line = Circle.from_radius(time, radius)
    return line
