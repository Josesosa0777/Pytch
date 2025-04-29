# -*- dataeval: init -*-

from interface import iCalc
import numpy

sgn_group = [
	{
		"velocity": ("VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
	},
	{
		"velocity": ("ARS4xx Device.AlgoVehCycle.VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
	},

]
ACC_PED_SPEED_RANGE = (0.0, 4.0) # (lower_bound, upper_bound)m/s


class cFill(iCalc):

	def check(self):
		source = self.get_source()
		group = source.selectSignalGroup(sgn_group)
		return group

	def fill(self, group):
		time, velocity, unit = group.get_signal_with_unit('velocity')
		percentage_vehicle_in_speed_range = numpy.count_nonzero((velocity >= ACC_PED_SPEED_RANGE[0]) & (velocity <= ACC_PED_SPEED_RANGE[1])) / float(velocity.size)
		print(unit)
		return time, percentage_vehicle_in_speed_range


if __name__ == '__main__':
	from config.Config import init_dataeval

	meas_path = r"C:\KBData\__PythonToolchain\Meas\acc_ped_stop\2021-04-21\mi5id787__2021-04-21_13-07-33.mat"
	config, manager, manager_modules = init_dataeval(['-m', meas_path])
	flr25_common_time = manager_modules.calc('calc_vehicle_in_accped_speed_range@aebs.fill', manager)
	print flr25_common_time
