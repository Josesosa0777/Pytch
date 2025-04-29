# -*- dataeval: init -*-

"Plot attributes of tr0 radar & asso'd camera tracks"

import numpy as np

from interface import iView
import datavis
from aebs.fill.metatrack import LinkedObject

class MyView(iView):
  dep = 'fill_flr20_msg_tracks@aebs.fill', 'fill_flc20_raw_tracks@aebs.fill'
  
  def fill(self):
    radar = self.modules.fill(self.dep[0])[0]
    t = radar.time
    cameras = self.modules.fill(self.dep[1]).rescale(t)
    camera = LinkedObject(cameras, radar.video_asso_masks)
    return t, radar, camera
  
  def view(self, t, radar, camera):
    pn = datavis.cPlotNavigator(title="Radar (tr0) and asso'd camera tracks")
    # id
    ax = pn.addAxis(ylabel='id')
    pn.addSignal2Axis(ax, 'radar message', t, radar.id)
    pn.addSignal2Axis(ax, 'camera id', t, camera.id)
    # position
    ax = pn.addAxis(ylabel='pos')
    pn.addSignal2Axis(ax, 'radar dx', t, radar.dx, unit='m')
    pn.addSignal2Axis(ax, 'camera dx', t, camera.dx, unit='m')
    # angle
    ax = pn.addAxis(ylabel='angle')
    pn.addSignal2Axis(ax, 'radar angle', t, np.rad2deg(radar.angle), unit='deg')
    pn.addSignal2Axis(ax, 'camera angle', t, np.rad2deg(camera.angle), unit='deg')
    # angle diff
    ax = pn.addAxis(ylabel='angle diff')
    pn.addSignal2Axis(ax, 'angle diff', t, np.rad2deg(radar.angle-camera.angle), unit='deg')
    # register client
    self.sync.addClient(pn)
    return
