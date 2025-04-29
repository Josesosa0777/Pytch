# -*- dataeval: method -*-
import sys

import numpy

import interface
from measparser.signalproc import backwardderiv

import searchAEBSWarnEval_CVR2Warnings

DefParam = interface.NullParam

class cSearch(searchAEBSWarnEval_CVR2Warnings.cSearch):
  sensorSignalGroups = [
    {
      "vx_ego": ("General_radar_status", "actual_vehicle_speed"),
      "YR_ego": ("General_radar_status", "cvd_yawrate"),
    },
  ]

  onlineWarningGroups = [
    {
      "cm_collision_warning":  ("General_radar_status", "cm_collision_warning"),
      "cm_mitigation_braking": ("General_radar_status", "cm_mitigation_braking"),
      "cm_emergency_braking":  ("General_radar_status", "cm_emergency_braking"),
    },
  ]

  canSignalGroups = [
    {
      "BPAct_b":  ("EBC1_2Wab_EBS5Knorr", "EBS_Brake_switch"),
      "GPPos_uw": ("EEC2",                "AP_position"),
    },
    {
      "BPAct_b":  ("EBC1_2Wab_EBS5Knorr", "EBS_Brake_switch"),
      "GPPos_uw": ("EEC2-8CF00300",       "AP_position"),
    },
    {
      "BPAct_b":  ("EBC1", "EBSBrakeSwitch"),
      "GPPos_uw": ("EEC2", "AccelPedalPos1"),
    },
  ]

  dep = 'fillAC100_CW@aebs.fill', 'fillAC100@aebs.fill'

  sensor = 'AC100'
  s1Label = 'AC100_CO'
  idx_vote_group = 'AC100 track'
  cipvIndexDefault = 0
  cipvIndexKBAvoidance = cipvIndexDefault
  test_name = 'AC100 Warning'

  def set_accel_quantities(self, report, ego_quas, idx, start, data):
    return

  def get_handle(self, data, handles, interval):
    handle = handles[interval]
    return handle

  def set_calced_accel(self, time, data):
    data['ax_ego'] = backwardderiv(data['vx_ego'], time)
    data['ay_ego'] = numpy.zeros_like(time)
    return


  def calc_activity(self, data):
    if (    'cm_collision_warning'  in data
        and 'cm_mitigation_braking' in data
        and 'cm_emergency_braking'  in data):
      activity = (  (data['cm_collision_warning']  == 1)
                  | (data['cm_mitigation_braking'] == 1)
                  | (data['cm_emergency_braking']  == 1))
    else:
      activity = None
    return activity

  def calc_sensordata(self, signalgroup, time):
    sensordata = signalgroup.get_all_values(ScaleTime=time)
    alias = 'YR_ego'
    sensordata[alias] = numpy.deg2rad(sensordata[alias])
    print >> sys.stderr,\
    "%s in message General_radar_status converted to rad/sec" %alias
    return sensordata

