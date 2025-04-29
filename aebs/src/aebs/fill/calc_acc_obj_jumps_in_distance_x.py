# -*- dataeval: init -*-
import numpy as np
from interface import iCalc
from numpy.core.fromnumeric import size

INVALID_ID = 255
EGO_ASSOCIATION_LANE = 0
DISTX_THRESHOLD = 2
FAR_RANGE = 50
OBJECT_PASSED = 0
MOTION_STATE_ONCOMING = 0
STABLE_TRACK_DURATION = 150
TRACK_CHANGE_DURATION = 1


def find_consecutive(x):
	"""Find consecutive items in an array."""

	x = np.asanyarray(x)
	if x.ndim != 1:
		raise ValueError('only 1D array supported')
	n = x.shape[0]

	if n == 0:
		return np.array([]), np.array([]), np.array([])

	else:
		loc_run_start = np.empty(n, dtype=bool)
		loc_run_start[0] = True
		np.not_equal(x[:-1], x[1:], out=loc_run_start[1:])
		run_starts = np.nonzero(loc_run_start)[0]

		run_values = x[loc_run_start]

		run_lengths = np.diff(np.append(run_starts, n))
		duration_mask = (run_lengths > STABLE_TRACK_DURATION)
		#duration_mask = np.append(duration_mask, False)
		indices = np.where(duration_mask == True)
		start_indices = run_starts[indices]
		end_indices = run_starts[indices] + run_lengths[indices]
		stable_track_mask = np.zeros(size(x), dtype = bool)
		for val in indices[0]:
			curr_id = run_values[val]
			if curr_id != 255:
				stable_track_mask[run_starts[val]+1:run_starts[val] + run_lengths[val]] = True
		return stable_track_mask
		

class cFill(iCalc):
		dep = ('fill_flc25_aoa_acc_tracks', 'fillFLC25_AOA_ACC')

		def check(self):
				modules = self.get_modules()
				time, tracks = modules.fill("fillFLC25_AOA_ACC")
				acc_track = modules.fill("fill_flc25_aoa_acc_tracks")[0]
				return tracks[0], acc_track, time
		def fill(self, tracks, acc_track, time):
				timestamps = time
				obj = tracks
				acc_obj_ids = acc_track.object_id
				acc_obj_dx = acc_track.dx.data
				a_objects_dx_data = []

				o = {}
				stable_track_mask = find_consecutive(obj["id"])
				#stable_track_mask = np.zeros(size(obj["id"]), dtype = bool)
				#stable_track_mask[event_indices] = True

				dx_range_mask = np.array([(dx < FAR_RANGE) & (dx > OBJECT_PASSED) if ~np.isnan(dx) else False for dx in obj["dx"]], dtype=bool)
				delta_distx = obj["dx"][1:] - obj["dx"][:-1]
				delta_distx = np.insert(delta_distx, 0, 0)
				distx_mask = np.array([dx > DISTX_THRESHOLD if ~np.isnan(dx) else False for dx in delta_distx], dtype=bool)

				delta_disty = obj["dy"][1:] - obj["dy"][:-1]
				delta_disty = np.insert(delta_disty, 0, 0)
				disty_mask = np.array([dy > DISTX_THRESHOLD if ~np.isnan(dy) else False for dy in delta_disty], dtype=bool)

				dist_mask = distx_mask | disty_mask
				range_mask = dx_range_mask
				
				valid = obj["valid"]

				valid_obj_mask = (dist_mask & valid & range_mask & stable_track_mask)

				o['id'] = obj["id"]
				o['object_delta_distx'] = delta_distx
				o['object_distx_value'] = obj["dx"]
				o['valid_object_distx_mask'] = valid_obj_mask
				o['object_delta_disty'] = delta_disty
				o['object_disty_value'] = obj["dy"]

				a_objects_dx_data.append(o)
				return timestamps, a_objects_dx_data
				'''
				for index, obj in tracks.iteritems():
						o = {}
						motion_mask = obj.mov_dir[MOTION_STATE_ONCOMING] == False
						lane_data = obj.lane.join()
						lane_mask = (lane_data == EGO_ASSOCIATION_LANE)

						dx_range_mask = np.array([(dx < FAR_RANGE) & (dx > OBJECT_PASSED) if ~np.isnan(dx) else False for dx in obj.dx.data], dtype=bool)
						delta_distx = obj.dx.data[1:] - obj.dx.data[:-1]
						delta_distx = np.insert(delta_distx, 0, 0)
						distx_mask = np.array([dx > DISTX_THRESHOLD if ~np.isnan(dx) else False for dx in delta_distx], dtype=bool)

						delta_disty = obj.dy.data[1:] - obj.dy.data[:-1]
						delta_disty = np.insert(delta_disty, 0, 0)
						disty_mask = np.array([dy > DISTX_THRESHOLD if ~np.isnan(dy) else False for dy in delta_disty], dtype=bool)

						dist_mask = distx_mask | disty_mask
						range_mask = dx_range_mask
						
						valid_interval_mask = np.zeros(size(dist_mask), dtype = bool)

						for interval in obj.alive_intervals:
								start, end = interval
								valid_interval_mask[start + 1:end - 1:1] = True
						obj_id = np.where(obj.dx.mask, INVALID_ID, index)
						valid = obj.tr_state.valid.data & ~obj.tr_state.valid.mask

						acc_obj_mask = (obj.id == acc_obj_ids)
						valid_obj_mask = (dist_mask & lane_mask & valid_interval_mask & valid & range_mask & motion_mask & acc_obj_mask)

						o['id'] = obj_id
						o['object_delta_distx'] = delta_distx
						o['object_distx_value'] = obj.dx.data
						o['valid_object_distx_mask'] = valid_obj_mask
						o['object_delta_disty'] = delta_disty
						o['object_disty_value'] = obj.dy.data

						a_objects_dx_data.append(o)
				return timestamps, a_objects_dx_data
				'''
				
		
		
if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\corp.knorr-bremse.com\str\measure\DAS\ConvertedMeas_Xcellis\FER\ACC_F30\FC212993_FU212450\2021-11-05\mi5id787__2021-11-05_13-46-44.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		tracks = manager_modules.calc('calc_acc_obj_jumps_in_distance_x@aebs.fill', manager)
		print(tracks)