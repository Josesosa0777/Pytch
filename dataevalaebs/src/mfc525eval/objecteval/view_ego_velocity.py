# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
		def check(self):
				sgs = [
							{
								"EBC2_FrontAxleSpeed": ("EBC2_0B_s0B", "EBC2_FrontAxleSpeed_0B"),
								"VDC2_SteerWhlAngle": ("VDC2_0B_s0B","VDC2_SteerWhlAngle_0B"),
								"AOA_ACC_object_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_acc_object_id"),
								"AOA_ACC_object_dx": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_acc_object_dx"),

							},
							]
				# select signals
				group = self.source.selectLazySignalGroup(sgs)
				# give warning for not available signals
				for alias in sgs[0]:
						if alias not in group:
								self.logger.warning("Signal for '%s' not available" % alias)
				return group

		def view(self, group):
				pn = datavis.cPlotNavigator(title="Ego FrontAxleSpeed")

				ax = pn.addAxis(ylabel="EBC2_FrontAxleSpeed", ylim=(-5.0, 105.0))
				# EBC2 speed
				if 'EBC2_FrontAxleSpeed' in group:
						time00, value00, unit00 = group.get_signal_with_unit("EBC2_FrontAxleSpeed")
						pn.addSignal2Axis(ax, "EBC2_FrontAxleSpeed", time00, value00, unit=unit00)

				ax = pn.addAxis(ylabel="VDC2_SteerWhlAngle")
				# VDC2 Steering Wheel Angle
				if 'VDC2_SteerWhlAngle' in group:
						time00, value00, unit00 = group.get_signal_with_unit("VDC2_SteerWhlAngle")
						pn.addSignal2Axis(ax, "VDC2_SteerWhlAngle", time00, value00, unit=unit00)

				ax = pn.addAxis(ylabel="AOA_ACC_object_id")
				# VDC2 Steering Wheel Angle
				if 'AOA_ACC_object_id' in group:
						time00, value00, unit00 = group.get_signal_with_unit("AOA_ACC_object_id")
						pn.addSignal2Axis(ax, "AOA_ACC_object_id", time00, value00, unit=unit00)
				
				ax = pn.addAxis(ylabel="AOA_ACC_object_dx")
				# VDC2 Steering Wheel Angle
				if 'AOA_ACC_object_dx' in group:
						time00, value00, unit00 = group.get_signal_with_unit("AOA_ACC_object_dx")
						pn.addSignal2Axis(ax, "AOA_ACC_object_dx", time00, value00, unit=unit00)
				
				self.sync.addClient(pn)
				return

		def extend_aebs_state_axis(self, pn, ax):
				return
