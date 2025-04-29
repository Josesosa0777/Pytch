# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

import numpy as np
import numpy.ma as ma
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import TrackingState
from primitives.bases import PrimitiveCollection
import struct

logger = logging.getLogger('fill_ground_truth_objects')
TRACK_MESSAGE_NUM = 1


def latlon2dist(lat_ref, lon_ref, height_ref, lat_obj, lon_obj):
    R = 6378137.0
    r = 6356752.3142
    e = 0.0818191908426
    R_N_Lo = R * (1 - e ** 2) / ((1 - e ** 2 * np.sin((np.deg2rad(lat_ref)) ** 2) ** (3 / 2)))
    R_E_Lo = R / ((1 - e ** 2 * np.sin((np.deg2rad(lat_ref)) ** 2) ** (1 / 2)))

    SF_N = np.deg2rad(R_N_Lo + height_ref)
    SF_E = np.deg2rad(R_E_Lo + height_ref) * np.cos(np.deg2rad(lat_ref))

    dx = (lat_obj - lat_ref) * SF_N
    dy = (lon_obj - lon_ref) * SF_E
    return dx, dy


signalTemplate = ((
                      ("INS_Pos_abs_POI2", "INS_Lat_Abs_POI2"),
                      ("INS_Pos_abs_POI2", "INS_Long_Abs_POI2"),
                      ("INS_Pos_Height_POI1_2", "INS_Height_POI2"),
                      ("INS_VF", "INS_VXF"),
                      ("INS_VF", "INS_VYF"),
                      ("INS_Angle", "INS_ang_Yaw"),
                      ("RatesHoriz", "RZH"),
                      ("AccelHoriz", "AXH"),
                      ("AccelHoriz", "AYH"),
                      ("FB_4A_0", "Latitude"),
                      ("FB_4A_1", "Longitude"),
                      ("FB_4A_10", "FW_Distance"),
                      ("FB_4A_11", "Lat_Distance"),
                      ("FB_4A_3", "Velocity_North"),
                      ("FB_4A_3", "VelocityEast"),
                      ("FB_4A_4", "Acceleration_X"),
                      ("FB_4A_5", "Acceleration_Y"),
                      ("FB_4A_2", "Heading"),
                  ),
                  (
                      ("CAN_ADMA_INS_Pos_abs_POI2", "INS_Lat_Abs_POI2"),
                      ("CAN_ADMA_INS_Pos_abs_POI2", "INS_Long_Abs_POI2"),
                      ("CAN_ADMA_INS_Pos_HeighPOI1_2", "INS_Height_POI2"),
                      ("CAN_ADMA_GPS_VF", "GPS_VXF"),
                      ("CAN_ADMA_GPS_VF", "GPS_VYF"),
                      ("CAN_ADMA_INS_Angle", "INS_ang_Yaw"),
                      ("CAN_ADMA_RatesHoriz", "RZH"),
                      ("CAN_ADMA_AccelHoriz", "AXH"),
                      ("CAN_ADMA_AccelHoriz", "AYH"),
                      ("CAN_4active_FB_4A_0", "Latitude"),
                      ("CAN_4active_FB_4A_1", "Longitude"),
                      ("CAN_4active_FB_4A_10", "FW_Distance"),
                      ("CAN_4active_FB_4A_11", "Lat_Distance"),
                      ("CAN_4active_FB_4A_3", "Velocity_North"),
                      ("CAN_4active_FB_4A_3", "VelocityEast"),
                      ("CAN_4active_FB_4A_4", "Acceleration_X"),
                      ("CAN_4active_FB_4A_5", "Acceleration_Y"),
                      ("CAN_4active_FB_4A_2", "Heading"),
                  ),
                  (
                      ("CAN_ADMA_INS_Pos_abs_POI2", "INS_Lat_Abs_POI2"),
                      ("CAN_ADMA_INS_Pos_abs_POI2", "INS_Long_Abs_POI2"),
                      ("CAN_ADMA_INS_Pos_HeighPOI1_2", "INS_Height_POI2"),
                      ("CAN_ADMA_GPS_VF", "GPS_VXF"),
                      ("CAN_ADMA_GPS_VF", "GPS_VYF"),
                      ("CAN_ADMA_INS_Angle", "INS_ang_Yaw"),
                      ("CAN_ADMA_RatesHoriz", "RZH"),
                      ("CAN_ADMA_AccelHoriz", "AXH"),
                      ("CAN_ADMA_AccelHoriz", "AYH"),
                      ("CAN_4Active_FB_4A_0", "Latitude"),
                      ("CAN_4Active_FB_4A_1", "Longitude"),
                      ("CAN_4Active_FB_4A_10", "FW_Distance"),
                      ("CAN_4Active_FB_4A_11", "Lat_Distance"),
                      ("CAN_4Active_FB_4A_3", "Velocity_North"),
                      ("CAN_4Active_FB_4A_3", "VelocityEast"),
                      ("CAN_4Active_FB_4A_4", "Acceleration_X"),
                      ("CAN_4Active_FB_4A_5", "Acceleration_Y"),
                      ("CAN_4Active_FB_4A_2", "Heading"),
                  ),
)


