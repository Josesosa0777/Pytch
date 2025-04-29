# -*- dataeval: init -*-

import datavis
from interface import iView


class View(iView):
		dep = 'calc_lanes-flc25@aebs.fill', 'calc_lanes_flc25_abd@aebs.fill'

		def fill(self):
				CAN_signals = self.modules.fill(self.dep[0])
				t = CAN_signals.time
				ABDLaneData_Signals = self.modules.fill(self.dep[1]).rescale(t)
				return t, CAN_signals, ABDLaneData_Signals

		def view(self, t, CAN_signals, ABDLaneData_Signals):
				pn = datavis.cPlotNavigator(title = "Conti Polynomial vs CAN signal")
				# id
				ax = pn.addAxis(ylabel = 'left-left lane c0')
				pn.addSignal2Axis(ax, 'ABD Position_Left2', t, ABDLaneData_Signals.left_left_line.c0)
				pn.addSignal2Axis(ax, 'CAN Position_Left2', t, CAN_signals.left_left_line.c0)

				ax = pn.addAxis(ylabel = 'left-left lane c1')
				pn.addSignal2Axis(ax, 'ABD Heading_Angle_Left2', t, ABDLaneData_Signals.left_left_line.c1)
				pn.addSignal2Axis(ax, 'CAN Heading_Angle_Left2', t, CAN_signals.left_left_line.c1)

				ax = pn.addAxis(ylabel = 'left-left lane c2')
				pn.addSignal2Axis(ax, 'ABD Curvature_Left2', t, ABDLaneData_Signals.left_left_line.c2)
				pn.addSignal2Axis(ax, 'CAN Curvature_Left2', t, CAN_signals.left_left_line.c2)

				ax = pn.addAxis(ylabel = 'left-left lane c3')
				pn.addSignal2Axis(ax, 'ABD Curvature_Derivative_Left2', t, ABDLaneData_Signals.left_left_line.c3)
				pn.addSignal2Axis(ax, 'CAN Curvature_Derivative_Left2', t, CAN_signals.left_left_line.c3)

				ax = pn.addAxis(ylabel = 'view range')
				pn.addSignal2Axis(ax, 'ABD View_Range_Left2', t, ABDLaneData_Signals.left_left_line.view_range)
				pn.addSignal2Axis(ax, 'CAN View_Range_Left2', t, CAN_signals.left_left_line.view_range)

				# # register client
				self.sync.addClient(pn)
				return
