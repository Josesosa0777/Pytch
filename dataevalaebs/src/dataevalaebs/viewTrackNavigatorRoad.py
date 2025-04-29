import sys

import numpy

import datavis
import measparser
import interface

FUS_OBJID_NUM = 32
FUS_TRAJ_NUM = 20
FUS_TRAJBUF_NUM = 24
INVALID_TRAJ = 255
NOTRAJECTORIES = 999

class cParameter(interface.iParameter):
  def __init__(self, fusHandle):
    self.fusHandle = fusHandle
    self.genKeys()
    pass

# instantiation of module parameters
DEFPARAM = cParameter(NOTRAJECTORIES)
FUS_HANDLE_01 = cParameter(1)
FUS_HANDLE_02 = cParameter(2)
FUS_HANDLE_03 = cParameter(3)
FUS_HANDLE_04 = cParameter(4)
FUS_HANDLE_05 = cParameter(5)
FUS_HANDLE_06 = cParameter(6)
FUS_HANDLE_07 = cParameter(7)
FUS_HANDLE_08 = cParameter(8)
FUS_HANDLE_09 = cParameter(9)
FUS_HANDLE_10 = cParameter(10)
FUS_HANDLE_11 = cParameter(11)
FUS_HANDLE_12 = cParameter(12)
FUS_HANDLE_13 = cParameter(13)
FUS_HANDLE_14 = cParameter(14)
FUS_HANDLE_15 = cParameter(15)
FUS_HANDLE_16 = cParameter(16)
FUS_HANDLE_17 = cParameter(17)
FUS_HANDLE_18 = cParameter(18)
FUS_HANDLE_19 = cParameter(19)
FUS_HANDLE_20 = cParameter(20)
FUS_HANDLE_21 = cParameter(21)
FUS_HANDLE_22 = cParameter(22)
FUS_HANDLE_23 = cParameter(23)
FUS_HANDLE_24 = cParameter(24)
FUS_HANDLE_25 = cParameter(25)
FUS_HANDLE_26 = cParameter(26)
FUS_HANDLE_27 = cParameter(27)
FUS_HANDLE_28 = cParameter(28)
FUS_HANDLE_29 = cParameter(29)
FUS_HANDLE_30 = cParameter(30)
FUS_HANDLE_31 = cParameter(31)
FUS_HANDLE_32 = cParameter(32)
FUS_HANDLE_33 = cParameter(33)
FUS_HANDLE_34 = cParameter(34)
FUS_HANDLE_35 = cParameter(35)
FUS_HANDLE_36 = cParameter(36)
FUS_HANDLE_37 = cParameter(37)
FUS_HANDLE_38 = cParameter(38)
FUS_HANDLE_39 = cParameter(39)
FUS_HANDLE_40 = cParameter(40)
FUS_HANDLE_41 = cParameter(41)
FUS_HANDLE_42 = cParameter(42)
FUS_HANDLE_43 = cParameter(43)
FUS_HANDLE_44 = cParameter(44)
FUS_HANDLE_45 = cParameter(45)
FUS_HANDLE_46 = cParameter(46)
FUS_HANDLE_47 = cParameter(47)
FUS_HANDLE_48 = cParameter(48)
FUS_HANDLE_49 = cParameter(49)
FUS_HANDLE_50 = cParameter(50)
FUS_HANDLE_51 = cParameter(51)
FUS_HANDLE_52 = cParameter(52)
FUS_HANDLE_53 = cParameter(53)
FUS_HANDLE_54 = cParameter(54)
FUS_HANDLE_55 = cParameter(55)
FUS_HANDLE_56 = cParameter(56)
FUS_HANDLE_57 = cParameter(57)
FUS_HANDLE_58 = cParameter(58)
FUS_HANDLE_59 = cParameter(59)
FUS_HANDLE_60 = cParameter(60)
FUS_HANDLE_61 = cParameter(61)
FUS_HANDLE_62 = cParameter(62)
FUS_HANDLE_63 = cParameter(63)

