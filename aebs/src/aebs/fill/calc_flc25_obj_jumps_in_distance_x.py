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


class cFill(iCalc):
		dep = ('fill_flc25_cem_tpf_tracks','fill_flc25_aoa_acc_tracks','fill_flc25_aoa_aebs_tracks',)

		def check(self):
				modules = self.get_modules()
				tracks = modules.fill("fill_flc25_cem_tpf_tracks")[0]
				acc_obj_id = modules.fill("fill_flc25_aoa_acc_tracks")[0]['object_id']
				aebs_obj_id = modules.fill("fill_flc25_aoa_aebs_tracks")[0]['object_id']
				return tracks, acc_obj_id, aebs_obj_id

		def fill(self, tracks, acc_obj_id, aebs_obj_id):
				timestamps = tracks.time
				a_objects_dx_data = []

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

						valid_obj_mask = (dist_mask & lane_mask & valid_interval_mask & valid & range_mask & motion_mask)

						valid_indices = np.flatnonzero(valid_obj_mask)
						near_time = 250
						for id in valid_indices:
							if id > near_time:
								func_obj_ids = np.unique(np.concatenate((acc_obj_id[id-near_time:id], aebs_obj_id[id-near_time:id]), axis=None))
								if obj_id[id] not in func_obj_ids:
									valid_obj_mask[id] = False

						o['id'] = obj_id
						o['object_delta_distx'] = delta_distx
						o['object_distx_value'] = obj.dx.data
						o['valid_object_distx_mask'] = valid_obj_mask
						o['object_delta_disty'] = delta_disty
						o['object_disty_value'] = obj.dy.data

						a_objects_dx_data.append(o)

				return timestamps, a_objects_dx_data

if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\corp.knorr-bremse.com\str\measure\DAS\ConvertedMeas_Xcellis\UseCase\ACC\F30\NY00_787\FC212280_FU212020\mts_recording_20210823_1\2021-08-23\mi5id787__2021-08-23_11-17-03.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		tracks = manager_modules.calc('calc_flc25_obj_jumps_in_distance_x@aebs.fill', manager)
		print(tracks)