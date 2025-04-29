# -*- dataeval: init -*-

import numpy as np

from interface import iParameter, iView
import datavis

# instantiation of module parameters
init_params = dict( ('TRACK_%03d' %i, dict(id=i)) for i in xrange(1,128) )

class cMyView(iView):
  dep = 'fill_flc20_raw_tracks@aebs.fill',

  def init(self, id):
    self.id = id
    return

  def check(self):
    modules = self.get_modules()
    tracks = modules.fill("fill_flc20_raw_tracks@aebs.fill")
    assert self.id in tracks, 'Track %d is not recorded' %self.id
    track = tracks[self.id]
    return track

  def view(self, track):
    t = track.time
    pn = datavis.cPlotNavigator(title='FLC20 internal track #%d' %self.id)
    # tracking state
    ax = pn.addAxis(ylabel='tracking')
    pn.addSignal2Axis(ax, 'valid',       t, track.tr_state.valid)
    pn.addSignal2Axis(ax, 'measured',    t, track.tr_state.measured)
    pn.addSignal2Axis(ax, 'historical',  t, track.tr_state.hist)
    # dx
    ax = pn.addAxis(ylabel='dx')
    pn.addSignal2Axis(ax, 'dx', t, track.dx, unit='m')
    # dy
    ax = pn.addAxis(ylabel='dy')
    pn.addSignal2Axis(ax, 'dy', t, track.dy, unit='m')
    # vx
    ax = pn.addAxis(ylabel='vx')
    pn.addSignal2Axis(ax, 'vx', t, track.vx, unit='m/s')
    # angle
    ax = pn.addAxis(ylabel='angle')
    pn.addSignal2Axis(ax, 'left',  t, np.rad2deg(track.angle_left),  unit='deg')
    pn.addSignal2Axis(ax, 'right', t, np.rad2deg(track.angle_right), unit='deg')
    # register client
    sync = self.get_sync()
    sync.addClient(pn)
    return
