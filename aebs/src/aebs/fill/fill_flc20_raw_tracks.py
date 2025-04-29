# -*- dataeval: init -*-

import numpy as np

from interface import iCalc
from primitives.bases import PrimitiveCollection
from measparser.signalgroup import select_allvalid_sgs, SignalGroupError
from measproc.IntervalList import maskToIntervals
from fill_flr20_4_fusion import rescaleCanMessages
from fill_flc20_4_fusion import N_SCAM_MESSAGES, createCameraTrackMasks
from flr20_raw_tracks_base import findUniqueIds, TrackFromMessage
from metatrack import MovingState, MovingDirection, ObjectType,\
                      BrakeLightStatus, BlinkerStatus, LaneStatus, TrackingState
from pyutils.enum import enum

INVALID_VIDEO_ID = 0

# enums (position counts)
MOTION_ST_VALS = (
  'NOT_DEFINED',
  'STANDING', # never moved lights on
  'PARKED', #never moved lights off
  'STOPPED_MOVABLE',
  'UNKNOWN_MOVABLE',
  'MOVING_MOVABLE',
  'STOPPED_ONCOMING',
  'UNKNOWN_ONCOMING',
  'MOVING_ONCOMING',
)
LANE_ST_VALS = (
  'NOT_ASSIGNED',
  'EGO_LANE',
  'NEXT_LANE_LEFT',
  'NEXT_LANE_RIGHT',
  'NEXT_NEXT_LANE_LEFT',
  'NEXT_NEXT_LANE_RIGHT',
)
OBJ_CLASS_VALS = (
  'UNDECIDED',
  'TRUCK',
  'CAR',
  'MOTORBIKE',
)
BRAKE_LIGHT_VALS = (
  'NOT_AVAILABLE',
  'ON',
  'OFF',
)
INDICATOR_VALS = (
  'NOT_AVAILABLE',
  'OFF',
  'LEFT',
  'RIGHT',
  'BOTH',
)
MOTION_STATUS  = enum( **dict((name, n) for n, name in enumerate(MOTION_ST_VALS)) )
LANE_STATUS    = enum( **dict((name, n) for n, name in enumerate(LANE_ST_VALS)) )
OBJ_CLASS      = enum( **dict((name, n) for n, name in enumerate(OBJ_CLASS_VALS)) )
BRAKE_LIGHT_ST = enum( **dict((name, n) for n, name in enumerate(BRAKE_LIGHT_VALS)) )
INDICATOR_ST   = enum( **dict((name, n) for n, name in enumerate(INDICATOR_VALS)) )

signals_Mar_27_2013 = {
  # signals of Video_Fusion_Protocol_Released_v1.4b_Mar_27_2013_TrwDebug_mod.dbc
  'Brake_Light'               : ('Video_Object_%d_B', 'Brake_Light_%d_B'              ),
  'Class'                     : ('Video_Object_%d_A', 'Class_%d_A'                    ),
  'Detection_Score'           : ('Video_Object_%d_B', 'Detection_Score_%d_B'          ),
  'ID'                        : ('Video_Object_%d_A', 'ID_%d_A'                       ),
  'Indicator'                 : ('Video_Object_%d_B', 'Indicator_%d_B'                ),
  'Inverse_TTC'               : ('Video_Object_%d_B', 'Inverse_TTC_%d_B'              ),
  'Lane'                      : ('Video_Object_%d_B', 'Lane_%d_B'                     ),
  'Longitudinal_Distance'     : ('Video_Object_%d_A', 'Longitudinal_Distance_%d_A'    ),
  'Longitudinal_Distance_STD' : ('Video_Object_%d_B', 'Longitudinal_Distance_STD_%d_B'),
  'Message_Counter_A'         : ('Video_Object_%d_A', 'Message_Counter_%d_A'          ),
  'Message_Counter_B'         : ('Video_Object_%d_B', 'Message_Counter_%d_B'          ),
  'Motion_Status'             : ('Video_Object_%d_B', 'Motion_Status_%d_B'            ),
  'Rate_Mean_Tan_Angle'       : ('Video_Object_%d_B', 'Rate_Mean_Tan_Angle_%d_B'      ),
  'Relative_Velocity'         : ('Video_Object_%d_A', 'Relative_Velocity_%d_A'        ),
  'Relative_Velocity_STD'     : ('Video_Object_%d_B', 'Relative_Velocity_STD_%d_B'    ),
  'Tan_Left_Angle'            : ('Video_Object_%d_A', 'Tan_Left_Angle_%d_A'           ),
  'Tan_Right_Angle'           : ('Video_Object_%d_A', 'Tan_Right_Angle_%d_A'          ),
  'Width'                     : ('Video_Object_%d_B', 'Width_%d_B'                    ),
}

