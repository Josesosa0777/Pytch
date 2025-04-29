# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
		dep = {
				'lane_change': "calc_flc25_object_lane_change@aebs.fill"
		}

		def fill(self):
				time, lane_change = self.modules.fill(self.dep['lane_change'])
				votes = self.batch.get_labelgroups('FLC25 events', 'FLC25 CEM TPF Object Info')
				report = Report(cIntervalList(time), 'FLC25 events', votes = votes)
				batch = self.get_batch()

				qua_group = 'FLC25 Object LaneChange check'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				for object in lane_change :

						idx = report.addInterval((object[1],object[2]))
						report.vote(idx, 'FLC25 events', 'Object Lane Change')
						report.vote(idx, 'FLC25 CEM TPF Object Info', str(object[0]))
						report.set(idx, qua_group, 'Object Info(current_id)', object[0])
						report.set(idx, qua_group, 'Object Info(previous_index)', object[1])
						report.set(idx, qua_group, 'Object Info(current_index)', object[2])
						report.set(idx, qua_group, 'Object Info(previous_lane)', object[3])
						report.set(idx, qua_group, 'Object Info(current_lane)', object[4])
						report.set(idx, qua_group, 'Object Info(previous_time)', object[5])
						report.set(idx, qua_group, 'Object Info(current_time)', object[6])
						report.set(idx, qua_group, 'Object Distance X', object[7])

				return report

		def search(self, report):
				self.batch.add_entry(report)
				return
