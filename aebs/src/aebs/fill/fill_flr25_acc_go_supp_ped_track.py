# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

import numpy as np
import numpy.ma as ma
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import MovingState, TrackingState
from primitives.bases import PrimitiveCollection
import struct

from pyutils.enum import enum

logger = logging.getLogger('fill_flr25_acc_paebs_track')
TRACK_MESSAGE_NUM = 1

MOTION_ST_VALS = (
		'NOT_DETECTED',
		'MOVING',
		'MOVING_STOPPED',
		'STATIC',
		'CROSSING',
		'ONCOMING',
		'DEFAULT',

)
MOTION_STATUS = enum(**dict((name, n) for n, name in enumerate(MOTION_ST_VALS)))

signalTemplate = (
("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_go_supp_object_dx"),
("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_go_supp_object_ax_rel"),
("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_go_supp_object_dy"),
("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_go_supp_object_id"),
("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_go_supp_object_motion_state"),
("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_go_supp_object_vx_rel"),
("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_go_supp_object_vy_rel"),

)


def createMessageGroups(signalTemplates):
		messageGroups = []
		messageGroup = {}
		for signalTemplate in signalTemplates:
				fullName = signalTemplate[1]
				shortName = fullName.split("object_")[-1]
				if shortName == 'id':
						shortName = 'object_id'
				messageGroup[shortName] = (signalTemplate[0], fullName)
		messageGroups.append(messageGroup)
		return messageGroups


messageGroup = createMessageGroups(signalTemplate)

class Flr25AccGoSuppPedTrack(ObjectFromMessage):
		_attribs = tuple(tmpl[1].split("object_")[-1] for tmpl in signalTemplate)
		_attribs =list(_attribs)
		_attribs.remove('id')
		_attribs.append('object_id')
		_attribs = tuple(_attribs)


		def __init__(self, id, time, source, group, invalid_mask, scaletime = None):
				self._invalid_mask = invalid_mask
				self._group = group
				super(Flr25AccGoSuppPedTrack, self).__init__(id, time, None, None, scaleTime = None)
				return

		def _create(self, signalName):
				value = self._group.get_value(signalName, ScaleTime = self.time)
				mask = ~self._invalid_mask
				out = np.ma.masked_all_like(value)
				out.data[mask] = value[mask]
				out.mask &= ~mask
				return out

		def id (self):
				data = np.repeat(np.uint8(self._id), self.time.size)
				arr = np.ma.masked_array(data, mask = self._dx.mask)
				return arr

		def object_id(self):
				return self._object_id

		def ax(self):
				return self._ax_rel

		def dx(self):
				return self._dx

		def dy(self):
				return self._dy

		def vx(self):
				return self._vx_rel

		def vy(self):
				return self._vy_rel

		def mov_state(self):
				crossing = self._motion_state == MOTION_STATUS.CROSSING
				moving = ((self._motion_state == MOTION_STATUS.MOVING) | (
								self._motion_state == MOTION_STATUS.ONCOMING) | crossing)
				stationary = self._motion_state == MOTION_STATUS.STATIC
				stopped = self._motion_state == MOTION_STATUS.MOVING_STOPPED
				not_detected = self._motion_state == MOTION_STATUS.DEFAULT
				default = ((self._motion_state == MOTION_STATUS.DEFAULT) | not_detected)
				dummy = np.zeros(self._motion_state.shape, dtype=bool)
				arr = np.ma.masked_array(dummy, mask=self._dx.mask)
				return MovingState(stat = stationary, stopped = stopped, moving = moving, unknown = default,crossing = crossing, crossing_left=arr,crossing_right=arr, oncoming = arr)

		def tr_state(self):
				valid_tr = ma.masked_array(~self._dx.mask, self._dx.mask)
				meas = np.ones_like(valid_tr)
				hist = np.ones_like(valid_tr)
				for st, end in maskToIntervals(~self._dx.mask):
						if st != 0:
								hist[st] = False
				return TrackingState(valid = valid_tr, measured = meas, hist = hist)

		def alive_intervals(self):
				new = self.tr_state.valid & ~self.tr_state.hist
				validIntervals = cIntervalList.fromMask(self.time, self.tr_state.valid)
				newIntervals = cIntervalList.fromMask(self.time, new)
				alive_intervals = validIntervals.split(st for st, _ in newIntervals)
				return alive_intervals


class Calc(iCalc):
		dep = 'calc_common_time-flr25',

		def check(self):
				modules = self.get_modules()
				source = self.get_source()
				commonTime = modules.fill(self.dep[0])
				groups = []
				for sg in messageGroup:
						groups.append(source.selectSignalGroup([sg]))
				return groups, commonTime

		def fill(self, groups, common_time):
				import time
				start = time.time()
				tracks = PrimitiveCollection(common_time)
				VALID_FLAG = False
				for _id, group in enumerate(groups):
						object_id = group.get_value("object_id", ScaleTime = common_time)
						invalid_mask = (object_id == 255) | (np.isnan(object_id))
#						if np.all(invalid_mask):
#								continue
						VALID_FLAG = True
						tracks[_id] = Flr25AccGoSuppPedTrack(_id, common_time, None, group, invalid_mask,
																				scaletime = common_time)
				done = time.time()
				elapsed = done - start
				logger.info("FLR25 ACC GO SUPP PED object creation completed in " + str(elapsed))
				if not VALID_FLAG:
					logging.warning("Error: {} :Measurement does not contain ACC GO PED object data".format(self.source.FileName))
				return tracks


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6168\shared-drive\measurements\ACC_evaluation\acc_evaluation\BendixTruck__2021-01-30_07-05-03.mat"
		# meas_path = r"\\pu2w6168\shared-drive\measurements\ACC_evaluation\UFO__2021-01-29_06-09-17.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		object = manager_modules.calc('fill_flr25_acc_go_supp_ped_track@aebs.fill', manager)
		print(object)
