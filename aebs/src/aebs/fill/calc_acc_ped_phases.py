# -*- dataeval: init -*-
import interface
import numpy

from primitives.aebs import AebsPhases

init_params = {
		'acc_ped_stop': dict(
						# add signals for paebs events
						sgn_group = [  # PAEBS
								{
										"PAEBSState"           : ("Rte_SWC_OutputManager_RPort_aps_om_hmi_DEP_aps_om_hmi_Buf",
																							"ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_aps_om_hmi_DEP_aps_om_hmi_Buf_aps_system_state"),
										"CollisionWarningLevel": ("Rte_SWC_OutputManager_RPort_aps_om_hmi_DEP_aps_om_hmi_Buf",
																							"ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_aps_om_hmi_DEP_aps_om_hmi_Buf_aps_warning_level"),

								},

						]),

}


class Calc(interface.iCalc):
		"""
		{ IS_NOT_READY=0, TEMP_NOT_AVAILABLE=1, IS_DEACTIVATED_BY_DRIVER=2, IS_READY=3, DRIVER_OVERRIDES_SYSTEM=4,
		COLLISION_WARNING_WITH_BRAKING=6, ERROR_INDICATION=14, NOT_AVAILABLE=15}
		"""
		COLLISION_WARNING_WITH_BRAKING = 6

		def init(self, sgn_group):
				self.sgn_group = sgn_group
				self.group = None  # used by user scripts
				return

		def check(self):
				self.group = self.source.selectLazySignalGroup(self.sgn_group).items()
				group = self.source.selectSignalGroup(self.sgn_group)
				time, status = group.get_signal('PAEBSState')
				level = group.get_value('CollisionWarningLevel', ScaleTime = time)
				return time, status, level

		def fill(self, time, status, level):
				acc_ped_stop_warning = status == self.COLLISION_WARNING_WITH_BRAKING
				return time, acc_ped_stop_warning


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\corp.knorr-bremse.com\str\Measure\DAS\ConvertedMeas\FER\pAEBS\2021-05-13\Bendix__2021-05-13_11-21-49.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		RoadHypothesisObject = manager_modules.calc('calc_acc_ped_phases-acc_ped_stop@aebs.fill', manager)
		print(RoadHypothesisObject)
