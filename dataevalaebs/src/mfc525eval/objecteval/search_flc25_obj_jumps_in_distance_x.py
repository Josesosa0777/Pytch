# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
		dep = {
				'obj_jump': "calc_flc25_obj_jumps_in_distance_x@aebs.fill"
		}

		def fill(self):
				time, a_objects_dx_data = self.modules.fill(self.dep['obj_jump'])
				event_votes = 'FLC25 events'
				votes = self.batch.get_labelgroups(event_votes)
				report = Report(cIntervalList(time), 'FLC25 events', votes = votes)
				batch = self.get_batch()

				qua_group = 'FLC25 check'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				for obj in a_objects_dx_data:
						intervals = maskToIntervals(obj['valid_object_distx_mask'])
						jumps = [[start] for start, end in intervals]

						for jump, interval in zip(jumps, intervals):
								idx = report.addInterval(interval)
								report.vote(idx, event_votes, "Object Jump")
								report.set(idx, qua_group, 'obj_distx_jump', obj['object_delta_distx'][jump])
								report.set(idx, qua_group, 'obj_distx_val', obj['object_distx_value'][jump])
								report.set(idx, qua_group, 'obj_id', obj['id'][jump])
								report.set(idx, qua_group, 'obj_disty_jump', obj['object_delta_disty'][jump])
								report.set(idx, qua_group, 'obj_disty_val', obj['object_disty_value'][jump])
				return report

		def search(self, report):
				self.batch.add_entry(report)
				return
