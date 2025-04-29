# -*- dataeval: init -*-

"""
Plot basic driver activities and FCW outputs

FCW-relevant driver activities (pedal activation, steering etc.) and
FCW outputs (in AEBS1 messages) are shown.
"""

import numpy as np

import datavis
from interface import iView


mps2kph = lambda v: v*3.6

class View(iView):
		dep = {
				'aps_data': 'fill_acc_ped_stop@aebs.fill'
		}
		def check(self):
				commonTime, signals = self.modules.fill(self.dep["aps_data"])

				return commonTime, signals

		def view(self, commonTime, signals):
				"""

				:param commonTime:
				:param signals: Rescaled signals
								"acc_pedal_pos"
								"vehicle_speed"
								"obj_speed"
								"ego_long_state"
								"aps_system_state"
								"acc_active"
								"aps_object_id"
								"eba_quality"
								"ped_confidence"
				:return:
				"""


				pn = datavis.cPlotNavigator(title="ACC PED Stop plots")

				acc_pedal_ax = pn.addAxis(ylabel="accel. p. pos.", ylim=(-5.0, 105.0))
				# accel. pedal
				if 'acc_pedal_pos' in signals:
						value00, unit00 = signals["acc_pedal_pos"]["value"], signals["acc_pedal_pos"]["unit"]
						pn.addSignal2Axis(acc_pedal_ax, "accel. p. pos.", commonTime, value00, unit=unit00)

				vehicle_speed_ax = pn.addAxis(ylabel="vehicle speed  [km/h]", ylim=(0, 30.0))
				# Vehicle Speed
				if 'vehicle_speed' in signals and 'obj_speed' in signals:
						vehicle_speed = signals["vehicle_speed"]["value"]
						obj_speed, unit02 = signals["obj_speed"]["value"], signals["obj_speed"]["unit"]

						obst_speed = vehicle_speed + obj_speed

						unit02 = "km/h"
						pn.addSignal2Axis(vehicle_speed_ax, "obst speed [km/h]", commonTime, mps2kph(obst_speed), unit=unit02)

				long_states_mapping = {0: "STANDSTILL_SECURED", 1: "STANDSTILL_UNSECURED", 2: "BACKWARD",
															 3: "INTENTION_TO_DRIVE_FWD", 4: "FORWARD", 5: "NEUTRAL_ROLLING", 6: "ERROR",
															 7: "NA"}  # 254, 255
				ego_long_state_ax = pn.addAxis(ylabel='logitudinal state', yticks=long_states_mapping,
												ylim=(min(long_states_mapping) - 0.5, max(long_states_mapping) + 0.5))
				# Logitudinal state
				if "ego_long_state" in signals:
						ego_long_state = signals["ego_long_state"]["value"]
						ego_long_state[ego_long_state == 254] = 6
						ego_long_state[ego_long_state == 255] = 7
						pn.addSignal2Axis(ego_long_state_ax, 'longitudinal state', commonTime, ego_long_state)

				aps_system_states_mapping = {0: "IS_NOT_READY", 1: "TEMP_NOT_AVAILABLE", 2: "IS_DEACTIVATED_BY_DRIVER", 3: "IS_READY",
															 4: "DRIVER_OVERRIDES_SYSTEM", 6: "COLLISION_WARNING_WITH_BRAKING", 7: "ERROR_INDICATION",
															 8: "NOT_AVAILABLE"}

				aps_sys_ax = pn.addAxis(ylabel='system state', yticks=aps_system_states_mapping,
												ylim=(min(aps_system_states_mapping) - 0.5, max(aps_system_states_mapping) + 0.5))
				# Sytem state
				if "aps_system_state" in signals:
						# ax.yaxis.set_label_position("right")
						# ax.yaxis.tick_right()
						system_state = signals["aps_system_state"]["value"]

						system_state[system_state == 14] = 6
						system_state[system_state == 15] = 7
						pn.addSignal2Axis(aps_sys_ax, 'system state', commonTime, system_state)
				acc_active_mapping = {0: "NOT_ACTIVE", 1: "ACTIVE"}

				aps_twinax = pn.addTwinAxis(aps_sys_ax, ylabel='acc status', yticks=acc_active_mapping, ylim=(min(acc_active_mapping) - 0.5, max(acc_active_mapping) + 0.5), color='black')

				if "acc_active" in signals:
						acc_active, unit02 = signals["acc_active"]["value"], signals["acc_active"]["unit"]
						pn.addSignal2Axis(aps_twinax, 'acc active', commonTime, acc_active, unit=unit02)

				ped_eba_ax = pn.addAxis(ylabel="ped confidence", ylim=(0.0, 10.0))

				if 'ped_confidence' in signals:
						value00, unit00 = signals["ped_confidence"]["value"], signals["ped_confidence"]["unit"]
						pn.addSignal2Axis(ped_eba_ax, "ped_confidence", commonTime, value00, unit=unit00, color="blue")
				if 'eba_quality' in signals:
						twinax = pn.addTwinAxis(ped_eba_ax, ylabel='eba quality', color='black', ylim=(-5.0, 100.0))

						value00, unit00 = signals["eba_quality"]["value"], signals["eba_quality"]["unit"]
						pn.addSignal2Axis(twinax, "eba_quality", commonTime, value00, unit=unit00, color="red")

				self.sync.addClient(pn)
				return

		def extend_aebs_state_axis(self, pn, ax):
				return

