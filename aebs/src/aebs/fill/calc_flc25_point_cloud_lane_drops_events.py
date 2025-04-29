# -*- dataeval: init -*-

from interface import iCalc

sgs = [
		{
				'egoLaneIndex': ('CEM_FDP_KB_M_p_RmfOutputIfMeas',
												 'MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_egoLaneIndex'),
		},
		{
				'egoLaneIndex': ('MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas',
												 'MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_egoLaneIndex'),
		},

]


class cFill(iCalc):
		dep = ('calc_common_time-flc25',)

		def check(self):
				source = self.get_source()
				group = source.selectSignalGroup(sgs)
				return group

		def fill(self, group):
				time = self.modules.fill('calc_common_time-flc25')
				rescale_kwargs = {'ScaleTime': time}
				_, ego_lane_index, unit = group.get_signal_with_unit('egoLaneIndex', **rescale_kwargs)
				lane_drops = (ego_lane_index == 5)
				return time, lane_drops


# if __name__ == '__main__':
# 		from config.Config import init_dataeval
#
# 		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\mfc525_interface" \
# 								r"\measurements\2020_08_27\NY00__2020-08-27_08-36-16.mat"
# 		config, manager, manager_modules = init_dataeval(['-m', meas_path])
# 		data = manager_modules.calc('calc_flc25_point_cloud_lane_drops_events@aebs.fill', manager)
# 		print data