TrajectorySignalGroup = {}
# objects' trajectories
for iFusObj in xrange(FUS_OBJID_NUM):
  TrajectorySignalGroup["fusObj%d.trajNumber" % iFusObj] = ("RadarFC", "fus.ObjData_TC.FusObj.i%d.TrajNumber" % iFusObj)
  TrajectorySignalGroup["fusObj%d.handle" % iFusObj] = ("RadarFC", "fus.ObjData_TC.FusObj.i%d.Handle" % iFusObj)
  TrajectorySignalGroup["fusObj%d.dx" % iFusObj] = ("RadarFC", "fus.ObjData_TC.FusObj.i%d.dxv" % iFusObj)
  TrajectorySignalGroup["fusObj%d.dy" % iFusObj] = ("RadarFC", "fus.ObjData_TC.FusObj.i%d.dyv" % iFusObj)
for iTraj in xrange(FUS_TRAJ_NUM):
  TrajectorySignalGroup["traj%d.curBuf" % iTraj] = ("RadarFC", "fus.ObjData_TC.Trajectory.i%d.TrajHistCurrentIndex" % iTraj)
  for iTrajBuf in xrange(FUS_TRAJBUF_NUM):
    TrajectorySignalGroup["traj%d.buf%d.dx" % (iTraj, iTrajBuf)] = ("RadarFC", "fus.ObjData_TC.Trajectory.i%d.TrajHistBuffer.i%d.dxv" % (iTraj, iTrajBuf))
    TrajectorySignalGroup["traj%d.buf%d.dy" % (iTraj, iTrajBuf)] = ("RadarFC", "fus.ObjData_TC.Trajectory.i%d.TrajHistBuffer.i%d.dyv" % (iTraj, iTrajBuf))
    TrajectorySignalGroup["traj%d.buf%d.trajEnd"   % (iTraj, iTrajBuf)] = ("RadarFC", "fus.ObjData_TC.Trajectory.i%d.TrajHistBuffer.i%d.b.b.TrajEnd_b" % (iTraj, iTrajBuf))
    TrajectorySignalGroup["traj%d.buf%d.trajValid" % (iTraj, iTrajBuf)] = ("RadarFC", "fus.ObjData_TC.Trajectory.i%d.TrajHistBuffer.i%d.b.b.Valid_b"   % (iTraj, iTrajBuf))
# ego trajectory
TrajectorySignalGroup["egoTraj.curBuf"] = ("RadarFC", "fus.General_TC.EgoTrajHistCurrentIndex")
for iTrajBuf in xrange(FUS_TRAJBUF_NUM):
  TrajectorySignalGroup["egoTraj.buf%d.dx" % iTrajBuf] = ("RadarFC", "fus.General_TC.EgoTrajHist.i%d.dxv" % iTrajBuf)
  TrajectorySignalGroup["egoTraj.buf%d.dy" % iTrajBuf] = ("RadarFC", "fus.General_TC.EgoTrajHist.i%d.dyv" % iTrajBuf)
# create list of signalgroups
TrajectorySignalGroups =  [ TrajectorySignalGroup, ]

Lines = [{'CurveLane': ('RadarFC', 'evi.General_TC.kapCurvTraj'),
          'CurveEgo':  ('RadarFC', 'dcp.kapCourse')}]
LinesAC100 = [{'cvd_yawrate':             ('General_radar_status', 'cvd_yawrate'),
               'actual_vehicle_speed':    ('General_radar_status', 'actual_vehicle_speed'),
               'estimated_road_curvature':('General_radar_status', 'estimated_road_curvature')}]

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

ROADRMOLanePolyA0 = 1.5
ROADRSOLanePolyA0 = 0.9
AC100LanePolyA0 = ROADRMOLanePolyA0

def polyClothoid(A0, A1, A2, A3, Distance):
  # f(dx) = 1/6 * a3 * x^3 + 1/2 * a2 * x^2 + tan(a1) * x + a0
  x = numpy.linspace(0.0, Distance, num=20)
  y = numpy.empty_like(x)
  y[0] = A0  # avoid computing 0*inf at x=0
  y[1:] = (A3 / 6.0) * numpy.power(x[1:], 3) + (A2 / 2.0) * numpy.power(x[1:], 2) + numpy.tan(A1) * x[1:] + A0
  return  y, x

def getTrajectoryTime(TrajectorySignalGroup):
  # assumption: all trajectory related signals are on common (TC) time
  TrajTime = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "fusObj0.handle")[0]
  return TrajTime

