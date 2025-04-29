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
    TrackingState
from primitives.bases import PrimitiveCollection
from pyutils.enum import enum

TRACK_MESSAGE_NUM = 20

MOTION_ST_VALS = (
    'MOVING',
    'STATIONARY',
    'ONCOMING',
    'CROSSING_LEFT',
    'CROSSING_RIGHT',
    'UNKNOWN',
    'STOPPED',
)
LANE_ST_VALS = (
    'UNKNOWN',
    'FAR_LEFT',
    'LEFT',
    'EGO',
    'RIGHT',
    'FAR_RIGHT',
)
OBJ_CLASS_VALS = (
    'POINT',
    'CAR',
    'TRUCK',
    'PEDESTRIAN',
    'MOTORCYCLE',
    'BICYCLE',
    'WIDE',
    'UNCLASSIFIED',
    'OTHER_VEHICLE',
    'TL',
)

MOTION_STATUS = enum(**dict((name, n) for n, name in enumerate(MOTION_ST_VALS)))
LANE_STATUS = enum(**dict((name, n) for n, name in enumerate(LANE_ST_VALS)))
OBJ_CLASS = enum(**dict((name, n) for n, name in enumerate(OBJ_CLASS_VALS)))

signalTemplate = (
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].General.uiID"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Kinematic.fDistXStd"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Kinematic.fDistYStd"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Kinematic.fAabsX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Kinematic.fAabsY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Kinematic.fArelX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Kinematic.fArelY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Kinematic.fDistY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Kinematic.fDistX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Kinematic.fVabsX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Kinematic.fVabsY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Kinematic.fVrelX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Kinematic.fVrelY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].PublicObjData.LaneInformation.eAssociatedLane"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Qualifiers.uiProbabilityOfExistence"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Attributes.eClassification"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Attributes.eDynamicProperty"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Qualifiers.uiEbaObjQuality"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].Qualifiers.uiAccObjQuality"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].ARSData.SensorSpecific.ucFusionQuality"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].ARSData.Geometry.fLength"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[%d].ARSData.Geometry.fWidth"),
)

# signalTemplate = (
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_General_uiID"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fDistXStd"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fDistYStd"),
#
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fAabsX"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fAabsY"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fArelX"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fArelY"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fDistY"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fDistX"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fVabsX"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fVabsY"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fVrelX"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fVrelY"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_PublicObjData_LaneInformation_eAssociatedLane"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Qualifiers_uiProbabilityOfExistence"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Attributes_eClassification"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Attributes_eDynamicProperty"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Qualifiers_uiEbaObjQuality"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Qualifiers_uiAccObjQuality"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_ARSData_SensorSpecific_ucFusionQuality"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_ARSData_Geometry_fLength"),
#     ("FCUArs430FusionObjectList_t",
#      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_ARSData_Geometry_fWidth"),
# )
signalTemplatesh5 = (
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_General_uiID"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fDistXStd"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fDistYStd"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fAabsX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fAabsY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fArelX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fArelY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fDistY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fDistX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fVabsX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fVabsY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fVrelX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fVrelY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_PublicObjData_LaneInformation_eAssociatedLane"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Qualifiers_uiProbabilityOfExistence"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Attributes_eClassification"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Attributes_eDynamicProperty"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Qualifiers_uiEbaObjQuality"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Qualifiers_uiAccObjQuality"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_ARSData_SensorSpecific_ucFusionQuality"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_ARSData_Geometry_fLength"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_ARSData_Geometry_fWidth"),

)

signalTemplateWithoutFusionQuality = (
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_General_uiID"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fDistXStd"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fDistYStd"),

    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fAabsX"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fAabsY"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fArelX"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fArelY"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fDistY"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fDistX"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fVabsX"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fVabsY"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fVrelX"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Kinematic_fVrelY"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_PublicObjData_LaneInformation_eAssociatedLane"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Qualifiers_uiProbabilityOfExistence"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Attributes_eClassification"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Attributes_eDynamicProperty"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Qualifiers_uiEbaObjQuality"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_Qualifiers_uiAccObjQuality"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_ARSData_Geometry_fLength"),
    ("FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI%dI_ARSData_Geometry_fWidth"),

)
signalTemplatesWithoutFusionQualityh5 = (
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_General_uiID"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fDistXStd"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fDistYStd"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fAabsX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fAabsY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fArelX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fArelY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fDistY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fDistX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fVabsX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fVabsY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fVrelX"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Kinematic_fVrelY"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_PublicObjData_LaneInformation_eAssociatedLane"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Qualifiers_uiProbabilityOfExistence"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Attributes_eClassification"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Attributes_eDynamicProperty"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Qualifiers_uiEbaObjQuality"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_Qualifiers_uiAccObjQuality"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_ARSData_Geometry_fLength"),
    ("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
     "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject%d_ARSData_Geometry_fWidth"),

)


