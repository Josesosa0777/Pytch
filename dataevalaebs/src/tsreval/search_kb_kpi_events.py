# -*- dataeval: init -*-
"""
:Name:
	search_kb_kpi_events.py
:Type:
	Search script
:Full Path:
	dataevalaebs/src/tsreval/search_kpi_events.py

:Sensors:
	FLC25(CEM_TPF)

:Short Description:
	The TSR KBKPIs compare can detected value with ground truth data and create report of False Positive, True Negative, True Positive, False
	 Negative events

:Large Description:
	Usage:
		- This script use data from postmarker JSON file
		- Find out traffic sign intervals from postmarker JSON and stores them into database for further analysis
		- Analyzes and compare ground truth with can tssdetectedvalue

:Dependencies:
	calc_tsr_kb_kpi_metrics@aebs.fill

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
import json
import os

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report
from measproc.IntervalList import maskToIntervals
from os.path import expanduser

class Search(iSearch):
		dep = 'calc_tsr_kb_kpi_metrics@aebs.fill'

		def fill(self):
				common_time, kpi_report, cumulative_results = self.modules.fill(self.dep)
				event_votes = 'TSR verdict'
				weather_condition = 'Weather Conditions'
				time_condition = 'Time'
				tsr_remark = 'TSR Remark'
				CAN_Signal_group='CAN_Signal_group'
				votes = self.batch.get_labelgroups(event_votes, weather_condition, time_condition,tsr_remark,CAN_Signal_group)
				report = Report(cIntervalList(common_time), 'TSR event', votes=votes)

				batch = self.get_batch()
				qua_group = 'TSR'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				for report_identifier, verdict in kpi_report.items():
					event_start_time, sign_class_id = report_identifier
					postmarker_labeling = verdict[0]
					can_data = verdict[1]
					event_verdict = postmarker_labeling['verdict']
					event_start_idx = self.get_index(event_start_time, common_time)

					idx = report.addInterval((event_start_idx, event_start_idx + 1,))
					report.vote(idx, event_votes, event_verdict)
					report.vote(idx, weather_condition, postmarker_labeling['weather_condition'])
					report.vote(idx, time_condition, postmarker_labeling['time_condition'])
					signal_grp={}
					if "TSR_SpeedLimit1_E8_sE8" in can_data:
						report.vote(idx, CAN_Signal_group,  'TSR_SpeedLimit1_E8_sE8')
						signal_grp['CAN_Signal_group']= 'TSR_SpeedLimit1_E8_sE8'
					elif "AutoHighLowBeamControl" in can_data:
						report.vote(idx, CAN_Signal_group,  'TSSDetectedValue')
						signal_grp['CAN_Signal_group'] ='TSSDetectedValue'
					else:
						report.vote(idx, CAN_Signal_group, '999')
					if (postmarker_labeling.has_key('Note')):
						report.vote(idx, tsr_remark, postmarker_labeling['Note'])
					if "TSR_SpeedLimit1_E8_sE8" in can_data:
						report.set(idx, qua_group, 'TSR_SpeedLimit1_E8_sE8', can_data['TSR_SpeedLimit1_E8_sE8'])
						report.set(idx, qua_group, 'TSR_SpeedLimit1Supplementary_E8_sE8', can_data['TSR_SpeedLimit1Supplementary_E8_sE8'])
						report.set(idx, qua_group, 'TSR_SpeedLimit2_E8_sE8', can_data['TSR_SpeedLimit2_E8_sE8'])
						report.set(idx, qua_group, 'TSR_SpeedLimitElectronic_E8_sE8', can_data['TSR_SpeedLimitElectronic_E8_sE8'])
						report.set(idx, qua_group, 'TSR_NoPassingRestriction_E8_sE8', can_data['TSR_NoPassingRestriction_E8_sE8'])
						report.set(idx, qua_group, 'TSR_CountryCode_E8_sE8',can_data['TSR_CountryCode_E8_sE8'])

					elif "AutoHighLowBeamControl"  in can_data:
						report.set(idx, qua_group, 'CAN_AutoHighLowBeamControl', can_data['AutoHighLowBeamControl'])
						report.set(idx, qua_group, 'CAN_TSSCurrentRegion', can_data['TSSCurrentRegion'])
						report.set(idx, qua_group, 'CAN_TSSDetectedStatus', can_data['TSSDetectedStatus'])
						report.set(idx, qua_group, 'CAN_TSSDetectedUoM', can_data['TSSDetectedUoM'])
						report.set(idx, qua_group, 'CAN_TSSDetectedValue', can_data['TSSDetectedValue'])
						report.set(idx, qua_group, 'CAN_TSSLifeTime', can_data['TSSLifeTime'])
						report.set(idx, qua_group, 'CAN_TSSOverspeedAlert', can_data['TSSOverspeedAlert'])


					report.set(idx, qua_group, 'CAN_sign_class_id', sign_class_id)
					report.set(idx, qua_group, 'CAN_TP', cumulative_results["TP"])
					report.set(idx, qua_group, 'CAN_TN', cumulative_results["TN"])
					report.set(idx, qua_group, 'CAN_FP', cumulative_results["FP"])
					report.set(idx, qua_group, 'CAN_FP1', cumulative_results["FP1"])
					report.set(idx, qua_group, 'CAN_FP2', cumulative_results["FP2"])
					report.set(idx, qua_group, 'CAN_FP3', cumulative_results["FP3"])
					report.set(idx, qua_group, 'CAN_FN', cumulative_results["FN"])
					report.set(idx, qua_group, 'CAN_GT_existance_false', cumulative_results["GT_existance_false"])
					report.set(idx, qua_group, 'CAN_GT_existance_true', cumulative_results["GT_existance_true"])
					report.set(idx, qua_group, 'CAN_Total_GT', cumulative_results["Total_GT"])
					report.set(idx, qua_group, 'can_duration', can_data['can_duration'])

				return report

		def get_index(self, start, common_time):
				st_index = max(common_time.searchsorted(start, side = "right") - 1, 0)

				return st_index

		#Adds entry in batch database
		def search(self, report):
				self.batch.add_entry(report)
				return