signals_RAIL = {
  # signals of RAIL (stripped version of Mar_27_2013)
  'Brake_Light'               : ('Video_Object_%d_B', 'Brake_Light'              ),
  'Class'                     : ('Video_Object_%d_A', 'Class'                    ),
  'Detection_Score'           : ('Video_Object_%d_B', 'Detection_Score'          ),
  'ID'                        : ('Video_Object_%d_A', 'ID'                       ),
  'Indicator'                 : ('Video_Object_%d_B', 'Indicator'                ),
  'Inverse_TTC'               : ('Video_Object_%d_B', 'Inverse_TTC'              ),
  'Lane'                      : ('Video_Object_%d_B', 'Lane'                     ),
  'Longitudinal_Distance'     : ('Video_Object_%d_A', 'Longitudinal_Distance'    ),
  'Longitudinal_Distance_STD' : ('Video_Object_%d_B', 'Longitudinal_Distance_STD'),
  'Message_Counter_A'         : ('Video_Object_%d_A', 'Message_Counter'          ), # "Message_Counter" signame is not unique
  'Message_Counter_B'         : ('Video_Object_%d_B', 'Message_Counter'          ),
  'Motion_Status'             : ('Video_Object_%d_B', 'Motion_Status'            ),
  'Rate_Mean_Tan_Angle'       : ('Video_Object_%d_B', 'Rate_Mean_Tan_Angle'      ),
  'Relative_Velocity'         : ('Video_Object_%d_A', 'Relative_Velocity'        ),
  'Relative_Velocity_STD'     : ('Video_Object_%d_B', 'Relative_Velocity_STD'    ),
  'Tan_Left_Angle'            : ('Video_Object_%d_A', 'Tan_Left_Angle'           ),
  'Tan_Right_Angle'           : ('Video_Object_%d_A', 'Tan_Right_Angle'          ),
  'Width'                     : ('Video_Object_%d_B', 'Width'                    ),
}

signals_2013_11_04 = {
  # signals of Video_Fusion_Protocol_2013-11-04_mod.dbc
  'Brake_Light'               : ('Video_Object_%d_B', 'Brake_Light_%d_B'              ),
  'Class'                     : ('Video_Object_%d_A', 'Class_%d_A'                    ),
  'Detection_Score'           : ('Video_Object_%d_B', 'Detection_Score_%d_B'          ),
  'ID'                        : ('Video_Object_%d_A', 'ID_%d_A'                       ),
  'Indicator'                 : ('Video_Object_%d_B', 'Indicator_%d_B'                ),
  'Inverse_TTC'               : ('Video_Object_%d_B', 'Inverse_TTC_%d_B'              ),
  'Lane'                      : ('Video_Object_%d_B', 'Lane_%d_B'                     ),
  'Longitudinal_Distance'     : ('Video_Object_%d_A', 'Longitudinal_Distance_%d_A'    ),
  'Longitudinal_Distance_STD' : ('Video_Object_%d_B', 'Longitudinal_Distance_STD_%d_B'),
  'Message_Counter_A'         : ('Video_Object_%d_A', 'Message_Counter_%d_A'          ),
  'Message_Counter_B'         : ('Video_Object_%d_B', 'Message_Counter_%d_B'          ),
  'Motion_Status'             : ('Video_Object_%d_B', 'Motion_Status_%d_B'            ),
  'Rate_Mean_Angle'           : ('Video_Object_%d_B', 'Rate_Mean_Angle_%d_B'          ),
  'Relative_Velocity'         : ('Video_Object_%d_A', 'Relative_Velocity_%d_A'        ),
  'Relative_Velocity_STD'     : ('Video_Object_%d_B', 'Relative_Velocity_STD_%d_B'    ),
  'Left_Angle'                : ('Video_Object_%d_A', 'Left_Angle_%d_A'               ),
  'Right_Angle'               : ('Video_Object_%d_A', 'Right_Angle_%d_A'              ),
  'Width'                     : ('Video_Object_%d_B', 'Width_%d_B'                    ),
}

