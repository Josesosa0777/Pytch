# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.lane_quality_state import lane_quality_dict

class Search(iSearch):
	sgs = [
		{
			"ego_LD_left_lane": ("MFC5xx Device.LD.LdOutput","MFC5xx_Device_LD_LdOutput_road_ego_left_available"),
			"ego_LD_right_lane": ("MFC5xx Device.LD.LdOutput","MFC5xx_Device_LD_LdOutput_road_ego_right_available"),
			"ego_velocity": ("MFC5xx Device.FCU.VehDynSync","MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
		}
]
	
	def check(self):
		group = self.source.selectSignalGroup(self.sgs)
		return group

	def fill(self, group):
		# get signals
		t, ego_ld_left = group.get_signal("ego_LD_left_lane")
		t, ego_ld_right = group.get_signal("ego_LD_right_lane")
		t, ego_velocity = group.get_signal("ego_velocity")
		# init report
		title = "FLC25 events"
		votes = self.batch.get_labelgroups(title)
		report = Report(cIntervalList(t), title, votes=votes)
		
		# find intervals
		n = min(len(ego_ld_left), len(ego_velocity))
		LD_doprouts_mask = (ego_ld_left[:n] == 0) | (ego_ld_right[:n] == 0) & (ego_velocity[:n] > 16)
		
		for st,end in maskToIntervals(LD_doprouts_mask):
				index = report.addInterval( (st,end) )
				report.vote(index, title, 'LD dropouts on HW')		

		report.sort()
		return report

	def search(self, report):
		self.batch.add_entry(report, result=self.PASSED)
		return
