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
						"ldws_state": ("FLI2_E8", "FLI2_LDWSState_E8_sE8"),
					},
				]
				group = self.source.selectSignalGroup(sgs)
				return group

		def fill(self, group):
				# load signals
				time, ldws_state_values = group.get_signal("ldws_state")

				# create report
				votes = self.batch.get_labelgroups("FLC25 LDWS")
				report = Report(cIntervalList(time), "FLC25 LDWS", votes=votes)

				batch = self.get_batch()
				qua_group = 'FLC25 LDWS'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				lane_available_masked_array = (ldws_state_values != 0) & (ldws_state_values != 15) & (ldws_state_values != 14)
				lane_available_intervals = maskToIntervals(lane_available_masked_array)

				#lane_available_count = 0
				for st, end in lane_available_intervals:
					interval_diff = end - st
					#lane_available_count = lane_available_count + interval_diff
					index = report.addInterval([st, end])
					report.set(index, qua_group, 'Available', interval_diff)

				lane_not_available = (ldws_state_values == 1)

				#lane_not_available_count = 0
				lane_not_available_intervals = maskToIntervals(lane_not_available)

				for st, end in lane_not_available_intervals:
					if (st != 0) and (ldws_state_values[st - 1] == 3):
						interval_difference = end - st
						#lane_not_available_count = lane_not_available_count + interval_difference
						index = report.addInterval([st, end])
						report.vote(index, 'FLC25 LDWS', 'Not Available')
						report.set(index, qua_group, 'Not Available', interval_difference)

				return report


		def search(self, report):
				self.batch.add_entry(report, result=self.PASSED)
				return
