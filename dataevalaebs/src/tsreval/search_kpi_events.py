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
				common_time, kpi_report, cumulative_results, is_conti_sign_detected = self.modules.fill(self.dep)
				event_votes = 'TSR verdict'
				weather_condition = 'Weather Conditions'
				time_condition = 'Time'
				tsr_remark = 'TSR Remark'
				CAN_Signal_group = 'CAN_Signal_group'
				votes = self.batch.get_labelgroups(event_votes, weather_condition, time_condition,tsr_remark,CAN_Signal_group)
				report = Report(cIntervalList(common_time), 'TSR event', votes=votes)

				batch = self.get_batch()
				qua_group = 'TSR'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				for report_identifier, verdict in kpi_report.items():
						sign_class_id, event_start_time = report_identifier
						event_verdict = verdict['verdict']
						event_start_idx = self.get_index(event_start_time, common_time)
						# Get conti intervals
						conti_sign_detection_duration = maskToIntervals(is_conti_sign_detected)
						if verdict['conti_uid'] != 99999999:
							# event_start_idx = self.get_index(event_time, conti_tsr_time)
							for conti_sign_detection in conti_sign_detection_duration:
								if conti_sign_detection[0] <= event_start_idx < conti_sign_detection[1]:
									idx = report.addInterval((event_start_idx, event_start_idx+1,))
									report.vote(idx, event_votes, event_verdict)
									report.vote(idx, weather_condition, verdict['weather_condition'])
									report.vote(idx, time_condition, verdict['time_condition'])
									if "TSR_SpeedLimit1_E8_sE8" in verdict:
										report.vote(idx, CAN_Signal_group, 'TSR_SpeedLimit1_E8_sE8')
									elif "AutoHighLowBeamControl" in verdict:
										report.vote(idx, CAN_Signal_group, 'TSSDetectedValue')
									else:
										report.vote(idx, CAN_Signal_group, '999')
									if(verdict.has_key('Note')):
										report.vote(idx, tsr_remark, verdict['Note'])

									if "AutoHighLowBeamControl" in verdict:
										report.set(idx, qua_group, 'AutoHighLowBeamControl', verdict['AutoHighLowBeamControl'])
										report.set(idx, qua_group, 'TSSCurrentRegion', verdict['TSSCurrentRegion'])
										report.set(idx, qua_group, 'TSSDetectedStatus', verdict['TSSDetectedStatus'])
										report.set(idx, qua_group, 'TSSDetectedUoM', verdict['TSSDetectedUoM'])
										report.set(idx, qua_group, 'TSSDetectedValue', verdict['TSSDetectedValue'])
										report.set(idx, qua_group, 'TSSLifeTime', verdict['TSSLifeTime'])
										report.set(idx, qua_group, 'TSSOverspeedAlert', verdict['TSSOverspeedAlert'])
									elif "TSR_SpeedLimit1_E8_sE8" in verdict:
										report.set(idx, qua_group, 'TSR_SpeedLimit1_E8_sE8', verdict['TSR_SpeedLimit1_E8_sE8'])
										report.set(idx, qua_group, 'TSR_SpeedLimit1Supplementary_E8_sE8', verdict['TSR_SpeedLimit1Supplementary_E8_sE8'])
										report.set(idx, qua_group, 'TSR_SpeedLimit2_E8_sE8', verdict['TSR_SpeedLimit2_E8_sE8'])
										report.set(idx, qua_group, 'TSR_SpeedLimitElectronic_E8_sE8',verdict['TSR_SpeedLimitElectronic_E8_sE8'])
										report.set(idx, qua_group, 'TSR_NoPassingRestriction_E8_sE8',verdict['TSR_NoPassingRestriction_E8_sE8'])
										report.set(idx, qua_group, 'TSR_CountryCode_E8_sE8', verdict['TSR_CountryCode_E8_sE8'])
									# else :
									# 		verdict["AutoHighLowBeamControl"] = 999
									# 		verdict["TSSCurrentRegion"] = 999
									# 		verdict["TSSDetectedStatus"] = 999
									# 		verdict["TSSDetectedUoM"] = 999
									# 		verdict["TSSDetectedValue"] = 999
									# 		verdict["TSSLifeTime"] = 999
									# 		verdict["TSSOverspeedAlert"] = 999
									report.set(idx, qua_group, 'sign_class_id', sign_class_id)
									report.set(idx, qua_group, 'TP', cumulative_results["Conti_KPI"]["TP"])
									report.set(idx, qua_group, 'FP', cumulative_results["Conti_KPI"]["FP"])
									report.set(idx, qua_group, 'FN', cumulative_results["Conti_KPI"]["FN"])
									report.set(idx, qua_group, 'Total_GT', cumulative_results["Total_GT"])
									report.set(idx, qua_group, 'conti_uid', verdict["conti_uid"])
									try:
										report.set(idx, qua_group, 'conti_duration', float(common_time[conti_sign_detection[1]] - common_time[conti_sign_detection[0]]))
									except:
										report.set(idx, qua_group, 'conti_duration', float(common_time[conti_sign_detection[1]-1] - common_time[conti_sign_detection[0]]))
						else:
							idx = report.addInterval((event_start_idx, event_start_idx + 1,))
							report.vote(idx, event_votes, event_verdict)
							report.vote(idx, weather_condition, verdict['weather_condition'])
							report.vote(idx, time_condition, verdict['time_condition'])
							if "TSR_SpeedLimit1_E8_sE8" in verdict:
								report.vote(idx, CAN_Signal_group, 'TSR_SpeedLimit1_E8_sE8')
							elif "AutoHighLowBeamControl" in verdict:
								report.vote(idx, CAN_Signal_group, 'TSSDetectedValue')
							else:
								report.vote(idx, CAN_Signal_group, '999')
							if (verdict.has_key('Note')):
								report.vote(idx, tsr_remark, verdict['Note'])
							if "AutoHighLowBeamControl" in verdict:
								report.set(idx, qua_group, 'AutoHighLowBeamControl', verdict['AutoHighLowBeamControl'])
								report.set(idx, qua_group, 'TSSCurrentRegion', verdict['TSSCurrentRegion'])
								report.set(idx, qua_group, 'TSSDetectedStatus', verdict['TSSDetectedStatus'])
								report.set(idx, qua_group, 'TSSDetectedUoM', verdict['TSSDetectedUoM'])
								report.set(idx, qua_group, 'TSSDetectedValue', verdict['TSSDetectedValue'])
								report.set(idx, qua_group, 'TSSLifeTime', verdict['TSSLifeTime'])
								report.set(idx, qua_group, 'TSSOverspeedAlert', verdict['TSSOverspeedAlert'])
							elif "TSR_SpeedLimit1_E8_sE8" in verdict:
								report.set(idx, qua_group, 'TSR_SpeedLimit1_E8_sE8', verdict['TSR_SpeedLimit1_E8_sE8'])
								report.set(idx, qua_group, 'TSR_SpeedLimit1Supplementary_E8_sE8',verdict['TSR_SpeedLimit1Supplementary_E8_sE8'])
								report.set(idx, qua_group, 'TSR_SpeedLimit2_E8_sE8', verdict['TSR_SpeedLimit2_E8_sE8'])
								report.set(idx, qua_group, 'TSR_SpeedLimitElectronic_E8_sE8',verdict['TSR_SpeedLimitElectronic_E8_sE8'])
								report.set(idx, qua_group, 'TSR_NoPassingRestriction_E8_sE8',verdict['TSR_NoPassingRestriction_E8_sE8'])
								report.set(idx, qua_group, 'TSR_CountryCode_E8_sE8', verdict['TSR_CountryCode_E8_sE8'])

							report.set(idx, qua_group, 'sign_class_id', sign_class_id)
							report.set(idx, qua_group, 'TP', cumulative_results["Conti_KPI"]["TP"])
							report.set(idx, qua_group, 'FP', cumulative_results["Conti_KPI"]["FP"])
							report.set(idx, qua_group, 'FN', cumulative_results["Conti_KPI"]["FN"])
							report.set(idx, qua_group, 'Total_GT', cumulative_results["Total_GT"])
							report.set(idx, qua_group, 'conti_uid', verdict["conti_uid"])
				return report

		def get_index(self, start, common_time):
				st_index = max(common_time.searchsorted(start, side = "right") - 1, 0)

				return st_index

		def search(self, report):
				self.batch.add_entry(report)
				return
