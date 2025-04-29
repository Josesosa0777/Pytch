# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
		dep = {
				'lane_merges': "calc_flc25_point_cloud_lane_merge_events@aebs.fill"
		}

		def fill(self):
				time, ego_leftLine_ego_rightLine_merge, ego_leftLine_ego_centerLine_merge, ego_rightLine_ego_centerLine_merge \
						= self.modules.fill(
								self.dep['lane_merges'])

				event_votes = 'FLC25 events'
				votes = self.batch.get_labelgroups(event_votes)
				report = Report(cIntervalList(time), 'FLC25 events', votes = votes)

				for key, value in {
						"Lane Merge ego_left-ego_right"  : ego_leftLine_ego_rightLine_merge,
						"Lane Merge ego_left-ego_center" : ego_leftLine_ego_centerLine_merge,
						"Lane Merge ego_right-ego_center": ego_rightLine_ego_centerLine_merge
				}.items():
						intervals = maskToIntervals(value)
						jumps = [[start] for start, end in intervals]

						for jump, interval in zip(jumps, intervals):
								idx = report.addInterval(interval)
								report.vote(idx, event_votes, key)
				return report

		def search(self, report):
				self.batch.add_entry(report)
				return
