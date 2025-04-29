# -*- dataeval: init -*-

"""
Plot AEBS-relevant kinematic information

Plot basic attributes of ego vehicle and primary track, including speed,
distance etc. 
"""

from numpy import rad2deg

import datavis
from interface import iView
from measparser.signalproc import rescale

DETAIL_LEVEL = 0

mps2kph = lambda v: v*3.6

class View(iView):
  dep = 'fill_flr20_aeb_track@aebs.fill', 'calc_flr20_egomotion@aebs.fill'
  
  def view(self):
    # process signals
    track = self.modules.fill(self.dep[0])
    t = track.time
    ego = self.modules.fill(self.dep[1])
    
    # create plot
    pn = datavis.cPlotNavigator(title='Ego vehicle and obstacle kinematics')
    
    # speed
    ax = pn.addAxis(ylabel='speed', ylim=(-5.0, 105.0))
    pn.addSignal2Axis(ax, 'ego speed', t, mps2kph(ego.vx), unit='km/h')
    track_vx_abs = rescale(ego.time, ego.vx, t)[1] + track.vx  # v_ego + v_track
    pn.addSignal2Axis(ax, 'obst. speed', t, mps2kph(track_vx_abs), unit='km/h')
    self.extend_speed_axis(pn, ax)
    # acceleration
    ax = pn.addAxis(ylabel='accel.', ylim=(-5.0, 5.0))
    pn.addSignal2Axis(ax, 'ego acceleration', t, ego.ax, unit='m/s^2')
    pn.addSignal2Axis(ax, 'obst. acceleration', t, track.ax_abs, unit='m/s^2')
    self.extend_accel_axis(pn, ax)
    # yaw rate
    if DETAIL_LEVEL > 0:
      ax = pn.addAxis(ylabel="yaw rate", ylim=(-12.0, 12.0))
      pn.addSignal2Axis(ax, "yaw rate", t, rad2deg(ego.yaw_rate), unit="deg/s")
    # dx
    ax = pn.addAxis(ylabel='long. dist.', ylim=(0.0, 80.0))
    pn.addSignal2Axis(ax, 'dx', t, track.dx, unit='m')
    ax = pn.addTwinAxis(ax, ylabel='lat. dist.', ylim=(-15.0, 15.0), color='g')
    pn.addSignal2Axis(ax, 'dy', t, track.dy, unit='m', color='g')
    # mov_state
    mapping = track.mov_state.mapping
    ax = pn.addAxis(ylabel='moving state', yticks=mapping,
                    ylim=(min(mapping)-0.5, max(mapping)+0.5))
    pn.addSignal2Axis(ax, 'obst. mov_st', t, track.mov_state.join(), color='g')
    # mov_dir
    if DETAIL_LEVEL > 0:
      mapping = track.mov_dir.mapping
      ax = pn.addAxis(ylabel='moving direction', yticks=mapping,
                      ylim=(min(mapping)-0.5, max(mapping)+0.5))
      pn.addSignal2Axis(ax, 'obst. mov_dir', t, track.mov_dir.join(), color='g')
    # confidence
    if DETAIL_LEVEL > 0:
      ax = pn.addAxis(ylabel='confidence', yticks={0:0, 1:1, 2:'no', 3:'yes'},
                      ylim=(-0.1, 3.1))
      pn.addSignal2Axis(ax, 'radar conf', t, track.radar_conf)
      pn.addSignal2Axis(ax, 'video conf', t, track.video_conf)
      pn.addSignal2Axis(ax, 'video associated', t, track.fused, offset=2,
                        displayscaled=True)
    
    # register client
    self.sync.addClient(pn)
    return

  def extend_speed_axis(self, pn, ax):
    return

  def extend_accel_axis(self, pn, ax):
    return
