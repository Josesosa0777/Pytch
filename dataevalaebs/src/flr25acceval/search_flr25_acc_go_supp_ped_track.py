# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
		dep = {
				'flr25_acc_ped_event': "fill_flr25_acc_go_supp_ped_track@aebs.fill"
		}

		def fill(self):
				acc_ped_track = self.modules.fill(
								self.dep['flr25_acc_ped_event'])

				event_votes = 'ACC event'
				votes = self.batch.get_labelgroups(event_votes)
				report = Report(cIntervalList(acc_ped_track.time), 'ACC event', votes = votes)
				# Add quantity
				batch = self.get_batch()
				qua_group = 'ACC check'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				intervals = maskToIntervals(~acc_ped_track[0].object_id.mask)
				jumps = [[start] for start, end in intervals]

				for jump, interval in zip(jumps, intervals):
						idx = report.addInterval(interval)
						report.vote(idx, event_votes, 'Pedestrian Go Suppression Target Present')
						report.set(idx, qua_group, 'pedestrian go suppression target present(dx)', acc_ped_track[0].dx.data[jump])

				return report

		def search(self, report):
				self.batch.add_entry(report)
				return
