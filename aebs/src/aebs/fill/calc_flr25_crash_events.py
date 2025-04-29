# -*- dataeval: init -*-

from interface import iCalc

sgs = [
	{
		"cat2_last_reset_reason": ("FS_SafeSection_Mirror",
								"ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_u_Cat2LastResetReason"),
		"address"            : ("FS_SafeSection_Mirror",
								"ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_Exception_Mcu_u_Address"),
	},
{
		"cat2_last_reset_reason": ("ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror",
								"ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_u_Cat2LastResetReason"),
		"address"            : ("ARS4xx Device.SW_Every10ms.FS_SafeSection_Mirror",
								"ARS4xx_Device_SW_Every10ms_FS_SafeSection_Mirror_FsData_Exception_Mcu_u_Address"),
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
		_, cat2_last_reset_reason, unit_vx = group.get_signal_with_unit('cat2_last_reset_reason', **rescale_kwargs)
		_, address, unit_vx = group.get_signal_with_unit('address', **rescale_kwargs)

		valid_reset_reason_data = cat2_last_reset_reason[~cat2_last_reset_reason.mask].data
		valid_address_data = address[~address.mask].data
		valid_radar_mask = (valid_reset_reason_data != 41)

		return time, valid_radar_mask, valid_reset_reason_data, valid_address_data


if __name__ == '__main__':
	from config.Config import init_dataeval

	meas_path = r'\\pu2w6474\shared-drive\measurements\new_meas_09_11_21\ARS4xx\mi5id787__2020-12-11_16-14-17.h5'
	config, manager, manager_modules = init_dataeval(['-m', meas_path])
	time, valid_radar_mask, valid_reset_reason_data, valid_address_data = manager_modules.calc('calc_flr25_crash_events@aebs.fill', manager)
	print (time, valid_radar_mask, valid_reset_reason_data, valid_address_data)
