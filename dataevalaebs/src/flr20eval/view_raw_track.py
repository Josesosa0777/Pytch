# -*- dataeval: init -*-

"""
Plots some attributes of the selected FLR21 internal object.
The object can be selected using the module parameter, which corresponds to the
object's internal identifier (not CAN message number).
"""

from interface import iView
import datavis

# instantiation of module parameters
init_params = dict( ('TRACK_%02d' %i, dict(id=i)) for i in xrange(21) )

class View(iView):
  dep = 'fill_flr20_raw_tracks@aebs.fill',

  TITLE_PAT = 'FLR21 internal track #%d'

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
    pn = datavis.cPlotNavigator(title=self.TITLE_PAT %self.id)
    # flags
    yticks = dict( (k,v) for k,v in zip(xrange(6),[0,1]*3) )
    ax = pn.addAxis(ylabel='flags', yticks=yticks)
    pn.addSignal2Axis(ax, 'fused',    t, track.fused,             offset=4, displayscaled=False)
    pn.addSignal2Axis(ax, 'measured', t, track.tr_state.measured, offset=2, displayscaled=False)
    pn.addSignal2Axis(ax, 'aeb',      t, track.aeb_track)
    # dx
    ax = pn.addAxis()
    pn.addSignal2Axis(ax, 'dx', t, track.dx, unit='m')
    ax = pn.addAxis()
    pn.addSignal2Axis(ax, 'dy', t, track.dy, unit='m')
    pn.addSignal2Axis(ax, 'dy corr', t, track.dy_corr, unit='m')
    ax = pn.addAxis()
    pn.addSignal2Axis(ax, 'vx', t, track.vx, unit='m/s')
    # moving state
    ax = pn.addAxis(ylabel='mov_st', yticks={0:0, 1:1})
    pn.addSignal2Axis(ax, 'stationary', t, track.mov_state.stat)
    pn.addSignal2Axis(ax, 'moving',     t, track.mov_state.moving)
    pn.addSignal2Axis(ax, 'stopped',    t, track.mov_state.stopped)
    # register client
    self.sync.addClient(pn)
    return
