# -*- dataeval: init -*-
import logging

import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measproc.Object import colorByVelocity
from pyutils.cache_manager import get_modules_cache, store_modules_cache

logger = logging.getLogger('fillFLC25_PAEBS_AOAOUTPUT_RESIM')

INVALID_ID = 300


class cFill(iObjectFill):
		# dep = 'fill_flc25_paebs_aoaoutput_tracks', 'calc_egomotion'
		dep = 'calc_paebs_resim_output', 'calc_radar_egomotion-flr25'

		def init(self):
			self.ResimData = None
			self.FltsObjNo = None
			self.CommonTime = None

		def check(self):
				modules = self.get_modules()
				paebs_resim_event, time, total_mileage = modules.fill("calc_paebs_resim_output")
				ego_orig = modules.fill('calc_radar_egomotion-flr25')
				egomotion = ego_orig.rescale(time)
				return paebs_resim_event, time, total_mileage, egomotion

		def fill(self, paebs_resim_event, time, total_mileage, egomotion):
				# import time
				# start = time.time()
				logger.info("FLC25 PAEBS AOA object retrieval is started, Please wait...")
				objects = []
				o = {}
				mask = np.zeros(len(time), dtype=bool)
				dx = np.zeros(len(time))
				dy = np.zeros(len(time))
				vx = np.zeros(len(time))
				vx_abs = np.zeros(len(time))
				vy_abs = np.zeros(len(time))
				lane = np.empty(len(time), dtype='S20')
				motion_state = np.empty(len(time), dtype='S20')

				alive_intervals = []
				i = 0
				for event in paebs_resim_event:
					i += 1
					interval = self.get_index((long(event["Start Time Abs"]), long(event["End Time Abs"]),), time)
					mask[interval[0]:interval[1]] = True
					if 'obj_distance_x' in event:
						dx[interval[0]:interval[1]] = event["obj_distance_x"]
						dy[interval[0]:interval[1]] = event["obj_distance_y"]
						vx[interval[0]:interval[1]] = event["obj_relative_velocity_x"]
						vx_abs[interval[0]:interval[1]] = event["obj_absolute_velocity_x"]
						vy_abs[interval[0]:interval[1]] = event["obj_absolute_velocity_y"]
						lane[interval[0]:interval[1]] = event["obj_lane"]
						motion_state[interval[0]:interval[1]] = event["obj_motion_state"]
					elif 'obj_distance_x_start' in event:
						dx[interval[0]:interval[1]] = event['obj_distance_x_start']
						dy[interval[0]:interval[1]] = event['obj_distance_y_start']
						vx[interval[0]:interval[1]] = event['obj_relative_velocity_x_start']
						vx_abs[interval[0]:interval[1]] = event["obj_absolute_velocity_x_start"]
						vy_abs[interval[0]:interval[1]] = event["obj_absolute_velocity_y_start"]
						lane[interval[0]:interval[1]] = event["obj_lane_start"]
						motion_state[interval[0]:interval[1]] = event["obj_motion_state_start"]

						alive_intervals.append((interval[0], interval[1]))

				o["dx"] = np.ma.array(dx, mask=~mask)
				o["dy"] = np.ma.array(dy, mask=~mask)
				o["vx"] = np.ma.array(vx, mask=~mask)
				o["id"] = np.where(~mask, INVALID_ID, 0)
				o["valid"] = mask

				o["label"] = np.array(["FLC25_PAEBS_AOA_RESIM_%d" % (id) for id in zip(o["id"])])
				o["type"] = np.where(~mask, self.get_grouptype('FLC25_PAEBS_AOAOUTPUT_STAT_RESIM'),
											self.get_grouptype('FLC25_PAEBS_AOAOUTPUT_MOV_RESIM'))
				init_intervals = [(st, st + 1) for st, end in alive_intervals]
				o["init"] = intervalsToMask(init_intervals,  len(time))
				o["color"] = [255, 0, 255]
				o["vx_abs"] = np.ma.array(vx_abs, mask=~mask)
				o["vy_abs"] = np.ma.array(vy_abs, mask=~mask)
				o["lane"] = np.ma.array(lane, mask=~mask)
				o["mov_state"] = np.ma.array(motion_state, mask=~mask)

				objects = [o]
				# done = time.time()
				# elapsed = done - start
				# logger.info("FLC25 PAEBS resim AOA object retrieval is completed in " + str(elapsed) + " seconds")
				return time, objects

		def get_index(self, interval, time):
				st_time, ed_time = interval
				st_time = st_time / 1000000.0
				ed_time = ed_time / 1000000.0
				start_index = (np.abs(time - st_time)).argmin()
				end_index = (np.abs(time - ed_time)).argmin()
				if start_index == end_index:
						end_index += 1
				return start_index, end_index


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Measurement\paebs_evalresim\Fusion_AEBS_aResimulation_Helios\measurements\2022-04-07\mi5id5033__2022-04-07_08-20-21.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti, objects = manager_modules.calc('fillFLC25_PAEBS_AOAOUTPUT_RESIM@aebs.fill', manager)
		print(objects)
