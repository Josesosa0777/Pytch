# -*- dataeval: init -*-

import numpy as np
from interface import iCalc


class cFill(iCalc):
		dep = ('fill_flc25_polylines@aebs.fill',)

		def check(self):
				all_lines, common_time = self.modules.fill('fill_flc25_polylines@aebs.fill')
				return all_lines, common_time

		def fill(self, all_lines, common_time):
				ego_leftLine_ego_rightLine_merge = np.zeros(len(common_time), dtype = bool)
				ego_leftLine_ego_centerLine_merge = np.zeros(len(common_time), dtype = bool)
				ego_rightLine_ego_centerLine_merge = np.zeros(len(common_time), dtype = bool)
				for index_sample in range(len(common_time)):
						ego_leftLine_y = all_lines['ego_leftLine'][:, 1]
						ego_centerLine_y = all_lines['ego_centerLine'][:, 1]
						ego_rightLine_y = all_lines['ego_rightLine'][:, 1]
						if min(len(ego_leftLine_y[index_sample]), len(ego_rightLine_y[index_sample])) != 1:
								for idx in range(min(len(ego_leftLine_y[index_sample]), len(ego_rightLine_y[index_sample]))):
										if ego_leftLine_y[index_sample][idx] == ego_rightLine_y[index_sample][idx]:
												ego_leftLine_ego_rightLine_merge[index_sample] = True
						if min(len(ego_leftLine_y[index_sample]), len(ego_centerLine_y[index_sample])) != 1:
								for idx in range(min(len(ego_leftLine_y[index_sample]), len(ego_centerLine_y[index_sample]))):
										if ego_leftLine_y[index_sample][idx] == ego_centerLine_y[index_sample][idx]:
												ego_leftLine_ego_centerLine_merge[index_sample] = True
						if min(len(ego_rightLine_y[index_sample]), len(ego_centerLine_y[index_sample])) != 1:
								for idx in range(min(len(ego_rightLine_y[index_sample]), len(ego_centerLine_y[index_sample]))):
										if ego_rightLine_y[index_sample][idx] == ego_centerLine_y[index_sample][idx]:
												ego_rightLine_ego_centerLine_merge[index_sample] = True
				return common_time, ego_leftLine_ego_rightLine_merge, ego_leftLine_ego_centerLine_merge, \
							 ego_rightLine_ego_centerLine_merge


# if __name__ == '__main__':
# 		from config.Config import init_dataeval
#
# 		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\mfc525_interface" \
# 								r"\measurements\2020_08_27\NY00__2020-08-27_08-36-16.mat"
# 		config, manager, manager_modules = init_dataeval(['-m', meas_path])
# 		data = manager_modules.calc('calc_flc25_point_cloud_lane_merge_events@aebs.fill', manager)
# 		print data
