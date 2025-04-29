import sys
import os

import numpy as np

import measparser
import datavis
import interface

from viewVideoOverlay import getVideoName

DefParam = interface.NullParam

SignalGroups = [
  {'VidTime': ('Multimedia', 'Multimedia_1')},
  {'VidTime': ('Multimedia', 'Multimedia')},
  {'VidTime': ('Multimedia', 'Pro9000')},
  {'VidTime': ('Multimedia', 'LifeCam')},
]

AccelGroups = [{'Accel': ('ECU',        'evi.General_TC.axvRef')},
               {'Accel': ('MRR1plus',   'evi.General_TC.axvRef')},
               {'Accel': ('RadarFC',   'evi.General_TC.axvRef')}]

Optionals = [{'ego_speed': ('ECU',      'evi.General_T20.vxvRef'),                 
              'ego_acc':   ('ECU',      'evi.General_T20.axvRef'),},
             {'ego_speed': ('MRR1plus', 'evi.General_T20.vxvRef'),
              'ego_acc':   ('MRR1plus', 'evi.General_T20.axvRef'),},
             {'ego_speed': ('RadarFC', 'evi.General_T20.vxvRef'),
              'ego_acc':   ('RadarFC', 'evi.General_T20.axvRef'),},]

LaneGroupsSCAM = [
  {
    "Position_Right":             ("LKA_Right_Lane_A", "Position"),
    "Heading_Angle_Right":        ("LKA_Right_Lane_B", "Heading_Angle"),
    "Curvature_Right":            ("LKA_Right_Lane_A", "Curvature"),
    "Curvature_Derivative_Right": ("LKA_Right_Lane_A", "Curvature_Derivative"),
    "View_Range_Right":           ("LKA_Right_Lane_B", "View_Range"),
    "Position_Left":              ("LKA_Left_Lane_A",  "Position"),
    "Heading_Angle_Left":         ("LKA_Left_Lane_B",  "Heading_Angle"),
    "Curvature_Left":             ("LKA_Left_Lane_A",  "Curvature"),
    "Curvature_Derivative_Left":  ("LKA_Left_Lane_A",  "Curvature_Derivative"),
    "View_Range_Left":            ("LKA_Left_Lane_B",  "View_Range"),
  },
  {
    "Position_Right":             ("Video_Lane_Right_A", "Position_Right_A"),
    "Heading_Angle_Right":        ("Video_Lane_Right_A", "Heading_Right_A"),
    "Curvature_Right":            ("Video_Lane_Right_A", "Curvature_Right_A"),
    "Curvature_Derivative_Right": ("Video_Lane_Right_A", "Curvature_Rate_Right_A"),
    "View_Range_Right":           ("Video_Lane_Right_B", "View_Range_Right_B"),
    "Position_Left":              ("Video_Lane_Left_A",  "Position_Left_A"),
    "Heading_Angle_Left":         ("Video_Lane_Left_A",  "Heading_Left_A"),
    "Curvature_Left":             ("Video_Lane_Left_A",  "Curvature_Left_A"),
    "Curvature_Derivative_Left":  ("Video_Lane_Left_A",  "Curvature_Rate_Left_A"),
    "View_Range_Left":            ("Video_Lane_Left_B",  "View_Range_Left_B"),
  },
]

LaneGroupsKBPre = [{"angle_left_marking": ("Marking_type", "angle_left_marking"),
                 "angle_right_marking": ("Marking_type", "angle_right_marking"),
                 "dist_left_road_marking": ("Marking_type", "dist_left_road_marking"),
                 "dist_right_road_marking": ("Marking_type", "dist_right_road_marking"),
                 "confidence_left_marking": ("Marking_type", "confidence_left_marking"),
                 "confidence_right_marking": ("Marking_type", "confidence_right_marking"),},]
LaneGroupsSIT = [{'CurveLane': ('RadarFC', 'evi.General_T20.kapCurvTraj')}]
LaneGroupsATS = [{'CurveEgo':  ('RadarFC', 'dcp.kapCourse')}]
LaneGroupsAC100 = [{'cvd_yawrate':             ('General_radar_status', 'cvd_yawrate'),
                    'actual_vehicle_speed':    ('General_radar_status', 'actual_vehicle_speed'),
                    'estimated_road_curvature':('General_radar_status', 'estimated_road_curvature')}]
                    
