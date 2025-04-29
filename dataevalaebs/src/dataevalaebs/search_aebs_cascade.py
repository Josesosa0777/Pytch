# -*- dataeval: init -*-

import numpy as np

import interface
from measproc import cIntervalList
from measproc.report2 import Report
from measparser.signalproc import rescale


init_params = {
  "FLR20_KB": dict(sensor='AC100', algo='KB'),
  "FLR20_FLR20": dict(sensor='AC100', algo='FLR20'),
  "FLR20_TRW": dict(sensor='AC100', algo='TRW'),
  "FLR20_RAIL": dict(sensor='AC100', algo='RAIL'),
}

class AC100(object):
  """
  AC100-specific parameters.
  """
  ego_fill = 'calc_flr20_egomotion@aebs.fill'
  aebobj_fill = 'fill_flr20_aeb_track@aebs.fill'

class KB(object):
  """
  KB AEBS algorithm specific parameters - old version.
  """
  algo_fill = 'calc_aebs_phases@aebs.fill'

class FLR20(object):
  """
  KB AEBS algorithm specific parameters.
  """
  algo_fill = 'calc_flr20_aebs_phases-radar@aebs.fill'

class TRW(object):
  """
  TRW AEBS algorithm specific parameters.
  """
  algo_fill = 'calc_trw_aebs_phases@aebs.fill'

class RAIL(object):
  """
  AEBS algorithm parameters that can be used with RAIL measurements.
  """
  algo_fill = 'calc_flr20_aebs_phases-rail@aebs.fill'

class Search(interface.iSearch):
  def init(self, sensor, algo):
    assert sensor in globals(), "parameter class for %s not defined" % sensor
    assert algo in globals(), "parameter class for %s not defined" % algo
    self.sensor = globals()[sensor]
    self.algo = globals()[algo]
    self.dep = (self.sensor.ego_fill,
      self.algo.algo_fill, self.sensor.aebobj_fill)
    return

  def _create_report(self, time):
    batch = self.get_batch()
    votes = batch.get_labelgroups('AEBS cascade phase')
    names = batch.get_quanamegroups('ego vehicle', 'target')
    emptyIntervals = cIntervalList(time)
    title = "AEBS cascade phases"
    return Report(emptyIntervals, title, votes=votes, names=names)

  def _add_intervals(self, report, mask, phasename, ego_vx, obj_vx):
    time = report.intervallist.Time
    for start, end in cIntervalList.fromMask(time, mask):
      intind = report.addInterval((start, end))
      report.vote(intind, 'AEBS cascade phase', phasename)
      end_ = max(end-1, start)
      report.set(intind, 'ego vehicle', 'speed start', ego_vx[start])
      report.set(intind, 'ego vehicle', 'speed end', ego_vx[end_])
      # obj_vx: handling object loss during the phases
      obj_vx_st = obj_vx[start] if obj_vx[start] is not np.ma.masked else np.NaN
      report.set(intind, 'target', 'vx start', obj_vx_st)
      obj_vx_end = obj_vx[end_] if obj_vx[end_] is not np.ma.masked else np.NaN
      report.set(intind, 'target', 'vx end', obj_vx_end)
    return

  def fill(self):
    # cascade
    aebs = self.get_modules().fill(self.algo.algo_fill)
    # ego vx
    ego_motion = self.get_modules().fill(self.sensor.ego_fill)
    _, ego_vx = rescale(ego_motion.time, ego_motion.vx, aebs.time)
    # obj vx (relative)
    aebobj = self.get_modules().fill(self.sensor.aebobj_fill)
    _, obj_vx = rescale(aebobj.time, aebobj.vx, aebs.time)
    # report
    report = self._create_report(aebs.time)
    self._add_intervals(report, aebs.warning,
      'warning', ego_vx, obj_vx)
    self._add_intervals(report, aebs.partial_braking,
      'partial braking', ego_vx, obj_vx)
    self._add_intervals(report, aebs.emergency_braking,
      'emergency braking', ego_vx, obj_vx)
    self._add_intervals(report, aebs.incrash_braking,
      'in-crash braking', ego_vx, obj_vx)
    precrash = aebs.warning | aebs.partial_braking | aebs.emergency_braking
    self._add_intervals(report, precrash,
      'pre-crash intervention', ego_vx, obj_vx)
    full = precrash | aebs.incrash_braking
    self._add_intervals(report, full,
      'full cascade', ego_vx, obj_vx)
    return report

  def search(self, report):
    tags = ('AEBS',)
    result = self.FAILED if report.isEmpty() else self.PASSED
    self.get_batch().add_entry(report, result=result, tags=tags)
    return
