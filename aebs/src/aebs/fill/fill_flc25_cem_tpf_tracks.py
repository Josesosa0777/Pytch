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
    TrackingState, MeasuredBy, ContributingSensors
from primitives.bases import PrimitiveCollection
from pyutils.enum import enum

TRACK_MESSAGE_NUM = 100

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
    'EGO',
    'LEFT',
    'RIGHT',
    'OUTSIDE_LEFT',
    'OUTSIDE_RIGHT',
    'SNA',
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

BRAKE_LIGHT_VALS = (
    'UNKNOWN',
    'NO_BRAKING',
    'REGULAR_BRAKING',
    'HEAVY_BREAKING',
    'SNA',
)
INDICATOR_VALS = (
    'UNKNOWN',
    'NO_FLASHING',
    'FLASHING_LEFT',
    'FLASHING_RIGHT',
    'HAZARD_FLASHING',
)
MEASURED_BY_VALS = (
    'NO_INFO',
    'PREDICTION',
    'RADAR_ONLY',
    'CAMERA_ONLY',
    'FUSED',
)
CONTRIBUTING_SENSORS_VALS = (
    'NONE',
    'RADAR_ONLY',
    'CAMERA_ONLY',
    'FUSED',
)
MOTION_STATUS = enum(**dict((name, n) for n, name in enumerate(MOTION_ST_VALS)))
LANE_STATUS = enum(**dict((name, n) for n, name in enumerate(LANE_ST_VALS)))
OBJ_CLASS = enum(**dict((name, n) for n, name in enumerate(OBJ_CLASS_VALS)))
BRAKE_LIGHT_ST = enum(**dict((name, n) for n, name in enumerate(BRAKE_LIGHT_VALS)))
INDICATOR_ST = enum(**dict((name, n) for n, name in enumerate(INDICATOR_VALS)))
MEASURED_BY_ST = enum(**dict((name, n) for n, name in enumerate(MEASURED_BY_VALS)))
CONTRIBUTING_SENSORS_ST = enum(**dict((name, n) for n, name in enumerate(CONTRIBUTING_SENSORS_VALS)))

signalTemplate = (
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].general.uiID"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fAabsX"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fAabsY"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fArelX"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fArelY"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fDistY"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fDistX"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fVabsX"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fVabsY"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fVrelX"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fVrelY"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].laneStatus.eAssociatedLane"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].qualifiers.uiProbabilityOfExistence"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].intension.eStatusBrakeLight"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].intension.eStatusTurnIndicator"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].classification.eClassification"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].dynamicProperty.eDynamicProperty"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].general.eMeasuredBy"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fDistXStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fDistYStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fVabsXStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fVabsYStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].geometry.fHeight"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].geometry.fLength"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].geometry.fWidth"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].addKinematic.fYawStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].addKinematic.fYaw"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].addKinematic.fDistZStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].addKinematic.fDistZ"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fVrelXStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].kinematic.fVrelYStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].laneStatus.uiAssociatedLaneConfidence"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].contributingSensors"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].classification.uiClassConfidence"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].general.fLifeTime"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].sensorSpecific.cameraId"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[%d].sensorSpecific.radarId"),
)

# signalTemplate = (
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_general_uiID"),
#
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fAabsX"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fAabsY"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fArelX"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fArelY"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fDistY"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fDistX"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fVabsX"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fVabsY"),
#
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fVrelX"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fVrelY"),
#
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_laneStatus_eAssociatedLane"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_qualifiers_uiProbabilityOfExistence"),
#
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_intension_eStatusBrakeLight"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_intension_eStatusTurnIndicator"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_classification_eClassification"),
#
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_dynamicProperty_eDynamicProperty"),
#
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_general_eMeasuredBy"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fDistXStd"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fDistYStd"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fVabsXStd"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fVabsYStd"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_geometry_fHeight"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_geometry_fLength"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_geometry_fWidth"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_addKinematic_fYawStd"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_addKinematic_fYaw"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_addKinematic_fDistZStd"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_addKinematic_fDistZ"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fVrelXStd"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_kinematic_fVrelYStd"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_laneStatus_uiAssociatedLaneConfidence"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_contributingSensors"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_classification_uiClassConfidence"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_general_fLifeTime"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_sensorSpecific_cameraId"),
#     ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObjectI%dI_sensorSpecific_radarId"),
# )

