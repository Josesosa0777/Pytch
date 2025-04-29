# -*- dataeval: init -*-

import numpy as np
from fillFLR20 import INVALID_TRACK_ID
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity

INVALID_ID = -1

class cFill(iObjectFill):
		dep = 'fill_flr25_aeb_track', 'calc_egomotion'

		def check(self):
				modules = self.get_modules()
				track = modules.fill("fill_flr25_aeb_track")
				ego_orig = modules.fill("calc_egomotion")
				egomotion = ego_orig.rescale(track.time)
				return track, egomotion

		def fill(self, track, egomotion):
				# create object
				o = {}
				track.object_id.data[track.object_id.mask] = 0
				o["id"] = np.where(track.dx.mask, INVALID_ID, track.object_id) # np.where(track.id.mask, INVALID_TRACK_ID, track.id.data)
				o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask
				o["label"] = np.array( ["FLR25_AEB_%d" %id for id in o["id"]] )
				track.dx.data[track.dx.mask] = 0
				track.dy.data[track.dy.mask] = 0
				o["dx"] = track.dx.data
				o["dy"] = track.dy.data
				o["type"] = np.where(track.id.mask,
						self.get_grouptype('NONE_TYPE'),
						self.get_grouptype('FLR25_AEB'))
				init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
				o["init"] = intervalsToMask(init_intervals, track.dx.size)
				o["color"] = colorByVelocity(egomotion.vx, track.vx, [0, 255, 0], [255, 0, 0], [0, 0, 255])
				track.vx.data[track.vx.mask] = 0
				track.vy.data[track.vy.mask] = 0
				track.ax.data[track.ax.mask] = 0

				o["ax_abs"] = track.ax_abs.data
				o["ax"] = track.ax.data

				#o["vx_abs"] = track.vx_abs.data
				#o["vy_abs"] = track.vy_abs.data
				o["vx"] = track.vx.data
				o["vy"] = track.vy.data

				#o["lane"] = track.lane.join()
				o["mov_state"] = track.mov_state.join()
				#o["obj_type"] = track.obj_type.join()
				o["measured_by"] = track.measured_by.join()
				objects = [o]
				return track.time, objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6168\shared-drive\measurements\ACC_evaluation\acc_evaluation\BendixTruck__2021-01-30_07-05-03.mat"
		# meas_path = r"\\pu2w6168\shared-drive\measurements\ACC_evaluation\UFO__2021-01-29_06-09-17.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		time,objects = manager_modules.calc('fillFLR25_AEB@aebs.fill', manager)
		print(objects)