# -*- dataeval: init -*-

import numpy as np

import interface
from measproc import cIntervalList
from measproc.report2 import Report
from measparser.signalproc import calcDutyCycle
from primitives.bases import PrimitiveCollection
from aebs.labeling.track import labelMovState


EGO_SPEED_MIN = 10.0/3.6
CONF_MIN = 0.5
ABS_DY_FROM_PATH_MAX = 2.0


init_params = {
  "FLR20_TRACKS": dict(sensor='AC100', obj_src='obj_fill'),
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

egopath_fill = 'calc_vbox_egopath@aebs.fill'


def find_objdy_from_path(obj,ego_path, view_range=200.0,mask=None,logger=None):
  time_size = ego_path.time.size
  obj_dx_abs = ego_path.dx + obj.range*np.cos(obj.angle + ego_path.heading)
  obj_dy_abs = ego_path.dy + obj.range*np.sin(obj.angle + ego_path.heading)
  dys = np.ma.masked_all_like(obj.time)
  for i in xrange(time_size):
    if logger is not None: logger.debug("time stamp index: %d" % i)
    if obj.time[i] is np.ma.masked or (mask is not None and not mask[i]):
      continue
    Ddx_abs = obj_dx_abs[i]-ego_path.dx[i]
    Ddy_abs = obj_dy_abs[i]-ego_path.dy[i]
    dist2 = Ddx_abs**2.0 + Ddy_abs**2.0
    for j in xrange(i, time_size):
      is_last_cycle = j+1 >= time_size
      if not is_last_cycle:
        Ddx_abs_next = obj_dx_abs[i]-ego_path.dx[j+1]
        Ddy_abs_next = obj_dy_abs[i]-ego_path.dy[j+1]
        dist2_next = Ddx_abs_next**2.0 + Ddy_abs_next**2.0
        view_range_exceeded_next = (
          (ego_path.dx[j+1]-ego_path.dx[i])**2.0 +
          (ego_path.dy[j+1]-ego_path.dy[i])**2.0 > view_range**2.0)
      if is_last_cycle or dist2_next > dist2 or view_range_exceeded_next:
        # point of interest found --> rotate to local vehicle coordinate system
        Dpsi = -1.0 * ego_path.heading[j]
        #dx= Ddx_abs*np.cos(Dpsi) - Ddy_abs*np.sin(Dpsi)
        dy = Ddx_abs*np.sin(Dpsi) + Ddy_abs*np.cos(Dpsi)
        break
      dist2 = dist2_next
      Ddx_abs = Ddx_abs_next
      Ddy_abs = Ddy_abs_next
    dys[i] = dy
  return dys


class Search(interface.iSearch):
  def init(self, sensor, obj_src):
    assert sensor in globals(), "parameter class for %s not defined" % sensor
    self.sensor = globals()[sensor]
    self.obj_fill = getattr(self.sensor, obj_src)
    self.dep = (self.sensor.ego_fill, self.obj_fill, egopath_fill)
    return

  def _create_report(self, intervals, rep_type):
    batch = self.get_batch()
    votes = batch.get_labelgroups(
      'standard', 'moving state', self.sensor.objind_labelgroup)
    names = batch.get_quanamegroups('ego vehicle', 'target')
    title = "AEB track classification - %s" % rep_type
    return Report(intervals, title, votes=votes, names=names)

  def fill(self):
    # load fills
    modules = self.get_modules()
    objects = modules.fill(self.obj_fill)
    if not isinstance(objects, PrimitiveCollection):
      objects = PrimitiveCollection(objects.time, {0: objects})  # for iteration
    time_scale = objects.time
    ego_motion = modules.fill(self.sensor.ego_fill).rescale(time_scale)
    ego_path = modules.fill(egopath_fill).rescale(time_scale)._smooth()  # hack
    
    # create reports
    report_exp = self._create_report(cIntervalList(time_scale), "expected")
    report_fact = self._create_report(cIntervalList(time_scale), "factual")
    ego_moving = (ego_motion.vx > EGO_SPEED_MIN)
    if not np.any(ego_moving):
      return report_exp, report_fact  # optimization
    
    # add intervals
    for obj in objects.itervalues():
      self.logger.debug("object id: x")
      filter_mask = (ego_moving &
        ~obj.mov_dir.oncoming & (obj.radar_conf > CONF_MIN) & (obj.vx < 0.0))
      dy_from_path = find_objdy_from_path(obj, ego_path, mask=filter_mask)#, logger=self.logger)
      inlane_mask = np.abs(dy_from_path) < ABS_DY_FROM_PATH_MAX
      
      aeb_exp_mask = filter_mask & inlane_mask
      aeb_exp_intvals = cIntervalList.fromMask(time_scale, aeb_exp_mask)
      aeb_exp_intvals = aeb_exp_intvals.intersect(obj.alive_intervals)
      
      aeb_fact_intvals = aeb_exp_intvals.intersect(
        cIntervalList.fromMask(time_scale, obj.aeb_track) )
      
      entries = {report_exp: aeb_exp_intvals, report_fact: aeb_fact_intvals}
      for report, intvals in entries.iteritems():
        self.logger.debug("report: x")
        for st, end in intvals:
          self.logger.debug("interval: (%d, %d)" % (st, end))
          end_ = max(end-1, 0)
          index = report.addInterval([st, end])
          report.vote(index, 'standard', 'valid')
          report.vote(index, self.sensor.objind_labelgroup, str(obj.id[st]))
          report.set(index, 'target', 'dx start', obj.dx[st])
          report.set(index, 'target', 'dx end', obj.dx[end_])
          report.set(index, 'target', 'fused duty',
            calcDutyCycle(time_scale[st:end], obj.fused[st:end]))
          report.set(index, 'target', 'aeb duty',
            calcDutyCycle(time_scale[st:end], obj.aeb_track[st:end]))
          report.set(index, 'ego vehicle','speed', ego_motion.vx[st:end].mean())
          labelMovState(report, index, obj, (st, end), wholetime=False)
    return report_exp, report_fact

  def search(self, *reports):
    tags = (self.sensor.permaname,)
    for report in reports:
      result = self.FAILED if report.isEmpty() else self.PASSED
      self.batch.add_entry(report, result=result, tags=tags)
    return
