# -*- dataeval: init -*-

import numpy as np

from interface import iParameter, iView
import datavis

# instantiation of module parameters
init_params = dict( ('TRACK_%03d' %i, dict(id=i)) for i in xrange(0,100) )

class cMyView(iView):
  dep = 'fill_flc25_cem_tpf_tracks@aebs.fill',

  def init(self, id):
    self.id = id
    return

  def check(self):
    modules = self.get_modules()
    tracks, signals = modules.fill("fill_flc25_cem_tpf_tracks@aebs.fill")
    assert self.id in tracks, 'Track %d is not recorded' %self.id
    track = tracks[self.id]
    return track

  def view(self, track):
    t = track.time
    pn = datavis.cPlotNavigator(title='FLC25 internal track #%d' %self.id)
    # dx
    ax = pn.addAxis(ylabel='dx', ylim = (-5.0, 100.0))
    pn.addSignal2Axis(ax, 'dx', t, track.dx, unit='m')
    pn.addSignal2Axis(ax, 'dy', t, track.dy, unit='m')
    # poe
    ax = pn.addAxis(ylabel='PoE', ylim = (-5.0, 100.0))
    pn.addSignal2Axis(ax, 'PoE', t, track.video_conf, unit='%')
    # vx
    ax = pn.addAxis(ylabel='vx')
    pn.addSignal2Axis(ax, 'vx', t, track.vx, unit='m/s')
    # Lane
    mapping = track.lane.mapping
    ax = pn.addAxis(ylabel='LaneAssoc', yticks=mapping, ylim=(min(mapping)-0.5, max(mapping)+0.5))
    pn.addSignal2Axis(ax, 'LaneAssoc', t, track.lane.join(), unit = '')
    # Lane
    mapping = track.obj_type.mapping
    ax = pn.addAxis(ylabel='Obj Type', yticks=mapping, ylim=(min(mapping)-0.5, max(mapping)+0.5))
    pn.addSignal2Axis(ax, 'Obj Type', t, track.obj_type.join(), unit = '')
  
    # register client
    sync = self.get_sync()
    sync.addClient(pn)
    return
