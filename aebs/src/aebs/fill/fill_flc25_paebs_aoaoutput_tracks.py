# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np
import numpy.ma as ma
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import BlinkerStatus, BrakeLightStatus, LaneStatus, MovingDirection, MovingState, ObjectType, \
		TrackingState, MeasuredBy
from primitives.bases import PrimitiveCollection
from pyutils.enum import enum

TRACK_MESSAGE_NUM = 3

MOTION_ST_VALS = (
		'NOT_DETECTED',
		'MOVING',
		'MOVING_STOPPED',
		'STATIC',
		'CROSSING',
		'ONCOMING',
		'DEFAULT'
)
LANE_ST_VALS = (
		'UNKNOWN',
		'EGO',
		'LEFT',
		'RIGHT',
		'OUTSIDE_LEFT',
		'OUTSIDE_RIGHT',

)

MOTION_STATUS = enum(**dict((name, n) for n, name in enumerate(MOTION_ST_VALS)))
LANE_STATUS = enum(**dict((name, n) for n, name in enumerate(LANE_ST_VALS)))

signalTemplate = (
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI%dI_dx"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI%dI_dx_std"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI%dI_dy"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI%dI_dy_std"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI%dI_lane"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI%dI_motion_state"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI%dI_vx_abs"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI%dI_vx_abs_std"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI%dI_vx_rel"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI%dI_vy_abs"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI%dI_vy_abs_std"),

)
signalTemplateh5 = (
("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects%d_dx"),
("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects%d_dx_std"),
("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects%d_dy"),
("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects%d_dy_std"),
("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects%d_lane"),
("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects%d_motion_state"),
("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects%d_vx_abs"),
("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects%d_vx_abs_std"),
("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects%d_vx_rel"),
("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects%d_vy_abs"),
("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects%d_vy_abs_std"),

)


# Alternate AOA signals to be added
signalTemplate2 =(
("MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsInput_sensor_input_paebs_object%d_lon_dist"),
("MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsInput_sensor_input_paebs_object%d_lat_dist"),
("MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsInput_sensor_input_paebs_object%d_motion_state"),
("MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsInput_sensor_input_paebs_object%d_lon_veloc_rel"),
)


def createMessageGroups(MESSAGE_NUM, signalTemplates):
		messageGroups = []
		for m in xrange(MESSAGE_NUM):
				messageGroup1 = {}
				signalDict = []
				for signalTemplate in signalTemplates:
						fullName = signalTemplate[1] % m
						shortName = fullName.split("I_")[-1]
						messageGroup1[shortName] = (signalTemplate[0], fullName)
				signalDict.append(messageGroup1)
				messageGroup2 = {}
				for signalTemplateh in signalTemplateh5:
						fullName = signalTemplateh[1] % m
						shortName = fullName.split("objects%d_" %m)[-1]
						messageGroup2[shortName] = (signalTemplateh[0], fullName)
				signalDict.append(messageGroup2)
				messageGroups.append(signalDict)
		return messageGroups


messageGroups = createMessageGroups(TRACK_MESSAGE_NUM, signalTemplate)



