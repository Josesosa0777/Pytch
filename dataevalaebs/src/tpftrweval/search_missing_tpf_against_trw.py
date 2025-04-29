# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
		dep = {
				'missing_objects': "calc_tpf_trw_obj_mapping@aebs.fill"
		}

		def fill(self):
				time, missing_objects = self.modules.fill(self.dep['missing_objects'])
				votes = self.batch.get_labelgroups('TPF TRW Compare', 'FLR20 object', 'FLC25 CEM TPF New ID')
				report = Report(cIntervalList(time), 'TPF TRW Compare', votes=votes)
				batch = self.get_batch()

				qua_group = 'TPF TRW Compare'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				for obj in missing_objects:
						Index = max(time.searchsorted(obj[0], side = 'right') - 1, 0)
						if obj[0] == time[-1]:
								LOWER = Index - 1
								UPPER = Index
						else:
								LOWER = Index
								UPPER = Index + 1
						idx = report.addInterval((LOWER, UPPER))
						report.vote(idx, 'TPF TRW Compare', "MissingObjectsInTPF")
						report.set(idx, qua_group, 'timestamp', obj[0])
						report.set(idx, qua_group, 'trw_dx', obj[1])
						report.set(idx, qua_group, 'trw_dy', obj[2])
						report.vote(idx, 'FLR20 object', str(obj[3]))
						# report.set(idx, qua_group, 'trw_track_id', obj[3])
						report.set(idx, qua_group, 'trw_alive_time', obj[4])
						report.vote(idx, 'FLC25 CEM TPF New ID', str(obj[5]))
						# report.set(idx, qua_group, 'nearest_tpf_track_id', obj[5])
						report.set(idx, qua_group, 'nearest_tpf_distance', obj[7])
						report.set(idx, qua_group, 'nearest_tpf_delta_vx', obj[6])
						report.set(idx, qua_group, 'nearest_tpf_alive_time', obj[8])



				return report

		def search(self, report):
				self.batch.add_entry(report)
				return
