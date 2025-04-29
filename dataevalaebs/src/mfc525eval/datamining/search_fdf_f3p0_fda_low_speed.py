# -*- dataeval: init -*-

import numpy as np
from dataio.src import measparser

from interface import iSearch
from dataio.src.measparser.signalproc import rescale
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.lane_quality_state import lane_quality_dict

class Search(iSearch):

	sgs = [
		{
				"acc_follow_distance_alert_state": ("MFC5xx Device.KB.MTSI_stKBFreeze_010ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_010ms_t_sFlc25_OmLonControlMessages_prop1_acc_follow_distance_alert_state"),
				"EBC2_MeanSpdFA": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
		}
]
	
	def check(self):
		group = self.source.selectSignalGroup(self.sgs)
		return group

	def fill(self, group):
		# get signals
		t1, follow_distane_alert_state = group.get_signal("acc_follow_distance_alert_state")
		t2, mean_speed = group.get_signal("EBC2_MeanSpdFA")
		t, v = rescale(t2, mean_speed, t1)
		title = "Fusion3 Data Mining"
		votes = self.batch.get_labelgroups(title)
		report = Report(cIntervalList(t1), title, votes=votes)
		batch = self.get_batch()

		qua_group = 'FLC25 check'
		quas = batch.get_quanamegroup(qua_group)
		report.setNames(qua_group, quas)

		  #  FollowDistanceAlertState
		  #    0 = System Not Ready
		  #    1 = System Ready and No FDA Warning
		  #    2 = FDA Level 1 Warning
		  #    3 = FDA Level 2 Warning
		  #    4 = FDA Level 3 Warning
		  #    5 = Forward FDA Warning Active
		  #    6 = Forward FDA Warning with Braking
		  #    7 = Forward FDA Emergency Braking Active		

		# find intervals
		fda_low_speed = (follow_distane_alert_state > 1) & (follow_distane_alert_state < 5) & (mean_speed >= 8) & (mean_speed <= 14.5)

		for st,end in maskToIntervals(fda_low_speed):
				index = report.addInterval( (st,end) )
				report.vote(index, title, 'FDA Low Speed')

		report.sort()
		return report

	def search(self, report):
		self.batch.add_entry(report, result=self.PASSED)
		return
