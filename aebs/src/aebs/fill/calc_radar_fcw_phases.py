# -*- dataeval: init -*-

import interface
from primitives.fcw import FcwPhases

init_params = {
		'flr25': dict(
						sgn_group = [
							{
								'AEBSState'            : ("AEBS1_A0", "AEBS1_AEBSState_A0"),
								'CollisionWarningLevel': ("AEBS1_A0", "AEBS1_CollisionWarningLevel_A0"),
							},
							{
								"AEBSState"            : ("AEBS1_A0_sA0", "AEBS1_AEBSState_A0_sA0"),
								"CollisionWarningLevel": ("AEBS1_A0_sA0", "AEBS1_CollisionWarningLevel_A0_sA0"),
							},
							{
								'AEBSState'            : ("AEBS1_A0_sA0", "AEBS1_AEBSState_A0"),
								'CollisionWarningLevel': ("AEBS1_A0_sA0", "AEBS1_CollisionWarningLevel_A0"),
							},
							{
								"AEBSState": ("CAN_Vehicle_AEBS1_2A","AEBS1_AEBSState_2A"),
								"CollisionWarningLevel": ("CAN_Vehicle_AEBS1_2A","AEBS1_CollisionWarningLevel_2A"),
							}
						]),
}

class Calc(interface.iCalc):
		PRELIMINARY_WARNING = 2
		COLLISION_WARNING = 4
		AEBS_STATE_COLLISION_WARNING = 5

		def init(self, sgn_group):
				self.sgn_group = sgn_group
				self.group = None  # used by user scripts

				return

		def check(self):
				self.group = self.source.selectLazySignalGroup(self.sgn_group).items()
				group = self.source.selectSignalGroup(self.sgn_group)
				time, status = group.get_signal('AEBSState')
				level = group.get_value('CollisionWarningLevel', ScaleTime = time)
				return time, status, level

		def fill(self, time, status, level):
				preliminary_warning = (status == self.AEBS_STATE_COLLISION_WARNING) & (level == self.PRELIMINARY_WARNING)
				collision_warning = (status == self.AEBS_STATE_COLLISION_WARNING) & (level == self.COLLISION_WARNING)

				phases = FcwPhases(
								time, preliminary_warning, collision_warning
				)
				return phases
