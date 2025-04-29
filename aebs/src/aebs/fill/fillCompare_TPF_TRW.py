# -*- dataeval: init -*-
import logging

import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity
from pyutils.cache_manager import get_modules_cache, store_modules_cache

logger = logging.getLogger('fillFLC25_CEM_TPF')

INVALID_ID = 255
INVALID_TRACK_ID = -1


class cFill(iObjectFill):
		dep = 'fill_flc25_cem_tpf_tracks', 'calc_egomotion', 'fill_flr20_raw_tracks',

		def check(self):
				modules = self.get_modules()
				tpf_raw_tracks, _ = modules.fill("fill_flc25_cem_tpf_tracks")
				ego_orig = modules.fill("calc_egomotion")
				trw_raw_tracks = modules.fill("fill_flr20_raw_tracks")

				egomotion = ego_orig.rescale(tpf_raw_tracks.time)
				return tpf_raw_tracks, egomotion, trw_raw_tracks

		def fill(self, tpf_rw_tracks, egomotion, trw_raw_tracks):
				import time
				start = time.time()
				logger.info("TPF TRW object retrieval is started, Please wait...")
				tpf_objects = []
				for id, track in tpf_rw_tracks.iteritems():
						o = {}
						o["id"] = np.where(track.dx.mask, INVALID_ID, id)
						o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask

						object_type = np.empty(track.dx.shape, dtype='string')
						object_type[:] = 'U'
						car = np.where(track.obj_type.car, 1, 0)
						truck = np.where(track.obj_type.truck, 2, 0)
						motorcycle = np.where(track.obj_type.motorcycle, 3, 0)
						pedestrian = np.where(track.obj_type.pedestrian, 4, 0)
						bicycle = np.where(track.obj_type.bicycle, 5, 0)
						unknown = np.where(track.obj_type.unknown, 6, 0)
						point = np.where(track.obj_type.point, 7, 0)
						wide = np.where(track.obj_type.wide, 8, 0)

						object_type[car == 1] = 'C'
						object_type[truck == 2] = 'T'
						object_type[motorcycle == 3] = 'M'
						object_type[pedestrian == 4] = 'P'
						object_type[bicycle == 5] = 'B'
						object_type[unknown == 6] = 'U'
						object_type[point == 7] = 'POINT'
						object_type[wide == 8] = 'WIDE'

						o["label"] = np.array(
								["FLC25_CEM_TPF_%d_%s" % (id, obj_type) for id, obj_type in zip(o["id"], object_type.data)])
						track.dx.data[track.dx.mask] = 0
						track.dy.data[track.dy.mask] = 0
						o["dx"] = track.dx.data
						o["dy"] = track.dy.data
						o["vx"] = track.vx.data
						o["vx_abs"] = track.vx_abs.data
						o["obj_type"] = track.obj_type.join()
						o["type"] = np.where(track.mov_state.stat.data & ~track.mov_state.stat.mask,
								self.get_grouptype('FLC25_CEM_TPF_STAT'),
								self.get_grouptype('FLC25_CEM_TPF_MOV'))
						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track.dx.size)
						# ongoing: green, stationary: red, oncoming: blue
						o["color"] = colorByVelocity(egomotion.vx, track.vx.data,
								[0, 255, 0], [255, 0, 0], [0, 0, 255])  # [R, G, B]

						o["alive_intervals"] = track.alive_intervals

						tpf_objects.append(o)

				trw_objects = []
				# loop through all tracks
				for id, track in trw_raw_tracks.iteritems():
						# create object
						o = {}
						o["id"] = np.where(track.dx.mask, INVALID_TRACK_ID, id)
						o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask
						o["dx"] = track.dx.data
						o["dy"] = track.dy.data
						o["vx"] = track.vx.data
						o["vx_abs"] = track.vx_abs.data
						o["alive_intervals"] = track.alive_intervals
						stationary = track.mov_state.stat.data & ~track.mov_state.stat.mask
						fused = track.fused.data & ~track.fused.mask
						o["type"] = np.where(track.dx.mask,
								self.get_grouptype('NONE_TYPE'),
								np.where(fused,
										np.where(stationary,
												self.get_grouptype('FLR20_FUSED_STAT'),
												self.get_grouptype('FLR20_FUSED_MOV'),
										),
										np.where(stationary,
												self.get_grouptype('FLR20_RADAR_ONLY_STAT'),
												self.get_grouptype('FLR20_RADAR_ONLY_MOV'),
										)
								)
						)
						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track.dx.size)
						# label
						label_fused = ["FLR20_%d_%d" % (i, j) for i, j in zip(o["id"], track.video_id.data)]
						label_radar_only = ["FLR20_%d" % id for id in o["id"]]
						o["label"] = np.where(fused, label_fused, label_radar_only)
						trw_objects.append(o)

				done = time.time()
				elapsed = done - start
				logger.info("TPF TRW object retrieval is completed in " + str(elapsed) + " seconds")
				return tpf_rw_tracks.time, trw_raw_tracks.time, tpf_objects, trw_objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6343\tool-share\eval_team\meas\conti\mfc525\Latest_data_from_gergely\2020-08-27\NY00__2020" \
								r"-08" \
								r"-27_08-26-14.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillFLC25_CEM_TPF@aebs.fill', manager)
		print(objects)