def createMessageGroups(MESSAGE_NUM, signalTemplates):
    messageGroups = []
    for m in xrange(MESSAGE_NUM):
        messageGroup1 = {}
        signalDict = []
        for signalTemplate in signalTemplates:
            fullName = signalTemplate[1] % m
            if "fPosX" in fullName or "fPosY" in fullName:
                full_position_string = fullName.split('_aShapePointCoordinatesI')[1]
                pos_index, pos_string = full_position_string.split('I_')
                shortName = pos_string + pos_index
            else:
                # array_signal = signalTemplate[1].split('[')
                # if len(array_signal) == 2:
                #     array_value = array_signal[1].split(',')[1][:-1]
                #     shortName = array_signal[0].split('_')[-1] + array_value
                # else:
				shortName = signalTemplate[1].split('.')[-1]

            messageGroup1[shortName] = (signalTemplate[0], fullName)
        signalDict.append(messageGroup1)
        messageGroup2 = {}
        for signalTemplateh5 in signalTemplatesh5:
            fullName = signalTemplateh5[1] % m
            if "fPosX" in fullName or "fPosY" in fullName:
                full_position_string = fullName.split('_aShapePointCoordinatesI')[1]
                pos_index, pos_string = full_position_string.split('I_')
                shortName = pos_string + pos_index
            else:
                array_signal = signalTemplateh5[1].split('[')
                if len(array_signal) == 2:
                    array_value = array_signal[1].split(',')[1][:-1]
                    shortName = array_signal[0].split('_')[-1] + array_value
                else:
                    shortName = signalTemplateh5[1].split('_')[-1]

            messageGroup2[shortName] = (signalTemplateh5[0], fullName)
        signalDict.append(messageGroup2)
        messageGroups.append(signalDict)
    return messageGroups


def createMessageGroupsWithoutFusionQuality(MESSAGE_NUM, signalTemplates):
    messageGroups = []
    for m in xrange(MESSAGE_NUM):
        messageGroup1 = {}
        signalDict = []
        for signalTemplate in signalTemplates:
            fullName = signalTemplate[1] % m
            if "fPosX" in fullName or "fPosY" in fullName:
                full_position_string = \
                    fullName.split('_aShapePointCoordinatesI')[1]
                pos_index, pos_string = full_position_string.split('I_')
                shortName = pos_string + pos_index
            else:
                array_signal = signalTemplate[1].split('[')
                if len(array_signal) == 2:
                    array_value = array_signal[1].split(',')[1][:-1]
                    shortName = array_signal[0].split('_')[-1] + array_value
                else:
                    shortName = signalTemplate[1].split('_')[-1]

            messageGroup1[shortName] = (signalTemplate[0], fullName)
        signalDict.append(messageGroup1)
        messageGroup2 = {}
        for signalTemplateh5 in signalTemplatesWithoutFusionQualityh5:
            fullName = signalTemplateh5[1] % m
            if "fPosX" in fullName or "fPosY" in fullName:
                full_position_string = \
                    fullName.split('_aShapePointCoordinatesI')[1]
                pos_index, pos_string = full_position_string.split('I_')
                shortName = pos_string + pos_index
            else:
                array_signal = signalTemplateh5[1].split('[')
                if len(array_signal) == 2:
                    array_value = array_signal[1].split(',')[1][:-1]
                    shortName = array_signal[0].split('_')[-1] + array_value
                else:
                    shortName = signalTemplateh5[1].split('_')[-1]

            messageGroup2[shortName] = (signalTemplateh5[0], fullName)
        signalDict.append(messageGroup2)
        messageGroups.append(signalDict)
    return messageGroups


