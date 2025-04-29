# -*- dataeval: init -*-

import sys

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
    return detdata['speedred_kph'], detdata['vx_kph']

  def view(self, speedred_kph, vx_kph):
    title = "Maximum possible speed reduction vs. relative approaching speed"
    nav = datavis.MatplotlibNavigator(title=title)
    nav.setUserWindowTitle(title)
    ax = nav.fig.add_subplot(111)
    speedkph_bins = np.arange(0.0, 100.0+1.0, 10.0)
    H, xedges, yedges = histogram2d(
      -vx_kph, speedred_kph, bins=(speedkph_bins, speedkph_bins),
      continuous=True, normed=True, cond_givenaxis='x', toplotframe=True)
    extent = (xedges[0], xedges[-1], yedges[0], yedges[-1])
    im = ax.imshow(H, extent=extent, cmap='OrRd')
    ax.plot(-vx_kph, speedred_kph, 'bx')
    ax.set_xlabel("relative speed [km/h]")
    ax.set_ylabel("speed reduction [km/h]")
    limits = [speedkph_bins[0], speedkph_bins[-1]]
    ax.set_xlim(limits)
    ax.set_ylim(limits)
    if np.any(-vx_kph < limits[0]) or np.any(-vx_kph > limits[1]) or \
       np.any(speedred_kph < limits[0]) or np.any(speedred_kph > limits[1]):
      print >> sys.stderr, "Warning: data outside the axes limits"
    nav.fig.colorbar(im)
    self.get_sync().addStaticClient(nav)
    return
