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
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.aebs_object.ax_abs"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.aebs_object.ax_rel"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.aebs_object.dx"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.aebs_object.dy"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.aebs_object.id"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.aebs_object.motion_state"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.aebs_object.source"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.aebs_object.vx_rel"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.aebs_object.vy_rel"),

)

signalTemplate = (
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_ax_abs"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_ax_rel"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_dx"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_dy"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_id"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_motion_state"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_source"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_vx_rel"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_vy_rel"),
)

signalTemplatesh4 = (
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlts_DebugSignals_ts_meas_aebs_object_ax_abs"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlts_DebugSignals_ts_meas_aebs_object_ax_rel"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlts_DebugSignals_ts_meas_aebs_object_dx"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlts_DebugSignals_ts_meas_aebs_object_dy"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlts_DebugSignals_ts_meas_aebs_object_id"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlts_DebugSignals_ts_meas_aebs_object_motion_state"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlts_DebugSignals_ts_meas_aebs_object_source"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlts_DebugSignals_ts_meas_aebs_object_vx_rel"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlts_DebugSignals_ts_meas_aebs_object_vy_rel"),
)
signalTemplatesh5 = (
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_ax_abs"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_ax_rel"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_dx"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_dy"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_id"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_motion_state"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_source"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_vx_rel"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_vy_rel"),
)


def createMessageGroups(MESSAGE_NUM, signalTemplates):
    messageGroups = []
    for m in xrange(MESSAGE_NUM):
        signalDict = []
        messageGroup1 = {}
        for signalTemplate in signalTemplates:
            fullName = signalTemplate[1]
            shortName = fullName.split('object_')[-1]
            if shortName == 'id':
                shortName = 'object_id'
            if shortName == 'source':
                shortName = 'object_source'

            messageGroup1[shortName] = (signalTemplate[0], fullName)
        signalDict.append(messageGroup1)
        messageGroup2 = {}
        for signalTemplateh5 in signalTemplatesh5:
            fullName = signalTemplateh5[1]
            shortName = fullName.split('object_')[-1]
            if shortName == 'id':
                shortName = 'object_id'
            if shortName == 'source':
                shortName = 'object_source'
            messageGroup2[shortName] = (signalTemplateh5[0], fullName)
        signalDict.append(messageGroup2)
        messageGroup3 = {}
        for signalTemplateh4 in signalTemplatesh4:
            fullName = signalTemplateh4[1]
            shortName = fullName.split('object_')[-1]
            if shortName == 'id':
                shortName = 'object_id'
            if shortName == 'source':
                shortName = 'object_source'
            messageGroup3[shortName] = (signalTemplateh4[0], fullName)
        signalDict.append(messageGroup3)
        messageGroups.append(signalDict)
    return messageGroups


messageGroups = createMessageGroups(TRACK_MESSAGE_NUM, signalTemplate)


