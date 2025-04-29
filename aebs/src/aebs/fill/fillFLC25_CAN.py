# -*- dataeval: init -*-
import logging

import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity
from pyutils.cache_manager import get_modules_cache, store_modules_cache

logger = logging.getLogger('fillFLC25_CAN')

INVALID_ID = 254


class cFill(iObjectFill):
		dep = 'fill_flc25_can_tracks', 'calc_egomotion'

		def check(self):
				modules = self.get_modules()
				tracks, signals = modules.fill("fill_flc25_can_tracks")
				ego_orig = modules.fill("calc_egomotion")
				egomotion = ego_orig.rescale(tracks.time)
				return tracks,signals, egomotion

		def fill(self, tracks,signals, egomotion):
				import time
				start = time.time()
				logger.info("Retrieving FLC25 CAN objects, Please wait...")
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

						o["label"] = np.array(["FLC25_CAN%d_%s" % (idx, obj_type) for idx, obj_type in zip(o["id"], object_type.data)])
						track.dx.data[track.dx.mask] = 0
						track.dy.data[track.dy.mask] = 0
						o["dx"] = track.dx.data
						o["signal_mapping"]["dx"] = signals[id]["RelDistX"]
						o["dy"] = track.dy.data
						o["signal_mapping"]["dy"] = signals[id]["RelDistY"]
						o["type"] = np.where(track.mov_state.stat.data & ~track.mov_state.stat.mask,
																 self.get_grouptype('FLC25_CAN_STAT'),
																 self.get_grouptype('FLC25_CAN_MOV'))
						o["signal_mapping"]["type"] = signals[id]["DynState"]
						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track.dx.size)
						# ongoing: green, stationary: red, oncoming: blue
						o["color"] = colorByVelocity(egomotion.vx, track.vx.data,
																				 [0, 255, 0], [255, 0, 0], [0, 0, 255])  # [R, G, B]

						o["ax"] = track.ax.data
						o["signal_mapping"]["ax"] = signals[id]["RelAccX"]
						o["vx"] = track.vx.data
						o["signal_mapping"]["vx"] = signals[id]["RelVelX"]
						o["vy"] = track.vy.data
						o["signal_mapping"]["vy"] = signals[id]["RelVelY"]
						o["ay"] = track.ay.data
						o["signal_mapping"]["ay"] = signals[id]["RelAccY"]
						# extra data
						o["width"] = track.width.data
						o["signal_mapping"]["width"] = signals[id]["TrackWidth"]
						o["mov_state"] = track.mov_state.join()
						o["signal_mapping"]["mov_state"] = signals[id][
							"DynState"]
						o["video_conf"] = track.video_conf.data
						o["signal_mapping"]["video_conf"] = signals[id]["Confidence"]
						o["obj_type"] = track.obj_type.join()
						o["signal_mapping"]["obj_type"] = signals[id][
							"Classification"]
						o["measured_by"] = track.measured_by.join()
						o["signal_mapping"]["measured_by"] = signals[id][
							"FusionState"]
						o["tracking_state"] = track.tracking_state.data
						o["signal_mapping"]["tracking_state"] = signals[id][
							"TrackingState"]
						o["cut_in_cut_out"] = track.cut_in_cut_out.data
						o["signal_mapping"]["cut_in_cut_out"] = signals[id][
							"CutInCutOut"]
						o["custom_labels"] = {'video_conf': 'Probability Of Existence'}
						objects.append(o)

				done = time.time()
				elapsed = done - start
				# logger.info("FLC25 CAN object retrieval is completed in " + str(elapsed) + " seconds")
				return tracks.time, objects

if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\hmc_issue\UnknownTruckId__2021-02-18_07-31-46.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillFLC25_CAN@aebs.fill', manager)
		print(conti)
