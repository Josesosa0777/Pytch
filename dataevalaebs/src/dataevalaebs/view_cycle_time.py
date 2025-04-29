# -*- dataeval: init -*-
import numpy

from interface.Interfaces import iView
from datavis.MatplotlibNavigator import MatplotlibNavigator

from search_ecu_performance import Search

class View(iView):
  def check(self):
    group = self.get_source().selectSignalGroup([Search.group])
    return group

  def fill(self, group):
    time, proc_load = group.get_signal('proc_load')
    dt = numpy.diff(time) * 1000

    peak = dt.max()
    mean = dt.mean()
    return dt, peak, mean

  def view(self, dt, peak, mean):
    mn = MatplotlibNavigator()
    self.get_sync().addStaticClient(mn)
    mn.fig.suptitle(  'Cycle time histogram: peak=%.2f [ms], avg=%.2f [ms]'
                    % (peak, mean))
    ax = mn.fig.add_subplot(1,1,1)
    ax.hist(dt, bins=20)
    ax.set_xlim(30.0, 50.0)
    ax.set_ylim(0.0, 4000.0)
    return

