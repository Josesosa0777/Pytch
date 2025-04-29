# -*- dataeval: init -*-
import numpy

from interface.Interfaces import iView
from datavis.MatplotlibNavigator import MatplotlibNavigator

from search_ecu_performance import Search

class View(iView):
  def check(self):
    group = {
      'no_tracks': ('General_radar_status', 'number_of_tracks'),
    }
    group.update(Search.group)
    group = self.get_source().selectSignalGroup([group])
    return group

  def view(self, group):
    time, proc_load = group.get_signal('proc_load')
    no_tracks = group.get_value('no_tracks', ScaleTime=time)

    mn = MatplotlibNavigator()
    self.get_sync().addStaticClient(mn)
    mn.fig.suptitle('Number of tracks per processor load')
    ax = mn.fig.add_subplot(1,1,1, ylabel='processor load', xlabel='number of tracks')
    ax.plot(no_tracks, proc_load, 'b.')
    ax.set_xlim(0.0, 20.0)
    ax.set_ylim(20.0, 120.0)
    return

