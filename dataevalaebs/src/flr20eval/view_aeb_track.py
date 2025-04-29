# -*- dataeval: init -*-

"""
Plots some attributes of the FLR21 CW object (collision warning candidate).
"""

from interface import iView
import datavis

class MyView(iView):
  dep = 'fill_flr20_aeb_track@aebs.fill',

  def check(self):
    modules = self.get_modules()
    track = modules.fill("fill_flr20_aeb_track@aebs.fill")
    return track

  def view(self, track):
    pn = datavis.cPlotNavigator(title='FLR21 AEB track')
    t = track.time
    # id
    ax = pn.addAxis(ylabel='id')
    pn.addSignal2Axis(ax, 'track id', t, track.id)
    pn.addSignal2Axis(ax, 'target id', t, track.refl_id, alpha=.3)
    twinax = pn.addTwinAxis(ax, color='r')
    pn.addSignal2Axis(twinax, 'video id',  t, track.video_id, alpha=.5)
    # flags
    yticks = dict( (k,v) for k,v in zip(xrange(6),[0,1]*3) )
    ax = pn.addAxis(ylabel='flags', yticks=yticks)
    pn.addSignal2Axis(ax, 'fused',     t, track.fused, offset=4, displayscaled=False)
    pn.addSignal2Axis(ax, 'measured',  t, track.tr_state.measured, offset=2, displayscaled=False)
    pn.addSignal2Axis(ax, 'secondary', t, track.secondary)
    # mov_state
    ax = pn.addAxis(ylabel='mov_st', yticks=track.mov_state.mapping)
    pn.addSignal2Axis(ax, 'mov_st', t, track.mov_state.join())
    # position
    ax = pn.addAxis(ylabel='pos')
    pn.addSignal2Axis(ax, 'dx', t, track.dx, unit='m')
    twinax = pn.addTwinAxis(ax, color='g')
    pn.addSignal2Axis(twinax, 'dy', t, track.dy, unit='m')
    pn.addSignal2Axis(twinax, 'dy corr', t, track.dy_corr, unit='m')
    # speed & acceleration
    ax = pn.addAxis(ylabel='rel. speed\nand accel.')
    pn.addSignal2Axis(ax, 'vx', t, track.vx, unit='m/s')
    twinax = pn.addTwinAxis(ax, color='g')
    pn.addSignal2Axis(twinax, 'ax', t, track.ax, unit='m/s^2')
    # conf
    ax = pn.addAxis(ylabel='conf')
    pn.addSignal2Axis(ax, 'radar conf', t, track.radar_conf)
    pn.addSignal2Axis(ax, 'video conf', t, track.video_conf)
    # register client
    sync = self.get_sync()
    sync.addClient(pn)
    return