signalTemplatesh5 = (
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_general_uiID"),

    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fAabsX"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fAabsY"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fArelX"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fArelY"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fDistY"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fDistX"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fVabsX"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fVabsY"),

    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fVrelX"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fVrelY"),

    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_laneStatus_eAssociatedLane"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_qualifiers_uiProbabilityOfExistence"),

    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_intension_eStatusBrakeLight"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_intension_eStatusTurnIndicator"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_classification_eClassification"),

    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_dynamicProperty_eDynamicProperty"),

    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_general_eMeasuredBy"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fDistXStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fDistYStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fVabsXStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fVabsYStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_geometry_fHeight"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_geometry_fLength"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_geometry_fWidth"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_addKinematic_fYawStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_addKinematic_fYaw"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_addKinematic_fDistZStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_addKinematic_fDistZ"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fVrelXStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_kinematic_fVrelYStd"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_laneStatus_uiAssociatedLaneConfidence"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_contributingSensors"),
    ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_classification_uiClassConfidence"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_general_fLifeTime"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_sensorSpecific_cameraId"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_aObject%d_sensorSpecific_radarId"),
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
                full_position_string = fullName.split('_aShapePointCoordinates')[1]
                pos_index, pos_string = full_position_string.split('I_')
                shortName = pos_string + pos_index
            else:
                array_signal = signalTemplateh5[1].split('[')
                if len(array_signal) == 2:
                    array_value = array_signal[1].split(',')[1][:-1]
                    shortName = array_signal[0].split('_')[-1] + array_value
                else:
                    shortName = signalTemplateh5[1].split('_')[-1]
            messageGroup2[shortName] = ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas", fullName)
        signalDict.append(messageGroup2)
        messageGroups.append(signalDict)
    return messageGroups


messageGroups = createMessageGroups(TRACK_MESSAGE_NUM, signalTemplate)