def processObjectTrajectory(TrajectorySignalGroup, fusHandle):
  nTimeStamps = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "fusObj0.handle")[0].size
  # associate handle to id's
  handleToIndex = numpy.empty(nTimeStamps)
  handleToIndex.fill(numpy.NaN)
  for iFusIndex in xrange(FUS_OBJID_NUM):
    Handles = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "fusObj%d.handle" % iFusIndex)[1]
    handleToIndex = numpy.where(Handles == fusHandle, iFusIndex, handleToIndex)
  # preallocation
  xValues = [numpy.empty(0)] * nTimeStamps
  yValues = [numpy.empty(0)] * nTimeStamps
  # cycle on time values
  for iTime in xrange(nTimeStamps):
    fusIndex = handleToIndex[iTime]
    if numpy.isnan(fusIndex):
      # no fusion index for the given handle
      continue
    trajIndex = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "fusObj%d.trajNumber" % fusIndex)[1][iTime]
    if trajIndex == INVALID_TRAJ:
      # no history for this object at this timestamp
      continue
    bufIndex = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "traj%d.curBuf" % trajIndex)[1][iTime]
    iBuffer = 0
    # cycle on buffers
    while iBuffer < FUS_TRAJBUF_NUM:
      # check condition
      trajEnd   = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "traj%d.buf%d.trajEnd"   % (trajIndex, bufIndex))[1][iTime]
      trajValid = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "traj%d.buf%d.trajValid" % (trajIndex, bufIndex))[1][iTime]
      if trajEnd > 0 or trajValid < 1:  # "boolean" type: numpy.int32
        break
      # store values
      value = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "traj%d.buf%d.dx" % (trajIndex, bufIndex))[1][iTime]
      xValues[iTime] = numpy.insert(xValues[iTime], 0, value)  # insert to the beginning
      value = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "traj%d.buf%d.dy" % (trajIndex, bufIndex))[1][iTime]
      yValues[iTime] = numpy.insert(yValues[iTime], 0, value)
      # update index
      bufIndex = bufIndex-1 if bufIndex > 0 else FUS_TRAJBUF_NUM-1
      iBuffer += 1
    if iBuffer > 0:
      # connect trajectory with the current position
      value = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "fusObj%d.dx" % fusIndex)[1][iTime]
      xValues[iTime] = numpy.append(xValues[iTime], value)
      value = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "fusObj%d.dy" % fusIndex)[1][iTime]
      yValues[iTime] = numpy.append(yValues[iTime], value)
  return xValues, yValues

def processEgoTrajectory(TrajectorySignalGroup):
  nTimeStamps = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "fusObj0.handle")[0].size
  # put all buffer data into two matrices
  xValues = numpy.empty((FUS_TRAJBUF_NUM, nTimeStamps))
  yValues = numpy.empty((FUS_TRAJBUF_NUM, nTimeStamps))
  for iBuffer in xrange(FUS_TRAJBUF_NUM):
    Value = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "egoTraj.buf%d.dx" % iBuffer)[1]
    xValues[iBuffer,:] = Value
    Value = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "egoTraj.buf%d.dy" % iBuffer)[1]
    yValues[iBuffer,:] = Value
  xValues = xValues.T
  yValues = yValues.T
  # make most recent data the last element of the vectors
  BufIndices = interface.Source.getSignalFromSignalGroup(TrajectorySignalGroup, "egoTraj.curBuf")[1]
  ShiftValues = FUS_TRAJBUF_NUM - BufIndices - 1
  for iTime in xrange(nTimeStamps):
    xValues[iTime] = numpy.roll(xValues[iTime], ShiftValues[iTime])
    yValues[iTime] = numpy.roll(yValues[iTime], ShiftValues[iTime])
  # connect trajectory with the current position (which is always the origin)
  xValues = numpy.hstack((xValues, numpy.zeros((nTimeStamps, 1))))
  yValues = numpy.hstack((yValues, numpy.zeros((nTimeStamps, 1))))
  return xValues, yValues

