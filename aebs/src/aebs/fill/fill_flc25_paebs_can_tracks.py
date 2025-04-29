# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

import numpy as np
import numpy.ma as ma
from metatrack import LaneStatus, ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import MovingDirection, MovingState, ObjectType, \
		TrackingState, MeasuredBy
from primitives.bases import PrimitiveCollection
from pyutils.enum import enum

TRACK_MESSAGE_NUM = 3

MOTION_ST_VALS = (
		'UNKNOWN',
		'MOVING',
		'ONCOMING',
		'CROSSING',
		'STATIONARY',
		'STOPPED',
)

OBJ_CLASS_VALS = (
		'UNCLASSIFIED',
		'POINT',
		'WIDE',
		'MOTORCYCLE',
		'CAR_OR_VAN',
		'TRUCK_OR_COACH',
)
LANE_ST_VALS = (
		'UNKNOWN',
		'EGO',
		'LEFT',
		'RIGHT',
		'OUTSIDE_LEFT',
		'OUTSIDE_RIGHT',
		'SNA',
)
MOTION_STATUS = enum(**dict((name, n) for n, name in enumerate(MOTION_ST_VALS)))
OBJ_CLASS = enum(**dict((name, n) for n, name in enumerate(OBJ_CLASS_VALS)))
LANE_STATUS = enum(**dict((name, n) for n, name in enumerate(LANE_ST_VALS)))
signalTemplate = (
		("Paebs_Track%d_A", "Checksum"),
		("Paebs_Track%d_A", "Dx"),
		("Paebs_Track%d_A", "Dx_Std"),
		("Paebs_Track%d_A", "Dy"),
		("Paebs_Track%d_A", "FrameSyncCounter"),
		("Paebs_Track%d_B", "Checksum"),
		("Paebs_Track%d_B", "Dy_Std"),
		("Paebs_Track%d_B", "FrameSyncCounter"),
		("Paebs_Track%d_B", "Vx_Rel"),
		("Paebs_Track%d_B", "Vx_Rel_Std"),
		("Paebs_Track%d_C", "Checksum"),
		("Paebs_Track%d_C", "FrameSyncCounter"),
		("Paebs_Track%d_C", "Vx_Abs"),
		("Paebs_Track%d_C", "Vy_Rel"),
		("Paebs_Track%d_C", "Vy_Rel_Std"),
		("Paebs_Track%d_D", "Checksum"),
		("Paebs_Track%d_D", "FrameSyncCounter"),
		("Paebs_Track%d_D", "Vx_Abs_Std"),
		("Paebs_Track%d_D", "Vy_Abs"),
		("Paebs_Track%d_D", "Vy_Abs_Std"),
		("Paebs_Track%d_E", "Checksum"),
		("Paebs_Track%d_E", "FrameSyncCounter"),
		("Paebs_Track%d_E", "Lane"),
		("Paebs_Track%d_E", "Motion_State"),
)


def createMessageGroups(MESSAGE_NUM, signalTemplates):
		messageGroups = []
		for m in xrange(1, MESSAGE_NUM + 1):
				messageGroup = {}
				for signalTemplate in signalTemplates:
						fullName = signalTemplate[1]
						shortName = signalTemplate[1]
						messageGroup[shortName] = (signalTemplate[0] % m, fullName)
				messageGroups.append(messageGroup)
		return messageGroups


messageGroups = createMessageGroups(TRACK_MESSAGE_NUM, signalTemplate)


