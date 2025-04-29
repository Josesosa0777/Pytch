# -*- dataeval: init -*-

from interface import iView
import datavis
from search_flr20_obj_fus_availability import sgs

video_sgs  = [ {"SensorStatus": ("Video_Data_General_B", "SensorStatus"),}, ]

class View(iView):
  def check(self):
    source = self.get_source()
    radar_group = source.selectSignalGroup(sgs)
    video_group = source.selectSignalGroup(video_sgs)
    return radar_group, video_group

  def view(self, radar_group, video_group):
    pn = datavis.cPlotNavigator(title='Object fusion availability')
    ax = pn.addAxis()
    for alias in radar_group:
      self.plot(pn, ax, radar_group, alias)
    rule = video_group.get_conversion_rule("SensorStatus")
    ax = pn.addAxis(yticks=rule)
    self.plot(pn, ax, video_group, "SensorStatus")
    # register client
    sync = self.get_sync()
    sync.addClient(pn)
    return

  def plot(self, pn, ax, group, alias):
    t,v = group.get_signal(alias)
    pn.addSignal2Axis(ax, alias, t, v)
    return
