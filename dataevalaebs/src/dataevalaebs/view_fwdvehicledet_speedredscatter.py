# -*- dataeval: init -*-

import numpy as np

import datavis
import calc_fwdvehicledet_quantities
from interface.modules import ModuleName

init_params = calc_fwdvehicledet_quantities.init_params

class View(calc_fwdvehicledet_quantities.ViewBase):
  def init(self, sensor):
    calc_fwdvehicledet_quantities.ViewBase.init(self, sensor)
    self.dep = (ModuleName.extend_prj_name('calc_fwdvehicledet_quantities-%s@dataevalaebs' \
                % self.sensor.productname, self._prj_name), )
    return

  def check(self):
    return

  def fill(self):
    detdata = self.get_modules().fill(self.dep[0])
    return detdata['speedred_kph'], detdata['vx_kph']

  def view(self, speedred_kph, vx_kph):
    title = "Maximum possible speed reduction"
    nav = datavis.MatplotlibNavigator(title=title)
    nav.setUserWindowTitle(title)
    ax = nav.fig.add_subplot(111)
    apprnumbers = np.arange(speedred_kph.size) + 1
    ax.scatter(apprnumbers, -vx_kph, color='k', label="ideal system")
    ax.scatter(apprnumbers, speedred_kph, color='r', label=self.sensor.productname)
    ax.axhline(10.0, color='k', linestyle='-.')
    ax.axhline(20.0, color='k', linestyle='--')
    ax.set_xlim((0, apprnumbers[-1]+1))
    ax.set_ylim((-1.0, 120.0))
    ax.set_xlabel("# approach")
    ax.set_ylabel("speed reduction [km/h]")
    ax.legend(loc=9, ncol=2, mode="expand", prop={'size':12})
    ax.grid()
    self.get_sync().addStaticClient(nav)
    return
