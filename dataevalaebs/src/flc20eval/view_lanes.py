# -*- dataeval: init -*-

"""
Plots the left and right lines' properties (curve coefficients and view range),
detected by FLC20.
"""

import datavis
import interface

class View(interface.iView):
  dep = ('calc_flc20_lanes@aebs.fill',)

  def fill(self):
    lanes = self.get_modules().fill('calc_flc20_lanes@aebs.fill')
    return lanes

  def view(self, lanes):
    pn = datavis.cPlotNavigator(title="Lane information", subplotGeom=(5,2))

    time = lanes.time

    left = lanes.left_line
    ax = pn.addAxis(rowNr=1, colNr=1)
    pn.addSignal2Axis(ax, "View_Range_L", time, left.view_range, unit="m")
    ax = pn.addAxis(rowNr=2, colNr=1)
    pn.addSignal2Axis(ax, "C0_L", time, left.c0, unit="-")
    ax = pn.addAxis(rowNr=3, colNr=1)
    pn.addSignal2Axis(ax, "C1_L", time, left.c1, unit="-")
    ax = pn.addAxis(rowNr=4, colNr=1)
    pn.addSignal2Axis(ax, "C2_L", time, left.c2, unit="-")
    ax = pn.addAxis(rowNr=5, colNr=1)
    pn.addSignal2Axis(ax, "C3_L", time, left.c3, unit="-")

    right = lanes.right_line
    ax = pn.addAxis(rowNr=1, colNr=2)
    pn.addSignal2Axis(ax, "View_Range_R", time, right.view_range, unit="m")
    ax = pn.addAxis(rowNr=2, colNr=2)
    pn.addSignal2Axis(ax, "C0_R", time, right.c0, unit="-")
    ax = pn.addAxis(rowNr=3, colNr=2)
    pn.addSignal2Axis(ax, "C1_R", time, right.c1, unit="-")
    ax = pn.addAxis(rowNr=4, colNr=2)
    pn.addSignal2Axis(ax, "C2_R", time, right.c2, unit="-")
    ax = pn.addAxis(rowNr=5, colNr=2)
    pn.addSignal2Axis(ax, "C3_R", time, right.c3, unit="-")

    self.get_sync().addClient(pn)
    return
