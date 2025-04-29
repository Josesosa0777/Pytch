# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
		dep = {
				'Detected_objs': "calc_flc25_num_of_detected_objects@aebs.fill"
		}

		def fill(self):
				time, detected_objs_mask, detected_objs = self.modules.fill(self.dep['Detected_objs'])
				event_votes = 'FLC25 events'
				votes = self.batch.get_labelgroups(event_votes)
				report = Report(cIntervalList(time), 'FLC25 events', votes = votes)
				batch = self.get_batch()

				qua_group = 'FLC25 check'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				intervals = maskToIntervals(detected_objs_mask)
				jumps = [[start] for start, end in intervals]

				for jump, interval in zip(jumps, intervals):
						idx = report.addInterval(interval)
						report.vote(idx, event_votes, "NumOfDetectedObjects")
						report.set(idx, qua_group, 'max_num_of_detected_obj', detected_objs[jump])
				return report

		def search(self, report):
				self.batch.add_entry(report)
				return
