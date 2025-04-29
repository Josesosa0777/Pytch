# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
		dep = {
				'fusion_degradation': "calc_flc25_acc_obj_fusion_degradation@aebs.fill"
		}

		def fill(self):
				time, acc_obj, eventMask = self.modules.fill(self.dep['fusion_degradation'])
				event_votes = 'FLC25 events'
				votes = self.batch.get_labelgroups(event_votes)
				report = Report(cIntervalList(time), 'FLC25 events', votes = votes)
				batch = self.get_batch()

				qua_group = 'FLC25 check'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				
				intervals = maskToIntervals(eventMask)
				jumps = [[start] for start, end in intervals]

				for jump, interval in zip(jumps, intervals):
						idx = report.addInterval(interval)
						report.vote(idx, event_votes, "Fusion degradation")
						report.set(idx, qua_group, 'obj_distx_val', acc_obj['dx'][jump])
						report.set(idx, qua_group, 'measured_by', acc_obj['measured_by'][jump])
						report.set(idx, qua_group, 'obj_id', acc_obj['id'][jump])

				return report

		def search(self, report):
				self.batch.add_entry(report)
				return
