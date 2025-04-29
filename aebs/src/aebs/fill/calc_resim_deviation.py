# -*- dataeval: init -*-
import logging

from interface import iCalc
from measparser.SignalSource import cSignalSource
import numpy as np
import os
from measproc.IntervalList import maskToIntervals
from measparser import signalproc

class cFill(iCalc):
		sgn_group = [  # TODO change these signal groups as per availabilities of signals in resim meas
				{
						"engspeed": ("EEC1_00_s00", "EngineSpeed"),

				},
				{
						"engspeed": ("EEC1", "EngineSpeed_s00"),

				},
				{
						"engspeed": ("EEC1_s00", "EngSpeed"),

				},
				{
						"engspeed": ("EEC1_00_s00_EEC1_00_CAN21_4_4_idx84064", "EngineSpeed"),
				},
				{
						"engspeed": ("EEC1_00", "EEC1_EngSpd_00"),
				},
				{
						"engspeed": ("EEC1_00_s00_EEC1_00_CAN20_4_4_idx85179", "EngineSpeed"),
				},
				{
						"engspeed": ("EEC1_00", "EngineSpeed_s00"),
				},
				{
						"engspeed": ("EEC1_00", "EEC1_EngSpd_00_s00"),
				},
				{
						"engspeed": ("EEC1_00_s00", "EEC1_EngSpd_00"),
				},
				{
						"engspeed": ("EEC1_00","EngineSpeed_s00"),
				},
				{
						"engspeed": ("EEC1","EngSpeed_s00"),
				},
				{	"engspeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
							  "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EEC1_EEC1_EngSpd"),
				}
		]

		def check(self):
				# Load resim source meas
				resim_source = self.get_source()
				resim_group = resim_source.selectSignalGroup(self.sgn_group)
				# Load original source meas
				self.original_source_name = os.path.join(os.path.dirname(resim_source.FileName), "source",
				                                    resim_source.BaseName.replace("_tsrresim", ""))
				if not os.path.isfile(self.original_source_name):
						return None, None

				original_source = cSignalSource(self.original_source_name)
				original_group = original_source.selectSignalGroup(self.sgn_group)

				return resim_group, original_group

		def fill(self, resim_group, original_group):
				import kbtools
				actual_deviation = 0
				if resim_group is None:
						logging.warning(
										"Source measurement missing from measrootpath/source, Ignore this warning if it is not "
										"resimulation "
										"report generation")
						return actual_deviation, 0

				# Rescale all signals to common signal length
				# Use cross-correlation to find lag
				self.t_original_engspd, self.v_original_engspd = original_group.get_signal("engspeed")
				self.t_resim_engspd, self.v_resim_engspd = resim_group.get_signal("engspeed")

				self.getCommonTime()
				self.rescaleSignals()
				actual_deviation, common_index_point = self.getActualDeviationUsingArgWhere()
				logging.info("====== Actual deviation = {} seconds ===========".format(actual_deviation))
				return actual_deviation, common_index_point

		def getCommonTime(self):
				# Get maximum sampled signal
				pass

		def rescaleSignals(self):
				pass
				# _, value_rescale = signalproc.rescale(self.t_original_engspd, self.v_original_engspd, self.t_original_accel)

		def getActualDeviationUsingArgWhere(self):
				common_index_point = 0
				window_size = 400 #len(self.v_resim_engspd) // 10 # one tenth of total size
				logging.info("Sliding window size {}".format(window_size))
				resim_engspd_window = self.v_resim_engspd[:window_size]
				for i in range(len(self.v_original_engspd) - window_size):
						if np.array_equal(resim_engspd_window, self.v_original_engspd[i:i + window_size]):
								common_index_point = i
								logging.info("Common point found at index: {}".format(i))
								break
				if common_index_point ==0:
					logging.info("Common point not found using windowing logic........... ")

				# Using another method
				# Find  diff i.e delta between max value from original/src and resim signal
				resim_signal_duration=self.t_resim_engspd[-1] - self.t_resim_engspd[0]
				org_signal_duration=self.t_original_engspd[-1] - self.t_original_engspd[0]
				diff_org_resim_duration=org_signal_duration-resim_signal_duration

				logging.info("Difference in signal duration: {} sec".format(org_signal_duration-resim_signal_duration))
				logging.info("Resim signal duration: {} sec".format(self.t_resim_engspd[-1] - self.t_resim_engspd[0]))
				logging.info("Original signal duration: {} sec".format(self.t_original_engspd[-1] - self.t_original_engspd[0]))

				if diff_org_resim_duration > 0 and diff_org_resim_duration > (org_signal_duration/2):
					logging.warning("{}: Signal is shorter than video .........".format(self.original_source_name))
					logging.warning("Keep this measurement data outside of the KPI calculation")

				resim_max_value_at = self.t_resim_engspd[np.argmax(self.v_resim_engspd >= max(self.v_resim_engspd))] - \
									 self.t_resim_engspd[0]  # 197.97428
				original_max_value_at = self.t_original_engspd[
											np.argmax(self.v_original_engspd >= max(self.v_original_engspd))] - \
										self.t_original_engspd[0]  # 198.34729981
				delta = original_max_value_at - resim_max_value_at
				logging.info("Using max logic, delta: {} seconds".format(delta))
				cycle_time = self.t_original_engspd[1] - self.t_original_engspd[0]

				try:
					delta_indexes = int(delta // cycle_time)
					logging.info("Using max logic, delta index: {} indexes".format(delta_indexes))
				except Exception as e:
					pass

				delta_using_windowing = self.t_original_engspd[common_index_point] - self.t_original_engspd[0]
				logging.info("Using windowing logic, delta: {} seconds".format(delta_using_windowing))
				if delta < 0:
					delta = 0
					#raise ValueError("Please check measurement and Video file durations of Resim and Original")

				#If delta not found using windowing method use other method
				if delta_using_windowing == 0:
						delta_using_windowing = delta
				return delta_using_windowing, 0

				#self.t_original_engspd[common_index_point] - self.t_original_engspd[0], common_index_point
				#return <deviation_time: Used in postmarker point shifting>, <deviation_index: Used in conti data shifting>
				#TODO: Enable or disable shifting by passing zero or value

# If video size is greater than signal size.. check if signal_size

if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"X:\TSR\Resim\FC222150\USA\00_files_needs_to_check\2021-10-29\mi5id5321__2021-10-29_12-32-08_tsrresim.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		flr25_common_time = manager_modules.calc('calc_resim_deviation@aebs.fill', manager)
		print flr25_common_time
