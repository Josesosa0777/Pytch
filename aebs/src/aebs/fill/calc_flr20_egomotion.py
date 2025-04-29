# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import sys

import numpy as np
import scipy.signal

from measparser.signalgroup import SignalGroupError
from primitives.egomotion import EgoMotion
import interface

EXP_UNITS = {
  'yawrate_radar_deg': (u'\u00B0/s', u'°/s'),  # degree/s
  'yawrate_ref':       ('rad/s',),
  'yawrate_deg':       (u'\u00B0/s', u'°/s'),  # degree/s
  'vx':                ('m/s',),
}

UNKNOWN_FRAME_MSG = 'Warning: ' \
  'unknown FLR20 coordinate frame, assuming right=positive configuration (%s)'

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

def is_left_positive(source, exception=False):
  """
  Checks the direction of the lateral axis of the radar's coordinate frame,
  based on the radar's and a reference sensor's yaw rate signals (prefers the
  sign which gives the smaller LS error).
  """
  radar_sgs = [
    {'yawrate_radar_deg': ('General_radar_status', 'cvd_yawrate')},
  ]
  ref_sgs = [
    {'yawrate_ref': ('VDC2--Message--S_CAM_J1939_Jan_16_2013', 'YawRate')},
    {'yawrate_ref': ('VDC2--Message--H566_All_v_04', 'YawRate')},
    {'yawrate_ref': ('VDC2_0B',  'VDC2_YawRate_0B')},
    {"yawrate_ref": ("CAN_Vehicle_VDC2_3E","VDC2_YawRate_3E")},
    {'yawrate_ref': ('VDC2',     'YAW_Rate')},
    {'yawrate_ref': ('VDC2',     'YawRate')},
    {'yawrate_ref': ('RadarFC',  'evi.General_TC.psiDtOpt')},
    {'yawrate_ref': ('MRR1plus', 'evi.General_TC.psiDtOpt')},
  ]
  left_positive = False
  try:
    radar_group = source.selectSignalGroup(radar_sgs)
    ref_group   = source.selectSignalGroup(ref_sgs)
    time, yawrate_radar_deg, unit_radar = \
      radar_group.get_signal_with_unit('yawrate_radar_deg')
    #check_unit('yawrate_radar_deg', unit_radar)
    yawrate_radar = np.deg2rad(yawrate_radar_deg)
    _, yawrate_ref, unit_ref = \
      ref_group.get_signal_with_unit('yawrate_ref', ScaleTime=time)
    #check_unit('yawrate_ref', unit_ref)
  except (SignalGroupError, AssertionError), error:
    if exception:
      raise
    else:
      print >> sys.stderr, UNKNOWN_FRAME_MSG % error.message
      return left_positive
  else:
    left_positive = (np.sum(( yawrate_radar-yawrate_ref)**2.0) <
                     np.sum((-yawrate_radar-yawrate_ref)**2.0))
  return left_positive

### Copied from viewAEBS_1_accelerations
### TODO: rm
def _LPF_butter_4o_5Hz(t, input_signal):
# input:  t             time [sec] signal as np array
#         input_signal  input signal as np array 
# return: filtered signal as np array 

  # parameters
  n_order  = 4                      # filter order of butterworth filter
  f0 = 5.0                          # -3dB corner frequency [Hz] of butterworth filter
  
  fs = 1.0/np.mean(np.diff(t))      # sampling frequency (assumption: constant sampling interval)
  f_nyq = fs/2.0                    # Nyquist frequency (= 1/2 sampling frequency)
  Wn = f0/f_nyq                     # normalized corner frequency  (related to Nyquist frequency)
  
  # calculate filter coefficients
  B,A = scipy.signal.butter(n_order, Wn)
 
  # calculate filter 
  out_signal = scipy.signal.lfilter(B,A,input_signal)
  
  return out_signal
###

class Calc(interface.iCalc):
  dep = ('calc_flr20_common_time',)

  def check(self):
    sgs = [{
      'vx':          ('General_radar_status', 'actual_vehicle_speed'),
      'yawrate_deg': ('General_radar_status', 'cvd_yawrate'),
    }]
    optsgs = [{
      'ax': ('General_radar_status', 'vehicle_reference_acceleration'),
    }]
    group = self.source.selectSignalGroup(sgs)
    optgroup = self.source.selectLazySignalGroup(optsgs)
    return group, optgroup

  def fill(self, group, optgroup):
    time = self.get_modules().fill('calc_flr20_common_time')
    rescale_kwargs = {'ScaleTime': time, 'Order': 'valid'}
    # vx
    _, vx, unit_vx = group.get_signal_with_unit('vx', **rescale_kwargs)
    #check_unit('vx', unit_vx)
    # yaw rate
    _, yawrate_deg, unit_yawrate = \
      group.get_signal_with_unit('yawrate_deg', **rescale_kwargs)
    #check_unit('yawrate_deg', unit_yawrate)
    yaw_rate = np.deg2rad(yawrate_deg)
    if not is_left_positive(self.source):
      yaw_rate *= -1.0
    # ax
    if 'ax' in optgroup:
      ax = optgroup.get_value('ax', **rescale_kwargs)
    else:
      self.logger.debug(
        "'vehicle_reference_acceleration' not available; calculating ax")
      d_vx = np.gradient(vx)
      d_t = np.gradient(time)
      ax = np.where(d_t > 0.0, d_vx/d_t, 0.0)
      ax = _LPF_butter_4o_5Hz(time, ax)
    # return value
    ego_motion = EgoMotion(time, vx, yaw_rate, ax)
    return ego_motion
