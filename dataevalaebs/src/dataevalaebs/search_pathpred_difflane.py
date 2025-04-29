# -*- dataeval: init -*-

import numpy as np

import interface
from measproc import cIntervalList
from measproc.report2 import Report
from measparser.signalproc import calcDutyCycle
from aebs.labeling.track import labelMovState


TTC_LIMIT = 3.0
EGO_SPEED_MIN = 10.0/3.6
CONF_LIMIT = 0.5
DY_INLANE_LIMIT = 1.5
DY_OUTLANE_LIMIT = 1.5
OBJFUS_CONSTRAINT = True


init_params = {
  "FLR20_TRACKS": dict(sensor='AC100'),
}

class AC100(object):
  """
  AC100-specific parameters.
  """
  permaname = 'AC100'
  productname = "FLR20"
  objind_labelgroup = 'AC100 track'
  ego_fill = 'calc_flr20_egomotion@aebs.fill'
  obj_fill = 'fill_flr20_raw_tracks@aebs.fill'
  pathpred_lf_fill = 'calc_flr20_pathpred_lf@aebs.fill'
  pathpred_ro_fill = 'calc_flr20_pathpred_ro@aebs.fill'


class Search(interface.iSearch):
  def init(self, sensor):
    assert sensor in globals(), "parameter class for %s not defined" % sensor
    self.sensor = globals()[sensor]
    self.dep = (self.sensor.ego_fill, self.sensor.obj_fill,
                self.sensor.pathpred_lf_fill, self.sensor.pathpred_ro_fill)
    return

  def _create_report(self, intervals):
    batch = self.get_batch()
    votes = batch.get_labelgroups(
      'standard', 'moving state', self.sensor.objind_labelgroup)
    names = batch.get_quanamegroups('ego vehicle', 'target')
    title = "AEBS object candidates"
    return Report(intervals, title, votes=votes, names=names)

  def fill(self):
    # load fills
    modules = self.get_modules()
    objects = modules.fill(self.sensor.obj_fill)
    time_scale = objects.time
    ego_motion = modules.fill(self.sensor.ego_fill).rescale(time_scale)
    pathpred_lf = modules.fill(self.sensor.pathpred_lf_fill).rescale(time_scale)
    pathpred_ro = modules.fill(self.sensor.pathpred_ro_fill).rescale(time_scale)

    # create report
    report = self._create_report(cIntervalList(time_scale))
    ego_moving = (ego_motion.vx > EGO_SPEED_MIN)
    if not np.any(ego_moving):
      return report  # optimization

    # add intervals
    for obj in objects.itervalues():
      ttc = np.where((obj.dx>=0.0) & (obj.vx<-1e-5), -obj.dx/obj.vx, np.inf)
      dx_ = np.atleast_2d(obj.dx).T
      dy_corr_lf = obj.dy - pathpred_lf.eval(dx_).flatten()
      dy_corr_ro = obj.dy - pathpred_ro.eval(dx_).flatten()
      inlane_lf = np.abs(dy_corr_lf) <= DY_INLANE_LIMIT
      inlane_ro = np.abs(dy_corr_ro) <= DY_INLANE_LIMIT
      outlane_lf = np.abs(dy_corr_lf) > DY_OUTLANE_LIMIT
      outlane_ro = np.abs(dy_corr_ro) > DY_OUTLANE_LIMIT
      candidates_mask = (ego_moving & (ttc < TTC_LIMIT) & 
        (obj.radar_conf > CONF_LIMIT) & ~obj.mov_dir.oncoming &
        ((inlane_ro & outlane_lf) | (inlane_lf & outlane_ro)))
      if OBJFUS_CONSTRAINT:
        candidates_mask &= obj.fused

      candidates_intvals = cIntervalList.fromMask(time_scale, candidates_mask)
      candidates_intvals = candidates_intvals.intersect(obj.alive_intervals)
      candidates_intvals = candidates_intvals.merge(0.5)  # smooth
      for st, end in candidates_intvals:
        index = report.addInterval([st, end])
        report.vote(index, 'standard', 'valid')
        report.vote(index, self.sensor.objind_labelgroup, str(obj.id[st]))
        report.set(index, 'target', 'ttc min', ttc[st:end].min())
        report.set(index, 'target', 'confidence avg',
          obj.radar_conf[st:end].mean())
        report.set(index, 'target', 'dy curve avg (radar-only)',
          dy_corr_ro[st:end].mean())
        report.set(index, 'target', 'dy curve avg (lane fusion)',
          dy_corr_lf[st:end].mean())
        report.set(index, 'target', 'fused duty',
          calcDutyCycle(time_scale[st:end], obj.fused[st:end]))
        report.set(index, 'target', 'aeb duty',
          calcDutyCycle(time_scale[st:end], obj.aeb_track[st:end]))
        report.set(index, 'ego vehicle', 'speed', ego_motion.vx[st:end].mean())
        labelMovState(report, index, obj, (st, end), wholetime=False)
    return report

  def search(self, report):
    tags = ('AEBS', self.sensor.permaname)
    result = self.FAILED if report.isEmpty() else self.PASSED
    batch = self.get_batch()
    batch.add_entry(report, result=result, tags=tags)
    return
