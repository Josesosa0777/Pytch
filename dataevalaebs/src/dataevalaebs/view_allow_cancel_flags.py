# -*- dataeval: init -*-

from interface.Interfaces import iView
from datavis.PlotNavigator import cPlotNavigator

init_params = {
  'get': dict(dep='get_trw_allow_flags'),
  'sim': dict(dep='sim_allow_flags@trw'),
}

class View(iView):
  def init(self, dep):
    self.dep = dep,
    return

  def view(self):
    sync = self.get_sync()
    pn = cPlotNavigator(title="%s allow cancel flags" % self.dep)
    sync.addClient(pn)

    group = self.get_modules().fill(self.dep[0])
    values = group.get_all_values()
    time = group.select_time_scale()
    for name in sorted(values):
      ax = pn.addAxis()
      pn.addSignal2Axis(ax, name, time, values[name])
    return

