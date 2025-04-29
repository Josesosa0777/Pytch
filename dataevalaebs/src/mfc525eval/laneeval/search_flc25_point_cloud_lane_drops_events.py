# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
		dep = {
				'lane_drops': "calc_flc25_point_cloud_lane_drops_events@aebs.fill"
		}

		def fill(self):
				time, lane_drops_events = self.modules.fill(self.dep['lane_drops'])

				event_votes = 'FLC25 events'
				votes = self.batch.get_labelgroups(event_votes)
				report = Report(cIntervalList(time), 'FLC25 events', votes = votes)
				intervals = maskToIntervals(lane_drops_events)
				jumps = [[start] for start, end in intervals]
				for jump, interval in zip(jumps, intervals):
						idx = report.addInterval(interval)
						report.vote(idx, event_votes, "Lane Drops")
				return report

		def search(self, report):
				self.batch.add_entry(report)
				return
