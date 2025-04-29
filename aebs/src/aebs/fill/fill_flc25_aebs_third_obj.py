# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

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


MEASURED_BY_VALS = (
		'UNKNOWN',
		'RADAR_ONLY',
		'CAMERA_ONLY',
		'FUSED',
		'SNA',
)

MOTION_STATUS = enum(**dict((name, n) for n, name in enumerate(MOTION_ST_VALS)))
MEASURED_BY_ST = enum(**dict((name, n) for n, name in enumerate(MEASURED_BY_VALS)))

signalTemplate = (
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_bitfield"),
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_dist_from_path"),
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_dx"),
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_dy"),
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_id"),
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_lane_conf"),
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_length"),
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_life_time"),
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_motion_state"),
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_source"),
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_vx_rel"),
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_vy_rel"),
		("MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_width"),
)

signalTemplate2 = (
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_bitfield_value"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_dx"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_dy"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_fusion_history"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_id"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_lane"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_lane_conf"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_lat_distance_from_path"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_length"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_life_time"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_motion_state"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_predicted_lat_dist"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_source"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_vx_rel"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_vy_rel"),
("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_aebs_third_width"),

)


def createMessageGroups(signalTemplates, signalTemplate2):
		messageGroups = []
		messageGroup = {}
		for signalTemplate in signalTemplates:
				fullName = signalTemplate[1]
				shortName = fullName.split("obj_")[-1]
				if shortName == 'id':
						shortName = 'object_id'
				if shortName == 'source':
						shortName = 'object_source'
				if shortName == 'bitfield':
					shortName = 'bitfield_value'
				if shortName == 'dist_from_path':
					shortName = 'lat_distance_from_path'
				messageGroup[shortName] = (signalTemplate[0], fullName)
		messageGroups.append(messageGroup)
		messageGroup2 = {}
		for signalTemplate in signalTemplate2:
			fullName = signalTemplate[1]
			shortName = fullName.split("third_")[-1]
			if shortName == 'id':
				shortName = 'object_id'
			if shortName == 'source':
				shortName = 'object_source'
			messageGroup2[shortName] = (signalTemplate[0], fullName)
		messageGroups.append(messageGroup2)
		return messageGroups


messageGroups = createMessageGroups(signalTemplate, signalTemplate2)


class Flc25AebsThirdObjectTrack(ObjectFromMessage):
		_attribs1 = tuple(tmpl[1].split("obj_")[-1] for tmpl in signalTemplate)
		_attribs1 = list(_attribs1)
		_attribs1.remove('id')
		_attribs1.append('object_id')
		_attribs1.remove('source')
		_attribs1.append('object_source')
		_attribs1.remove('bitfield')
		_attribs1.append('bitfield_value')
		_attribs1.remove('dist_from_path')
		_attribs1.append('lat_distance_from_path')

		_attribs2 = tuple(tmpl[1].split("third_")[-1] for tmpl in signalTemplate2)
		_attribs2 = list(_attribs2)
		_attribs2.remove('id')
		_attribs2.append('object_id')
		_attribs2.remove('source')
		_attribs2.append('object_source')
		_attribs = set(_attribs1 + _attribs2)

		_attribs = tuple(_attribs)

		_special_methods = 'alive_intervals'
		_reserved_names = ObjectFromMessage._reserved_names + ('get_selection_timestamp',)

		def __init__(self, id, time, source, group, invalid_mask, scaletime = None):
				self._invalid_mask = invalid_mask
				self._group = group
				super(Flc25AebsThirdObjectTrack, self).__init__(id, time, None, None, scaleTime = None)
				return
		def get_selection_timestamp(self, timestamp):
				start, end = self.alive_intervals.findInterval(timestamp)
				return start

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

		def dy(self):
				return self._dy

		def range(self):
				return np.sqrt(np.square(self.dx) + np.square(self.dy))

		def angle(self):
				return np.arctan2(self.dy, self.dx)

		def bitfield_value(self):
				return self._bitfield_value

		def lat_distance_from_path(self):
				return self._lat_distance_from_path

		def lane_conf(self):
				return self._lane_conf

		def length(self):
				return self._length

		def width(self):
				return self._width

		def life_time(self):
				return self._life_time

		def lane(self):
			return self._lane

		def predicted_lat_dist(self):
			return self._predicted_lat_dist

		def fusion_history(self):
			return self._fusion_history

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



		def vx(self):
				return self._vx_rel

		def vy(self):
				return self._vy_rel

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

				commonTime = modules.fill(self.dep[0])
				groups = []
				for sg in messageGroups:
					try:
						groups.append(self.source.selectSignalGroup([sg]))
					except:
						continue

				return groups, commonTime


		def fill(self, groups, common_time):
				tracks = PrimitiveCollection(common_time)
				VALID_FLAG = False
				for _id, group in enumerate(groups):
						object_id = group.get_value("object_id", ScaleTime = common_time)
						invalid_mask = (object_id == 255) | (np.isnan(object_id))
						VALID_FLAG = True
						tracks[_id] = Flc25AebsThirdObjectTrack(_id, common_time, None, group, invalid_mask,
																										scaletime = common_time)
				if not VALID_FLAG:
						logging.warning("Error: {} :Measurement does not contain AEBS third object data".format(self.source.FileName))
				return tracks



if __name__ == '__main__':
		from config.Config import init_dataeval
		meas_path = r"C:\KBData\Measurement\aebs_debugging_concept\latest_meas\HMC-QZ-STR__2022-03-15_10-22-15.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		tracks = manager_modules.calc('fill_flc25_aebs_third_obj@aebs.fill', manager)
		print(tracks)
