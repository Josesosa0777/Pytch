# -*- dataeval: init -*-

import sys

import numpy as np

import interface
from measproc import cIntervalList
from measproc.IntervalList import intervalsToMask
from measproc.report2 import Report
from aebs.proc.AEBSWarningSim import calcSpeedReduction


EGO_SPEED_MIN = 10.0/3.6
CONSTSPEED_ABSACCEL_MAX = 1.0
OBJ_ABSDY_MAX = 10.0
OBJ_VX_MAX = -10.0/3.6         # ego is at least 10 km/h faster
STABLEEND_TTC_MAX = 1.8        # dx=40 m   @ v=80 km/h
STABLEEND_ABSCURV_TOL = 0.005  # w=0.1 1/s @ v=80 km/h

init_params = {
  "FLR20": dict(sensor='AC100'),
}

class AC100(object):
  """
  AC100-specific parameters and functions.
  """
  permaname = 'AC100'
  ego_fill = 'calc_flr20_egomotion@aebs.fill'
  obj_fill = 'fill_flr20_raw_tracks@aebs.fill'
  objind_labelgroup = 'AC100 track'


def iter_events(ego, objects):
  """Find forward vehicle approach events."""
  ego_moving = ego.vx >= EGO_SPEED_MIN
  for obj in objects.itervalues():
    for life_int in obj.alive_intervals:
      life = intervalsToMask([life_int], obj.time.size)
      obj_approach = obj.vx <= OBJ_VX_MAX
      obj_inpath = np.abs(obj.dy) <= OBJ_ABSDY_MAX
      obj_aebtr = obj.aeb_track
      relevant = life & ego_moving & obj_approach & obj_inpath & obj_aebtr
      # no restriction on acceleration --> ability to find events where
      # detection was stable during the braking only
      if np.any(relevant):
        most_relevant_int = cIntervalList.fromMask(obj.time, relevant)[-1] #last
        stable_int = find_stable_int(obj, life_int, most_relevant_int)
        yield obj, life_int, stable_int
  return

def find_stable_int(obj, life_int, stable_subint):
  """Find the stable detection interval of a forward vehicle approach event."""
  timestamp = stable_subint[0]
  life_ints = cIntervalList(obj.time, [life_int])
  aebtr_ints = cIntervalList.fromMask(obj.time, obj.aeb_track)
  stable_int = life_ints.intersect(aebtr_ints).findInterval(timestamp)
  return stable_int

def calc_approachspeed(ego, obj, life_int):
  """Calculate the approaching speed."""
  life = intervalsToMask([life_int], obj.time.size)
  ego_moving = ego.vx >= EGO_SPEED_MIN
  ego_constspeed = np.abs(ego.ax) <= CONSTSPEED_ABSACCEL_MAX
  obj_constspeed = \
    np.abs(obj._acceleration_over_ground) <= CONSTSPEED_ABSACCEL_MAX  # TODO: rm
    ###
    # np.abs(obj.ax + ego.ax) <= CONSTSPEED_ABSACCEL_MAX
    ###
  speedsamplingint = life & ego_moving & ego_constspeed & obj_constspeed
  if np.any(speedsamplingint):
    speedsamplingstart, speedsamplingend = cIntervalList.fromMask(
      obj.time, speedsamplingint).findLongestIntervals()[-1]
  else:
    print>>sys.stderr,"Warning: possibly improper approaching speed calculation"
    speedsamplingstart, speedsamplingend = life_int
  egospeed = np.mean(ego.vx[speedsamplingstart:speedsamplingend])
  objspeed = np.mean(obj.vx[speedsamplingstart:speedsamplingend])  # relative
  return egospeed, objspeed

