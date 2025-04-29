# -*- dataeval: init -*-
"""
:Name:
	search_kpi_events.py
:Type:
	Search script
:Full Path:
	dataevalaebs/src/tsreval/search_kpi_events.py

:Sensors:
	FLC25(CEM_TPF)

:Short Description:
	The TSR KPIs compare conti detections with ground truth data and create report of False Positive, True Positive, False
	 Negative events

:Large Description:
	Usage:
		- This script use data from postmarker JSON file
		- Find out traffic sign intervals from postmarker JSON and stores them into database for further analysis
		- Analyzes and compare ground truth with conti camera detections

:Dependencies:
	calc_tsr_kpi_metrics@aebs.fill

:Output Data Image/s:
	.. image:: ../images/search_postmarker_events.png

:Event Name:
	TSR

:Event Labels:
	verdict, sign_class_id

:Event Values:
	verdict

.. note::
	For source code click on [source] tag beside functions
"""
from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report
from measproc.IntervalList import maskToIntervals

class Search(iSearch):
		dep = 'calc_tsr_kpi_metrics@aebs.fill'

		def fill(self):
				common_time, kpi_report, cumulative_results = self.modules.fill(self.dep)
				event_votes = 'TSR verdict'
				votes = self.batch.get_labelgroups(event_votes)
				report = Report(cIntervalList(common_time), 'TSR event', votes=votes)

				batch = self.get_batch()
				qua_group = 'TSR'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				for report_identifier, verdict in kpi_report.items():
						sign_class_id, event_start_time = report_identifier
						event_verdict = verdict['verdict']
						event_start_idx = self.get_index(event_start_time, common_time)
						idx = report.addInterval((event_start_idx, event_start_idx+1,))
						report.vote(idx, event_votes, event_verdict)
						report.set(idx, qua_group, 'sign_class_id', sign_class_id)
						report.set(idx, qua_group, 'TP', cumulative_results["Conti_KPI"]["TP"])
						report.set(idx, qua_group, 'FP', cumulative_results["Conti_KPI"]["FP"])
						report.set(idx, qua_group, 'FN', cumulative_results["Conti_KPI"]["FN"])
						report.set(idx, qua_group, 'conti_uid', verdict["conti_uid"])
				return report

		def get_index(self, start, common_time):
				st_index = max(common_time.searchsorted(start, side = "right") - 1, 0)

				return st_index

		def search(self, report):
				self.batch.add_entry(report)
				return
