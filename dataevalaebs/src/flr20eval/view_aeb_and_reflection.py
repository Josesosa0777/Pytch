# -*- dataeval: init -*-

"""
Show CW track & target attributes simultaneously
"""

import numpy as np

from interface import iView
import datavis
from aebs.fill.metatrack import LinkedObject

class View(iView):
  dep = 'fill_flr20_aeb_track@aebs.fill', 'fill_flr20_raw_targets@aebs.fill',
  
  def view(self):
    aeb = self.modules.fill(self.dep[0])
    t = aeb.time
    targets = self.modules.fill(self.dep[1])#.rescale(t)
    refl = LinkedObject(targets, aeb.refl_asso_masks)
    
    # create PlotNavigator client
    base_title = 'FLR21 CW track and targets'
    title = "%s\n%s" % (base_title, self.source.getBaseName())
    pn = datavis.cPlotNavigator(title=title, subplotGeom=(1, 3))
    tar_sty = dict(color='r', marker='.', linewidth=0.0)
    tax_sty = dict(color='0.75', marker='.', linewidth=0.0)
    # quick hack to store window position independently from the measurement
    pn.createWindowId = lambda x,title=None: base_title
    pn.getWindowId = lambda: base_title
    pn._windowId = pn.createWindowId(None)
    # dx
    ax = pn.addAxis(rowNr=1, colNr=1, ylabel='distance [m]')
    for i, tax in targets.iteritems():
      pn.addSignal2Axis(ax, 'dx - target (%d)' % i, t, tax.dx, **tax_sty)
    pn.addSignal2Axis(ax, 'dx - target (asso\'d)', t, refl.dx, **tar_sty)
    pn.addSignal2Axis(ax, 'dx - CW', t, aeb.dx, color='b')
    # vx
    ax = pn.addAxis(rowNr=1, colNr=2, ylabel='rel. speed [m/s]')
    for i, tax in targets.iteritems():
      pn.addSignal2Axis(ax, 'vx - target (%d)' % i, t, tax.vx, **tax_sty)
    pn.addSignal2Axis(ax, 'vx - target (asso\'d)', t, refl.vx, **tar_sty)
    pn.addSignal2Axis(ax, 'vx - CW', t, aeb.vx, color='b')
    ax.set_xlabel('time [s]')
    # angle
    ax = pn.addAxis(rowNr=1, colNr=3, ylabel='angle [deg]')
    for i, tax in targets.iteritems():
      pn.addSignal2Axis(ax, 'angle - target (%d)' % i, t, np.rad2deg(tax.angle), **tax_sty)
    pn.addSignal2Axis(ax, 'angle - target (asso\'d)', t, np.rad2deg(refl.angle), **tar_sty)
    pn.addSignal2Axis(ax, 'angle - CW', t, np.rad2deg(aeb.angle), color='b')
    # # dy
    # ax = pn.addAxis(rowNr=1, colNr=3, ylabel='dist.')
    # for i, tax in targets.iteritems():
      # pn.addSignal2Axis(ax, 'dy - target (%d)' % i, t, tax.dy, unit='m', **tax_sty)
    # pn.addSignal2Axis(ax, 'dy - target (asso\'d)', t, refl.dy, unit='m', **tar_sty)
    # pn.addSignal2Axis(ax, 'dy - CW', t, aeb.dy,  unit='m', color='b') # note: fused lateral position
    # register client
    self.sync.addClient(pn)
    return
