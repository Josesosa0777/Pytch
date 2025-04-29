# -*- dataeval: init -*-
import logging
import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity

logger = logging.getLogger('fillFLR25_ACC')

INVALID_ID = -1


class cFill(iObjectFill):
		dep = 'fill_flr25_acc_track', 'calc_egomotion'

		def check(self):
				modules = self.get_modules()
				tracks = modules.fill("fill_flr25_acc_track")
				ego_orig = modules.fill("calc_egomotion")
				egomotion = ego_orig.rescale(tracks.time)
				return tracks, egomotion

		def fill(self, tracks, egomotion):
				import time
				start = time.time()
				logger.info("FLR25 ACC object retrieval is started, Please wait...")

				# create object
				objects = []
				for id, track in tracks.iteritems():
						o = {}
						track.object_id.data[track.object_id.mask] = 0
						o["id"] = np.where(track.dx.mask, INVALID_ID, track.object_id)
						o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask
						o["label"] =np.array( ["FLR25_ACC_%d" %id for id in o["id"]] )
						track.dx.data[track.dx.mask] = 0
						track.dy.data[track.dy.mask] = 0
						o["dx"] = track.dx.data
						o["dy"] =  track.dy.data
						o["type"] = np.where(track.dx.mask,
																 self.get_grouptype('NONE_TYPE'),
																 np.where(track.mov_state.moving,
																					self.get_grouptype('FLR25_ACC_MOV'),
																					np.where(track.mov_state.stopped,
																									 self.get_grouptype('FLR25_ACC_STOPPED'),
																									 self.get_grouptype('FLR25_ACC_STAT'))
																					)
																 )
						init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
						o["init"] = intervalsToMask(init_intervals, track.dx.size)
						o["color"] = colorByVelocity(egomotion.vx, track.vx, [0, 255, 0], [255, 0, 0], [0, 0, 255])

						# Object Kinematic
						track.vx.data[track.vx.mask] = 0
						track.vy.data[track.vy.mask] = 0
						track.ax.data[track.ax.mask] = 0

						o["ax_abs"] = track.ax_abs.data
						o["ax"] = track.ax.data

						o["vx_abs"] = track.vx_abs.data
						o["vy_abs"] = track.vy_abs.data
						o["vx"] = track.vx.data
						o["vy"] = track.vy.data

						o["lane"] = track.lane.join()
						o["mov_state"] = track.mov_state.join()
						o["obj_type"] = track.obj_type.join()
						o["measured_by"] = track.measured_by.join()
						objects.append(o)

				done = time.time()
				elapsed = done - start
				logger.info("FLR25 ACC object retrieval is completed in " + str(elapsed) + " seconds")
				return tracks.time, objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6168\shared-drive\measurements\ACC_evaluation\acc_evaluation\BendixTruck__2021-01-30_07-05-03.mat"
		# meas_path = r"\\pu2w6168\shared-drive\measurements\ACC_evaluation\UFO__2021-01-29_06-09-17.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		time,objects = manager_modules.calc('fillFLR25_ACC@aebs.fill', manager)
		print(objects)