def createMessageGroups(signalTemplates):
    messageGroups = []
    for group_tmp in signalTemplates:
        messageGroup = {}
        for signalTemplate in group_tmp:
            fullName = signalTemplate[1]
            shortName = fullName
            messageGroup[shortName] = (signalTemplate[0], fullName)
        messageGroups.append(messageGroup)
    return messageGroups


messageGroup = createMessageGroups(signalTemplate)


class GroundTruthTrack(ObjectFromMessage):
    _attribs = tuple({signal[1] for group in signalTemplate for signal in group})

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

    def INS_Lat_Abs_POI2(self):
        return self._INS_Lat_Abs_POI2

    def INS_Long_Abs_POI2(self):
        return self._INS_Long_Abs_POI2

    def INS_Height_POI2(self):
        return self._INS_Height_POI2

    def INS_VXF(self):
        if hasattr(self, '_INS_VXF'):
            return self._INS_VXF
        else:
            return self._GPS_VXF

    def INS_VYF(self):
        if hasattr(self, '_INS_VYF'):
            return self._INS_VYF
        else:
            return self._GPS_VYF

    # Convert yaw value from deg to rad
    def INS_ang_Yaw(self):
        return np.deg2rad(self._INS_ang_Yaw)

    def RZH(self):
        return self._RZH

    def AXH(self):
        return self._AXH

    def AYH(self):
        return self._AYH

    '''Get Ground Truth Data and Convert into float(to fix the issue caused by dcnvt conversion tool)'''

    def Latitude(self):
        return self._Latitude

    def Longitude(self):
        return self._Longitude

    def FW_Distance(self):
        return self._FW_Distance

    def Lat_Distance(self):
        return self._Lat_Distance

    def Velocity_North(self):
        return self._Velocity_North

    def VelocityEast(self):
        return self._VelocityEast

    def Acceleration_X(self):
        return self._Acceleration_X

    def Acceleration_Y(self):
        return self._Acceleration_Y

    def Heading(self):
        return self._Heading

    def roll_ned(self):
        return (np.full(self._INS_ang_Yaw.shape, np.pi))

    def tr_state(self):
        valid = ma.masked_array(~self._Lat_Distance.mask, self._Lat_Distance.mask)
        meas = np.ones_like(valid)
        hist = np.ones_like(valid)
        for st, end in maskToIntervals(~self._Lat_Distance.mask):
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
        groups.append(source.selectSignalGroup(messageGroup))
        return groups, commonTime

    def fill(self, groups, common_time):
        import time
        start = time.time()
        details_GroundTruthObject = PrimitiveCollection(common_time)
        # Create List of Hypothesis objects
        for _id, group in enumerate(groups):
            invalid_mask = np.zeros(common_time.size, bool)
            details_GroundTruthObject[_id] = GroundTruthTrack(_id, common_time, None, group, invalid_mask,
                                                              scaletime=common_time)

        reldistx, reldisty = latlon2dist(details_GroundTruthObject[0]["INS_Lat_Abs_POI2"],
                                         details_GroundTruthObject[0]["INS_Long_Abs_POI2"],
                                         details_GroundTruthObject[0]["INS_Height_POI2"],
                                         details_GroundTruthObject[0]["Latitude"],
                                         details_GroundTruthObject[0]["Longitude"])
        dx_ref = []
        dy_ref = []
        v_obj_vut_relx = []
        v_obj_vut_rely = []
        a_obj_in_ref_x = []
        a_obj_in_ref_y = []
        v_obj_in_ref_x = []
        v_obj_in_ref_y = []

        for k in range(0, len(reldistx)):
            # relative distance
            x_rotation = np.matrix([[1, 0], [0, np.cos(details_GroundTruthObject[0]["roll_ned"][k])]])
            z_rotation = np.matrix([[np.cos(details_GroundTruthObject[0]["INS_ang_Yaw"][k]),
                                     -np.sin(details_GroundTruthObject[0]["INS_ang_Yaw"][k])],
                                    [np.sin(details_GroundTruthObject[0]["INS_ang_Yaw"][k]),
                                     np.cos(details_GroundTruthObject[0]["INS_ang_Yaw"][k])]])

            matmul1 = x_rotation.dot(z_rotation)
            matmul2 = matmul1.dot([reldistx[k], reldisty[k]])
            dx_ref = np.append(dx_ref, matmul2.item(0))
            dy_ref = np.append(dy_ref, matmul2.item(1))
            # relative velocity
            v_ref_in_ref = matmul1.dot([details_GroundTruthObject[0]["INS_VXF"][k],
                                        details_GroundTruthObject[0]["INS_VYF"][k]])

            v_obj_in_ref = matmul1.dot([details_GroundTruthObject[0]["Velocity_North"][k],
                                        details_GroundTruthObject[0]["VelocityEast"][k]])
            v_obj_in_ref_x = np.append(v_obj_in_ref_x, v_obj_in_ref.item(0))
            v_obj_in_ref_y = np.append(v_obj_in_ref_y, v_obj_in_ref.item(1))

            crossprod = np.cross([0, 0, details_GroundTruthObject[0]["RZH"][k]], [dx_ref[k], dy_ref[k], 0])

            v_obj_ref = v_obj_in_ref - v_ref_in_ref - crossprod[:2]
            v_obj_vut_relx = np.append(v_obj_vut_relx, v_obj_ref.item(0))
            v_obj_vut_rely = np.append(v_obj_vut_rely, v_obj_ref.item(1))

            # relative acceleration

            a_obj_in_ref = matmul1.dot([details_GroundTruthObject[0]["Acceleration_X"][k],
                                        details_GroundTruthObject[0]["Acceleration_Y"][k]])
            a_obj_in_ref_x = np.append(a_obj_in_ref_x, a_obj_in_ref.item(0))
            a_obj_in_ref_y = np.append(a_obj_in_ref_y, a_obj_in_ref.item(1))

        GroundTruthObject = {}
        GroundTruthObject["dx"] = dx_ref

        GroundTruthObject["dy"] = dy_ref
        GroundTruthObject["vx"] = v_obj_vut_relx
        GroundTruthObject["vy"] = v_obj_vut_rely
        GroundTruthObject["vx_abs"] = v_obj_in_ref_x
        GroundTruthObject["vy_abs"] = v_obj_in_ref_y
        GroundTruthObject["ax"] = a_obj_in_ref_x
        GroundTruthObject["ay"] = a_obj_in_ref_y
        GroundTruthObject["alive_intervals"] = details_GroundTruthObject[0]["alive_intervals"]
        GroundTruthObject["tr_state"] = details_GroundTruthObject[0]["tr_state"]
        GroundTruthObject["time"] = common_time

        done = time.time()
        elapsed = done - start
        logger.info("Ground truth object creation completed in " + str(elapsed))
        return GroundTruthObject


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Python_Toolchain_2\Evaluation_data\PAEBS\ground_truth\mi5id5511__2024-03-14_09-36-19.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    object = manager_modules.calc('fill_ground_truth_raw_tracks@aebs.fill', manager)
    print(object)
