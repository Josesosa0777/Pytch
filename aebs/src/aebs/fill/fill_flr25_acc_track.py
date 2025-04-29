# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

import numpy as np
import numpy.ma as ma
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import LaneStatus, MeasuredBy, MovingDirection, MovingState, ObjectType, TrackingState
from primitives.bases import PrimitiveCollection
from pyutils.enum import enum

logger = logging.getLogger('fill_flr25_acc_track')

MOTION_ST_VALS = (
		'NOT_DETECTED',
		'MOVING',
		'MOVING_STOPPED',
		'STATIC',
		'CROSSING',
		'ONCOMING',
		'DEFAULT',

)
OBJ_CLASS_VALS = (
		'NONE',
		'UNKNOWN',
		'CAR',
		'TRUCK',
		'PEDESTRIAN',
		'CYCLIST',
		'MOTORBIKE',
		'MAX_VALUE',
)
LANE_ST_VALS = (
		'UNKNOWN',
		'FAR_LEFT',
		'LEFT',
		'EGO',
		'RIGHT',
		'FAR_RIGHT',
)
MEASURED_BY_VALS = (
		'UNKNOWN',
		'RADAR_ONLY',
		'CAMERA_ONLY',
		'FUSED',
		'SNA',
)

MOTION_STATUS = enum(**dict((name, n) for n, name in enumerate(MOTION_ST_VALS)))
OBJ_CLASS = enum(**dict((name, n) for n, name in enumerate(OBJ_CLASS_VALS)))
MEASURED_BY_ST = enum(**dict((name, n) for n, name in enumerate(MEASURED_BY_VALS)))
LANE_STATUS = enum(**dict((name, n) for n, name in enumerate(LANE_ST_VALS)))

signalTemplate = (

		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_ax_rel"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_ax_abs"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_dx"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_dx_std"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_dy"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_dy_std"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_id"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_lane"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_motion_state"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_obj_class"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_source"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_vx_abs"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_vx_abs_std"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_vx_rel"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_vx_rel_std"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_vy_rel"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_vy_rel_std"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_vy_abs"),
		("Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf",
		 "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_sensor_DEP_postp_im_sensor_Buf_acc_object_vy_abs_std"),

)


def createMessageGroups(signalTemplates):
		messageGroups = []
		messageGroup = {}
		for signalTemplate in signalTemplates:
				fullName = signalTemplate[1]
				shortName = fullName.split("object_")[-1]
				if shortName == 'id':
						shortName = 'object_id'
				if shortName == 'source':
						shortName = 'object_source'
				messageGroup[shortName] = (signalTemplate[0], fullName)
		messageGroups.append(messageGroup)
		return messageGroups


messageGroup = createMessageGroups(signalTemplate)


