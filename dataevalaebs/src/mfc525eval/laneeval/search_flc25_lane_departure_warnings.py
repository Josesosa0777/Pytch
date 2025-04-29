# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.lane_quality_state import lane_quality_dict

class Search(iSearch):
	optdep = {
		'egospeedstart': 'set_egospeed-start@egoeval', 
		'egospeedmin': 'set_egospeed-min@egoeval',
		'drivdist': 'set_drivendistance@egoeval',
	}

	sgs = [
		{
				"flc25_lane_departure_left": ("FLI1_E8_CAN20","FLI1_LaneDepartImminentLeft_E8"),
				"flc25_lane_departure_right": ("FLI1_E8_CAN20","FLI1_AcousticalWarningRight_E8"),
				#"flc20_lane_departure_left": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI1_lane_departure_imminent_left_side"),
				#"flc20_lane_departure_lright": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI1_lane_departure_imminent_right_side"),
				"flc20_lane_departure_left": ("FLI1_E8_CAN26","FLI1_LaneDepartImminentLeft_E8"),
				"flc20_lane_departure_lright": ("FLI1_E8_CAN26","FLI1_LaneDepartImminentRight_E8"),

				#"C0_left_wheel": ("Bendix_Info2","C0_left_wheel_Left_B"),
				#"C0_right_wheel": ("Bendix_Info2","C0_right_wheel_Right_B")
		},
		{
			"flc25_lane_departure_left": ("FLI1_E8_sE8","LaneDepartureImminentLeftSide"),
			"flc25_lane_departure_right": ("FLI1_E8_sE8","LaneDepartureImminentRightSide"),
			"flc20_lane_departure_left": ("FLI1_E8_CAN26","FLI1_LaneDepartImminentLeft_E8"),
			"flc20_lane_departure_lright": ("FLI1_E8_CAN26","FLI1_LaneDepartImminentRight_E8")
		},
		{
			"flc25_lane_departure_left": ("FLI1_E8_sE8_FLI1_E8_CAN22","FLI1_LaneDepImminentLeft_E8"),
			"flc25_lane_departure_right": ("FLI1_E8_sE8_FLI1_E8_CAN22","FLI1_LaneDepImminentRight_E8"),
			"flc20_lane_departure_left": ("FLI1_E8_sE8_FLI1_E8_CAN26","FLI1_LaneDepImminentLeft_E8"),
			"flc20_lane_departure_lright": ("FLI1_E8_sE8_FLI1_E8_CAN26","FLI1_LaneDepImminentRight_E8")
		}
]
	
	def check(self):
		group = self.source.selectSignalGroup(self.sgs)
		return group

	def fill(self, group):
		# get signals
		_,flc25_left_departure = group.get_signal("flc25_lane_departure_left")
		t,flc25_right_departure = group.get_signal("flc25_lane_departure_right")
		_,flc20_left_departure = group.get_signal("flc20_lane_departure_left")
		t1,flc20_right_departure = group.get_signal("flc20_lane_departure_lright")
		#_,C0_left_wheel = group.get_signal("C0_left_wheel")
		#_,C0_right_wheel = group.get_signal("C0_right_wheel")
		# init report
		title = "FLC25 LDWS"
		votes = self.batch.get_labelgroups(title)
		report = Report(cIntervalList(t), title, votes=votes)
		batch = self.get_batch()

		qua_group = 'FLC25 check'
		quas = batch.get_quanamegroup(qua_group)
		report.setNames(qua_group, quas)

		# find intervals
		flc25_left_warnings = (flc25_left_departure == 1)
		flc25_right_warnings = (flc25_right_departure == 1)
		flc20_left_warnings = (flc20_left_departure == 1)
		flc20_right_warnings = (flc20_right_departure == 1)

		for st,end in maskToIntervals(flc25_left_warnings):
				index = report.addInterval( (st,end) )
				report.vote(index, title, 'FLC25 ldws left')
				#report.set(index, qua_group, 'C0_left_wheel', C0_left_wheel[np.where(t1 == t[st])])

		for st,end in maskToIntervals(flc25_right_warnings):
				index = report.addInterval( (st,end) )
				report.vote(index, title, 'FLC25 ldws right')
				#report.set(index, qua_group, 'C0_right_wheel', C0_right_wheel[np.where(t1 == t[st])])

		for st,end in maskToIntervals(flc20_left_warnings):
				index = report.addInterval( (st,end) )
				report.vote(index, title, 'FLC20 ldws left')
				#report.set(index, qua_group, 'C0_left_wheel', C0_left_wheel[np.where(t1 == t[st])])

		for st,end in maskToIntervals(flc20_right_warnings):
				index = report.addInterval( (st,end) )
				report.vote(index, title, 'FLC20 ldws right')
				#report.set(index, qua_group, 'C0_right_wheel', C0_right_wheel[np.where(t1 == t[st])])
		report.sort()
		return report

	def search(self, report):
		self.batch.add_entry(report, result=self.PASSED)
		return
