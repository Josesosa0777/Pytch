# -*- dataeval: init -*-
import copy

import numpy as np
from interface import iCalc
import math

TIME_TOLERANCE = 0.080
DELTA_VELOCITY_TOLERANCE = 10  # +/- 2
DISTANCE_TOLERANCE = 3


class cFill(iCalc):
		dep = ('fillCompare_TPF_TRW')

		def check(self):
				modules = self.get_modules()
				tpf_time, trw_time, tpf_objects, trw_objects = modules.fill("fillCompare_TPF_TRW")
				return trw_objects, tpf_objects, tpf_time, trw_time

		def fill(self, trw_objects, tpf_objects, tpf_time, trw_time):
				timestamps = tpf_time
				detected_objects_raw_data = []
				for index, track_object in enumerate(tpf_objects):
						for interval_start, interval_end in track_object["alive_intervals"]:
								alive_time = timestamps[interval_end - 1] - timestamps[interval_start]
								if alive_time >= 0.8:  # TRW was detecting an object for at least 1s mean TPF should be at least for 0.8
										detected_objects_raw_data.append(
												(index, alive_time, interval_start, interval_end, timestamps[interval_start], timestamps[interval_end - 1], 'TPF',
												track_object["vx_abs"],
												track_object["dx"],
												track_object["dy"],
												))  # track_object["obj_type"][interval_start:interval_end - 1]
#[interval_start:interval_end - 1]
				timestamps = trw_time
				for index, track_object in enumerate(trw_objects):
						for interval_start, interval_end in track_object["alive_intervals"]:
								alive_time = timestamps[interval_end - 1] - timestamps[interval_start]
								ActualType = track_object["type"][interval_start]
								if alive_time >= 1 and (ActualType == self.get_grouptype('FLR20_FUSED_STAT') or ActualType == self.get_grouptype('FLR20_FUSED_MOV')):  # TRW was detecting an object for at least 1s mean TPF should be at least for 0.8
										detected_objects_raw_data.append(
												(index, alive_time, interval_start, interval_end, timestamps[interval_start], timestamps[interval_end - 1], 'TRW',
												track_object["vx_abs"],
												track_object["dx"],
												track_object["dy"]))

				sorted_tracked_objects_change_raw_data = sorted(detected_objects_raw_data, key=lambda x: x[2])

				copy_sorted_tracked_objects_change_raw_data = copy.deepcopy(sorted_tracked_objects_change_raw_data)

				missing_tpf_with_respect_to_trw = []
				for track_id, alive_time, track_interval_start, track_interval_end, track_timestamp_start, track_timestamp_end, track_state, track_vx, track_dx, track_dy in \
								sorted_tracked_objects_change_raw_data:
						if track_state == 'TRW':
								TPF_FOUND = False
								distance_list_all_tpf = []
								distance_list_closest_tpf = []
								lower_bound = track_timestamp_start
								upper_bound = track_timestamp_start + (alive_time * 0.2)
								requred_alive_time = 0.8 * alive_time
								for internal_id, internal_alive_time, internal_interval_start, internal_interval_end, internal_timestamp_start, internal_timestamp_end, internal_state, internal_vx, internal_dx, internal_dy in \
												copy_sorted_tracked_objects_change_raw_data:
										# if internal_timestamp > track_end_timestamp:
										# 		break
										if (internal_state == 'TPF') and (upper_bound > internal_timestamp_start) and (internal_alive_time >= requred_alive_time):
												intersect_time = max(track_timestamp_start, internal_timestamp_start)
												tpf_idx = max(tpf_time.searchsorted(intersect_time, side='right') - 1, 0)
												trw_idx = max(trw_time.searchsorted(intersect_time, side='right') - 1, 0)
												distance = math.sqrt((internal_dx[tpf_idx] - track_dx[trw_idx]) ** 2 + (internal_dy[tpf_idx] - track_dy[trw_idx]) ** 2)
												delta_vx = abs(abs(internal_vx[tpf_idx]) - abs(track_vx[trw_idx]))
												distance_list_all_tpf.append((distance, delta_vx, internal_alive_time, track_dx[trw_idx], track_dy[trw_idx], (internal_id, internal_alive_time, internal_interval_start, internal_timestamp_start, internal_timestamp_end, internal_state, internal_vx, internal_dx, internal_dy)))
												if (distance < DISTANCE_TOLERANCE) and (delta_vx < DELTA_VELOCITY_TOLERANCE):
														TPF_FOUND = True
														distance_list_closest_tpf.append((distance, delta_vx, internal_alive_time, (internal_id, internal_alive_time, internal_interval_start, internal_interval_end, internal_timestamp_start, internal_timestamp_end, internal_state, internal_vx, internal_dx, internal_dy)))

								if TPF_FOUND:
										sorted_tpf_obj = sorted(distance_list_closest_tpf, key=lambda x: (x[0], x[1]))
										nearest_tpf_obj = sorted_tpf_obj[0][3]
										copy_sorted_tracked_objects_change_raw_data.remove(nearest_tpf_obj)
								else:
										nearest_tpf_obj_distance = None  # default None: No nearest TPF found
										nearest_tpf_obj_delta_vx = None  # default None: No nearest TPF found
										nearest_tpf_internal_id = None  # default None: No nearest TPF found
										nearest_tpf_obj_alive_time = None  # default None: No nearest TPF found
										track_dx_in = None
										track_dy_in = None
										if len(distance_list_all_tpf) > 0:
												sorted_tpf_obj_ = sorted(distance_list_all_tpf, key=lambda x: x[0])
												nearest_tpf_obj_distance = sorted_tpf_obj_[0][0]
												nearest_tpf_obj_delta_vx = sorted_tpf_obj_[0][1]
												nearest_tpf_obj_alive_time = sorted_tpf_obj_[0][2]
												track_dx_in = sorted_tpf_obj_[0][3]
												track_dy_in = sorted_tpf_obj_[0][4]
												nearest_tpf_internal_id = sorted_tpf_obj_[0][5][0]
										else:
												pass
										missing_tpf_with_respect_to_trw.append((track_timestamp_start, track_dx_in, track_dy_in, track_id, alive_time, nearest_tpf_internal_id, nearest_tpf_obj_delta_vx, nearest_tpf_obj_distance, nearest_tpf_obj_alive_time))
				return timestamps, missing_tpf_with_respect_to_trw


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\__PythonToolchain\Support\tasks\KPIs\trw_tpf\HMC-QZ-STR__2020-11-19_14-16-50.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		result = manager_modules.calc('calc_flc25_object_track_switchovers@aebs.fill', manager)
		print result
