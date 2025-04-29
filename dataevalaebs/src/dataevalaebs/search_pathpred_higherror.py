# -*- dataeval: init -*-

import numpy as np

import interface
from measproc import cIntervalList
from measproc.report2 import Report
from measparser.signalproc import calcDutyCycle
import pathpred.pathpredictor


RMS_LIMIT = 1.5
PREDTIME_OF_INTEREST = 4.0
EGO_SPEED_MIN = 10.0/3.6
CALC_OTHER = True


class Search(interface.iSearch):
  dep = ('calc_vbox_egopath@aebs.fill', 'calc_flr20_pathpred_lf@aebs.fill',
         'calc_flr20_egomotion@aebs.fill', 'calc_flc20_lanes@aebs.fill')

  def _create_report(self, intervals):
    batch = self.get_batch()
    votes = batch.get_labelgroups('standard')
    names = batch.get_quanamegroups('ego vehicle', 'path prediction')
    title = "Path prediction error"
    return Report(intervals, title, votes=votes, names=names)

  def check(self):
    sgs = [{
      "lane_valid": ("General_radar_status", "LF_is_video_valid"),
      "moving_radar_valid": ("General_radar_status", "LF_is_radar_valid"),
    }]
    group = self.get_source().selectSignalGroup(sgs)
    return group

  def fill(self, group):
    # load fills
    modules = self.get_modules()
    pred_line = modules.fill(self.dep[1])
    time_scale = pred_line.time
    ego_motion = modules.fill(self.dep[2]).rescale(time_scale)
    if not np.any(ego_motion.vx > EGO_SPEED_MIN):
      return self._create_report(cIntervalList(time_scale))  # optimization
    ref_path = modules.fill(self.dep[0]).rescale(time_scale)._smooth()  # hack

    # processing ref_path
    n_steps = PREDTIME_OF_INTEREST / np.diff(time_scale).mean()
    ref_slpath = ref_path.slice(0, n_steps)
    #ref_slpath = ref_slpath.rescale_slices(0.1)  # TODO: fix
    ref_slpath_dxs = ref_slpath.get_dxs()

    # processing pred_line
    pred_slpath = pred_line.get_slicedpath(ref_slpath_dxs)
    # calculate errors
    errors = ref_slpath.calc_rms_pos_errors(pred_slpath)
    # load additional signals
    lane_valid = group.get_value('lane_valid', ScaleTime=time_scale)
    moving_radar_valid = \
      group.get_value('moving_radar_valid', ScaleTime=time_scale)

    # processing other_pred_line
    if CALC_OTHER:
      lanes = modules.fill(self.dep[3]).rescale(time_scale)
      pp = pathpred.pathpredictor.PathPredictor()
      other_pred_line, _ = pp.predict(ego_motion, lanes)
      other_pred_slpath = other_pred_line.get_slicedpath(ref_slpath_dxs)
      other_errors = ref_slpath.calc_rms_pos_errors(other_pred_slpath)

    # create intervals
    high_errors = (errors > RMS_LIMIT)
    ego_moving = (ego_motion.vx > EGO_SPEED_MIN)
    intvals = cIntervalList.fromMask(time_scale, high_errors & ego_moving)
    intvals = intvals.merge(0.5).drop(0.1)  # smooth

    report = self._create_report(intvals)
    # add labels/quantities
    for i, (st, end) in enumerate(intvals):
      report.vote(i, 'standard', 'valid')
      report.set(i, 'ego vehicle', 'speed', ego_motion.vx[st:end].mean())
      report.set(i, 'ego vehicle','yaw rate',ego_motion.yaw_rate[st:end].mean())
      report.set(i, 'path prediction', 'rms error avg', errors[st:end].mean())
      report.set(i, 'path prediction', 'lane valid duty',
        calcDutyCycle(time_scale[st:end], lane_valid[st:end]))
      report.set(i, 'path prediction', 'moving radar valid duty',
        calcDutyCycle(time_scale[st:end], moving_radar_valid[st:end]))
      other_rms = other_errors[st:end].mean() if CALC_OTHER else np.NaN
      report.set(i, 'path prediction', 'other rms error avg', other_rms)
    return report

  def search(self, report):
    tags = ('path prediction', 'SDF')  # TODO: add sensor
    result = self.FAILED if report.isEmpty() else self.PASSED
    batch = self.get_batch()
    batch.add_entry(report, result=result, tags=tags)
    return