messageGroups_Mar_27_2013 = []
messageGroups_RAIL        = []
messageGroups_2013_11_04  = []

signalsNgroups = (
  (signals_Mar_27_2013, messageGroups_Mar_27_2013),
  (signals_RAIL, messageGroups_RAIL),
  (signals_2013_11_04, messageGroups_2013_11_04),
)

# fill in the message groups
for signals, groups in signalsNgroups:
  for m in xrange(N_SCAM_MESSAGES):
    group = {}
    for shortname, (devtemplate,sigtemplate) in signals.iteritems():
      devname = devtemplate %m
      signame = sigtemplate %m if '%d' in sigtemplate else sigtemplate
      group[shortname] = (devname, signame)
    groups.append(group)

class Flc20Track_Mar_27_2013(TrackFromMessage):
  _attribs = tuple( signals_Mar_27_2013.iterkeys() )

  def rescale(self, scaleTime, **kwargs):
    return self.__class__(self._id, self._msgTime, self._msgMasks, self._source,
                          self._groups, self._dirCorr, scaleTime=scaleTime, **kwargs)

  def id(self):
    data = np.repeat( np.uint8(self._id), self.time.size )
    arr = np.ma.masked_array(data, mask=self.dx.mask)
    return arr

  def angle(self):
    return (self.angle_left + self.angle_right) / 2.

  def angle_left(self):
    return self._dirCorr * np.arctan(self._Tan_Left_Angle)

  def angle_right(self):
    return self._dirCorr * np.arctan(self._Tan_Right_Angle)

  def dx(self):
    return self._Longitudinal_Distance

  def dy(self):
    return (self.dy_left + self.dy_right) / 2.

  def dy_left(self):
    return self._dirCorr * self.dx * self._Tan_Left_Angle

  def dy_right(self):
    return self._dirCorr * self.dx * self._Tan_Right_Angle

  def vx(self):
    return self._Relative_Velocity

  def range(self):
    return self.dx / np.cos(self.angle)

  def width(self):
    return self._Width

  def mov_state(self):
    stationary = (   (self._Motion_Status == MOTION_STATUS.STANDING)
                   | (self._Motion_Status == MOTION_STATUS.PARKED) )
    stopped    = (   (self._Motion_Status == MOTION_STATUS.STOPPED_MOVABLE)
                   | (self._Motion_Status == MOTION_STATUS.STOPPED_ONCOMING) )
    moving     = (   (self._Motion_Status == MOTION_STATUS.MOVING_MOVABLE)
                   | (self._Motion_Status == MOTION_STATUS.MOVING_ONCOMING) )
    unknown = ~(stationary | stopped | moving)
    # dummy data
    dummy = np.zeros(self._Motion_Status.shape, dtype=bool)
    arr = np.ma.masked_array(dummy, mask=self.dx.mask)
    return MovingState(stat=stationary, stopped=stopped, moving=moving, unknown=unknown, crossing=arr, crossing_left=arr, crossing_right=arr, oncoming=arr)

  def mov_dir(self):
    oncoming = (   (self._Motion_Status == MOTION_STATUS.STOPPED_ONCOMING)
                 | (self._Motion_Status == MOTION_STATUS.MOVING_ONCOMING) )
    ongoing  = (   (self._Motion_Status == MOTION_STATUS.STOPPED_MOVABLE)
                 | (self._Motion_Status == MOTION_STATUS.MOVING_MOVABLE) )
    undef = ~(ongoing | oncoming)
    dummy = np.zeros(self._Motion_Status.shape, dtype=bool)
    arr = np.ma.masked_array(dummy, mask=self.dx.mask)
    return MovingDirection(oncoming=oncoming, ongoing=ongoing, undefined=undef, crossing=arr, crossing_left=arr, crossing_right=arr)

  def tr_state(self):
    valid = self._ID != INVALID_VIDEO_ID
    meas  = np.ones_like(valid)
    hist  = np.ones_like(valid)
    # object is considered new when first packet received (except meas start)
    for st,end in maskToIntervals(~self._ID.mask):
      if st != 0:
        hist[st] = False
    return TrackingState(valid=valid, measured=meas, hist=hist)

  def lane(self):
    same         = self._Lane == LANE_STATUS.EGO_LANE
    left         = self._Lane == LANE_STATUS.NEXT_LANE_LEFT
    right        = self._Lane == LANE_STATUS.NEXT_LANE_RIGHT
    uncorr_left  = self._Lane == LANE_STATUS.NEXT_NEXT_LANE_LEFT
    uncorr_right = self._Lane == LANE_STATUS.NEXT_NEXT_LANE_RIGHT
    unknown = ~(same | left | right | uncorr_left | uncorr_right)
    lane = LaneStatus(same=same, left=left, right=right, uncorr_left=uncorr_left,
                      uncorr_right=uncorr_right, unknown=unknown)
    return lane

  def obj_type(self):
    car        = self._Class == OBJ_CLASS.CAR
    truck      = self._Class == OBJ_CLASS.TRUCK
    motorcycle = self._Class == OBJ_CLASS.MOTORBIKE
    pedestrian = np.ma.masked_array( np.zeros_like(self._Class), mask=self._Class.mask) # n/a
    bicycle    = np.ma.masked_array( np.zeros_like(self._Class), mask=self._Class.mask) # n/a
    unknown = ~(car | truck | motorcycle)
    dummy = np.zeros(self._Motion_Status.shape, dtype=bool)
    arr = np.ma.masked_array(dummy, mask=self.dx.mask)
    return ObjectType(car=car, truck=truck, motorcycle=motorcycle, pedestrian=pedestrian, bicycle=bicycle, unknown=unknown, point=arr, wide=arr)

  def brake_light(self):
    on  = self._Brake_Light == BRAKE_LIGHT_ST.ON
    off = self._Brake_Light == BRAKE_LIGHT_ST.OFF
    unknown = ~(on | off)
    return BrakeLightStatus(on=on, off=off, unknown=unknown)

  def blinker(self):
    off   = self._Indicator == INDICATOR_ST.OFF
    left  = self._Indicator == INDICATOR_ST.LEFT
    right = self._Indicator == INDICATOR_ST.RIGHT
    both  = self._Indicator == INDICATOR_ST.BOTH
    unknown = ~(off | left | right | both)
    return BlinkerStatus(off=off, left=left, right=right, both=both, unknown=unknown)


