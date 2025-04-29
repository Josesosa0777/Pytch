# -*- dataeval: init -*-
import logging
import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity

logger = logging.getLogger('fillGROUND_TRUTH')

INVALID_ID = 1


class cFill(iObjectFill):
		dep = 'fill_ground_truth_raw_tracks', 'calc_egomotion'

		def check(self):
				modules = self.get_modules()
				tracks = modules.fill("fill_ground_truth_raw_tracks")
				ego_orig = modules.fill("calc_egomotion")
				egomotion = ego_orig.rescale(tracks["time"])
				return tracks, egomotion

		def fill(self, tracks, egomotion):
				import time
				start = time.time()
				logger.info("Ground truth object retrieval is started, Please wait...")

				# create object
				objects = []
				object = {}
				object["id"] = np.zeros(tracks["dx"].shape, dtype = 'int')
				object["valid"] = tracks["tr_state"].valid.data & ~tracks["tr_state"].valid.mask
				object_type = np.empty(tracks["dx"].shape, dtype = 'string')
				object_type[:] = 'U'
				obj_type = np.ones(tracks["dx"].shape, dtype = 'int')
				gps = np.where(obj_type, 1, 0)
				object_type[gps == 1] = 'G'
				object["label"] =np.array( ["GT_FREEBOARD_%d" %id for id in object["id"]] )
				object["dx"] = tracks["dx"]
				object["dy"] = tracks["dy"]
				object["type"] = np.ones(tracks["dx"].shape, dtype = 'int')
				object["type" ][:]=  self.get_grouptype('GT_FREEBOARD_STAT')
				init_intervals = [(st, st + 1) for st, end in tracks["alive_intervals"]]
				object["init"] = intervalsToMask(init_intervals, tracks["dx"].size)
				object["color"] = colorByVelocity(egomotion.vx, tracks["vx"], [0, 255, 0], [255, 0, 0], [0, 0, 255])

				# Object Kinematic
				object["ax"] = tracks["ax"]
				object["ay"] = tracks["ay"]
				object["vx_abs"] = tracks["vx_abs"]
				object["vy_abs"] = tracks["vy_abs"]
				object["vx"] = tracks["vx"]
				object["vy"] = tracks["vy"]
				objects.append(object)


				done = time.time()
				elapsed = done - start
				logger.info("Ground truth object retrieval is completed in " + str(elapsed) + " seconds")
				return tracks["time"],objects


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\Users\wattamwa\Desktop\pAEBS\HMC-QZ-STR__2020-11-25_12-57-05.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		time,objects = manager_modules.calc('fillGROUND_TRUTH@aebs.fill', manager)
		print(objects)