class cView(interface.iView):
  def check(self):
    AviFile = getVideoName(interface.Source.FileName)
    Group = interface.Source.selectSignalGroup(SignalGroups,
                                               StrictTime=interface.StrictlyGrowingTimeCheck,
                                               TimeMonGapIdx=5)
    return AviFile, Group

  def fill(self, AviFile, Group):
    return AviFile, Group

  def view(self, Param, AviFile, Group):
    VN = datavis.cVideoNavigator(AviFile, self.vidcalibs)
    TimeVidTime, VidTime = interface.Source.getSignalFromSignalGroup(Group, 'VidTime')
    interface.Sync.addClient(VN, (TimeVidTime, VidTime))
    VN.setDisplayTime(TimeVidTime, VidTime)

    VN.setLegend(interface.ShapeLegends)
    VN.addGroups(interface.Groups)
    
    for Status in interface.Objects.get_selected_by_parent(interface.iFill):
      ScaleTime_, Objects = interface.Objects.fill(Status)
      VN.setObjects(ScaleTime_, Objects)
    
    try:
      AccelGroup = interface.Source.selectSignalGroup(AccelGroups)
    except measparser.signalgroup.SignalGroupError:
      print >> sys.stderr, 'Warning: cabin movement compensation unavailable'
    else:
      Time, Accel = interface.Source.getSignalFromSignalGroup(AccelGroup, 'Accel')
      AccelComp = Accel / 50.0  # empirical value
      VN.setAccelComp(Time, AccelComp)   
    
    lanes = []
    lane_time = None
    try:
      LaneGroup = interface.Source.selectSignalGroup(LaneGroupsSCAM)
    except measparser.signalgroup.SignalGroupError:
      sys.stderr.write('SCAM signals not available, lanes not displayed\n')  
    else:
      lane = {}
      lane_time, lane["range"] = interface.Source.getSignalFromSignalGroup(LaneGroup, "View_Range_Right")
      lane["C0"] = -interface.Source.getSignalFromSignalGroup(LaneGroup, "Position_Right", ScaleTime=lane_time)[1]
      lane["C1"] = -interface.Source.getSignalFromSignalGroup(LaneGroup, "Heading_Angle_Right", ScaleTime=lane_time)[1]
      lane["C2"] = -interface.Source.getSignalFromSignalGroup(LaneGroup, "Curvature_Right", ScaleTime=lane_time)[1]
      lane["C3"] = -interface.Source.getSignalFromSignalGroup(LaneGroup, "Curvature_Derivative_Right", ScaleTime=lane_time)[1]
      lane["color"] = [0, 255, 0]
      lanes.append(lane)
      lane = {}
      lane["range"] = interface.Source.getSignalFromSignalGroup(LaneGroup, "View_Range_Left", ScaleTime=lane_time)[1]
      lane["C0"] = -interface.Source.getSignalFromSignalGroup(LaneGroup, "Position_Left", ScaleTime=lane_time)[1]
      lane["C1"] = -interface.Source.getSignalFromSignalGroup(LaneGroup, "Heading_Angle_Left", ScaleTime=lane_time)[1]
      lane["C2"] = -interface.Source.getSignalFromSignalGroup(LaneGroup, "Curvature_Left", ScaleTime=lane_time)[1]
      lane["C3"] = -interface.Source.getSignalFromSignalGroup(LaneGroup, "Curvature_Derivative_Left", ScaleTime=lane_time)[1]
      lane["color"] = [0, 255, 0]
      lanes.append(lane)
    try:
      LaneGroup = interface.Source.selectSignalGroup(LaneGroupsKBPre)
    except measparser.signalgroup.SignalGroupError:
      sys.stderr.write('KBCam Premium signals not available, lanes not displayed\n')  
    else:
      lane = {}
      if lane_time is not None:
        conf = interface.Source.getSignalFromSignalGroup(LaneGroup, "confidence_right_marking", ScaleTime=lane_time)[1]
      else:
        lane_time, conf = interface.Source.getSignalFromSignalGroup(LaneGroup, "confidence_right_marking")
      lane["range"] = np.where(np.logical_and(conf > 0.0, conf <= 1.0), 20.0, 0.0)
      lane["C0"] = -interface.Source.getSignalFromSignalGroup(LaneGroup, "dist_right_road_marking", ScaleTime=lane_time)[1]
      lane["C1"] = -np.deg2rad(interface.Source.getSignalFromSignalGroup(LaneGroup, "angle_right_marking", ScaleTime=lane_time)[1])
      lane["color"] = [255, 0, 0]
      lanes.append(lane)
      lane = {}
      lane["range"] = np.where(interface.Source.getSignalFromSignalGroup(LaneGroup, "confidence_left_marking", ScaleTime=lane_time)[1] > 0, 20.0, 0.0)
      lane["C0"] = +interface.Source.getSignalFromSignalGroup(LaneGroup, "dist_left_road_marking", ScaleTime=lane_time)[1]
      lane["C1"] = -np.deg2rad(interface.Source.getSignalFromSignalGroup(LaneGroup, "angle_left_marking", ScaleTime=lane_time)[1])
      lane["color"] = [255, 0, 0]
      lanes.append(lane)
    try:
      LaneGroup = interface.Source.selectSignalGroup(LaneGroupsSIT)
    except measparser.signalgroup.SignalGroupError:
      sys.stderr.write('CVR3 SIT signals not available, lanes not displayed\n')  
    else:
      lane = {}
      if lane_time is not None:
        curv = interface.Source.getSignalFromSignalGroup(LaneGroup, "CurveLane", ScaleTime=lane_time)[1]
      else:
        lane_time, curv = interface.Source.getSignalFromSignalGroup(LaneGroup, "CurveLane", ScaleTime=lane_time)
      lane["range"] = np.ones_like(curv) * 100.0
      lane["C0"] = -np.ones_like(curv) * -0.9
      lane["C1"] = -np.zeros_like(curv)
      lane["C2"] = +curv
      lane["color"] = [255, 0, 0]
      lanes.append(lane)
      lane = {}
      lane["range"] = np.ones_like(curv) * 100.0
      lane["C0"] = -np.ones_like(curv) * 0.9
      lane["C1"] = -np.zeros_like(curv)
      lane["C2"] = +curv
      lane["color"] = [255, 0, 0]
      lanes.append(lane)
    try:
      LaneGroup = interface.Source.selectSignalGroup(LaneGroupsATS)
    except measparser.signalgroup.SignalGroupError:
      sys.stderr.write('CVR3 ATS signals not available, lanes not displayed\n')  
    else:
      lane = {}
      if lane_time is not None:
        curv = interface.Source.getSignalFromSignalGroup(LaneGroup, "CurveEgo", ScaleTime=lane_time)[1]
      else:
        lane_time, curv = interface.Source.getSignalFromSignalGroup(LaneGroup, "CurveEgo")
      lane["range"] = np.ones_like(curv) * 100.0
      lane["C0"] = -np.ones_like(curv) * -1.5
      lane["C1"] = -np.zeros_like(curv)
      lane["C2"] = +curv
      lane["color"] = [0, 0, 255]
      lanes.append(lane)
      lane = {}
      lane["range"] = np.ones_like(curv) * 100.0
      lane["C0"] = -np.ones_like(curv) * 1.5
      lane["C1"] = -np.zeros_like(curv)
      lane["C2"] = +curv
      lane["color"] = [0, 0, 255]
      lanes.append(lane)
    try:
      LaneGroup = interface.Source.selectSignalGroup(LaneGroupsAC100)
    except measparser.signalgroup.SignalGroupError:
      sys.stderr.write('AC100 signals not available, lanes not displayed\n')  
    else:
      lane = {}
      if lane_time is not None:
        curv = interface.Source.getSignalFromSignalGroup(LaneGroup, "estimated_road_curvature", ScaleTime=lane_time)[1]
      else:
        lane_time, curv = interface.Source.getSignalFromSignalGroup(LaneGroup, "estimated_road_curvature")
      # # Old measurements: normalization correction needed (guess: unsigned, factor=2e-5, offset=-0.32768)
      # curv = 2.0 * np.where(curv < 0.08192, curv, curv - 0.16384)
      
      # New measurements: radius -> curvature; right=positive -> left=positive conversion needed
      with np.errstate(divide='ignore'):
        curv = -1.0 / curv
      lane["range"] = np.ones_like(curv) * 100.0
      lane["C0"] = -np.ones_like(curv) * -1.5
      lane["C1"] = -np.zeros_like(curv)
      lane["C2"] = +curv
      lane["color"] = [255, 0, 255]
      lanes.append(lane)
      lane = {}
      lane["range"] = np.ones_like(curv) * 100.0
      lane["C0"] = -np.ones_like(curv) * 1.5
      lane["C1"] = -np.zeros_like(curv)
      lane["C2"] = +curv
      lane["color"] = [255, 0, 255]
      lanes.append(lane)
    if lanes:
      VN.setLanes(lane_time, lanes)
      
    try:
      OptGroup = interface.Source.selectSignalGroup(Optionals)
    except measparser.signalgroup.SignalGroupError:
      pass
    else:
      for Name in OptGroup:
        Time, Value = interface.Source.getSignalFromSignalGroup(OptGroup, Name)
        Unit = interface.Source.getPhysicalUnitFromSignalGroup(OptGroup, Name)
        VN.setSignal(Name, Time, Value, Unit)
    return
