# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
Search for LDWS warnings
"""

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.camera_sensor_status import flc20_sensor_status_dict
from aebs.par.line_props import line_type_dict


__version__ = 1.2


sgs = [{
  "FLI1_LaneDepartImminentRight_E8": ("FLI1_E8", "FLI1_LaneDepartImminentRight_E8"),
  "FLI1_LaneDepartImminentLeft_E8": ("FLI1_E8", "FLI1_LaneDepartImminentLeft_E8"),
}]

optsgs_common = [{
  "SensorStatus": ("Video_Data_General_B", "SensorStatus"),
  "Me_Line_Changed_Left_B": ("Video_Lane_Left_B", "Me_Line_Changed_Left_B"),
  "Me_Line_Changed_Right_B": ("Video_Lane_Right_B", "Me_Line_Changed_Right_B"),
}]

optsgs_left = [{
  "LineType": ("Video_Lane_Left_A", "Line_Type_Left_A"),
  "C0_wheel": ("Bendix_Info", "C0_left_wheel"),  # [m], right is positive
  "Lateral_Velocity": ("Bendix_Info2", "Lateral_Velocity_Left_B"),  # [cm/s], right is positive
}]

optsgs_right = [{
  "LineType": ("Video_Lane_Right_A", "Line_Type_Right_A"),
  "C0_wheel": ("Bendix_Info", "C0_right_wheel"),  # [m], right is positive
  "Lateral_Velocity": ("Bendix_Info2", "Lateral_Velocity_Right_B"),  # [cm/s], right is positive
}]

class Search(iSearch):
  optdep = {
    'egospeedstart': 'set_egospeed-start@egoeval', 
    'yawratestart': 'set_yawrate-start@egoeval', 
  }
  
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    optgroup_common = self.source.selectLazySignalGroup(optsgs_common)
    optgroup_left = self.source.selectLazySignalGroup(optsgs_left)
    optgroup_right = self.source.selectLazySignalGroup(optsgs_right)
    return group, optgroup_common, optgroup_left, optgroup_right
  
  def fill(self, group, optgroup_common, optgroup_left, optgroup_right):
    # get mandatory signals
    # assumption: left and right signals are in the same message
    time, LDW_left = group.get_signal("FLI1_LaneDepartImminentLeft_E8")
    LDW_right = group.get_value("FLI1_LaneDepartImminentRight_E8")
    
    # get optional signals (common)
    optvalues_left = {}
    get_signals(optvalues_left, optsgs_common[0], optgroup_common, time, self.logger)
    optvalues_right = optvalues_left.copy()
    # get optional signals (specialized for left and right sides)
    get_signals(optvalues_left,  optsgs_left[0],  optgroup_left,  time, self.logger)
    get_signals(optvalues_right, optsgs_right[0], optgroup_right, time, self.logger)
    
    # create report
    names = self.batch.get_quanamegroups('lane', 'ego vehicle')
    votes = self.batch.get_labelgroups('lane', 'line type', 'camera status', 'manoeuvre type')
    report = Report(cIntervalList(time), "LDWS warnings", names=names, votes=votes)
    
    # register intervals
    register_intervals(report, 'left',  LDW_left,  optvalues_left)
    register_intervals(report, 'right', LDW_right, optvalues_right)
    
    # set general quantities
    for qua in 'egospeedstart', 'yawratestart':
      if self.optdep[qua] in self.passed_optdep:
        set_qua_for_report = self.modules.get_module(self.optdep[qua])
        set_qua_for_report(report)
      else:
        self.logger.warning("Inactive module: %s" % self.optdep[qua])
    return report
  
  def search(self, report):
    tags={}
    result = self.FAILED if report.isEmpty() else self.PASSED
    self.batch.add_entry(report, result=result, tags=tags)
    return


def get_signals(optvalues, aliases, optgroup, ScaleTime, logger):
  for alias in aliases:
    if alias in optgroup:
      optvalues[alias] = optgroup.get_value(alias, ScaleTime=ScaleTime)
    else:
      logger.warning("'%s' signal not available; cannot set corresponding quantities" % alias)
  return

def register_intervals(report, lane, signal, optvalues):
  time = report.intervallist.Time
  
  for st,end in maskToIntervals(signal != 0):
    index = report.addInterval([st, end])
    
    report.vote(index, 'lane', lane)
    
    if 'C0_wheel' in optvalues:
      report.set(index, 'lane', 'line distance start', -1.0 * optvalues['C0_wheel'][st] )
    if 'Lateral_Velocity' in optvalues:
      report.set(index, 'ego vehicle', 'lateral speed start', -1.0 * optvalues['Lateral_Velocity'][st] / 100.0) 
    if 'LineType' in optvalues:
      report.vote(index, 'line type', line_type_dict[optvalues['LineType'][st]])
    if 'SensorStatus' in optvalues:
      report.vote(index, 'camera status', flc20_sensor_status_dict[optvalues['SensorStatus'][st]])
    if 'Me_Line_Changed_Left_B' in optvalues and 'Me_Line_Changed_Right_B' in optvalues:
      change2left = detect_lane_change(time, optvalues['Me_Line_Changed_Left_B'], st)
      change2right = detect_lane_change(time, optvalues['Me_Line_Changed_Right_B'], st)
      if change2left and not change2right:
        report.vote(index, 'manoeuvre type', 'left lane change')
      elif change2right and not change2left:
        report.vote(index, 'manoeuvre type', 'right lane change')
      elif not change2right and not change2left:
        report.vote(index, 'manoeuvre type', 'straight driving')
      else:
        report.vote(index, 'manoeuvre type', 'unclassifiable')
  return

def detect_lane_change(time, signal, idx, t_tol_pre=0.1, t_tol_post=2.0):
  idx_pre = time.searchsorted(time[idx]-t_tol_pre)
  idx_post = time.searchsorted(time[idx]+t_tol_post)
  return signal[idx_pre : idx_post+1].any()
