# -*- dataeval: init -*-

"""
:Organization: KNORR-BREMSE Technology Center India Private Limited
:Type:
		Calc script
:Sensors:
	FLC25
:ECU Port:
	CEM_TPF
:Usage:
		- Find out scenarios where same physical object ID changes it ID
:Background:
		Continental MFC525 Camera is used for detection of objects in front of vehicles.
		MFC525 stores detected objects in object arrays[Maximum 100] internally with IDs 0-99.
		These IDs are automatically assigned to the detected objects by continental camera software.
		KB functions are highly dependent upon object IDs. So changing object IDs while vehicle is
		running for same detected object can hamper ACC or other main functions. So idea is to
		find out scenarios where same physical object ID changes it ID.
:Output:
	dictionary output
	track_switchovers[(current_index, previous_index)] =
	((
	(current_id, current_index,current_timestamp,current_state, current_vx,current_vx_abs,current_dx, current_dy),
	internal_id,previous_index,previous_timestamp,previous_state,previous_vx,previous_vx_abs,previous_dx,previous_dy
	)))
Algorithm:
		- Check if Object is in EGO Lane (eLaneAssociation)
		- Define a DistY +/- range (to not rely on Conti lane assosiation)
		- Check that Objects are valid DistX > 0.0
		- Find end of it's life cycle
		- Calculate search window for possible distances with the rel velocity (+/- 5sec)
		- Check if new object is in the search window
:Dependency:
		fill_flc25_cem_tpf_tracks@aebs.fill
.. image:: ../images/calc_flc25_object_track_switchovers_1.png
   :height: 200px
   :width: 200px
   :scale: 50%
   :alt: Plot Output
   :align: left
"""

import copy

import numpy as np
from interface import iCalc

TRACK_SWITCH_TIME = 0.300
VELOCITY_TOLERANCE = 0.020
FAR_RANGE = 100


class cFill(iCalc):
		dep = ('fill_flc25_cem_tpf_tracks','fill_flc25_aoa_acc_tracks')

		def check(self):
				modules = self.get_modules()
				track_objects = modules.fill("fill_flc25_cem_tpf_tracks")[0]
				acc_obj = modules.fill("fill_flc25_aoa_acc_tracks")[0]
				return track_objects, acc_obj

		def fill(self, track_objects, acc_obj):
				timestamps = track_objects.time
				acc_id = acc_obj.object_id
				tracked_objects_change_raw_data = []
				for index, track_object in track_objects.iteritems():
						for interval_start, interval_end in track_object.alive_intervals:
								ego_lane_vehicles = np.any(((track_object.dy[interval_start:interval_end]) < 2) & (
												(track_object.dy[interval_start:interval_end]) > -2))
								if ego_lane_vehicles:
										if track_object.vx_abs[interval_start] > 0:
												tracked_objects_change_raw_data.append(
																(index, interval_start, timestamps[interval_start], 'start',
																 track_object.vx[interval_start:interval_end - 1],
																 track_object.vx_abs[interval_start:interval_end - 1],
																 track_object.dx[interval_start:interval_end - 1],
																 track_object.dy[interval_start:interval_end - 1]))
												tracked_objects_change_raw_data.append(
																(index, interval_end - 1, timestamps[interval_end - 1], 'end',
																 track_object.vx[interval_start:interval_end - 1],
																 track_object.vx_abs[interval_start:interval_end - 1],
																 track_object.dx[interval_start:interval_end - 1],
																 track_object.dy[interval_start:interval_end - 1]))
				sorted_tracked_objects_change_raw_data = sorted(tracked_objects_change_raw_data, key = lambda x: x[1])

				copy_sorted_tracked_objects_change_raw_data = copy.deepcopy(sorted_tracked_objects_change_raw_data)

				track_switchovers = {}
				for track_id, track_index, track_timestamp, track_state, track_vx, track_vx_abs, track_dx, track_dy in \
								sorted_tracked_objects_change_raw_data:
						if track_state == 'end':
								track_end_timestamp = track_timestamp + TRACK_SWITCH_TIME
								for internal_id, internal_track_index, internal_timestamp, internal_state, internal_vx, \
										internal_vx_abs, internal_dx, internal_dy in \
												copy_sorted_tracked_objects_change_raw_data:
										if internal_timestamp > track_end_timestamp:
												break
										if internal_timestamp < track_timestamp:
												continue
										if internal_state == 'start':
												if len(internal_vx_abs) != 0 and len(track_vx_abs) != 0:
														if abs(track_vx_abs[-1] - internal_vx_abs[0]) < VELOCITY_TOLERANCE:
																if internal_track_index > track_index:
																		if internal_dx[0] < FAR_RANGE:
																			if acc_id[track_index] == track_id or acc_id[internal_track_index] == internal_id:
																				track_switchovers[(track_index, internal_track_index)] = (((track_id, track_index,
																																														track_timestamp,
																																														track_state, track_vx[-1],
																																														track_vx_abs[-1],
																																														track_dx[-1], track_dy[
																																																-1]),
																																													 (internal_id,
																																														internal_track_index,
																																														internal_timestamp,
																																														internal_state,
																																														internal_vx[0],
																																														internal_vx_abs[0],
																																														internal_dx[0],
																																														internal_dy[0])))
				return timestamps, track_switchovers


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\corp.knorr-bremse.com\str\measure\DAS\ConvertedMeas_Xcellis\FER\ACC_F30\FC212520_FU212450\2021-09-14\mi5id787__2021-09-14_15-18-34.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		result = manager_modules.calc('calc_acc_object_track_switchovers@aebs.fill', manager)
		print result