class Flc20Track_RAIL(Flc20Track_Mar_27_2013):
  _attribs = tuple( signals_RAIL.iterkeys() )


class Flc20Track_2013_11_04(Flc20Track_Mar_27_2013):
  _attribs = tuple( signals_2013_11_04.iterkeys() )

  def angle_left(self):
    return self._dirCorr * self._Left_Angle

  def angle_right(self):
    return self._dirCorr * self._Right_Angle

  def dy_left(self):
    return self._dirCorr * self.dx * np.tan(self._Left_Angle)

  def dy_right(self):
    return self._dirCorr * self.dx * np.tan(self._Right_Angle)


versions = [
  dict(sgs=messageGroups_Mar_27_2013, cls=Flc20Track_Mar_27_2013),
  dict(sgs=messageGroups_RAIL       , cls=Flc20Track_RAIL),
  dict(sgs=messageGroups_2013_11_04 , cls=Flc20Track_2013_11_04),
]

class cFill(iCalc):
  dep = 'calc_flc20_common_time',

  def check(self):
    modules = self.get_modules()
    msgTime = modules.fill('calc_flc20_common_time')
    for version in versions[::-1]: # latest version checked first to speed up loading
      filtgroups = self.source.filterSignalGroups(version['sgs'])
      firstgroup = version['sgs'][0]
      try:
        optgroups = select_allvalid_sgs( filtgroups, len(firstgroup) )
      except SignalGroupError:
        continue
      else:
        cls = version['cls']
        break
    else:
      raise SignalGroupError('Missing camera track data!')
    return msgTime, optgroups, cls

  def fill(self, msgTime, optgroups, cls):
    # rescale signals (needed for track masks) to common message time
    names = ('ID',)
    messages = rescaleCanMessages(msgTime, self.source, optgroups,
                  names=names, InvalidValue=0)
    # find unique track ids
    ids = [message['ID'].compressed() for message in messages.itervalues()]
    uniqueIds = findUniqueIds(ids, exclude=INVALID_VIDEO_ID)
    # create track masks
    trackMasks = createCameraTrackMasks(messages, uniqueIds)
    # y coord axis direction correction (align to land vehicle coord. frame)
    dirCorr = -1
    # create empty tracks
    rawTracks = PrimitiveCollection(msgTime)
    for id, messageMasks in trackMasks.iteritems():
      rawTracks[id] = cls(id, msgTime, messageMasks, self.source, optgroups, dirCorr)
    return rawTracks
