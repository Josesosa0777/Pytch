# -*- dataeval: init -*-

from interface import iCalc

sgs = [
	{
		"amber_warning_lamp_status": ("DM1_sA0", "AmberWarningLampStatus_DM1_sA0"),
		"failure_mode_id"            : ("DM1_sA0", "FailureModeIdentifier_DM1_sA0"),
	},
	{
		"amber_warning_lamp_status": ("DM1_sA0", "AmberWarningLampStatus_DM1"),
		"failure_mode_id"            : ("DM1_sA0", "FailureModeIdentifier_DM1"),
	},
	{
		"amber_warning_lamp_status": ("DM1", "AmberWarningLampStatus_DM1"),
		"failure_mode_id"            : ("DM1", "FailureModeIdentifier_DM1"),
	},
]


class cFill(iCalc):
	dep = ('calc_common_time-flr25',)

	def check(self):
		source = self.get_source()
		group = source.selectSignalGroup(sgs)
		return group

	def fill(self, group):
		time = self.modules.fill('calc_common_time-flr25')
		rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
		# vx
		_, amber_warning_lamp_status, unit_vx = group.get_signal_with_unit('amber_warning_lamp_status', **rescale_kwargs)
		_, failure_mode_id, unit_vx = group.get_signal_with_unit('failure_mode_id', **rescale_kwargs)

		valid_warning_lamp_data = amber_warning_lamp_status[~amber_warning_lamp_status.mask].data
		valid_failure_mode_id_data = failure_mode_id[~failure_mode_id.mask].data
		valid_warning_lamp_mask = (valid_warning_lamp_data != 0)
		valid_failure_mode_id_mask = (valid_warning_lamp_data != 0)

		return time, valid_warning_lamp_mask, valid_failure_mode_id_mask, valid_warning_lamp_data, valid_failure_mode_id_data