class cTrackNavigatorRoad(interface.iView):
  def view(cls, viewParam):
    TN = datavis.cTrackNavigator()
    TN.addGroups(interface.Groups)
    TN.setLegend(interface.Legends)
    
    for GroupName, (LeftAngle, RightAngle, kwargs) in interface.ViewAngles.iteritems():
      TN.setViewAngle(LeftAngle, RightAngle, GroupName, **kwargs)
    
    Tracks = []
    try:
      Params = interface.Source.selectSignalGroup(Lines)
    except measparser.signalgroup.SignalGroupError, Error:
      print >> sys.stderr, 'CVR3 lanes are not added to the TrackNavigator.\n%s' % Error.message
    else:
      Tracks.append(('CVR3_SIT_SO', 'CurveLane', (
        ('r', (-ROADRSOLanePolyA0, ROADRSOLanePolyA0), 100.0),
        ('r', (-(ROADRSOLanePolyA0 + 2 * ROADRSOLanePolyA0), (ROADRSOLanePolyA0 + 2 * ROADRSOLanePolyA0)), 100.0),
        ('r', (-(ROADRSOLanePolyA0 + 4 * ROADRSOLanePolyA0), (ROADRSOLanePolyA0 + 4 * ROADRSOLanePolyA0)), 100.0))))
      Tracks.append(('CVR3_SIT_MO', 'CurveLane', (
        ('y', (-ROADRMOLanePolyA0, ROADRMOLanePolyA0), 200.0),
        ('y', (-(ROADRMOLanePolyA0 + 2 * ROADRMOLanePolyA0), (ROADRMOLanePolyA0 + 2 * ROADRMOLanePolyA0)), 200.0),
        ('y', (-(ROADRMOLanePolyA0 + 4 * ROADRMOLanePolyA0), (ROADRMOLanePolyA0 + 4 * ROADRMOLanePolyA0)), 200.0))))
      Tracks.append(('CVR3_ATS', 'CurveEgo', (
        ('b', (-ROADRMOLanePolyA0, ROADRMOLanePolyA0), 200.0),
        ('b', (-(ROADRMOLanePolyA0 + 2 * ROADRMOLanePolyA0), (ROADRMOLanePolyA0 + 2 * ROADRMOLanePolyA0)), 200.0),
        ('b', (-(ROADRMOLanePolyA0 + 4 * ROADRMOLanePolyA0), (ROADRMOLanePolyA0 + 4 * ROADRMOLanePolyA0)), 200.0))))
    try:
      AC100Params = interface.Source.selectSignalGroup(LinesAC100)
    except measparser.signalgroup.SignalGroupError, Error:
      print >> sys.stderr, 'AC100 lanes are not added to the TrackNavigator.\n%s' % Error.message
    else:
      AC100Time, AC100Curve = interface.Source.getSignalFromSignalGroup(AC100Params, 'estimated_road_curvature')
      # # Old measurements: normalization correction needed (guess: unsigned, factor=2e-5, offset=-0.32768)
      # AC100Curve = 2.0 * numpy.where(AC100Curve < 0.08192, AC100Curve, AC100Curve - 0.16384)
      
      # New measurements: radius -> curvature; right=positive -> left=positive conversion needed
      with numpy.errstate(divide='ignore'):
        AC100Curve = -1.0 / AC100Curve
      Tracks.append(('AC100Road', (AC100Time, AC100Curve), (
        ('m', (-AC100LanePolyA0, AC100LanePolyA0), 100.0),
        ('m', (-(AC100LanePolyA0 + 2 * AC100LanePolyA0), (AC100LanePolyA0 + 2 * AC100LanePolyA0)), 100.0),
        ('m', (-(AC100LanePolyA0 + 4 * AC100LanePolyA0), (AC100LanePolyA0 + 4 * AC100LanePolyA0)), 100.0))))

    for TrackName, CurveAlias, Lanes in Tracks:
      if isinstance(CurveAlias, str):
        TrackTime, Curve = interface.Source.getSignalFromSignalGroup(Params, CurveAlias)
      else:
        TrackTime, Curve = CurveAlias
      for Color, Aliases, Dist in Lanes:
        for Alias in Aliases:
          Track = TN.addTrack(TrackName, TrackTime, color=Color)
          if isinstance(Alias, str):
            Time, Value = interface.Source.getSignalFromSignalGroup(Params, Alias)
          else:
            Time = TrackTime
            Value = Alias * numpy.ones_like(TrackTime)
          FuncName = Track.addFunc(polyClothoid)
          Track.addParam(FuncName, 'A0', Time, Value)
          Track.addParam(FuncName, 'A1', TrackTime, numpy.zeros_like(TrackTime))
          Track.addParam(FuncName, 'A2', TrackTime, Curve)
          Track.addParam(FuncName, 'A3', TrackTime, numpy.zeros_like(TrackTime))
          Track.addParam(FuncName, 'Distance', TrackTime, Dist * numpy.ones_like(TrackTime))

    try:
      LaneGroupSCAM = interface.Source.selectSignalGroup(LaneGroupsSCAM)
    except measparser.signalgroup.SignalGroupError, Error:
      print >> sys.stderr, 'S-Cam lanes are not added to the TrackNavigator.\n%s' % Error.message
    else:
      TrackTime, _ = interface.Source.getSignalFromSignalGroup(LaneGroupSCAM, 'Position_Right')
      # right
      Track = TN.addTrack('S-Cam lanes', TrackTime, color='g')
      FuncName = Track.addFunc(polyClothoid)
      _, A0 = interface.Source.getSignalFromSignalGroup(LaneGroupSCAM, 'Position_Right')
      Track.addParam(FuncName, 'A0', TrackTime, -A0)
      _, A1 = interface.Source.getSignalFromSignalGroup(LaneGroupSCAM, 'Heading_Angle_Right')
      Track.addParam(FuncName, 'A1', TrackTime, -A1)
      _, A2 = interface.Source.getSignalFromSignalGroup(LaneGroupSCAM, 'Curvature_Right')
      Track.addParam(FuncName, 'A2', TrackTime, -A2)
      _, A3 = interface.Source.getSignalFromSignalGroup(LaneGroupSCAM, 'Curvature_Derivative_Right')
      Track.addParam(FuncName, 'A3', TrackTime, -A3)
      _, R  = interface.Source.getSignalFromSignalGroup(LaneGroupSCAM, 'View_Range_Right')
      Track.addParam(FuncName, 'Distance', TrackTime, R)
      # left
      Track = TN.addTrack('S-Cam lanes', TrackTime, color='g')
      FuncName = Track.addFunc(polyClothoid)
      _, A0 = interface.Source.getSignalFromSignalGroup(LaneGroupSCAM, 'Position_Left')
      Track.addParam(FuncName, 'A0', TrackTime, -A0)
      _, A1 = interface.Source.getSignalFromSignalGroup(LaneGroupSCAM, 'Heading_Angle_Left')
      Track.addParam(FuncName, 'A1', TrackTime, -A1)
      _, A2 = interface.Source.getSignalFromSignalGroup(LaneGroupSCAM, 'Curvature_Left')
      Track.addParam(FuncName, 'A2', TrackTime, -A2)
      _, A3 = interface.Source.getSignalFromSignalGroup(LaneGroupSCAM, 'Curvature_Derivative_Left')
      Track.addParam(FuncName, 'A3', TrackTime, -A3)
      _, R  = interface.Source.getSignalFromSignalGroup(LaneGroupSCAM, 'View_Range_Left')
      Track.addParam(FuncName, 'Distance', TrackTime, R)
        
    for StatusName in interface.Objects.get_selected_by_parent(interface.iFill):
      Time, Objects = interface.Objects.fill(StatusName)
      for Object in Objects:
        TN.addObject(Time, Object)
    
    if viewParam.fusHandle != NOTRAJECTORIES:
      try:
        TrajectorySignalGroup = interface.Source.selectSignalGroup(TrajectorySignalGroups)
      except measparser.signalgroup.SignalGroupError, Error:
        print >> sys.stderr, 'Trajectories are not added to the TrackNavigator.\n%s' % Error.message
      else:
        TrajTime = getTrajectoryTime(TrajectorySignalGroup)
        xObjTraj, yObjTraj = processObjectTrajectory(TrajectorySignalGroup, viewParam.fusHandle)
        TN.addDataset(TrajTime, xObjTraj, yObjTraj, 'FUS_H_%d trajectory' % viewParam.fusHandle)
        xEgoTraj, yEgoTraj = processEgoTrajectory(TrajectorySignalGroup)
        TN.addDataset(TrajTime, xEgoTraj, yEgoTraj, 'Ego trajectory')

    interface.Sync.addClient(TN)
    return
