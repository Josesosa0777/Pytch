# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
		dep = {
				'acc_obj_unstable_track': "calc_flc25_acc_obj_unstable_tracking@aebs.fill"
		}

		def fill(self):
				time, event_mask, obj_id = self.modules.fill(self.dep['acc_obj_unstable_track'])
				event_votes = 'FLC25 events'
				votes = self.batch.get_labelgroups(event_votes)
				report = Report(cIntervalList(time), 'FLC25 events', votes = votes)
				batch = self.get_batch()

				qua_group = 'FLC25 check'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				
				intervals = maskToIntervals(event_mask)
				jumps = [[start] for start, end in intervals]

				for jump, interval in zip(jumps, intervals):
						idx = report.addInterval(interval)
						report.vote(idx, event_votes, "ACC Unstable tracking")
						report.set(idx, qua_group, 'obj_id', obj_id[jump])
				return report

		def search(self, report):
				self.batch.add_entry(report)
				return
