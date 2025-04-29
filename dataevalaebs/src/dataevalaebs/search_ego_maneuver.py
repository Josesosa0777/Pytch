# -*- dataeval: init -*-

import numpy as np

import interface
from measproc import cIntervalList
from measproc.report2 import Report


EGO_SPEED_MIN = 10.0/3.6
LINE_OFFSET_LIMIT = 0.2
LANE_WIDTH_LIMIT = 2.8
LINE_VIEWRANGE_LIMIT = 10.0


class Search(interface.iSearch):
  dep = ('calc_flr20_egomotion@aebs.fill', 'calc_flc20_lanes@aebs.fill')

  def _create_report(self, intervals):
    batch = self.get_batch()
    votes = batch.get_labelgroups('standard', 'manoeuvre type')
    names = batch.get_quanamegroups('ego vehicle')
    title = "Ego maneuvers"
    return Report(intervals, title, votes=votes, names=names)

  def _search_lane_change(self, report, left_valid, left_fulfill,
                          right_valid, right_fulfill, ego_motion, label):
    lane_change_oneline = left_fulfill | right_fulfill
    lane_change_twolines = left_fulfill & right_fulfill
    lane_change = np.where(left_valid & right_valid,
      lane_change_twolines, lane_change_oneline)
    lane_change &= (ego_motion.vx > EGO_SPEED_MIN)
    lane_change_intvals = cIntervalList.fromMask(
      report.intervallist.Time, lane_change)
    lane_change_intvals = lane_change_intvals.merge(0.5)  # smooth
    for st, end in lane_change_intvals:
      index = report.addInterval([st, end])
      report.vote(index, 'standard', 'valid')
      report.vote(index, 'manoeuvre type', label)
      report.set(index, 'ego vehicle', 'speed', ego_motion.vx[st:end].mean())
    return

  def fill(self):
    # load fills
    modules = self.get_modules()
    ego_motion = modules.fill(self.dep[0])
    time_scale = ego_motion.time
    lines = modules.fill(self.dep[1]).rescale(time_scale)

    # create report
    report = self._create_report(cIntervalList(time_scale))
    ego_moving = (ego_motion.vx > EGO_SPEED_MIN)
    if not np.any(ego_moving):
      return report  # optimization

    # lane change detection
    left_line_valid = lines.left_line.view_range > LINE_VIEWRANGE_LIMIT
    left_line_close = left_line_valid & (lines.left_line.c0 < LINE_OFFSET_LIMIT)
    left_line_far = left_line_valid & (lines.left_line.c0 > LANE_WIDTH_LIMIT)
    right_line_valid = lines.right_line.view_range > LINE_VIEWRANGE_LIMIT
    right_line_close = right_line_valid&(lines.right_line.c0>-LINE_OFFSET_LIMIT)
    right_line_far = right_line_valid & (lines.right_line.c0<-LANE_WIDTH_LIMIT)

    self._search_lane_change(report, left_line_valid, left_line_close,
      right_line_valid, right_line_far, ego_motion, 'left lane change')
    self._search_lane_change(report, left_line_valid, left_line_far,
      right_line_valid, right_line_close, ego_motion, 'right lane change')

    # TODO: extend maneuver types
    return report

  def search(self, report):
    tags = ()  # TODO: extend
    result = self.FAILED if report.isEmpty() else self.PASSED
    batch = self.get_batch()
    batch.add_entry(report, result=result, tags=tags)
    return