class Flc25PaebsCanTrack(ObjectFromMessage):
		_attribs = tuple(tmpl[1] for tmpl in signalTemplate)
		_special_methods = 'alive_intervals'

		def __init__(self, id, time, source, group, invalid_mask, scaletime = None):
				self._invalid_mask = invalid_mask
				self._group = group
				super(Flc25PaebsCanTrack, self).__init__(id, time, None, None, scaleTime = None)
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
				arr = np.ma.masked_array(data, mask = self._Dx.mask)
				return arr

		def dx(self):
				return self._Dx
		def dx_std(self):
				return self._Dx_Std

		def dy(self):
				return self._Dy
		def dy_std(self):
				return self._Dy_Std


		def range(self):
				return np.sqrt(np.square(self.dx) + np.square(self.dy))

		def angle(self):
				return np.arctan2(self.dy, self.dx)

		def vx(self):
				return self._Vx_Rel
		def vx_std(self):
				return self._Vx_Rel_Std

		def vx_abs(self):
				return self._Vx_Abs

		def vy(self):
				return self._Vy_Rel

		def vy_std(self):
				return self._Vy_Rel_Std

		def vy_abs(self):
				return self._Vy_Abs

		def vx_abs_std(self):
				return self._Vx_Abs_Std

		def vy_abs_std(self):
				return self._Vy_Abs_Std

		def ttc(self):
				with np.errstate(divide = 'ignore'):
						ttc = np.where(self.vx < -1e-3,  # avoid too large (meaningless) values
													 -self.dx / self.vx,
													 np.inf)
				return ttc

		def invttc(self):
				return 1. / self.ttc

		def mov_dir(self):
				crossing = self._Motion_State == MOTION_STATUS.CROSSING

				stationary = self._Motion_State == MOTION_STATUS.STATIONARY
				stopped = self._Motion_State == MOTION_STATUS.STOPPED
				unknown = self._Motion_State == MOTION_STATUS.UNKNOWN

				ongoing = self._Motion_State == MOTION_STATUS.MOVING
				oncoming = self._Motion_State == MOTION_STATUS.ONCOMING
				undefined = unknown | stationary | stopped
				dummy = np.zeros(self._Motion_State.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._Dx.mask)
				return MovingDirection(oncoming = oncoming, ongoing = ongoing, undefined = undefined, crossing=crossing, crossing_left=arr,crossing_right=arr)



		def mov_state(self):
				crossing = self._Motion_State == MOTION_STATUS.CROSSING
				moving = self._Motion_State == MOTION_STATUS.MOVING
				oncoming = self._Motion_State == MOTION_STATUS.ONCOMING
				stationary = self._Motion_State == MOTION_STATUS.STATIONARY
				stopped = self._Motion_State == MOTION_STATUS.STOPPED
				unknown = self._Motion_State == MOTION_STATUS.UNKNOWN
				dummy = np.zeros(self._Motion_State.shape, dtype = bool)
				arr = np.ma.masked_array(dummy, mask = self._Dx.mask)
				return MovingState(stat = stationary, stopped = stopped, moving = moving, unknown = unknown,crossing=crossing, crossing_left=arr,crossing_right=arr, oncoming=oncoming)

		def tr_state(self):
				valid = ma.masked_array(~self._Dx.mask, self._Dx.mask)
				meas = np.ones_like(valid)
				hist = np.ones_like(valid)
				for st, end in maskToIntervals(~self._Dx.mask):
						if st != 0:
								hist[st] = False
				return TrackingState(valid = valid, measured = meas, hist = hist)
		def lane(self):
				same = self._Lane == LANE_STATUS.EGO
				left = self._Lane == LANE_STATUS.LEFT
				right = self._Lane == LANE_STATUS.RIGHT
				uncorr_left = self._Lane == LANE_STATUS.OUTSIDE_LEFT
				uncorr_right = self._Lane == LANE_STATUS.OUTSIDE_RIGHT
				sna = self._Lane == LANE_STATUS.SNA
				unknown_Lane = self._Lane == LANE_STATUS.UNKNOWN
				unknown = (sna | unknown_Lane)
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
						groups.append(source.selectSignalGroup([sg]))
				return groups, commonTime

		def fill(self, groups, common_time):
				tracks = PrimitiveCollection(common_time)
				VALID_FLAG = False
				for _id, group in enumerate(groups):
						dx = group.get_value("Dx", ScaleTime = common_time)
						invalid_mask = (dx == 300) | (np.isnan(dx))
#						if np.all(invalid_mask):
#								continue
						VALID_FLAG = True
						tracks[_id] = Flc25PaebsCanTrack(_id, common_time, self.source, group, invalid_mask, scaletime = common_time)
				if not VALID_FLAG:
						logging.warning("Error: {} :Measurement does not contain PAEBS CAN object data".format(self.source.FileName))
				return tracks


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6168\shared-drive\measurements\pAEBS\new_requirment\CAN\HMC-QZ-STR__2020-12-04_15-19-23.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		tracks = manager_modules.calc('fill_flc25_paebs_can_tracks@aebs.fill', manager)
		print(tracks)
