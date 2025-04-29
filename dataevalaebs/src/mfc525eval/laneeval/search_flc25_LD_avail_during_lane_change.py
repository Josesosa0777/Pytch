# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.lane_quality_state import lane_quality_dict

class Search(iSearch):
	sgs = [
		{
			"LaneChangeEvent_side": ("MFC5xx Device.LD.LdOutput","MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_laneChangeEvent_side"),
			"ego_velocity": ("MFC5xx Device.FCU.VehDynSync","MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
		},
		{
			"LaneChangeEvent_side": ("LdOutput","MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_laneChangeEvent_side"),
			"ego_velocity": ("VehDynSync","MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
		}
]
	
	def check(self):
		group = self.source.selectSignalGroup(self.sgs)
		return group

	def fill(self, group):
		# get signals
		t,lane_change_event = group.get_signal("LaneChangeEvent_side")
		t,ego_velocity = group.get_signal("ego_velocity")
		# init report
		title = "FLC25 events"
		votes = self.batch.get_labelgroups(title)
		report = Report(cIntervalList(t), title, votes=votes)
		
		# find intervals
		n = min(len(lane_change_event), len(ego_velocity))
		ego_lane_change = (lane_change_event[:n] == 1) & (ego_velocity[:n] > 16)
		
		for st,end in maskToIntervals(ego_lane_change):
				index = report.addInterval( (st,end) )
				report.vote(index, title, 'LD during ego lane change')		

		report.sort()
		return report

	def search(self, report):
		self.batch.add_entry(report, result=self.PASSED)
		return
