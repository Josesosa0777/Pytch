# -*- dataeval: init -*-
import logging

import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity

logger = logging.getLogger('fillSLR25_Front')

INVALID_ID = 255


class cFill(iObjectFill):
		dep = 'fill_slr25_front_tracks', 'calc_egomotion'

		def check(self):
				modules = self.get_modules()
				tracks, signals = modules.fill("fill_slr25_front_tracks")
				ego_orig = modules.fill("calc_egomotion")
				egomotion = ego_orig.rescale(tracks.time)
				return tracks,signals, egomotion

		def fill(self, tracks,signals, egomotion):
				import time
				start = time.time()
				logger.info("SLR25 Front object retrieval is started, Please wait...")
				objects = []
				for id, track in tracks.iteritems():
						o = {}
						o["signal_mapping"] = {}
						if isinstance(id, int):
							o["id"] = np.where(track.dx.mask, INVALID_ID, id)

							o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask

							object_type = np.empty(track.dx.shape, dtype = 'string')
							object_type[:] = 'U'

							temp_object_type = np.empty(track.dx.shape, dtype = 'int')
							temp_object_type[:] = 5

							car = np.where(track.obj_type.car, 1, 0)
							truck = np.where(track.obj_type.truck, 2, 0)
							motorcycle = np.where(track.obj_type.motorcycle, 3, 0)
							pedestrian = np.where(track.obj_type.pedestrian, 4, 0)
							bicycle = np.where(track.obj_type.bicycle, 5, 0)
							unknown = np.where(track.obj_type.unknown, 6, 0)
							point = np.where(track.obj_type.point, 7, 0)
							wide = np.where(track.obj_type.wide, 8, 0)
							mirror =np.where(track.obj_type.mirror, 9, 0)
							multiple = np.where(track.obj_type.multiple, 10, 0)
							initialized = np.where(track.obj_type.initialized, 11, 0)

							object_type[car == 1] = 'C'
							object_type[truck == 2] = 'T'
							object_type[motorcycle == 3] = 'M'
							object_type[pedestrian == 4] = 'P'
							object_type[bicycle == 5] = 'B'
							object_type[unknown == 6] = 'U'
							object_type[point == 7] = 'D'
							object_type[wide == 8] = 'W'
							object_type[mirror==9] = 'G'
							object_type[multiple==10] = 'X'
							object_type[initialized==11] = 'I'

							temp_object_type[car == 1] = 0
							temp_object_type[truck == 2] = 1
							temp_object_type[motorcycle == 3] = 2
							temp_object_type[pedestrian == 4] = 3
							temp_object_type[bicycle == 5] = 4
							temp_object_type[unknown == 6] = 5
							temp_object_type[point == 7] = 6
							temp_object_type[wide == 8] = 7
							temp_object_type[mirror == 9] = 8
							temp_object_type[multiple == 10] = 9
							temp_object_type[initialized == 11] = 10

							# o["label"] = np.array(
							# 				["SLR25_Front_%d_%s" % (idx, obj_type) for idx, obj_type in zip(o["id"], object_type.data)])
							o["label"] = np.array(
											["SLR25_Front" for idx, obj_type in zip(o["id"], object_type.data)])
							track.dx.data[track.dx.mask] = 0
							track.dy.data[track.dy.mask] = 0
							o["dx"] = track.dx.data
							o["signal_mapping"]["dx"] = signals[id][0]["fDistX"]
							# o["dx_std"] = track.dx.data
							# o["signal_mapping"]["dx_std"] = signals[id][0]["fDistXStd"]
							o["dy"] = track.dy.data
							o["signal_mapping"]["dy"] = signals[id][0]["fDistY"]
							# o["dy_std"] = track.dy.data
							# o["signal_mapping"]["dy_std"] = signals[id][0]["fDistYStd"]
							o["type"] = np.where(track.mov_state.stat.data & ~track.mov_state.stat.mask,
																	 self.get_grouptype('SLR25_Front_STAT'),
																	 self.get_grouptype('SLR25_Front_MOV'))
							o["signal_mapping"]["type"] = signals[id][0]["eDynamicProp"]
							init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
							o["init"] = intervalsToMask(init_intervals, track.dx.size)
							# ongoing: green, stationary: red, oncoming: blue
							o["color"] = colorByVelocity(egomotion.vx, track.vx.data,[0, 255, 0], [255, 0, 0], [0, 0, 255])  # [R, G, B]
							o["ax_std"] = track.ax_std.data
							o["signal_mapping"]["ax_std"] = signals[id][0]["fArelXStd"]
							o["ay_std"] = track.ay_std.data
							o["signal_mapping"]["ay_std"] = signals[id][0]["fArelYStd"]
							o["ax"] = track.ax.data
							o["signal_mapping"]["ax"] = signals[id][0]["fArelX"]
							o["ay"] = track.ay.data
							o["signal_mapping"]["ay"] = signals[id][0]["fArelY"]
							# o["vx_abs"] = track.vx_abs.data
							# o["signal_mapping"]["vx_abs"] = signals[id][0]["fVabs"]
							o["vx"] = track.vx.data
							o["signal_mapping"]["vx"] = signals[id][0]["fVrelX"]
							o["vy"] = track.vy.data
							o["signal_mapping"]["vy"] = signals[id][0]["fVrelY"]


							o["mov_state"] = track.mov_state.join()
							o["signal_mapping"]["mov_state"] = signals[id][0][
								"eDynamicProp"]
							o["video_conf"] = track.video_conf.data
							o["signal_mapping"]["video_conf"] = signals[id][0][
								"fProbOfExist"]

							o["obj_type"] = temp_object_type
							o["signal_mapping"]["obj_type"] = signals[id][0][
								"eObjType"]


							o["custom_labels"] = {'video_conf': 'Probability Of Existence',}
							o["obj_type_mapping"] = {0:'car', 1:'truck', 2:'motorcycle', 3:'pedestrian', 4:'bicycle',5: 'unknown', 6:'point', 7:'wide',8:'mirror',9:'multiple' , 10:'initialized'}
							o['BSD5_LatDispMIOFront_D0'] = tracks['BSD5_LatDispMIOFront_D0']
							o['BSD5_LonDispMIOFront_D0'] = tracks['BSD5_LonDispMIOFront_D0']
							objects.append(o)
				done = time.time()
				elapsed = done - start
				logger.info("SLR25 Front object retrieval is completed in " + str(elapsed) + " seconds")
				return tracks.time, objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\pytch2_development\SRR_eval\meas\2024-08-28\mi5id5506__2024-08-28_14-51-16.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillSLR25_Front@aebs.fill', manager)
		print(objects)
