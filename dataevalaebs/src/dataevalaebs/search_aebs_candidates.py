# -*- dataeval: init -*-

import numpy as np

import interface
from measproc import cIntervalList
from measproc.report2 import Report
from measparser.signalproc import calcDutyCycle
from primitives.bases import PrimitiveCollection
from aebs.labeling.track import labelMovState


TTC_LIMIT = 3.0
EGO_SPEED_MIN = 10.0/3.6
CONF_LIMIT = 0.5
OBJFUS_CONSTRAINT = True


init_params = {
  "FLR20_TRACKS": dict(sensor='AC100', obj_src='obj_fill'),
  "FLR20_AEBTRACK": dict(sensor='AC100', obj_src='aebobj_fill'),
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
  aebobj_fill = 'fill_flr20_aeb_track@aebs.fill'


class Search(interface.iSearch):
  def init(self, sensor, obj_src):
    assert sensor in globals(), "parameter class for %s not defined" % sensor
    self.sensor = globals()[sensor]
    self.obj_fill = getattr(self.sensor, obj_src)
    self.dep = (self.sensor.ego_fill, self.obj_fill)
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
    objects = modules.fill(self.obj_fill)
    if not isinstance(objects, PrimitiveCollection):
      objects = PrimitiveCollection(objects.time, {0: objects})  # for iteration
    time_scale = objects.time
    ego_motion = modules.fill(self.sensor.ego_fill).rescale(time_scale)

    # create report
    report = self._create_report(cIntervalList(time_scale))
    ego_moving = (ego_motion.vx > EGO_SPEED_MIN)
    if not np.any(ego_moving):
      return report  # optimization

    # add intervals
    for obj in objects.itervalues():
      candidates_mask = (ego_moving & (obj.ttc < TTC_LIMIT) &
        (obj.radar_conf > CONF_LIMIT) & ~obj.mov_dir.oncoming)
      if OBJFUS_CONSTRAINT:
        candidates_mask &= obj.fused
      candidates_intvals = cIntervalList.fromMask(time_scale, candidates_mask)
      candidates_intvals = candidates_intvals.intersect(obj.alive_intervals)
      candidates_intvals = candidates_intvals.merge(0.5)  # smooth
      for st, end in candidates_intvals:
        index = report.addInterval([st, end])
        report.vote(index, 'standard', 'valid')
        report.vote(index, self.sensor.objind_labelgroup, str(obj.id[st]))
        report.set(index, 'target', 'ttc min', obj.ttc[st:end].min())
        report.set(index, 'target', 'confidence avg',
          obj.radar_conf[st:end].mean())
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