messageGroups = createMessageGroups(TRACK_MESSAGE_NUM, signalTemplate)
messageGroupsWithoutFusionQuality = createMessageGroupsWithoutFusionQuality(TRACK_MESSAGE_NUM,
                                                                            signalTemplateWithoutFusionQuality)


class Flc25ArsFcuTrack(ObjectFromMessage):
    attribs = []
    for signalTemplate in signalTemplate:
        fullName = signalTemplate[1]
        if "fPosX" in fullName or "fPosY" in fullName:
            full_position_string = fullName.split('_aShapePointCoordinatesI')[1]
            pos_index, pos_string = full_position_string.split('I_')
            shortName = pos_string + pos_index
        else:
            # array_signal = signalTemplate[1].split('[')
            # if len(array_signal) == 2:
            #     array_value = array_signal[1].split(',')[1][:-1]
            #     shortName = array_signal[0].split('_')[-1] + array_value
            # else:
			shortName = signalTemplate[1].split('.')[-1]
        attribs.append(shortName)

    _attribs = tuple(attribs)
    _special_methods = 'alive_intervals'

    def __init__(self, id, time, source, group, invalid_mask, scaletime=None):
        self._invalid_mask = invalid_mask
        self._group = group
        super(Flc25ArsFcuTrack, self).__init__(id, time, None, None, scaleTime=None)
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
        arr = np.ma.masked_array(data, mask=self._fDistX.mask)
        return arr

    def dx(self):
        return self._fDistX

    def general_uid(self):
        return self._uiID

    def dx_std(self):
        return self._fDistXStd

    def dy(self):
        return self._fDistY

    def dy_std(self):
        return self._fDistYStd

    def range(self):
        return np.sqrt(np.square(self.dx) + np.square(self.dy))

    def angle(self):
        return np.arctan2(self.dy, self.dx)

    def ax_abs(self):
        return self._fAabsX

    def ay_abs(self):
        return self._fAabsY

    def ax(self):
        return self._fArelX

    def ay(self):
        return self._fArelY

    def vx_abs(self):
        return self._fVabsX

    def vy_abs(self):
        return self._fVabsY

    def vx(self):
        return self._fVrelX

    def vy(self):
        return self._fVrelY

    def width(self):
        return self._fWidth

    def length(self):
        return self._fLength

    def video_conf(self):
        return self._uiProbabilityOfExistence

    def ttc(self):
        with np.errstate(divide='ignore'):
            ttc = np.where(self.vx < -1e-3,  # avoid too large (meaningless) values
                           -self.dx / self.vx,
                           np.inf)
        return ttc

    def invttc(self):
        return 1. / self.ttc

    def aeb_obj_quality(self):
        return self._uiEbaObjQuality

    def acc_obj_quality(self):
        return self._uiAccObjQuality

    def fusion_quality(self):
        return self._ucFusionQuality

    def mov_dir(self):
        crossing_left = self._eDynamicProperty == MOTION_STATUS.CROSSING_LEFT
        crossing_right = self._eDynamicProperty == MOTION_STATUS.CROSSING_RIGHT

        stationary = self._eDynamicProperty == MOTION_STATUS.STATIONARY
        stopped = self._eDynamicProperty == MOTION_STATUS.STOPPED
        unknown = self._eDynamicProperty == MOTION_STATUS.UNKNOWN

        ongoing = self._eDynamicProperty == MOTION_STATUS.MOVING
        oncoming = self._eDynamicProperty == MOTION_STATUS.ONCOMING
        undefined = (unknown | stationary | stopped)
        dummy = np.zeros(self._eDynamicProperty.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._fDistX.mask)
        return MovingDirection(oncoming=oncoming, ongoing=ongoing, undefined=undefined, crossing=arr,
                               crossing_left=crossing_left, crossing_right=crossing_right)

    def obj_type(self):
        point = self._eClassification == OBJ_CLASS.POINT
        car = self._eClassification == OBJ_CLASS.CAR
        truck = self._eClassification == OBJ_CLASS.TRUCK
        pedestrian = self._eClassification == OBJ_CLASS.PEDESTRIAN
        motorcycle = self._eClassification == OBJ_CLASS.MOTORCYCLE
        bicycle = self._eClassification == OBJ_CLASS.BICYCLE
        wide = self._eClassification == OBJ_CLASS.WIDE
        unclassified = self._eClassification == OBJ_CLASS.UNCLASSIFIED
        other_vehicle = self._eClassification == OBJ_CLASS.OTHER_VEHICLE
        tl = self._eClassification == OBJ_CLASS.TL
        unknown = (unclassified | other_vehicle | tl)

        return ObjectType(unknown=unknown, pedestrian=pedestrian, motorcycle=motorcycle, car=car,
                          truck=truck,
                          bicycle=bicycle, point=point, wide=wide)

    def mov_state(self):
        crossing_left = self._eDynamicProperty == MOTION_STATUS.CROSSING_LEFT
        crossing_right = self._eDynamicProperty == MOTION_STATUS.CROSSING_RIGHT
        moving = self._eDynamicProperty == MOTION_STATUS.MOVING
        oncoming = self._eDynamicProperty == MOTION_STATUS.ONCOMING
        stationary = self._eDynamicProperty == MOTION_STATUS.STATIONARY
        stopped = self._eDynamicProperty == MOTION_STATUS.STOPPED
        unknown = self._eDynamicProperty == MOTION_STATUS.UNKNOWN
        dummy = np.zeros(self._eDynamicProperty.shape, dtype=bool)
        arr = np.ma.masked_array(dummy, mask=self._fDistX.mask)
        return MovingState(stat=stationary, stopped=stopped, moving=moving, unknown=unknown, crossing=arr,
                           crossing_left=crossing_left, crossing_right=crossing_right, oncoming=oncoming)

    def tr_state(self):
        valid = ma.masked_array(~self._fDistX.mask, self._fDistX.mask)
        meas = np.ones_like(valid)
        hist = np.ones_like(valid)
        for st, end in maskToIntervals(~self._fDistX.mask):
            if st != 0:
                hist[st] = False
        return TrackingState(valid=valid, measured=meas, hist=hist)

    def lane(self):
        same = self._eAssociatedLane == LANE_STATUS.EGO
        left = self._eAssociatedLane == LANE_STATUS.LEFT
        right = self._eAssociatedLane == LANE_STATUS.RIGHT
        uncorr_left = self._eAssociatedLane == LANE_STATUS.FAR_LEFT
        uncorr_right = self._eAssociatedLane == LANE_STATUS.FAR_RIGHT
        unknown_lane = self._eAssociatedLane == LANE_STATUS.UNKNOWN
        lane = LaneStatus(same=same, left=left, right=right, uncorr_left=uncorr_left,
                          uncorr_right=uncorr_right, unknown=unknown_lane)
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

        isFusionQualityAvailable = source.checkSignal("MFC5xx Device.FCU.FCUArs430FusionObjectList_t",
                                                      "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObject0_ARSData_SensorSpecific_ucFusionQuality") or source.checkSignal(
            "FCUArs430FusionObjectList_t",
            "MFC5xx_Device_FCU_FCUArs430FusionObjectList_t_aFusionObjectI0I_ARSData_SensorSpecific_ucFusionQuality") or source.checkSignal("MFC5xx Device.FCU.FCUArs430FusionObjectList_t","MFC5xx Device.FCU.FCUArs430FusionObjectList_t.aFusionObject[0].ARSData.SensorSpecific.ucFusionQuality")

        if isFusionQualityAvailable:
            for sg in messageGroups:
                groups.append(source.selectSignalGroup(sg))
        else:
            for sg in messageGroupsWithoutFusionQuality:
                groups.append(source.selectSignalGroup(sg))
        return groups, commonTime

    def fill(self, groups, common_time):
        tracks = PrimitiveCollection(common_time)
        signals = messageGroups
        VALID_FLAG = False
        for _id, group in enumerate(groups):
            object_id = group.get_value("uiID", ScaleTime=common_time)
            invalid_mask = (object_id == 255) | (np.isnan(object_id))
            #						if np.all(invalid_mask):
            #								continue
            VALID_FLAG = True
            tracks[_id] = Flc25ArsFcuTrack(_id, common_time, self.source, group, invalid_mask, scaletime=common_time)
        if not VALID_FLAG:
            logging.warning("Error: {} :Measurement does not contain ARS FCU object data".format(self.source.FileName))
        return tracks, signals


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    tracks = manager_modules.calc('fill_flc25_ars_fcu_tracks@aebs.fill', manager)
    print(tracks)

