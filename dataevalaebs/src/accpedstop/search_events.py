# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report
from measproc.IntervalList import maskToIntervals

class Search(iSearch):
		dep = {
				'phases': 'calc_acc_ped_phases-acc_ped_stop@aebs.fill',
		}

		def fill(self):
				self.algo = "FLC25 Warning"
				time, phases = self.modules.fill(self.dep['phases'])
				event_votes = 'ACC event'
				votes = self.batch.get_labelgroups(event_votes)
				report = Report(cIntervalList(time), 'ACC event', votes=votes)

				# phase_votes = 'PAEBS cascade phase' #using same label for PAEBS
				# algo_votes = 'PAEBS algo' #using same label for PAEBS
				# votes = self.batch.get_labelgroups(phase_votes, algo_votes)
				# report = Report(cIntervalList(time), 'PAEBS warnings', votes=votes)  #using same label for PAEBS
				# exclusive, cascade_phases = votes[phase_votes]

				# levels = 5
				# jumps, warnings = phases.merge_phases(levels)
				warnings = maskToIntervals(phases)
				jumps = [[start] for start, end in warnings]
				for jump, interval in zip(jumps, warnings):
						idx = report.addInterval(interval)
						# report.vote(idx, algo_votes, self.algo)
						report.vote(idx, event_votes, "Pedestrian Stop Intervention")

				# for qua in 'egospeedstart', 'paebtrack':
				# 		if self.optdep[qua] in self.passed_optdep:
				# 				set_qua_for_report = self.modules.get_module(self.optdep[qua])
				# 				set_qua_for_report(report)
				# 		else:
				# 				self.logger.warning("Inactive module: %s" % self.optdep[qua])
				return report

		def search(self, report):
				self.batch.add_entry(report)
				return
