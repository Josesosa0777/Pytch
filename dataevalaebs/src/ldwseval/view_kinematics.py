# -*- dataeval: init -*-

"""
Plot LDWS-relevant kinematic and geometric information

Plot basic attributes of ego vehicle and primary lines, including speed,
distance etc. 
"""

from numpy import rad2deg

import datavis
from interface import iView

mps2kph = lambda v: v*3.6

class View(iView):
  dep = 'calc_egomotion@aebs.fill', 'calc_flc20_lanes@aebs.fill'
  
  def view(self):
    # process signals
    ego = self.modules.fill(self.dep[0])
    et = ego.time
    lanes = self.modules.fill(self.dep[1])
    lt = lanes.time
    
    # create plot
    pn = datavis.cPlotNavigator(title='Ego vehicle and lane information')
    
    # speed
    ax = pn.addAxis(ylabel='speed', ylim=(-5.0, 105.0))
    pn.addSignal2Axis(ax, 'ego speed', et, mps2kph(ego.vx), unit='km/h')
    # acceleration
    ax = pn.addAxis(ylabel='accel.', ylim=(-5.0, 5.0))
    pn.addSignal2Axis(ax, 'ego acceleration', et, ego.ax, unit='m/s^2')
    # yaw rate
    ax = pn.addAxis(ylabel="yaw rate", ylim=(-12.0, 12.0))
    pn.addSignal2Axis(ax, "yaw rate", et, rad2deg(ego.yaw_rate), unit="deg/s")
    # line offsets
    ax = pn.addAxis(ylabel='line dist.', ylim=(-4.0, 4.0))
    pn.addSignal2Axis(ax, 'left line dist.', lt, lanes.left_line.a0, unit='m')
    pn.addSignal2Axis(ax, 'right line dist.', lt, lanes.right_line.a0, unit='m')
    
    # register client
    self.sync.addClient(pn)
    return