class Flr25AccTrack(ObjectFromMessage):
		_attribs = tuple(tmpl[1].split("object_")[-1] for tmpl in signalTemplate)
		_attribs = list(_attribs)
		_attribs.remove('id')
		_attribs.append('object_id')
		_attribs.remove('source')
		_attribs.append('object_source')
		_attribs = tuple(_attribs)
		_special_methods = 'alive_intervals'
		def __init__(self, id, time, source, group, invalid_mask, scaletime = None):
				self._invalid_mask = invalid_mask
				self._group = group
				super(Flr25AccTrack, self).__init__(id, time, None, None, scaleTime = None)
				return

		def _create(self, signalName):
				value = self._group.get_value(signalName, ScaleTime = self.time)
				mask = ~self._invalid_mask
				out = np.ma.masked_all_like(value)
				out.data[mask] = value[mask]
				out.mask &= ~mask
				return out

		def id(self):
				data = np.repeat(np.uint8(self._id), self.time.size)
				arr = np.ma.masked_array(data, mask = self._dx.mask)
				return arr

		def object_id(self):
				return self._object_id

		def dx(self):
				return self._dx

		def dx_std(self):
				return self._dx_std

		def dy(self):
				return self._dy

		def dy_std(self):
				return self._dy_std

		def range(self):
				return np.sqrt(np.square(self.dx) + np.square(self.dy))

		def angle(self):
				return np.arctan2(self.dy, self.dx)

		def vx(self):
				return self._vx_rel

		def vx_std(self):
				return self._vx_rel_std

		def vy(self):
				return self._vy_rel

		def vy_std(self):
				return self._vy_rel_std

		def ax_abs(self):
				return self._ax_abs

		def ax(self):
				return self._ax_rel

		def vx_abs(self):
				return self._vx_abs

		def vx_abs_std(self):
				return self._vx_abs_std

		def vy_abs(self):
				return self._vy_abs

		def vy_abs_std(self):
				return self._vy_abs_std

		def ttc(self):
				with np.errstate(divide = 'ignore'):
						ttc = np.where(self.vx < -1e-3,  # avoid too large (meaningless) values
													 -self.dx / self.vx,
													 np.inf)
				return ttc

		def invttc(self):
				return 1. / self.ttc

		def mov_dir(self):
				crossing = self._motion_state == MOTION_STATUS.CROSSING

				stationary = self._motion_state == MOTION_STATUS.STATIC
				stopped = self._motion_state == MOTION_STATUS.MOVING_STOPPED
				unknown = self._motion_state == MOTION_STATUS.DEFAULT

				ongoing = self._motion_state == MOTION_STATUS.MOVING
				oncoming = self._motion_state == MOTION_STATUS.ONCOMING
				undefined = (unknown | stationary | stopped)
				dummy = np.zeros(self._motion_state.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._dx.mask)
				return MovingDirection(oncoming = oncoming, ongoing = ongoing, undefined = undefined, crossing = crossing,
															 crossing_left = arr, crossing_right = arr)

		def obj_type(self):
				none_identified = self._obj_class == OBJ_CLASS.NONE
				car = self._obj_class == OBJ_CLASS.CAR
				truck = self._obj_class == OBJ_CLASS.TRUCK
				pedestrian = self._obj_class == OBJ_CLASS.PEDESTRIAN
				motorcycle = self._obj_class == OBJ_CLASS.MOTORBIKE
				bicycle = self._obj_class == OBJ_CLASS.CYCLIST
				unknown = self._obj_class == OBJ_CLASS.UNKNOWN
				unclassified = self._obj_class == OBJ_CLASS.MAX_VALUE
				no_found = (none_identified | unknown | unclassified)
				dummy = np.zeros(self._obj_class.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._dx.mask)
				return ObjectType(unknown = no_found, pedestrian = pedestrian, motorcycle = motorcycle, car = car,
													truck = truck, bicycle = bicycle, point = arr, wide = arr)

		def mov_state(self):
				crossing = self._motion_state == MOTION_STATUS.CROSSING
				moving = self._motion_state == MOTION_STATUS.MOVING
				oncoming = self._motion_state == MOTION_STATUS.ONCOMING
				stationary = self._motion_state == MOTION_STATUS.STATIC
				stopped = self._motion_state == MOTION_STATUS.MOVING_STOPPED
				unknown = self._motion_state == MOTION_STATUS.DEFAULT
				dummy = np.zeros(self._motion_state.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._dx.mask)
				return MovingState(stat = stationary, stopped = stopped, moving = moving, unknown = unknown,
													 crossing = crossing, crossing_left = arr, crossing_right = arr, oncoming = oncoming)

		def measured_by(self):
				no_info = self._object_source == MEASURED_BY_ST.UNKNOWN
				radar_only = self._object_source == MEASURED_BY_ST.RADAR_ONLY
				camera_only = self._object_source == MEASURED_BY_ST.CAMERA_ONLY
				fused = self._object_source == MEASURED_BY_ST.FUSED
				dummy = np.zeros(self._object_source.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._dx.mask)
				return MeasuredBy(none = no_info, prediction = arr, radar_only = radar_only, camera_only = camera_only,
													fused = fused)
		def lane(self):
				same = self._lane == LANE_STATUS.EGO
				left = self._lane == LANE_STATUS.LEFT
				right = self._lane == LANE_STATUS.RIGHT
				uncorr_left = self._lane == LANE_STATUS.FAR_LEFT
				uncorr_right = self._lane == LANE_STATUS.FAR_RIGHT
				unknown = self._lane == LANE_STATUS.UNKNOWN
				return LaneStatus(same = same, left = left, right = right, uncorr_left = uncorr_left,
													uncorr_right = uncorr_right, unknown = unknown)

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
						tracks[_id] = Flr25AccTrack(_id, common_time, None, group, invalid_mask,
																				scaletime = common_time)
				done = time.time()
				elapsed = done - start
				logger.info("FLR25 ACC object creation completed in " + str(elapsed))
				if not VALID_FLAG:
					logging.warning("Error: {} :Measurement does not contain ACC object data".format(self.source.FileName))
				return tracks


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\hdf5_test" \
								r"\device_name_isse" \
								r"\BendixTruck__2021-01-30_07-05-03.mat"
		# meas_path = r"\\pu2w6168\shared-drive\measurements\ACC_evaluation\UFO__2021-01-29_06-09-17.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		object = manager_modules.calc('fill_flr25_acc_track@aebs.fill', manager)
		print(object)
