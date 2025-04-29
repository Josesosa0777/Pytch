# -*- dataeval: init -*-

"""
Plots some attributes of the selected FLC20 object.
The object can be selected using the module parameter, which corresponds to the
object's internal identifier (not CAN message number).
"""

from interface import iView
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
    ax = pn.addAxis(ylabel='position')
    pn.addSignal2Axis(ax, 'dx', t, track.dx, unit='m')
    pn.addSignal2Axis(ax, 'dy', t, track.dy, unit='m')
    # angle
    ax = pn.addAxis(ylabel='angle')
    pn.addSignal2Axis(ax, 'left',  t, track.angle_left, unit='deg')
    pn.addSignal2Axis(ax, 'right', t, track.angle_right, unit='deg')
    # register client
    sync = self.get_sync()
    sync.addClient(pn)
    return