class Flc25CemTpfTrack(ObjectFromMessage):
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
        super(Flc25CemTpfTrack, self).__init__(id, time, None, None, scaleTime=None)
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

    def ay(self):
        return self._fArelY

    def ay_abs(self):
        return self._fAabsY

    def ax(self):
        return self._fArelX

    def ax_abs(self):
        return self._fAabsX

    def vx(self):
        return self._fVrelX

    def vx_std(self):
        return self._fVrelXStd

    def vx_abs(self):
        return self._fVabsX

    def vy(self):
        return self._fVrelY

    def vy_std(self):
        return self._fVrelYStd

    def vy_abs(self):
        return self._fVabsY

    def vx_abs_std(self):
        return self._fVabsXStd

    def vy_abs_std(self):
        return self._fVabsYStd

    def dz(self):
        return self._fDistZ

    def dz_std(self):
        return self._fDistZStd

    def yaw(self):
        return self._fYaw

    def yaw_std(self):
        return self._fYawStd

    def height(self):
        return self._fHeight

    def width(self):
        return self._fWidth

    def length(self):
        return self._fLength

    def life_time(self):
        return self._fLifeTime

    def camera_id(self):
        return self._cameraId

    def radar_id(self):
        return self._radarId

    def video_conf(self):
        return self._uiProbabilityOfExistence

    def lane_conf(self):
        return self._uiAssociatedLaneConfidence

    def class_conf(self):
        return self._uiClassConfidence

    def ttc(self):
        with np.errstate(divide='ignore'):
            ttc = np.where(self.vx < -1e-3,  # avoid too large (meaningless) values
                           -self.dx / self.vx,
                           np.inf)
        return ttc

    def invttc(self):
        return 1. / self.ttc

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
        uncorr_left = self._eAssociatedLane == LANE_STATUS.OUTSIDE_LEFT
        uncorr_right = self._eAssociatedLane == LANE_STATUS.OUTSIDE_RIGHT
        sna = self._eAssociatedLane == LANE_STATUS.SNA
        unknown_lane = self._eAssociatedLane == LANE_STATUS.UNKNOWN
        unknown = (sna | unknown_lane)
        lane = LaneStatus(same=same, left=left, right=right, uncorr_left=uncorr_left,
                          uncorr_right=uncorr_right, unknown=unknown)
        return lane

    def brake_light(self):
        unknown_breaking = self._eStatusBrakeLight == BRAKE_LIGHT_ST.UNKNOWN
        no_breaking = self._eStatusBrakeLight == BRAKE_LIGHT_ST.NO_BRAKING
        regular_breaking = self._eStatusBrakeLight == BRAKE_LIGHT_ST.REGULAR_BRAKING
        heavy_breaking = self._eStatusBrakeLight == BRAKE_LIGHT_ST.HEAVY_BREAKING
        sna = self._eStatusBrakeLight == BRAKE_LIGHT_ST.HEAVY_BREAKING
        unknown = (unknown_breaking | sna)
        on = (regular_breaking | heavy_breaking)
        return BrakeLightStatus(on=on, off=no_breaking, unknown=unknown)

    def blinker(self):
        unknwon_blinker = self._eStatusTurnIndicator == INDICATOR_ST.UNKNOWN
        off = self._eStatusTurnIndicator == INDICATOR_ST.NO_FLASHING
        left = self._eStatusTurnIndicator == INDICATOR_ST.FLASHING_LEFT
        right = self._eStatusTurnIndicator == INDICATOR_ST.FLASHING_RIGHT
        both = self._eStatusTurnIndicator == INDICATOR_ST.HAZARD_FLASHING
        return BlinkerStatus(off=off, left=left, right=right, both=both, unknown=unknwon_blinker)

    def measured_by(self):
        no_info = self._eMeasuredBy == MEASURED_BY_ST.NO_INFO
        prediction = self._eMeasuredBy == MEASURED_BY_ST.PREDICTION
        radar_only = self._eMeasuredBy == MEASURED_BY_ST.RADAR_ONLY
        camera_only = self._eMeasuredBy == MEASURED_BY_ST.CAMERA_ONLY
        fused = self._eMeasuredBy == MEASURED_BY_ST.FUSED
        return MeasuredBy(none=no_info, prediction=prediction, radar_only=radar_only, camera_only=camera_only,
                          fused=fused)

    def contributing_sensors(self):
        none = self._contributingSensors == CONTRIBUTING_SENSORS_ST.NONE
        radar_only = self._contributingSensors == CONTRIBUTING_SENSORS_ST.RADAR_ONLY
        camera_only = self._contributingSensors == CONTRIBUTING_SENSORS_ST.CAMERA_ONLY
        fused = self._contributingSensors == CONTRIBUTING_SENSORS_ST.FUSED
        return ContributingSensors(none=none, radar_only=radar_only, camera_only=camera_only, fused=fused)

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
        signals = messageGroups
        VALID_FLAG = False
        for _id, group in enumerate(groups):
            object_id = group.get_value("uiID", ScaleTime=common_time)
            invalid_mask = (object_id == 255) | (np.isnan(object_id))
            #						if np.all(invalid_mask):
            #								continue
            VALID_FLAG = True
            tracks[_id] = Flc25CemTpfTrack(_id, common_time, self.source, group, invalid_mask, scaletime=common_time)
        if not VALID_FLAG:
            logging.warning("Error: {} :Measurement does not contain CEM TPF object data".format(self.source.FileName))
        return tracks, signals


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    tracks, signals = manager_modules.calc('fill_flc25_cem_tpf_tracks@aebs.fill', manager)
    print(tracks)
    print(signals)
