# -*- dataeval: init -*-

import numpy as np

import datavis
import calc_fwdvehicledet_quantities
from measparser.signalproc import histogram2d
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
    return detdata['egospeed_kph'], detdata['dx_stable']

  def view(self, egospeed_kph, dx_stable):
    title = "Stable detection distance vs. approaching speed"
    nav = datavis.MatplotlibNavigator(title=title)
    nav.setUserWindowTitle(title)
    ax = nav.fig.add_subplot(111)
    speedkph_bins = np.arange(0.0, 100.0+1.0, 10.0)
    dxstable_bins = np.arange(0.0, 100.0+1.0, 10.0)
    H, xedges, yedges = histogram2d(
      egospeed_kph, dx_stable, bins=(speedkph_bins, dxstable_bins),
      continuous=True, normed=True, cond_givenaxis='x', toplotframe=True)
    extent = (xedges[0], xedges[-1], yedges[0], yedges[-1])
    im = ax.imshow(H, extent=extent, cmap='OrRd')
    ax.plot(egospeed_kph, dx_stable, 'bx')
    ax.set_xlabel("ego speed [km/h]")
    ax.set_ylabel("stable detection distance [m]")
    nav.fig.colorbar(im)
    self.get_sync().addStaticClient(nav)
    return