class Flc25PaebsAoaOutputTracks(ObjectFromMessage):
		attribs = []

		for signalTemplate in signalTemplate:
				fullName = signalTemplate[1]
				shortName = fullName.split('I_')[-1]
				attribs.append(shortName)

		_attribs = tuple(attribs)
		_special_methods = 'alive_intervals'
		_reserved_names = ObjectFromMessage._reserved_names + ('get_selection_timestamp',)

		def __init__(self, id, time, source, group, invalid_mask, scaletime = None):
				self._invalid_mask = invalid_mask
				self._group = group
				super(Flc25PaebsAoaOutputTracks, self).__init__(id, time, None, None, scaleTime = None)
				return

		def _create(self, signalName):
				value = self._group.get_value(signalName, ScaleTime = self.time)
				mask = ~self._invalid_mask
				out = np.ma.masked_all_like(value)
				out.data[mask] = value[mask]
				out.mask &= ~mask
				return out

		def get_selection_timestamp(self, timestamp):
				start, end = self.alive_intervals.findInterval(timestamp)
				return start

		def id(self):
				data = np.repeat(np.uint8(self._id), self.time.size)
				arr = np.ma.masked_array(data, mask = self._dx.mask)
				return arr


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

		def vx_abs(self):
				return self._vx_abs

		def vy_abs(self):
				return self._vy_abs

		def vx_abs_std(self):
				return self._vx_abs_std

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

		def tr_state(self):
				valid = ma.masked_array(~self._dx.mask, self._dx.mask)
				meas = np.ones_like(valid)
				hist = np.ones_like(valid)
				for st, end in maskToIntervals(~self._dx.mask):
						if st != 0:
								hist[st] = False
				return TrackingState(valid = valid, measured = meas, hist = hist)

		def mov_dir(self):
				crossing = self._motion_state == MOTION_STATUS.CROSSING

				stationary = self._motion_state == MOTION_STATUS.STATIC
				stopped = self._motion_state == MOTION_STATUS.MOVING_STOPPED
				default = self._motion_state == MOTION_STATUS.DEFAULT
				not_detected = self._motion_state == MOTION_STATUS.NOT_DETECTED
				ongoing = self._motion_state == MOTION_STATUS.MOVING
				oncoming = self._motion_state == MOTION_STATUS.ONCOMING
				undefined = (default | not_detected | stationary | stopped)
				dummy = np.zeros(self._motion_state.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._dx.mask)
				return MovingDirection(oncoming = oncoming, ongoing = ongoing, undefined = undefined, crossing = crossing,
															 crossing_left = arr, crossing_right = arr)

		def mov_state(self):
				crossing = self._motion_state == MOTION_STATUS.CROSSING

				moving = self._motion_state == MOTION_STATUS.MOVING
				oncoming = self._motion_state == MOTION_STATUS.ONCOMING
				stationary = self._motion_state == MOTION_STATUS.STATIC
				stopped = self._motion_state == MOTION_STATUS.MOVING_STOPPED
				default = self._motion_state == MOTION_STATUS.DEFAULT
				not_detected = self._motion_state == MOTION_STATUS.NOT_DETECTED
				unknown = (default | not_detected)
				dummy = np.zeros(self._motion_state.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._dx.mask)
				return MovingState(stat = stationary, stopped = stopped, moving = moving, unknown = unknown,
													 crossing = crossing,
													 crossing_left = arr, crossing_right = arr, oncoming = oncoming)

		def tr_state(self):
				valid = ma.masked_array(~self._dx.mask, self._dx.mask)
				meas = np.ones_like(valid)
				hist = np.ones_like(valid)
				for st, end in maskToIntervals(~self._dx.mask):
						if st != 0:
								hist[st] = False
				return TrackingState(valid = valid, measured = meas, hist = hist)

		def lane(self):
				same = self._lane == LANE_STATUS.EGO
				left = self._lane == LANE_STATUS.LEFT
				right = self._lane == LANE_STATUS.RIGHT
				uncorr_left = self._lane == LANE_STATUS.OUTSIDE_LEFT
				uncorr_right = self._lane == LANE_STATUS.OUTSIDE_RIGHT

				unknown = self._lane == LANE_STATUS.UNKNOWN

				lane = LaneStatus(same = same, left = left, right = right, uncorr_left = uncorr_left,
													uncorr_right = uncorr_right, unknown = unknown)
				return lane

		def alive_intervals(self):
				new = self.tr_state.valid & ~self.tr_state.hist
				validIntervals = cIntervalList.fromMask(self.time, self.tr_state.valid)
				newIntervals = cIntervalList.fromMask(self.time, new)
				alive_intervals = validIntervals.split(st for st, _ in newIntervals)
				return alive_intervals



class Calc(iCalc):
		dep = 'calc_common_time-flc25',

		def check(self):
				modules = self.get_modules()
				source = self.get_source()
				commonTime = modules.fill(self.dep[0])
				groups = []
				for sg in messageGroups:
						groups.append(source.selectSignalGroup(sg))
				return groups, commonTime

		def fill(self, groups, common_time):
				tracks = PrimitiveCollection(common_time)

				for _id, group in enumerate(groups):
						dx = group.get_value("dx", ScaleTime = common_time)
						invalid_mask = (dx == 300) | (np.isnan(dx))
#						if np.all(invalid_mask):
#								continue

						tracks[_id] = Flc25PaebsAoaOutputTracks(_id, common_time, self.source, group, invalid_mask,
																										scaletime = common_time)

				return tracks


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6474\shared-drive\measurements\new_meas_09_11_21\mi5id787__2021-10-28_00-03-59.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		tracks = manager_modules.calc('fill_flc25_paebs_aoaoutput_tracks@aebs.fill', manager)
		print(tracks)
