# -*- dataeval: init -*-

import numpy as np

import datavis
import interface


init_params = {
  "FLR20": dict(sensor='AC100'),
}

class AC100(object):
  """
  AC100-specific parameters.
  """
  permaname = 'AC100'
  productname = "FLR20"
  ego_fill = 'calc_flr20_egomotion@aebs.fill'


class View(interface.iView):
  def init(self, sensor):
    assert sensor in globals(), "parameter class for %s not defined" % sensor
    self.sensor = globals()[sensor]
    self.dep = (self.sensor.ego_fill,)
    return

  def fill(self):
    ego_motion = self.get_modules().fill(self.sensor.ego_fill)
    return ego_motion

  def view(self, ego_motion):
    title = "Ego motion (%s)" % self.sensor.productname
    pn = datavis.cPlotNavigator(title=title)

    time = ego_motion.time

    ax = pn.addAxis(ylim=(-1.0, 100.0))
    pn.addSignal2Axis(ax, "speed", time, ego_motion.vx * 3.6, unit="km/h")
    ax = pn.addAxis(ylim=(-12.0, 12.0))
    pn.addSignal2Axis(
      ax, "yaw rate", time, np.rad2deg(ego_motion.yaw_rate), unit="deg/s")
    ax = pn.addAxis(ylim=(-6.0, 6.0))
    pn.addSignal2Axis(ax, "acceleration", time, ego_motion.ax, unit="m/s2")

    self.get_sync().addClient(pn)
    return
