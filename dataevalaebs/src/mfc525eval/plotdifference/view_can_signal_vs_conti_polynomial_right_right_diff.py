# -*- dataeval: init -*-

import datavis
from interface import iView


class View(iView):
		dep = 'calc_lanes-flc25@aebs.fill', 'calc_lanes_flc25_abd@aebs.fill'

		def fill(self):
				CAN_signals = self.modules.fill(self.dep[0])
				t = CAN_signals.time
				ABDLaneData_signals = self.modules.fill(self.dep[1]).rescale(t)
				return t, CAN_signals, ABDLaneData_signals

		def view(self, t, CAN_signals, ABDLaneData_signals):
				pn = datavis.cPlotNavigator(title = "Conti Polynomial vs CAN signal - Difference")
				# id
				ax = pn.addAxis(ylabel = 'right-right lane c0')
				diff_0 = ABDLaneData_signals.right_right_line.a0 - CAN_signals.right_right_line.c0
				pn.addSignal2Axis(ax, 'diff_c0', t, diff_0)

				ax = pn.addAxis(ylabel = 'right-right lane c1')
				diff_1 = ABDLaneData_signals.right_right_line.c1 - CAN_signals.right_right_line.c1
				pn.addSignal2Axis(ax, 'diff_c1', t, diff_1)

				ax = pn.addAxis(ylabel = 'right-right lane c2')
				diff_2 = ABDLaneData_signals.right_right_line.c2 - CAN_signals.right_right_line.c2
				pn.addSignal2Axis(ax, 'diff_c2', t, diff_2)

				ax = pn.addAxis(ylabel = 'right-right lane c3')
				diff_3 = ABDLaneData_signals.right_right_line.c3 - CAN_signals.right_right_line.c3
				pn.addSignal2Axis(ax, 'diff_c3', t, diff_3)

				ax = pn.addAxis(ylabel = 'view range')
				diff_view_range = ABDLaneData_signals.right_right_line.view_range - CAN_signals.right_right_line.view_range
				pn.addSignal2Axis(ax, 'diff_view_range', t, diff_view_range)

				# # register client
				self.sync.addClient(pn)
				return
