# -*- dataeval: init -*-

import numpy as np

import interface
import measproc
import measparser
from calc_flr20_egomotion import is_left_positive

N_AC100_TR = 10
TRACK_IS_EMPTY = 0
INVALID_AC100_TRACK = -1

def _getSignalOrZerosFromSignalGroup(Source, Group, Alias, **kwargs):
  try:
    Time, Value = Source.getSignalFromSignalGroup(Group, Alias, **kwargs)
  except KeyError:
    assert 'ScaleTime' in kwargs, "Unable to get signal without 'ScaleTime'"
    ScaleTime = kwargs['ScaleTime']
    Time, Value = ScaleTime, np.zeros_like(ScaleTime)
  return Time, Value

# signal groups for signals which must be present (checked before fill method runs)
SignalGroups = [{'actual_vehicle_speed': ('General_radar_status', 'actual_vehicle_speed')}]

# signal groups for replaceable signals
AxSignalGroups = [{'actual_vehicle_accel': ('RadarFC',  'evi.General_TC.axvRef')},
                  {'actual_vehicle_accel': ('MRR1plus', 'evi.General_TC.axvRef')},
                  {'actual_vehicle_accel': ('ECU',      'evi.General_TC.axvRef')}]

# optional track signal templates (not all the tracks might be present)
Aliases = 'track_selection_status',\
          'range',\
          'uncorrected_angle',\
          'relative_velocitiy',\
          'acceleration_over_ground',\
          'power',\
          'internal_track_index',\
          'tracking_status',\
          'CW_track'

# optional signals of the optional tracks (not all optional track must contain optional signals)
OptAliases = 'is_video_associated',\
             'radar_confidence',\
             'video_confidence'

GroupLen = len(Aliases)
TrackSignalGroups = []
OptTrackSignalGroups = []
for k in xrange(N_AC100_TR):
  SignalGroup = {}
  for Alias in Aliases:
    Name = 'tr%d_%s' %(k, Alias)
    SignalGroup[Alias] = ('Tracks', Name)
  TrackSignalGroups.append(SignalGroup)
  OptSignalGroup = {}
  for OptAlias in OptAliases:
    OptName = 'tr%d_%s' %(k, OptAlias)
    OptSignalGroup[OptAlias] = ('Tracks', OptName)
  OptTrackSignalGroups.append(OptSignalGroup)

class cFill(interface.iObjectFill):
  def check(self):
    EgoGroup = interface.Source.selectSignalGroup(SignalGroups)
    TrackGroups, Errors = interface.Source._filterSignalGroups(TrackSignalGroups)
    measparser.signalgroup.check_onevalid(TrackGroups, Errors, GroupLen)
    OptTrackGroups = interface.Source.filterSignalGroups(OptTrackSignalGroups)
    AxGroups, Errors = interface.Source._filterSignalGroups(AxSignalGroups)
    AxGroupLengths = []
    for AxGroup in AxGroups:
      AxGroupLengths.append(len(AxGroup.keys()))
    AxGroupLen = max(AxGroupLengths)
    measparser.signalgroup.check_onevalid(AxGroups, Errors, AxGroupLen)
    return EgoGroup, TrackGroups, OptTrackGroups, AxGroups

  def fill(self, EgoGroup, TrackGroups, OptTrackGroups, AxGroups):
    Signals = measparser.signalgroup.extract_signals(EgoGroup, TrackGroups)
    ScaleTime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    kwargs = dict(ScaleTime=ScaleTime)
    EgoSpeed = interface.Source.getSignalFromSignalGroup(EgoGroup, 'actual_vehicle_speed', **kwargs)[1]
    Objects = []
    for AxGroup in AxGroups:
      if AxGroup:
        EgoAccel = interface.Source.getSignalFromSignalGroup(AxGroup, 'actual_vehicle_accel', **kwargs)[1]
        break
    else:
      EgoAccel = measparser.signalproc.backwardderiv(EgoSpeed, ScaleTime, initialmode='copy_back')
    dirCorr = 1.0 if is_left_positive(interface.Source) else -1.0
    
    # loop through all tracks
    for k, (Group, OptGroup) in enumerate(zip(TrackGroups, OptTrackGroups)):
      # skip track if its signals are not present
      if len(Group) != GroupLen:
        continue
      
      # mandatory signals
      TrackSelStat = interface.Source.getSignalFromSignalGroup(Group, 'track_selection_status', **kwargs)[1]
      Range        = interface.Source.getSignalFromSignalGroup(Group, 'range',                  **kwargs)[1]
      AngleDeg     = dirCorr * interface.Source.getSignalFromSignalGroup(Group, 'uncorrected_angle', **kwargs)[1]
      AngleRad     = np.radians(AngleDeg)
      RelVelocity  = interface.Source.getSignalFromSignalGroup(Group, 'relative_velocitiy',     **kwargs)[1]
      AbsAccel     = interface.Source.getSignalFromSignalGroup(Group, 'acceleration_over_ground',   **kwargs)[1]
      Power        = interface.Source.getSignalFromSignalGroup(Group, 'power', **kwargs)[1]
      TrackIndex   = interface.Source.getSignalFromSignalGroup(Group, 'internal_track_index',   **kwargs)[1]
      TrackingStatus = interface.Source.getSignalFromSignalGroup(Group, 'tracking_status',   **kwargs)[1]
      CwFlag       = interface.Source.getSignalFromSignalGroup(Group, 'CW_track',   **kwargs)[1]
      
      # optional signals
      Fused = _getSignalOrZerosFromSignalGroup(interface.Source, OptGroup, 'is_video_associated', **kwargs)[1]
      RadarConf = _getSignalOrZerosFromSignalGroup(interface.Source, OptGroup, 'radar_confidence', **kwargs)[1]
      VideoConf = _getSignalOrZerosFromSignalGroup(interface.Source, OptGroup, 'video_confidence', **kwargs)[1]
      
      o = dict(track=k)
      o["id"] = np.where(TrackingStatus != TRACK_IS_EMPTY, TrackIndex, INVALID_AC100_TRACK)
      labelList  = map(lambda index: "AC100_%d" %index, TrackIndex)
      o["label"] = np.array(labelList)
      # transformation from polar to vehicle coordinates
      o["dx"]  = Range * np.cos(AngleRad)
      o["dy"]  = Range * np.sin(AngleRad)
      o["vx"]  = RelVelocity
      o["vy"]  = np.zeros_like(RelVelocity)
      o["ax"]  = AbsAccel - EgoAccel
      o["power"] = Power
      o["aeb_track"] = CwFlag
      o["fused"]  = Fused
      o["radar_conf"] = RadarConf
      o["video_conf"] = VideoConf
      # calculate signal used for selection
      o["stand"] = (TrackSelStat & (2**4))>0   # Bit4: stationary
      o["type"] = np.where( o["stand"], 
                            self.get_grouptype('AC100_STAT'), 
                            self.get_grouptype('AC100_MOV'))
      #                                                                   moving: green stat: red    ongoing: blue
      o["color"] = measproc.Object.colorByVelocity(EgoSpeed, RelVelocity, [0, 255, 0],  [255, 0, 0], [0, 0, 255])
      Objects.append(o)
    return ScaleTime, Objects
