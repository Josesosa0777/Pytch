from collections import OrderedDict

import numpy as np

from aebs.fill.flr20_raw_tracks_base import CM_SYSTEM_STATUS
from pyutils.enum import enum
from measproc.IntervalList import maskToIntervals

def labelMovState(report, index, obj, interval, wholetime=False):
  slicer = slice(*interval)
  fn = np.all if wholetime else np.any
  # moving state
  if fn( obj.mov_state.stat[slicer] ):
    report.vote(index, 'moving state', 'stationary')
  if fn( obj.mov_state.stopped[slicer] ):
    report.vote(index, 'moving state', 'stopped')
  if fn( obj.mov_state.moving[slicer] ):
    report.vote(index, 'moving state', 'moving')
  if fn( obj.mov_state.unknown[slicer] ):
    report.vote(index, 'moving state', 'unclassified')
  return

def labelMovDir(report, index, obj, interval, wholetime=False):
  slicer = slice(*interval)
  fn = np.all if wholetime else np.any
  # moving direction
  if fn( obj.mov_dir.oncoming[slicer] ):
    report.vote(index, 'moving direction', 'oncoming')
  if fn( obj.mov_dir.ongoing[slicer] ):
    report.vote(index, 'moving direction', 'ongoing')
  return

def labelAssoState(report, index, obj, interval, wholetime=False):
  slicer = slice(*interval)
  fn = np.all if wholetime else np.any
  label_group = 'asso state'
  if fn( obj.measured_by[slicer] ):
    report.vote(index, label_group, 'fused')
  if not fn( obj.measured_by[slicer] ):
    report.vote(index, label_group, 'radar only')
  # TODO: check if no valid data exists to avoid applying label for non-existing
  return

def labelCmSystemStatus(report, index, cm_system_status, interval):
  slicer = slice(*interval)
  values = cm_system_status[slicer]
  if CM_SYSTEM_STATUS.WAITING in values:
    label = '4-Waiting'
  elif CM_SYSTEM_STATUS.BRAKING in values:
    label = '3-Braking'
  elif CM_SYSTEM_STATUS.WARNING in values:
    label = '2-Warning'
  elif CM_SYSTEM_STATUS.ALLOWED in values:
    label = '1-Allowed'
  elif CM_SYSTEM_STATUS.NOT_ALLOWED in values:
    label = '0-Not allowed'
  else:
    raise ValueError('No valid value in cm system status')
  label_group = 'cm system status'
  report.vote(index, label_group, label)
  return

class AllowCancelFlags:
  """
  Label allow cancel flags, and label the achived phased when the cancel flags
  would be active.
  """
  PHASE_GROUP = 'AEBS cascade phase'
  SUPPRESSION_GROUP = 'KB AEBS suppression'
  SUPPRESSION_RESULT_GROUP = 'KB AEBS suppression phase'
  LABEL_GROUPS = PHASE_GROUP, SUPPRESSION_GROUP, SUPPRESSION_RESULT_GROUP

  FLAGS = OrderedDict([
    ('warning', ('cw_allow_entry', 'cw_cancel')),
    ('partial braking', ('cmb_allow_entry', 'cmb_cancel')),
    ('emergency braking', ('cmb_allow_entry', 'cmb_cancel')),
  ])
  PHASE_LEVELS = len(FLAGS)
  GLOBAL_ALLOW = 'cm_allow_entry_global_conditions'
  GLOBAL_CANCEL = 'cm_cancel_global_conditions'

  PHASE_RESULT = enum(allowed=0, cancelled=1, closed=2, forbidden=3)
  """
  Enum for cascade phase result based on allow/cancel flags

  allowed : no problem
  closed : allow flag was inactive at the start of the phase
  forbidden ; cancel flag was active at the start of the phase
  cancelled : cancel flag was active during the phase after start
  """

  def __init__(self, values):
    self._values = values
    return

  def __call__(self, report, index, interval, jumps):
    start, end = interval
    starts = jumps
    ends = jumps[1:]
    ends.append(end)
    prev_phase = 'cancelled'

    for phase, start, end in zip(self.FLAGS, starts, ends):
      result = self._vote(report, index, phase, start, end)
      if result:
        if result == self.PHASE_RESULT.cancelled:
          report.vote(index, self.SUPPRESSION_RESULT_GROUP, phase)
        else:
          report.vote(index, self.SUPPRESSION_RESULT_GROUP, prev_phase)
        break
      prev_phase = phase
    else:
      report.vote(index, self.SUPPRESSION_RESULT_GROUP, phase)
    return

  def _vote(self, report, index, phase, start, end):
    allow, cancel = self.FLAGS[phase]

    global_allows = self._get_intervals(self.GLOBAL_ALLOW, start, end)
    global_allow_v = self._validate_allow_flag(global_allows, start, end)
    global_allow_v and report.vote(index, self.SUPPRESSION_GROUP, self.GLOBAL_ALLOW)

    allows = self._get_intervals(allow, start, end)
    allow_v = self._validate_allow_flag(allows, start, end)
    allow_v and report.vote(index, self.SUPPRESSION_GROUP, allow)

    start = self._get_common_start(global_allows, allows)
    if start != -1 and global_allow_v and allow_v:
      global_cancel_idx = self._get_first_index(self.GLOBAL_CANCEL, start, end)
      global_cancel_v = self._validate_cancel_flag(global_cancel_idx, start, end)
      global_cancel_v and report.vote(index, self.SUPPRESSION_GROUP, self.GLOBAL_CANCEL)

      cancel_idx = self._get_first_index(cancel, start, end)
      cancel_v = self._validate_cancel_flag(cancel_idx, start, end)
      cancel_v and report.vote(index, self.SUPPRESSION_GROUP, cancel)

      if global_cancel_v or cancel_v:
        if min(cancel_idx, global_cancel_idx) > start:
          result = self.PHASE_RESULT.cancelled
        else:
          result = self.PHASE_RESULT.forbidden
      else:
        result = self.PHASE_RESULT.allowed
    else:
      result = self.PHASE_RESULT.closed
    return result

  def _get_first_index(self, name, start, end):
    value = self._values[name][start:end].tolist()
    try:
      index = value.index(1)
    except ValueError:
      index = end
    else:
      index += start
    return index

  def _get_intervals(self, name, start, end):
    mask = self._values[name][start:end] == 1
    intervals = [(s + start, e + start) for s, e in maskToIntervals(mask)]
    return intervals

  @staticmethod
  def _validate_cancel_flag(idx, start, end):
    return idx < end

  @staticmethod
  def _validate_allow_flag(intervals, start, end):
    if intervals:
      s, e = intervals[0]
      return s == start
    return False

  @staticmethod
  def _get_common_start(global_intervals, intervals):
    start = -1
    if global_intervals and intervals:
      s, e  = global_intervals[0]
      ss, ee = intervals[0]
      if s == ss:
        start = s
    return start
 
class ContAllowCancelFlags(AllowCancelFlags):
  """
  Label allow/cancel flags and the achived phase under enabled flags like
  AllowCancelFlags, but the allow flags will be checked continuously while the
  event is active.
  """
  @staticmethod
  def _validate_allow_flag(intervals, start, end):
    if intervals:
      return True
    return False
 
  @staticmethod
  def _get_common_start(global_intervals, intervals):
    for start, end in global_intervals:
      for s, e in intervals:
        if s < end and e > start:
          return max(s, start)
    return -1

