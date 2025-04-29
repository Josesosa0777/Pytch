# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
Search for overtaking situations based on 3 patterns while approaching a forward vehicle with a minimal ego speed:
1. sudden gas pedal position change and steering wheel movement
2. drifting to the left side of the lane and sudden steering wheel movement -> before- and after-check
3. sudden steering wheel angle change

Afterlife-check decides if the situation looks like an overtake or not
"""

import numpy as np
import measparser

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from collections import namedtuple

Param = namedtuple('Param', ['value', 'min', 'max', 'unit', 'comment'])

# default parameters of the detection algorithm
defparams = dict(
  # paramname                  =      (value, min  , max , unit    , comment                                                             )
  # default check params
  range_max                    = Param(60   , 40   , 70  , 'm'     , 'maximum distance of track for default check'                       ),
  relative_speed_max           = Param(0    , -1   , 0   , 'm/s'   , 'maximum relative speed of track for default check'                 ),
  ego_speed_min                = Param(14   , 8    , 18  , 'm/s'   , 'minimum ego speed for default check'                               ),
  track_ax_abs_min             = Param(-1   , -1   , -0.5, 'm/s^2' , 'minimum acceleration (max deceleration) of track for default check'),
  # detection params
  view_range_min               = Param(14   , 10   , 20  , 'm'     , 'minimum view range of the left line for lane info reliability'     ),
  lane_width_min               = Param(2.5  , 2    , 3.5 , 'm'     , 'minimum width of the lane for lane info reliability'               ),
  offset_left_line_max         = Param(0.2  , 0    , 0.5 , 'm'     , 'maximum offset from the left line for lane type overtake'          ),
  gppos_speed_near_min         = Param(120  , 100  , 200 , '%/s'   , 'minimum gas pedal speed for near type overtake'                    ),
  gppos_speed_far_min          = Param(100  , 50   , 200 , '%/s'   , 'minimum gas pedal speed for far type overtake'                     ),
  gppos_change_near_min        = Param(20   , 10   , 50  , '%'     , 'minimum gas pedal change for near type overtake'                   ),
  gppos_change_far_min         = Param(10   , 10   , 30  , '%'     , 'minimum gas pedal change for far type overtake'                    ),
  gppos_speed_fallback_max     = Param(-20  , -100 , 0   , '%/s'   , 'maximum gas pedal fallback speed for gas pedal type overtake'      ),
  st_wh_speed_min              = Param(1.0  , 0.8  , 1.2 , 'rad/s' , 'minimum steering wheel speed for st.wh. type overtake'             ),
  st_wh_change_min             = Param(0.2  , 0.1  , 0.5 , 'rad'   , 'minimum steering wheel change for st.wh. type overtake'            ),
  range_lane_type_max          = Param(35   , 20   , 50  , 'm'     , 'maximum distance of track for lane type overtake'                  ),
  range_st_wh_type_max         = Param(16   , 10   , 25  , 'm'     , 'maximum distance of track for steering wheel type overtake'        ),
  range_near_type_max          = Param(16   , 10   , 25  , 'm'     , 'maximum distance of track for near type overtake'                  ),
  range_far_type_min           = Param(35   , 30   , 50  , 'm'     , 'minimum distance of track for far type overtake'                   ),
  st_wh_speed_lane_type_min    = Param(0.6  , 0.4  , 0.8 , 'rad/s' , 'minimum steering wheel speed for lane type overtake'               ),
  st_wh_speed_gppos_type_min   = Param(0.15 , 0.1  , 0.4 , 'rad/s' , 'minimum steering wheel speed for gas pedal type overtake'          ),
  relative_speed_far_type_max  = Param(-8   , -10  , -6  , 'm/s'   , 'maximum relative speed of track for far type overtake'             ),
  # afterlife check params
  ego_speed_fallback_time      = Param(0.4  , 0.04 , 1.0 , 's'     , 'ego speed fallback time window for afterlife check'                ),
  ego_speed_fallback_max       = Param(-0.1 , -0.3 , 0   , 'm/s'   , 'maximum ego speed fallback during afterlife check'                 ),
  detection_time_min           = Param(0.2  , 0.1  , 0.5 , 's'     , 'minimum detection time'                                            ),
)

# verify default parameter ranges
for name, param in defparams.iteritems():
  assert param.min <= param.value <= param.max, name

sgs  = [
{
  "SteerWhlAngle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
  "EEC2_appos_00": ("EEC2_00", "EEC2_APPos1_00"),
  "brake_ped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
  "Left_lane_pos": ("Video_Lane_Left_A", "C0_Left_A"),
},
]

class Search(iSearch):

  dep='fill_flr20_aeb_track@aebs.fill', 'calc_flr20_egomotion@aebs.fill', 'calc_flc20_lanes@aebs.fill',

  rule = { 1: u'left line',
           2: u'near',
           3: u'far',
           4: u'steering wheel',
  }

  rule1 = { 1: u'overtake',
            2: u'not enough st. wh.',
            3: u'long check',
            4: u'timeout'
  }

  def init(self):
    self.title = 'overtake'
    names = self.batch.get_quanamegroups('ego vehicle',)
    votes = self.batch.get_labelgroups('overtaking type', 'overtake information')
    self.kwargs = dict(votes = votes, names = names)
    # attach default parameter values to this instance
    for name, param in defparams.iteritems():
      setattr(self, name, param.value)
    return

  def check(self):
    group = self.source.selectSignalGroup(sgs)
    track = self.modules.fill('fill_flr20_aeb_track@aebs.fill')
    ego = self.modules.fill('calc_flr20_egomotion@aebs.fill')
    lanes = self.modules.fill('calc_flc20_lanes@aebs.fill')
    assert track.time is ego.time
    return group, track, ego, lanes

  def default_check(self, range, track_vx, ego_vx, brake_ped_pos, track_speed, id, track_ax):
    #obligatory conditions to start detection
    check = False
    if (     ( id or id == 0 )            #there is a target vehicle
         and np.all( range < self.range_max )         #fw vehicle is within 60 m
         and np.all( track_vx < self.relative_speed_max )       #fw vehicle's  rel. velocity < 0 -> approaching
         and np.all( ego_vx > self.ego_speed_min )        #ego speed > 14 m/s
         and np.all( brake_ped_pos == 0 ) #brake pedal is not used
         and np.all( track_speed > 3 )    #moving object
         and np.all( track_ax > self.track_ax_abs_min )      #fw vehicle doesn't decelerating rapidly
        ):
      check = True
    return check

  def detect_left_line(self, view_range_left, left_line, view_range_rigth, width):
    #drifting to the left side of the lane
    if np.any(view_range_left < self.view_range_min): #left line info is not reliable -> no lane detection
      return False
    if (     np.all(view_range_rigth > self.view_range_min) #if right line info is reliable
         and np.any( width < self.lane_width_min )         #and the lanewidth is not enough -> no lane detection
        ):
      return False
    for i in xrange( left_line.size - 1):
      if left_line[i+1] - left_line[i] > 0.001: #if not constantly drifting to the left side of the lane in the last 0.5 sec -> no lane detection
        return False
    if np.any(left_line < self.offset_left_line_max ): #close to the left line
      return True
    else:
      return False

  def detect_appos(self, appos_speed, appos ):
    #gas pedal speed and delta depends on the relative speed and distance(at high relative speed small gas pedal interaction is visible before warning)
    label = 0
    if (     np.any( appos_speed > self.gppos_speed_near_min )     #sudden gas pedal usage -> high gas pedal speed
         and np.max( appos ) - appos[0] > self.gppos_change_near_min #significant gas pedal position change
         and np.all( appos_speed > self.gppos_speed_fallback_max )     #no gas pedal fallback
        ):
      label = 1                              #overtake type: near
    elif (     np.any( appos_speed > self.gppos_speed_far_min )
           and np.max(appos) - appos[0] > self.gppos_change_far_min
           and np.all( appos_speed > self.gppos_speed_fallback_max )
          ):
      label = 2                              #overtake type: far
    return label

  def detect_steering_wheel_speed(self, st_wh_speed, st_wh):
  #sudden steering wheel movement
    if (     np.any( st_wh_speed > self.st_wh_speed_min )      #sudden steering wheel movement -> high steering wheel angular velocity
         and np.max( st_wh ) - st_wh[0] > self.st_wh_change_min #significant steering wheel angle change
        ):
      return True
    return False

  def overtake_check(self, brake_pedal, view_range, left_line, heading_angle, ego_speed, track_vx, last_speed, track_ax, fusion, lateral_distance):
    #afterlife check: decide the end of the overtaking situation
    check = True
    end = False
    if (     self.speed_check              #speed fallback can be checked
         and ego_speed - last_speed < self.ego_speed_fallback_max #significant speed fallback in the last 0.4 sec
        ):
      check = False
    if (     self.check_lane #lane info is reliable and can be checked
         and view_range > self.view_range_min
        ):
      if left_line[1] < -1.2: #left lane is in the middle of the vehicle -> lane change -> end of detection
        end = True
      elif (    left_line[1] - left_line[0] > 0.001     #drifting away from the left line
             or heading_angle[1] - heading_angle[0] > 0 #filtered heading angle is decreasing
            ):
        check = False
    else:
      self.check_lane = False #lane info is not reliable -> no further checking
    if lateral_distance[1] - lateral_distance[0] > 0: #lateral distance is increasing -> drifting closer to the fw vehicle's middle -> end of overtake situation
      check = False
    if (    brake_pedal > 0 #brake pedal usage
         or track_vx > self.relative_speed_max    #relative velocity > 0
         or ego_speed < self.ego_speed_min  #ego speed is low
         or track_ax < self.track_ax_abs_min   #fw vehicle is decelerating
        ):
      check = False         #any above condition is true -> end of overtaking situation
    return check, end

  def filter(self, data, time, T):
    #low pass filter
    filtered = np.zeros_like(data)
    filtered[0] = data[0]
    const = np.mean(np.diff(time))/T
    for i in xrange(1,data.size):
      filtered[i] = const*(data[i] - filtered[i-1]) + filtered[i-1]
    return filtered

  def search(self, group, track, ego, lanes):
    t = track.time
    dt = np.mean(np.diff(t))
    T = 0.5 #filtering const.
    #signals
    steering_wheel = group.get_value("SteerWhlAngle", ScaleTime=t)
    filtered_steering_wheel = self.filter( steering_wheel, t, T )
    brppos = group.get_value("brake_ped_pos", ScaleTime=t)
    left_line = lanes.left_line.rescale(t)
    right_line = lanes.right_line.rescale(t)
    c0_scaled = left_line.c0 - 1.25
    heading_angle = self.filter(left_line.c1, t, T)
    lanewidth = left_line.c0 - right_line.c0
    time1,appos = group.get_signal("EEC2_appos_00")
    accpedpos = group.get_value("EEC2_appos_00", ScaleTime=t)
    time,wheelangle = group.get_signal("SteerWhlAngle")
    report = Report( cIntervalList(t), self.title, **self.kwargs )
    #derivative of signals
    wheelspeed = measparser.signalproc.backwardderiv(wheelangle,time)
    accpedspeed = measparser.signalproc.backwardderiv(appos,time1)
    t,wheelspeed_scaled = measparser.signalproc.rescale(time,wheelspeed,t)
    t,accpedspeed_scaled = measparser.signalproc.rescale(time1,accpedspeed,t)
    #auxiliary variables, initialize
    length = track.time.size
    a=int(np.floor(0.5/(dt))+1) #0.5s sampling time
    b=int(np.floor(self.ego_speed_fallback_time/(dt))+1) #0.4s for speed fallback check
    c=int(np.floor(4.0/(dt))+1) #4s after-check timeout
    overtake_type = np.zeros(length, dtype=np.uint8)
    info = np.zeros( length, dtype = np.uint8 )
    overtake_detected = False
    type, gaspedal = 0, 0
    lane, steeringwheel = False, False
    self.check_lane = False
    self.speed_check = False
    false_detection = False
    afterlife_end = False
    #print t[d:d+60]
    #print track.dy[d:d+60]
    #print track.video_conf[d:d+60]
    #loop in the measurement
    for i in xrange(2*a,length-1):
      #detecting possible overtake
      if not overtake_detected:
        type = 0
        #default check: every overtake situation must satisfy these conditions
        if not self.default_check( track.range[i-a:i+1], track.vx[i-a:i+1], ego.vx[i-a:i+1], brppos[i-a:i+1], track.vx_abs[i-a:i+1], track.id[i], track.ax_abs[i-a:i+1] ):
          continue
        else:
          #if check is OK, looking for overtaking patterns
          lane = self.detect_left_line( left_line.view_range[i-a:i+1], c0_scaled[i-a:i+1], right_line.view_range[i-a:i+1], lanewidth[i-a:i+1] )
          gaspedal = self.detect_appos( accpedspeed_scaled[i-a:i+1], accpedpos[i-a:i+1] )
          steeringwheel = self.detect_steering_wheel_speed( wheelspeed_scaled[i-a:i+1], steering_wheel[i-a:i+1] )
          if (     lane                                       #possible lane overtaking
               and np.max(wheelspeed_scaled[i-2*a:i+1]) > self.st_wh_speed_lane_type_min #steering wheel angular velocity was high
               and np.all( track.range[i-a:i+1] < self.range_lane_type_max )        #fw vehicle was close enough
              ):
            type = 1                                          #lane overtake
            print t[i], 'lane'
          elif (     gaspedal == 1                             #possible near type gas pedal overtaking
                 and np.max(wheelspeed_scaled[i-a:i+1]) > self.st_wh_speed_gppos_type_min #some steering wheel angular velocity
                 and np.all( track.range[i-a:i+1] < self.range_near_type_max )       #fw vehicle was really close
                ):
            type = 2                                           #near gas pedal overtake
            print t[i], 'near'
          elif (     gaspedal == 2                             #possible far type gas pedal overtaking
                 and np.max(wheelspeed_scaled[i-a:i+1]) > self.st_wh_speed_gppos_type_min #some steering wheel angular velocity
                 and np.any( track.range[i-a:i+1] > self.range_far_type_min )       #fw vehicle was far
                 and np.any( track.vx[i-a:i+1] < self.relative_speed_far_type_max )          #high relative velocity
                ):
            type = 3                                           #far gas pedal overtake
            print t[i], 'far'
          elif (     steeringwheel                       #possible steering wheel overtaking
                 and np.all( track.range[i-a:i+1] < self.range_st_wh_type_max ) #fw vehicel was really close
                ):
            type = 4                                     #steering wheel overtake
            print t[i], 'steeringwheel'
          if type:
            #initialize parameters for afterlife check
            j=i
            self.check_lane = left_line.view_range[i] > self.view_range_min
            overtake_detected = True
            counter = 0
      #check afterlife
      else:
        self.speed_check = (counter+1) > b #speed fallback can be checked or not (after 0.4s of the detection)
        #afterlife conditions
        check, lane_change = self.overtake_check(brppos[i], left_line.view_range[i], c0_scaled[i-1:i+1], heading_angle[i-1:i+1], ego.vx[i], track.vx[i], ego.vx[i-b], track.ax_abs[i], track.video_conf[i-1:i+1], track.dy[i-1:i+1])
        if (    not track.id[j] == track.id[i] #track changed -> end of situation
             or lane_change                    #lane changed -> end of situation
            ):
          afterlife_end = True
          if (     np.any( wheelspeed_scaled[j:i] < -0.3 )                               #steering wheel movement to the right
               and (np.max( steering_wheel[j:i] ) - np.min( steering_wheel[j:i] )) > 0.5 #significant steering wheel angle change
              ):
            info[j:i+1] = 1 #1: verified overtake
          elif track.time[i] - track.time[j] > self.detection_time_min: #overtake flag was true for more than 0.2 sec
            info[j:i+1] = 2 #2: not enough st. wh. but possible ot
          else:
            false_detection = True
            print track.time[i], 'not enough st.wh.'
          print 'overtake flag for',track.time[i] - track.time[j]
        elif not check:
          afterlife_end = True
          if track.time[i] - track.time[j] > self.detection_time_min: #check failed but overtake flag was true for more than 0.2 sec
            info[j:i+1] = 3 #3: long check, possible ot or dangerous situation
          else:
            false_detection = True
            print track.time[i], 'check failed'
          print 'overtake flag for',track.time[i] - track.time[j]
        elif counter == c: #overtake flag was up to 4 sec -> timeout, end of situation
          afterlife_end = True
          info[j:i+1] = 4 #4: timeout
          print track.time[i], 'timeout'
          print 'overtake flag for',track.time[i] - track.time[j]
        counter+=1
        if afterlife_end:
          if not false_detection:
            overtake_type[j:i+1] = type
          overtake_detected = False
          false_detection = False
          afterlife_end = False
    #database records
    for i in xrange(1,5):
      mask = overtake_type == i
      label = self.rule[i]
      for st, end in maskToIntervals(mask):
        index = report.addInterval( (st, end) )
        report.vote( index, 'overtaking type', label )
        report.vote( index, 'overtake information', self.rule1[info[st]] )
        report.set(index, 'ego vehicle', 'steering wheel speed', np.max(wheelspeed_scaled[st-2*a:st+1]))
        report.set(index, 'ego vehicle', 'appos', np.max( accpedpos[st-a:st+1] ) - accpedpos[st-a])
        report.set(index, 'ego vehicle', 'appos speed', np.max(accpedspeed_scaled[st-a:st+1]))
    report.sort()
    self.batch.add_entry(report, result=self.PASSED)
    return