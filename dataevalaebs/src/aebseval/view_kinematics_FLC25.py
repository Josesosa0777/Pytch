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

DETAIL_LEVEL = 1

mps2kph = lambda v: v*3.6

class View(iView):
  dep = 'fill_flc25_aoa_aebs_tracks@aebs.fill', 'calc_radar_egomotion-flr25@aebs.fill'
  
  def view(self):
    # process signals
    track = self.modules.fill(self.dep[0])
    t = track.time
    tracks = track[0]
    ego = self.modules.fill(self.dep[1])
    ego_time = ego.time
    
    # create plot
    pn = datavis.cPlotNavigator(title='Ego vehicle and obstacle kinematics')
    
    # speed
    ax = pn.addAxis(ylabel='speed', ylim=(-5.0, 100.0))
    pn.addSignal2Axis(ax, 'ego speed', ego_time, mps2kph(ego.vx), unit='km/h')
    track_vx_abs = rescale(ego.time, ego.vx, t)[1] + tracks.vx   # v_ego + v_track #rescale(ego.time, ego.vx, t)[1]
    pn.addSignal2Axis(ax, 'obst. speed', t,  mps2kph(track_vx_abs), unit='km/h')
    self.extend_speed_axis(pn, ax)

    # acceleration
    ax = pn.addAxis(ylabel = 'accel.conti', ylim = (-10.0, 10.0))
    pn.addSignal2Axis(ax, 'ego acceleration', ego_time, ego.ax, unit = 'm/s^2')
    pn.addSignal2Axis(ax, 'obst. acceleration', t, tracks.ax, unit='m/s^2') # ax_abs
    self.extend_accel_axis(pn, ax)

    # yaw rate
    if DETAIL_LEVEL > 0:
      ax = pn.addAxis(ylabel = "yaw rate", ylim = (-12.0, 12.0))
      pn.addSignal2Axis(ax, "yaw rate", ego_time, rad2deg(ego.yaw_rate), unit = "deg/s")
    # if DETAIL_LEVEL > 0:
    #   ax = pn.addAxis(ylabel = "yaw rate", ylim = (-12.0, 12.0))
    #   pn.addSignal2Axis(ax, "yaw rate", t, rad2deg(ego.yaw_rate), unit = "deg/s")
    # dx
    ax = pn.addAxis(ylabel = 'long. dist.', ylim = (0.0, 150.0))
    pn.addSignal2Axis(ax, 'dx', t, tracks.dx, unit = 'm')
    ax = pn.addTwinAxis(ax, ylabel = 'lat. dist.', ylim = (-15, 15), color = 'g')
    pn.addSignal2Axis(ax, 'dy', t, tracks.dy, unit = 'm', color = 'g')
    # mov_state
    mapping = tracks.mov_state.mapping
    ax = pn.addAxis(ylabel='moving state', yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
    pn.addSignal2Axis(ax, 'obst. mov_st', t, tracks.mov_state.join(), color='g')
    # mov_dir
    if DETAIL_LEVEL > 0:
      mapping = tracks.mov_dir.mapping
      ax = pn.addAxis(ylabel='moving direction', yticks=mapping,
                      ylim=(min(mapping)-0.5, max(mapping)+0.5))
      pn.addSignal2Axis(ax, 'obst. mov_dir', t, tracks.mov_dir.join(), color='g')

    # object_ID
    ax = pn.addAxis(ylabel='object_id', ylim=(0, 255))
    pn.addSignal2Axis(ax, 'object_id', t, tracks.object_id)
    # # confidence
    # if DETAIL_LEVEL > 0:
    #   ax = pn.addAxis(ylabel='confidence', yticks={0:0, 1:1, 2:'no', 3:'yes'},
    #                   ylim=(-0.1, 3.1))
    #   pn.addSignal2Axis(ax, 'radar conf', t, tracks.radar_conf)
    #   pn.addSignal2Axis(ax, 'video conf', t, tracks.video_conf)
    #   pn.addSignal2Axis(ax, 'video associated', t, tracks.fused, offset=2,
    #                     displayscaled=True)
    
    # register client
    self.sync.addClient(pn)
    return

  def extend_speed_axis(self, pn, ax):
    return

  def extend_accel_axis(self, pn, ax):
    return
