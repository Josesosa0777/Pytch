# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
Plots some attributes of the selected MB79 track
"""

from interface import iView
import datavis
from aebs.fill.calc_mb79_kb_track_slots import NUM_OF_TRACKS, TRACK_STATUS, MOTION_STATE

init_params = dict( ('TRACK_%02d' %i, dict(id=i)) for i in xrange(NUM_OF_TRACKS) )


class View(iView):
  dep = 'calc_mb79_kb_track_slots@aebs.fill',
  TITLE_PAT = 'MB79 KB track #%d'

  def init(self, id):
    self.id = id
    return

  def check(self):
    tracks = self.modules.fill(self.dep[0])
    assert self.id in tracks, 'Track slot %d has no valid object' %self.id
    track = tracks[self.id]
    return track

  def view(self, track):
    t = track.time
    graph = datavis.cPlotNavigator(title=self.TITLE_PAT%self.id)

    axis_pos = graph.addAxis(ylabel="pos")
    axis_vel = graph.addAxis(ylabel="vel")

    yticks = { getattr(TRACK_STATUS, field) : field for field in TRACK_STATUS._fields }
    axis_tr_state = graph.addAxis(ylabel="tr. st.", yticks=yticks, ylim=(min(TRACK_STATUS)-0.5, max(TRACK_STATUS)+0.5))

    yticks = { getattr(MOTION_STATE, field) : field for field in MOTION_STATE._fields }
    axis_movstate = graph.addAxis(ylabel="mot. st.", xlabel="time [s]",yticks=yticks, ylim=(min(MOTION_STATE)-0.5, max(MOTION_STATE)+0.5))

    graph.addSignal2Axis(axis_pos,      'dx',         t, track.dx, unit='m')
    graph.addSignal2Axis(axis_pos,      'dy',         t, track.dy, unit='m')

    graph.addSignal2Axis(axis_vel,      'vx_abs',     t, track.vx_abs, unit='m/s')
    graph.addSignal2Axis(axis_vel,      'vy_abs',     t, track.vy_abs, unit='m/s')

    graph.addSignal2Axis(axis_tr_state, 'tracking state', t, track._TrackStatus)

    graph.addSignal2Axis(axis_movstate,   'motion state',    t, track._ObjMotionState)

    self.sync.addClient(graph)
    return
