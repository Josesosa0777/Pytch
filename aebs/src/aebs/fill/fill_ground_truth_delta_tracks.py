# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

import numpy as np
import numpy.ma as ma
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import  TrackingState
from primitives.bases import PrimitiveCollection
import struct

logger = logging.getLogger('fill_ground_truth_delta_objects')
TRACK_MESSAGE_NUM = 1

signalTemplate = (
    ("Delta_Longitudinal", "Long_Delta_Distance"),
    ("Delta_Longitudinal", "Long_Delta_Velocity"),
    ("Delta_Lateral","Lat_Delta_Velocity"),
    ("Delta_Lateral","Lat_Delta_Distance"),

)


def createMessageGroups(signalTemplates):
    messageGroups = []
    messageGroup = {}
    for signalTemplate in signalTemplates:
        fullName = signalTemplate[1]
        shortName =fullName
        messageGroup[shortName] = (signalTemplate[0], fullName)
    messageGroups.append(messageGroup)
    return messageGroups


messageGroup = createMessageGroups(signalTemplate)


class GroundTruthTrack(ObjectFromMessage):
    _attribs = tuple(tmpl[1] for tmpl in signalTemplate)

    def __init__(self, id, time, source, group, invalid_mask, scaletime=None):
        self._invalid_mask = invalid_mask
        self._group = group

        super(GroundTruthTrack, self).__init__(id, time, None, None, scaleTime=None)
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
        arr = np.ma.masked_array(data, mask=self._invalid_mask)
        return arr

    def Long_Delta_Distance(self):
         return self._Long_Delta_Distance

    def Lat_Delta_Distance(self):
        return self._Lat_Delta_Distance

    def Long_Delta_Velocity(self):
        return self._Long_Delta_Velocity

    def Lat_Delta_Velocity(self):
        return self._Lat_Delta_Velocity

    def tr_state(self):
        valid = ma.masked_array(~self._Long_Delta_Distance.mask, self._Long_Delta_Distance.mask)
        meas = np.ones_like(valid)
        hist = np.ones_like(valid)
        for st, end in maskToIntervals(~self._Long_Delta_Distance.mask):
            if st != 0:
                hist[st] = False
        return TrackingState(valid=valid, measured=meas, hist=hist)

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
        for sg in messageGroup:
            groups.append(source.selectSignalGroup([sg]))
        return groups, commonTime

    def fill(self, groups, common_time):
        import time
        start = time.time()
        details_GroundTruthObject = PrimitiveCollection(common_time)

        for _id, group in enumerate(groups):
            invalid_mask = np.zeros(common_time.size, bool)
            details_GroundTruthObject[_id] = GroundTruthTrack(_id, common_time, None, group, invalid_mask,scaletime=common_time)
        GroundTruthObject = {}
        GroundTruthObject["dx"] = details_GroundTruthObject[0]["Long_Delta_Distance"]
        GroundTruthObject["dy"] = details_GroundTruthObject[0]["Lat_Delta_Distance"]
        GroundTruthObject["vx"] = details_GroundTruthObject[0]["Long_Delta_Velocity"]
        GroundTruthObject["vy"] = details_GroundTruthObject[0]["Lat_Delta_Velocity"]
        GroundTruthObject["alive_intervals"] = details_GroundTruthObject[0]["alive_intervals"]
        GroundTruthObject["tr_state"] = details_GroundTruthObject[0]["tr_state"]
        GroundTruthObject["time"] = common_time

        done = time.time()
        elapsed = done - start
        logger.info("Ground truth delta object creation completed in " + str(elapsed))
        return GroundTruthObject



if __name__ == '__main__':
    from config.Config import init_dataeval
    meas_path = r"C:\Users\wattamwa\Desktop\pAEBS\new_from_hagen\HMC-QZ-STR__2020-12-09_14-11-46.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    tracks = manager_modules.calc('fill_ground_truth_delta_tracks@aebs.fill', manager)
    print(tracks)

