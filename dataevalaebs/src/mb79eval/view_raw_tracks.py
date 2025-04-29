# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
Plots some attributes of the selected MB79 track
"""

import numpy as np

from interface import iView
import datavis

init_params = dict( ('TRACK_%02d' %i, dict(id=i)) for i in xrange(20) )

class View(iView):
  dep = 'calc_mb79_raw_tracks@aebs.fill',
  TITLE_PAT = 'MB79 track #%d'

  def init(self, id):
    self.id = id
    return

  def check(self):
    tracks = self.modules.fill(self.dep[0])
    assert self.id in tracks, 'Track %d is not recorded' %self.id
    track = tracks[self.id]
    return track

  def view(self, track):
    t = track.time
    graph = datavis.cPlotNavigator(title=self.TITLE_PAT%self.id)

    axis_range = graph.addAxis(ylabel="range")
    axis_dx_dy = graph.addAxis(ylabel="x,y")
    axis_angle = graph.addAxis(ylabel="angle")
    axis_movstate = graph.addAxis(ylabel="moving state", xlabel="time [s]")
    axis_class = graph.addAxis(ylabel='classification')
    axis_acc = graph.addAxis(ylabel='acceleration')
    axis_spd = graph.addAxis(ylabel='speed')
    axis_ref = graph.addAxis(ylabel='reference point')

    graph.addSignal2Axis(axis_range,      'range',      t, track.range, unit='m')

    graph.addSignal2Axis(axis_dx_dy,      'dx',         t, track.dx, unit='m')
    graph.addSignal2Axis(axis_dx_dy,      'dy',         t, track.dy, unit='m')

    graph.addSignal2Axis(axis_angle,      'angle',      t, np.rad2deg(track.angle), unit=u'°')

    graph.addSignal2Axis(axis_movstate,   'moving',     t, track.mov_state.moving)
    graph.addSignal2Axis(axis_movstate,   'stationary', t, track.mov_state.stat)
    graph.addSignal2Axis(axis_movstate,   'unknown',    t, track.mov_state.unknown)

    graph.addSignal2Axis(axis_ref,        'ref point',  t, track.ref_point)

    graph.addSignal2Axis(axis_acc,        'ax',         t, track.ax)
    graph.addSignal2Axis(axis_acc,        'ay',         t, track.ay)

    graph.addSignal2Axis(axis_spd,        'vx',         t, track.vx)
    graph.addSignal2Axis(axis_spd,        'vy',         t, track.vy)

    graph.addSignal2Axis(axis_class,      'car',        t, track.obj_type.car)
    graph.addSignal2Axis(axis_class,      'unknown',    t, track.obj_type.unknown)
    graph.addSignal2Axis(axis_class,      'pedestrian', t, track.obj_type.pedestrian)
    graph.addSignal2Axis(axis_class,      'truck',      t, track.obj_type.truck)
    graph.addSignal2Axis(axis_class,      'motorcycle', t, track.obj_type.motorcycle)
    graph.addSignal2Axis(axis_class,      'bicycle',    t, track.obj_type.bicycle)

    self.sync.addClient(graph)
    return
