# -*- dataeval: init -*-
"""
:Name:
	search_events.py
:Type:
	Search script
:Full Path:
	dataevalaebs/src/tsreval/search_events.py

:Sensors:
	FLC25(CEM_TPF)

:Short Description:
	Postmarker tool is an internal tool developed for labeling ground truth data. This manually labeled data is
	then compared with actual MFC525 camera detected traffic sign data. This search script finds out all such
	intervals where there is a label. This is the used for detailed analysis with conti sensor data.
	It stores conti sign class ID and postmarker_Lane_ref status.

:Large Description:
	Usage:
		- This script use data from postmarker JSON file
		- Find out traffic sign intervals from postmarker JSON and stores them into database for further analysis

:Dependencies:
	fill_postmarker_traffic_signs@aebs.fill

:Output Data Image/s:
	.. image:: ../images/search_postmarker_events.png

:Event Name:
	TSR

:Event Labels:
	postmarker_Lane_ref status

:Event Values:
	conti sign class ID

.. note::
	For source code click on [source] tag beside functions
"""
from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report
from measproc.IntervalList import maskToIntervals

class Search(iSearch):
		dep = 'fill_postmarker_traffic_signs@aebs.fill'

		def fill(self):
				common_time, objects = self.modules.fill(self.dep)
				event_votes = 'TSR event'
				votes = self.batch.get_labelgroups(event_votes)
				report = Report(cIntervalList(common_time), 'TSR event', votes=votes)

				# phase_votes = 'PAEBS cascade phase' #using same label for PAEBS
				# algo_votes = 'PAEBS algo' #using same label for PAEBS
				# votes = self.batch.get_labelgroups(phase_votes, algo_votes)
				# report = Report(cIntervalList(time), 'PAEBS warnings', votes=votes)  #using same label for PAEBS
				# exclusive, cascade_phases = votes[phase_votes]

				# levels = 5
				# jumps, warnings = phases.merge_phases(levels)
				batch = self.get_batch()
				qua_group = 'TSR'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				for tsr_object in objects:
						tsr_signs_from_postmarker_tool = tsr_object["is_sign_detected"]
						warnings = maskToIntervals(tsr_signs_from_postmarker_tool)
						jumps = [[start] for start, end in warnings]

						for jump, interval in zip(jumps, warnings):
								idx = report.addInterval(interval)
								# report.vote(idx, algo_votes, self.algo)
								report.vote(idx, event_votes, "TSR event")
								report.set(idx, qua_group, 'sign_class_id', tsr_object['sign_class_id'][jump])
								# report.set(idx, qua_group, 'sign_class_name', str(tsr_object['sign_class'][start]))
								report.set(idx, qua_group, 'postmarker_Lane_ref', int(bool(tsr_object['sign_status'][jump])))

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
