# -*- dataeval: init -*-
import logging

import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity
from pyutils.cache_manager import get_modules_cache, store_modules_cache

logger = logging.getLogger('fillFLC25_EM')

INVALID_ID = 255


class cFill(iObjectFill):
		dep = 'fill_flc25_em_tracks', 'calc_egomotion'

		def check(self):
				modules = self.get_modules()
				tracks, signals = modules.fill("fill_flc25_em_tracks")
				ego_orig = modules.fill("calc_egomotion")
				egomotion = ego_orig.rescale(tracks.time)
				return tracks, signals, egomotion

		def fill(self, tracks,signals, egomotion):
				import time
				start = time.time()
				logger.info("FLC25 EM object retrieval is started, Please wait...")
				objects = []
				# loop through all tracks
				for id, track in tracks.iteritems():
						# create object
						o = {}
						o["signal_mapping"] = {}
						o["id"] = np.where(track.dx.mask, INVALID_ID, id)
						o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask

						object_type = np.empty(track.dx.shape, dtype = 'string')
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
										["FLC25_EM_%d_%s" % (idx, obj_type) for idx, obj_type in zip(o["id"], object_type.data)])
						track.dx.data[track.dx.mask] = 0
						track.dy.data[track.dy.mask] = 0
						o["dx"] = track.dx.data
						o["signal_mapping"]["dx"] = signals[id][0]["fDistX"]
						o["dy"] = track.dy.data
						o["signal_mapping"]["dy"] = signals[id][0]["fDistY"]
						o["type"] = np.where(track.mov_state.stat.data & ~track.mov_state.stat.mask,
																 self.get_grouptype('FLC25_EM_STAT'),
																 self.get_grouptype('FLC25_EM_MOV'))
						o["signal_mapping"]["type"] = signals[id][0]["eDynamicProperty"]
						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track.dx.size)
						# ongoing: green, stationary: red, oncoming: blue
						o["color"] = colorByVelocity(egomotion.vx, track.vx.data,
																				 [0, 255, 0], [255, 0, 0], [0, 0, 255])  # [R, G, B]

						o["ax_abs"] = track.ax_abs.data
						o["signal_mapping"]["ax_abs"] = signals[id][0]["fAabsX"]
						o["ay_abs"] = track.ay_abs.data
						o["signal_mapping"]["ay_abs"] = signals[id][0]["fAabsY"]
						o["ax"] = track.ax.data
						o["signal_mapping"]["ax"] = signals[id][0]["fArelX"]
						o["ay"] = track.ay.data
						o["signal_mapping"]["ay"] = signals[id][0]["fArelY"]
						o["vx_abs"] = track.vx_abs.data
						o["signal_mapping"]["vx_abs"] = signals[id][0]["fVabsX"]
						o["vy_abs"] = track.vy_abs.data
						o["signal_mapping"]["vy_abs"] = signals[id][0]["fVabsY"]
						o["vx"] = track.vx.data
						o["signal_mapping"]["vx"] = signals[id][0]["fVrelX"]
						o["vy"] = track.vy.data
						o["signal_mapping"]["vy"] = signals[id][0]["fVrelY"]
						o["dx"] = track.dx.data
						o["signal_mapping"]["dx"] = signals[id][0]["fDistX"]
						o["dy"] = track.dy.data
						o["signal_mapping"]["dy"] = signals[id][0]["fDistY"]
						o["dx_std"] = track.dx_std.data
						o["signal_mapping"]["dx_std"] = signals[id][0]["fDistXStd"]
						o["dy_std"] = track.dy_std.data
						o["signal_mapping"]["dy_std"] = signals[id][0]["fDistYStd"]
						o["dz"] = track.dz.data
						o["signal_mapping"]["dz"] = signals[id][0]["fDistZ"]
						o["dz_std"] = track.dx_std.data
						o["signal_mapping"]["dz_std"] = signals[id][0]["fDistZStd"]
						o["yaw"] = track.yaw.data
						o["signal_mapping"]["yaw"] = signals[id][0]["fYaw"]
						o["yaw_std"] = track.yaw_std.data
						o["signal_mapping"]["yaw_std"] = signals[id][0]["fYawStd"]

						o["lane"] = track.lane.join()
						o["signal_mapping"]["lane"] = signals[id][0][
							"eAssociatedLane"]
						o["mov_state"] = track.mov_state.join()
						o["signal_mapping"]["mov_state"] = signals[id][0][
							"eDynamicProperty"]
						o["video_conf"] = track.video_conf.data
						o["signal_mapping"]["video_conf"] = signals[id][0][
							"uiProbabilityOfExistence"]
						o["lane_conf"] = track.lane_conf.data
						o["signal_mapping"]["lane_conf"] = signals[id][0][
							"uiAssociatedLaneConfidence"]
						o["obj_type"] = track.obj_type.join()
						o["signal_mapping"]["obj_type"] = signals[id][0][
							"eEbaObjClass"]
						o["custom_labels"] = {'video_conf': 'Probability Of Existence',"lane_conf" : "Associated Lane Confidence","lane" :"Associated Lane"}
						objects.append(o)

				done = time.time()
				elapsed = done - start
				# logger.info("FLC25 EM object retrieval is completed in " + str(elapsed) + " seconds")
				return tracks.time, objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path =  r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\hmc_issue\UnknownTruckId__2021-02-18_07-31-46.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillFLC25_EM@aebs.fill', manager)
		print(objects)
