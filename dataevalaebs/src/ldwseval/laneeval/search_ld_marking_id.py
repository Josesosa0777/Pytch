# -*- dataeval: init -*-

"""
Search for events of engine running / not running
"""

import interface
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(interface.iSearch):
		def check(self):
				sgs = [
					{
						"left_lane_marking_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
												 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_id"),
						"right_lane_marking_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
						"MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_id"),
					},
				]
				group = self.source.selectSignalGroup(sgs)
				return group

		def fill(self, group):
				# load signals
				left_lane_marking_id_time, left_lane_marking_id_values = group.get_signal("left_lane_marking_id")
				right_lane_marking_id_time, right_lane_marking_id_values = group.get_signal("right_lane_marking_id")

				# create report
				votes = self.batch.get_labelgroups("FLC25 LDWS")
				report = Report(cIntervalList(left_lane_marking_id_time), "FLC25 LDWS", votes=votes)

				left_lane_not_available_masked_array = (left_lane_marking_id_values == 255)

				left_lane_not_available_intervals = maskToIntervals(left_lane_not_available_masked_array)
				jumps = [[start] for start, end in left_lane_not_available_intervals]

				for jump, interval in zip(jumps, left_lane_not_available_intervals):
					idx = report.addInterval(interval)
					report.vote(idx, 'FLC25 LDWS', 'LeftLaneNotAvailable')

				right_lane_not_available_masked_array = (right_lane_marking_id_values == 255)

				right_lane_not_available_intervals = maskToIntervals(right_lane_not_available_masked_array)
				jumps = [[start] for start, end in right_lane_not_available_intervals]

				for jump, interval in zip(jumps, right_lane_not_available_intervals):
					idx = report.addInterval(interval)
					report.vote(idx, 'FLC25 LDWS', 'RightLaneNotAvailable')

				return report

		def search(self, report):
				self.batch.add_entry(report, result=self.PASSED)
				return