class Flc25AoaAebsTracks(ObjectFromMessage):
    attribs = []
    for signalTemplate in signalTemplate:
        fullName = signalTemplate[1]
        shortName = fullName.split('object_')[-1]
        if shortName == 'id':
            shortName = 'object_id'
        if shortName == 'source':
            shortName = 'object_source'
        attribs.append(shortName)

    _attribs = tuple(attribs)
    _special_methods = 'alive_intervals'

    def __init__(self, id, time, source, group, invalid_mask, scaletime=None):
        self._invalid_mask = invalid_mask
        self._group = group
        super(Flc25AoaAebsTracks, self).__init__(id, time, None, None, scaleTime=None)
        return

    def _create(self, signalName):
        value = self._group.get_value(signalName, ScaleTime=self.time)
        mask = ~self._invalid_mask
        out = np.ma.masked_all_like(value)
        out.data[mask] = value[mask]
        out.mask &= ~mask
        return out

    def id(self):
        data = np.repeat(np.uint8(self._id), self.time.size)
        arr = np.ma.masked_array(data, mask=self._dx.mask)
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

    def ax(self):
        return self._ax_rel

    def ax_abs(self):
        return self._ax_abs

    def vx(self):
        return self._vx_rel

    def vy(self):
        return self._vy_rel

    def ttc(self):
        with np.errstate(divide='ignore'):
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
        return TrackingState(valid=valid, measured=meas, hist=hist)

    def mov_dir(self):
        crossing = self._motion_state == MOTION_STATUS.CROSSING
        stationary = self._motion_state == MOTION_STATUS.STATIC
        stopped = self._motion_state == MOTION_STATUS.MOVING_STOPPED
        ongoing = self._motion_state == MOTION_STATUS.MOVING
        oncoming = self._motion_state == MOTION_STATUS.ONCOMING
        not_detected = self._motion_state == MOTION_STATUS.NOT_DETECTED
        defalut = self._motion_state == MOTION_STATUS.DEFAULT
        undefined = (defalut | not_detected | stopped | stationary)
        dummy = np.zeros(self._motion_state.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._dx.mask)
        return MovingDirection(oncoming=oncoming, ongoing=ongoing, undefined=undefined, crossing=crossing,
                               crossing_left=arr, crossing_right=arr)

    def mov_state(self):
        crossing = self._motion_state == MOTION_STATUS.CROSSING
        moving = self._motion_state == MOTION_STATUS.MOVING
        oncoming = self._motion_state == MOTION_STATUS.ONCOMING
        stationary = self._motion_state == MOTION_STATUS.STATIC
        stopped = self._motion_state == MOTION_STATUS.MOVING_STOPPED
        not_detected = self._motion_state == MOTION_STATUS.NOT_DETECTED
        default = self._motion_state == MOTION_STATUS.DEFAULT
        unknown = (not_detected | default)
        dummy = np.zeros(self._motion_state.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._dx.mask)
        return MovingState(stat=stationary, stopped=stopped, moving=moving, unknown=unknown, crossing=crossing,
                           crossing_left=arr, crossing_right=arr, oncoming=oncoming)

    def tr_state(self):
        valid = ma.masked_array(~self._dx.mask, self._dx.mask)
        meas = np.ones_like(valid)
        hist = np.ones_like(valid)
        for st, end in maskToIntervals(~self._dx.mask):
            if st != 0:
                hist[st] = False
        return TrackingState(valid=valid, measured=meas, hist=hist)

    def measured_by(self):
        no_info = self._object_source == MEASURED_BY_ST.UNKNOWN
        radar_only = self._object_source == MEASURED_BY_ST.RADAR_ONLY
        camera_only = self._object_source == MEASURED_BY_ST.CAMERA_ONLY
        fused = self._object_source == MEASURED_BY_ST.FUSED
        # dummy data
        dummy = np.zeros(self._object_source.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._dx.mask)
        return MeasuredBy(none=no_info, prediction=arr, radar_only=radar_only, camera_only=camera_only,
                          fused=fused)

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
            groups.append(source.selectSignalGroupOrEmpty(sg))

        return groups, commonTime

    def fill(self, groups, common_time):
        tracks = PrimitiveCollection(common_time)
        for _id, group in enumerate(groups):
            object_id = group.get_value("object_id", ScaleTime=common_time)
            # invalid_mask = (object_id == 255) | (np.isnan(object_id))
            invalid_mask = (np.isnan(object_id))
            if np.all(invalid_mask):
                continue
            # invalid_mask = np.zeros(common_time.size, bool)
            tracks[_id] = Flc25AoaAebsTracks(_id, common_time, self.source, group, invalid_mask,
                                             scaletime=common_time)
        return tracks


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r'C:\KBData\evaluation\pytch2_eval\slr_eval\test\2024-08-28\mi5id5506__2024-08-28_14-51-16.h5'
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    tracks = manager_modules.calc('fill_flc25_aoa_aebs_tracks@aebs.fill', manager)
    print(tracks)
