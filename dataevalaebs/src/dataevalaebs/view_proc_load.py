# -*- dataeval: init -*-

from interface.Interfaces import iView
from datavis.MatplotlibNavigator import MatplotlibNavigator

from search_ecu_performance import Search

class View(iView):
  def check(self):
    group = self.get_source().selectSignalGroup([Search.group])
    return group

  def fill(self, group):
    proc_load = group.get_value('proc_load')
    peak = proc_load.max()
    mean = proc_load.mean()
    return proc_load, peak, mean

  def view(self, proc_load, peak, mean):
    mn = MatplotlibNavigator()
    self.get_sync().addStaticClient(mn)
    mn.fig.suptitle(  'Processor load histogram: peak=%.2f [%%], avg=%.2f [%%]'
                    % (peak, mean))
    ax = mn.fig.add_subplot(1,1,1)
    ax.hist(proc_load, bins=20)
    ax.set_xlim(20.0, 120.0)
    ax.set_ylim(0.0, 4000.0)
    return
