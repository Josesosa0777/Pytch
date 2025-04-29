# -*- dataeval: init -*-
from interface import iCalc
import numpy as np


DISTANCE_THRESHOLD = 100
MOTION_STATE_ONCOMING = 2


class cFill(iCalc):
		dep = ('fill_flc25_cem_tpf_tracks','fill_flc25_aoa_acc_tracks')

		def check(self):
				modules = self.get_modules()
				track_objects = modules.fill("fill_flc25_cem_tpf_tracks")[0]
				acc_obj = modules.fill("fill_flc25_aoa_acc_tracks")[0]
				return track_objects, acc_obj
		def fill(self, track_objects, acc_obj):
				common_time = track_objects.time
				acc_id = acc_obj.object_id
				lane_changed_obj = []
				for ind, track_object in track_objects.iteritems():
						lane = track_object.lane.join()
						for interval_start, interval_end in track_object.alive_intervals:
								obj_life_time = track_object.time[interval_end - 1] - track_object.time[interval_start]
								if obj_life_time > 3:
										previous_lane_value = lane[interval_start]
										for current_index in range(interval_start + 1, interval_end):
												current_lane_value = lane[current_index]
												current_time_value = common_time[current_index]


												previous_index = current_index - 1
												previous_time_value = common_time[previous_index]

												if (previous_lane_value != current_lane_value):
														if (previous_lane_value == 0 and current_lane_value == 1):
																previous_time_value_before_1sec = max(current_time_value - 1, interval_start + 1)
																previous_index_before_1sec = max(
																				common_time.searchsorted(previous_time_value_before_1sec, side = 'right') - 1,
																				0)

																previous_dy_value_before_1sec = track_object.dy[previous_index_before_1sec]
																if (previous_dy_value_before_1sec > 2):
																		previous_lane_value_before_1sec = lane[previous_index_before_1sec]
																		if track_object.dx[current_index] < DISTANCE_THRESHOLD and track_object.mov_dir != MOTION_STATE_ONCOMING:
																			if (previous_lane_value_before_1sec != current_lane_value):
																					ids = [track_object.id[current_index], track_object.id[previous_index_before_1sec]]
																					if acc_id[current_index] in ids or acc_id[previous_index_before_1sec] in ids:
																						lane_changed_obj.append(
																										(
																												track_object.id[current_index],
																												previous_index, current_index,
																												previous_lane_value, current_lane_value,
																												previous_time_value, current_time_value,
																												track_object.dx[current_index],
																										)
																						)
																					break
														if (previous_lane_value == 0 and current_lane_value == 2):
																previous_time_value_before_1sec = max(current_time_value - 1, interval_start + 1)
																previous_index_before_1sec = max(
																				common_time.searchsorted(previous_time_value_before_1sec, side = 'right') - 1,
																				0)

																previous_dy_value_before_1sec = track_object.dy[previous_index_before_1sec]
																if (previous_dy_value_before_1sec > -2):
																		previous_lane_value_before_1sec = lane[previous_index_before_1sec]
																		if track_object.dx[current_index] < DISTANCE_THRESHOLD and track_object.mov_dir != MOTION_STATE_ONCOMING:
																			if (previous_lane_value_before_1sec != current_lane_value):
																				ids = [track_object.id[current_index], track_object.id[previous_index_before_1sec]]
																				if acc_id[current_index] in ids or acc_id[previous_index_before_1sec] in ids:
																					lane_changed_obj.append(
																									(
																											track_object.id[current_index],
																											previous_index, current_index,
																											previous_lane_value, current_lane_value,
																											previous_time_value, current_time_value,
																											track_object.dx[current_index],
																									)
																					)
																					break
														if (previous_lane_value == 1 and current_lane_value == 0):
																previous_time_value_before_1sec = max(current_time_value - 1, interval_start + 1)
																previous_index_before_1sec = max(
																				common_time.searchsorted(previous_time_value_before_1sec, side = 'right') - 1,
																				0)

																previous_dy_value_before_1sec = track_object.dy[previous_index_before_1sec]
																if (previous_dy_value_before_1sec > -2 and previous_dy_value_before_1sec < 2):
																		previous_lane_value_before_1sec = lane[previous_index_before_1sec]
																		if track_object.dx[current_index] < DISTANCE_THRESHOLD and track_object.mov_dir != MOTION_STATE_ONCOMING:
																			if (previous_lane_value_before_1sec != current_lane_value):
																				ids = [track_object.id[current_index], track_object.id[previous_index_before_1sec]]
																				if acc_id[current_index] in ids or acc_id[previous_index_before_1sec] in ids:
																					lane_changed_obj.append(
																									(
																											track_object.id[current_index],
																											previous_index, current_index,
																											previous_lane_value, current_lane_value,
																											previous_time_value, current_time_value,
																											track_object.dx[current_index],
																									)
																					)
																					break
														if (previous_lane_value == 2 and current_lane_value == 0):
																previous_time_value_before_1sec = max(current_time_value - 1, interval_start + 1)
																previous_index_before_1sec = max(
																				common_time.searchsorted(previous_time_value_before_1sec, side = 'right') - 1,
																				0)

																previous_dy_value_before_1sec = track_object.dy[previous_index_before_1sec]
																if (previous_dy_value_before_1sec > -2 and previous_dy_value_before_1sec < 2):
																		previous_lane_value_before_1sec = lane[previous_index_before_1sec]
																		if track_object.dx[current_index] < DISTANCE_THRESHOLD and track_object.mov_dir != MOTION_STATE_ONCOMING:
																			if (previous_lane_value_before_1sec != current_lane_value):
																				ids = [track_object.id[current_index], track_object.id[previous_index_before_1sec]]
																				if acc_id[current_index] in ids or acc_id[previous_index_before_1sec] in ids:
																					lane_changed_obj.append(
																									(
																											track_object.id[current_index],
																											previous_index, current_index,
																											previous_lane_value, current_lane_value,
																											previous_time_value, current_time_value,
																											track_object.dx[current_index],
																									)
																					)
																					break
												previous_lane_value = current_lane_value

				return common_time, lane_changed_obj


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\mat_testing\ld_output_test\MC41__2021-06-01_09-53-10.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		result = manager_modules.calc('calc_acc_object_lane_change@aebs.fill', manager)
		print result
