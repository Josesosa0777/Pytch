# -*- dataeval: init -*-

import numpy as np
from fillFLR20 import INVALID_TRACK_ID
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity
from measproc.IntervalList import maskToIntervals

INVALID_ID = -1

class cFill(iObjectFill):
		dep = 'calc_acc_ped_stop', 'calc_radar_egomotion-flr25'

		def check(self):
				modules = self.get_modules()
				track = modules.fill("calc_acc_ped_stop")
				ego_orig = modules.fill("calc_radar_egomotion-flr25")
				egomotion = ego_orig.rescale(track["time"])
				return track, egomotion

		def fill(self, track, egomotion):
				# create object
				o = {}
				mask = track["dx"].mask

				alive_intervals = maskToIntervals(~track["dx"].mask)


				o["dx"] = track["dx"]
				o["dy"] = track["dy"]
				o["vx"] = track["vx_rel"]
				o["id"] = np.where(mask, INVALID_ID, 0)  # np.where(track.id.mask, INVALID_TRACK_ID, track.id.data)
				o["valid"] = ~mask
				o["label"] = np.array(["FLR25_ACC_PED_STOP_%d" % id for id in o["id"]])

				o["type"] = np.where(mask,
						self.get_grouptype('NONE_TYPE'),
						self.get_grouptype('FLR25_ACC_PED_STOP'))
				init_intervals = [(st, st + 1) for st, end in alive_intervals]
				o["init"] = intervalsToMask(init_intervals, len(track["time"]))
				o["color"] = colorByVelocity(egomotion.vx, o["vx"], [0, 255, 0], [255, 0, 0], [0, 0, 255])
				objects = [o]
				return track["time"], objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6168\shared-drive\measurements\ACC_evaluation\acc_evaluation\BendixTruck__2021-01-30_07-05-03.mat"
		# meas_path = r"\\pu2w6168\shared-drive\measurements\ACC_evaluation\UFO__2021-01-29_06-09-17.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		time,objects = manager_modules.calc('fillFLR25_AEB@aebs.fill', manager)
		print(objects)