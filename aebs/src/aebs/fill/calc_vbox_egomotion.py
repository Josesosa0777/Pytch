# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import sys

import numpy as np

import interface
from primitives.bases import Primitive
from measparser.signalproc import rescale, calcUnorderedBurstTimeScale

G = 9.81
g2mpss = lambda accel: accel * G


EXP_UNITS = {
  'angvel': (u'\u00B0/s', u'�/s'),  # degree/s
  'accel':  ('g',),
}

def check_unit(alias, unit):
  """
  Check whether the signal's physical unit is the expected one or not.
  Raise AssertionError in the latter case. 
  """
  if unit == '':
    print >> sys.stderr, "Unit check not possible for %s." % alias
    return
  if unit not in EXP_UNITS[alias]:
    raise AssertionError('unexpected unit for %s: %s' % (alias, unit))
  return


def _rescale_signals(times_values, **kwargs):
  times = [time for time, value in times_values]
  time_scale = calcUnorderedBurstTimeScale(times)
  newvals = []
  for time, value in times_values:
    _, newval = rescale(time, value, time_scale, **kwargs)
    newvals.append(newval)
  return time_scale, newvals


class EgoMotionVBox(Primitive):
  def __init__(self, time, ax, ay, az, roll_rate, pitch_rate, yaw_rate):
    Primitive.__init__(self, time)
    self.ax = ax
    self.ay = ay
    self.az = az
    self.roll_rate = roll_rate
    self.pitch_rate = pitch_rate
    self.yaw_rate = yaw_rate
    return


class Calc(interface.iCalc):
  def check(self):
    sgs = [{
      "ax": ("IMU_XAccel_and_YawRate", "X_Accel"),
      "ay": ("IMU_YAccel_and_Temp", "Y_Accel"),
      "az": ("IMU_ZAccel", "Z_Accel"),
      "roll_rate":  ("IMU_Pitch_and_RollRate", "Roll_Rate"),
      "pitch_rate": ("IMU_Pitch_and_RollRate", "Pitch_Rate"),
      "yaw_rate":   ("IMU_XAccel_and_YawRate", "Yaw_Rate"),
    }]
    group = self.get_source().selectSignalGroup(sgs)
    return group
  
  def fill(self, group):
    t_v = []  # time-value pairs
    # ax
    time_ax, ax, unit_ax = group.get_signal_with_unit('ax')
    #check_unit('accel', unit_ax)
    ax = g2mpss(ax)
    t_v.append((time_ax, ax))
    # ay
    time_ay, ay, unit_ay = group.get_signal_with_unit('ay')
    #check_unit('accel', unit_ay)
    ay = -1.0 * g2mpss(ay)
    t_v.append((time_ay, ay))
    # az
    time_az, az, unit_az = group.get_signal_with_unit('az')
    #check_unit('accel', unit_az)
    az = -1.0 * g2mpss(az) + G
    t_v.append((time_az, az))
    # roll rate
    time_rollrate, roll_rate, unit_rollrate = \
      group.get_signal_with_unit('roll_rate')
    #check_unit('angvel', unit_rollrate)
    roll_rate = np.deg2rad(roll_rate)
    t_v.append((time_rollrate, roll_rate))
    # pitch rate
    time_pitchrate, pitch_rate, unit_pitchrate = \
      group.get_signal_with_unit('pitch_rate')
    #check_unit('angvel', unit_pitchrate)
    pitch_rate = -1.0 * np.deg2rad(pitch_rate)
    t_v.append((time_pitchrate, pitch_rate))
    # yaw rate
    time_yawrate, yaw_rate, unit_yawrate = \
      group.get_signal_with_unit('yaw_rate')
    #check_unit('angvel', unit_yawrate)
    yaw_rate = -1.0 * np.deg2rad(yaw_rate)
    t_v.append((time_yawrate, yaw_rate))
    
    # rescale all signals to a common time
    time, values = _rescale_signals(t_v, Order='valid')
    
    # return value
    ego_motion = EgoMotionVBox(time, *values)
    return ego_motion