def calc_stabledet(ego, obj, stable_int, egoapprspeed, objapprvx):
  """Calculate the stable detection related quantities."""
  stablestart, stableend = stable_int
  # calc quantities
  dx_stable = obj.dx[stablestart]
  vx_stable = obj.vx[stablestart]
  v_ego = ego.vx[stablestart]
  speedred, _ = calcSpeedReduction(dx_stable, vx_stable, v_ego)
  # check if stable detection was really stable or object was lost too early
  stableend_ = max(0, stableend-1)
  ttc_end = -1.0 * obj.dx[stableend_] / objapprvx  # quasi ttc for approach
  speed_end = ego.vx[stableend_]
  yawrate_end = ego.yaw_rate[stableend_]
  valid = (speed_end <= EGO_SPEED_MIN or ttc_end <= STABLEEND_TTC_MAX or
           abs(yawrate_end/speed_end) >= STABLEEND_ABSCURV_TOL)
  return dx_stable, speedred, valid


class Search(interface.iSearch):
  def init(self, sensor):
    assert sensor in globals(), "parameter class for %s not defined" % sensor
    self.sensor = globals()[sensor]
    self.dep = (self.sensor.ego_fill, self.sensor.obj_fill)
    return

  def _create_report_life(self, time):
    batch = self.get_batch()
    votes = batch.get_labelgroups('standard', self.sensor.objind_labelgroup)
    names = batch.get_quanamegroups('target', 'ego vehicle')
    emptyIntervals = cIntervalList(time)
    title = "AEBS use case - Forward vehicle detection (whole life)"
    return Report(emptyIntervals, title, votes=votes, names=names)

  def _create_report_stable(self, time):
    batch = self.get_batch()
    votes = batch.get_labelgroups('standard', self.sensor.objind_labelgroup)
    names = batch.get_quanamegroups('target', 'AEBS')
    emptyIntervals = cIntervalList(time)
    title = "AEBS use case - Forward vehicle detection (stable period)"
    return Report(emptyIntervals, title, votes=votes, names=names)

  def fill(self):
    modules = self.get_modules()
    objects = modules.fill(self.sensor.obj_fill)
    time = objects.time
    ego = modules.fill(self.sensor.ego_fill)
    ego = ego.rescale(time)
    report_life = self._create_report_life(time)
    report_stable = self._create_report_stable(time)
    # find object intervals
    for obj, life_int, stable_int in iter_events(ego, objects):
      # calculate quantities
      obj_id = str(obj.id[life_int[0]])
      dx_start = obj.dx[life_int[0]]
      egoapprspeed, objapprvx = calc_approachspeed(ego, obj, life_int)
      dx_stable, speedred, stable_valid = \
        calc_stabledet(ego, obj, stable_int, egoapprspeed, objapprvx)
      # store interval for object life
      index_life = report_life.addInterval(life_int)
      report_life.vote(index_life, 'standard', 'valid')
      report_life.vote(index_life, self.sensor.objind_labelgroup, str(obj_id))
      report_life.set(index_life, 'target', 'dx start', dx_start)
      report_life.set(index_life, 'target', 'vx', objapprvx)
      report_life.set(index_life, 'ego vehicle', 'speed', egoapprspeed)
      # store interval for stable period
      index_stable = report_stable.addInterval(stable_int)
      report_stable.vote(index_stable, 'standard',
        'valid' if stable_valid else 'invalid')
      report_stable.vote(index_stable,self.sensor.objind_labelgroup,str(obj_id))
      report_stable.set(index_stable, 'target', 'dx start', dx_stable)
      report_stable.set(index_stable, 'AEBS', 'speed reduction', speedred)
    return report_life, report_stable

  def search(self, report_life, report_stable):
    tags = ('AEBS', self.sensor.permaname)
    result_life = self.FAILED if report_life.isEmpty() else self.PASSED
    result_stable = self.FAILED if report_stable.isEmpty() else self.PASSED
    batch = self.get_batch()
    batch.add_entry(report_life, result=result_life, tags=tags)
    batch.add_entry(report_stable, result=result_stable, tags=tags)
    return
