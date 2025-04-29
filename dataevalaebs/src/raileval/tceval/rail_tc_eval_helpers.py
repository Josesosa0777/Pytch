import numpy as np

from measproc.EventFinder import cEventFinder
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList
import measproc

class cTestCaseEvalBasicHelpers(object):
  tc_passed = 'passed'
  tc_failed = 'failed'
  tc_incons = 'inconclusive'
  
  def __init__(self, batch):
    self.batch = batch
    return
  
  def create_report(self, time, title):
    votes = self.batch.get_labelgroups('result')
    qua_names = self.batch.get_quanamegroups('general')
    empty_intervals = cIntervalList(time)
    report = Report(empty_intervals, title, votes=votes, names=qua_names)
    return report
  
  def vote_intervals(self, report, interval, vote, comment=''):
    index = report.addInterval(interval)
    report.vote(index, 'result', vote)
    if comment:
      report.setComment(index, comment)
    return
  
  def def_ints(self, adj_ints, mask_4_comp, relation, value):
    ret_ints = self.def_ints_from_mask(adj_ints.Time, mask_4_comp, relation, value)
    ret_ints = ret_ints.intersect(adj_ints)
    return ret_ints
  
  def def_ints_from_mask(self, mask_time, mask_4_comp, relation, value):
    ret_ints = cEventFinder.compare(mask_time, mask_4_comp, relation, value)
    return ret_ints


class cTestCaseGeneralEvalHelpers(cTestCaseEvalBasicHelpers):
  def judge_results(self, report, ref_ints, first_ints, *chk_intervals, **kwargs):
    pass_comment = kwargs.get("pass_comment", "")
    fail_comment = kwargs.get("fail_comment", "")
    tmp = first_ints
    for chk_interval in chk_intervals:
      tmp = tmp.intersect(chk_interval)
    
    intervals_might_be_in = ref_ints.convertIndices(tmp)
    within_ids = []
    for start2, end2 in intervals_might_be_in:
      ids = [index for index, (start1, end1) in enumerate(ref_ints.Intervals)
             if start1 <= start2 and end2 <= end1]
      within_ids.extend(ids)
    within_ids = set(within_ids)
    all_ids = set(range(len(ref_ints)))
    ouside_ids = all_ids.difference(within_ids)
    within_ids = list(within_ids)
    ouside_ids = list(ouside_ids)
    within_ints = np.array(ref_ints.Intervals)
    within_ints = within_ints[within_ids]
    within_ints = within_ints.tolist()
    for start, end in within_ints:
      self.vote_intervals(report, (start, end), self.tc_passed, comment=pass_comment)
    ouside_ints = np.array(ref_ints.Intervals)
    ouside_ints = ouside_ints[ouside_ids]
    ouside_ints = ouside_ints.tolist()
    for start, end in ouside_ints:
      self.vote_intervals(report, (start, end), self.tc_failed, comment=fail_comment)
    return
  
  def det_casc_flow(self, adj_ints, aebs_state):
    warn_pres_ints = self.def_ints(adj_ints, aebs_state, measproc.equal, 5)
    part_pres_ints = self.def_ints(adj_ints, aebs_state, measproc.equal, 6)
    emer_pres_ints = self.def_ints(adj_ints, aebs_state, measproc.equal, 7)
    
    aebs_casc_ints = warn_pres_ints.union(part_pres_ints)
    aebs_casc_ints = aebs_casc_ints.union(emer_pres_ints)
    aebs_casc_ints = aebs_casc_ints.join(IndexLimit=2)
    return aebs_casc_ints
  
  def det_icb(self, adj_ints, dx, rel_vel, dx_start_icb, rel_vel_start_icb,
              aebs_state):
    dx_icb_close = self.def_ints(adj_ints, dx, measproc.less_equal, dx_start_icb)
    rel_vel_icb_close = self.def_ints(adj_ints, rel_vel, measproc.less_equal,
                                      rel_vel_start_icb)
    icb_imminent = dx_icb_close.intersect(rel_vel_icb_close)
    aebs_active = self.det_casc_flow(adj_ints, aebs_state)
    aebs_with_icb = cIntervalList(adj_ints.Time)
    for start, end in aebs_active:
      tmp = cIntervalList(adj_ints.Time)
      tmp.add(start, end)
      tmp_icb = tmp.intersect(icb_imminent)
      if tmp_icb:
        aebs_with_icb.add(start, end)
    return aebs_with_icb
  
  def det_aebs_react_on_override(self, override, inj_pos, state_before_override):
    override = override.intersect(inj_pos)
    immed_react_ints = state_before_override.neighbour(override)
    if immed_react_ints:
      override_ok = immed_react_ints.Intervals
    else:
      react_with_gap = override.intersect(state_before_override)
      override_ok = []
      for start, end in react_with_gap:
        t_start = react_with_gap.Time[start]
        t_end = react_with_gap.Time[end - 1]
        if t_end - t_start < 0.5:
          override_ok.append((start, end))
    return override_ok


class cTestCaseOverrideEvalHelpers(cTestCaseGeneralEvalHelpers):
  def get_gp_kick_override_ints(self, maneuver_intervals, GPPos, GPKickdown_B):
    gp_kickdown_on = self.def_ints(maneuver_intervals, GPKickdown_B,
                                   measproc.not_equal, 0)
    gp_kickdown_on =\
      gp_kickdown_on.intersect(self.def_ints(maneuver_intervals, GPPos,
                                             measproc.greater_equal, 95))
    return gp_kickdown_on
  
  def get_gp_no_kick_override_ints(self, maneuver_intervals, GPPos,
                                   GPKickdown_B, pAccelMinStop):
    gp_no_kickdown = self.def_ints(maneuver_intervals, GPPos,
                                   measproc.greater_equal, pAccelMinStop)
    gp_no_kickdown =\
      gp_no_kickdown.intersect(self.def_ints(maneuver_intervals,
                                             GPPos, measproc.less, 95))
    gp_no_kickdown =\
      gp_no_kickdown.intersect(self.def_ints(maneuver_intervals,
                                             GPKickdown_B, measproc.equal, 0))
    return gp_no_kickdown
  
  def get_bp_override_ints(self, maneuver_intervals, BPPos, pBrakeMinStop):
    bp_pressed = self.def_ints(maneuver_intervals, BPPos,
                               measproc.greater, pBrakeMinStop)
    return bp_pressed
  
  def get_dir_ind_override_ints(self, maneuver_intervals, DirIndL_b, DirIndR_b):
    dir_ind_active = np.logical_or(DirIndL_b, DirIndR_b)
    dir_ind_active = self.def_ints(maneuver_intervals, dir_ind_active,
                                   measproc.not_equal, 0)
    return dir_ind_active
  
  def get_aebs_deact_override_ints(self, maneuver_intervals, DriverActivationDemand_b):
    aebs_not_active = self.def_ints(maneuver_intervals,
                                    DriverActivationDemand_b, measproc.equal, 0)
    return aebs_not_active
  
  def get_gradient_override_ints(self, maneuver_intervals, value, p_min_stop,
                                 p_dt_min_stop, p_delta_min_stop):
    time_dt = np.gradient(maneuver_intervals.Time)
    value_dt = np.gradient(value, time_dt)
    fast_change = self.def_ints(maneuver_intervals, value_dt,
                                measproc.greater_equal, p_dt_min_stop)
    change_enough = self.def_ints(maneuver_intervals, value,
                                  measproc.greater_equal, p_delta_min_stop)
    if p_min_stop:
      change_enough =\
        change_enough.intersect(self.def_ints(maneuver_intervals, value,
                                              measproc.less, p_min_stop))
    change_enough = change_enough.addMargin(CycleMargins=(3,3))
    gp_gradient_ok = fast_change.intersect(change_enough)
    return gp_gradient_ok
  
  def override_eval_bwpe(self, maneuver_intervals, drov_inj_pos, drov_ints,
                         aebs_standby_ints, aebs_casc_ints, no_kickdown=False):
    # driver override stops the cascade:
    #    - (b)efore it (AEBS suppression)
    #    - in the (w)arning phase
    #    - in the (p)artial braking phase
    #    - in the (e)mergency braking phase
    driver_override_ok = []
    for idx, inj_pos in enumerate(drov_inj_pos):
      if idx == 0:
        if not no_kickdown:
          drov_ok = self.det_aebs_react_on_override(drov_ints, inj_pos, aebs_standby_ints)
        else:
          # no kickdown injection before cascade causes driver override only when AEBS state wants to change to warning level
          override = drov_ints.intersect(inj_pos)
          override = override.intersect(aebs_standby_ints.negate())
          drov_ok = aebs_standby_ints.neighbour(override)
      else:
        drov_ok = self.det_aebs_react_on_override(drov_ints, inj_pos, aebs_casc_ints)
      driver_override_ok.extend(drov_ok)
    driver_override_ok = list(set(driver_override_ok))
    driver_override_ok_ints =\
      cIntervalList.fromList(maneuver_intervals.Time, driver_override_ok)
    driver_override_ok_ints = driver_override_ok_ints.addMargin(CycleMargins=(0,3))
    return driver_override_ok_ints
  
  def override_eval_bwp(self, maneuver_intervals, drov_inj_pos, drov_ints,
                        aebs_standby_ints, aebs_casc_ints):
    # driver override stops the cascade:
    #    - (b)efore it (AEBS suppression)
    #    - in the (w)arning phase
    #    - in the (p)artial braking phase
    driver_override_ok = []
    for idx, inj_pos in enumerate(drov_inj_pos):
      if idx == 0:
        drov_ok = self.det_aebs_react_on_override(drov_ints, inj_pos, aebs_standby_ints)
      elif idx == 3:
        drov_ok = drov_ints.intersect(aebs_casc_ints)
        drov_ok = drov_ok.Intervals
      else:
        drov_ok = self.det_aebs_react_on_override(drov_ints, inj_pos, aebs_casc_ints)
      driver_override_ok.extend(drov_ok)
    driver_override_ok = list(set(driver_override_ok))
    driver_override_ok_ints =\
      cIntervalList.fromList(maneuver_intervals.Time, driver_override_ok)
    driver_override_ok_ints = driver_override_ok_ints.addMargin(CycleMargins=(0,3))
    return driver_override_ok_ints
  
  def override_eval_wp(self, maneuver_intervals, drov_inj_pos, drov_ints,
                       aebs_casc_ints):
    # driver override stops the cascade:
    #    - in the (w)arning phase
    #    - in the (p)artial braking phase
    driver_override_ok = []
    for idx, inj_pos in enumerate(drov_inj_pos):
      if idx == 0:
         # for some cases override lasts only some cycles before the cascade
         filter = cIntervalList(maneuver_intervals.Time, inj_pos)
         drov = filter.intersect(drov_ints)
         casc = filter.intersect(aebs_casc_ints)
         if drov.Intervals and casc.Intervals:
            if drov[0][0] < casc[0][0]:
              drov_ok = casc.Intervals
         # TODO: this was the bug!!! document it! indentation of the else block was wrong...
         else:
            drov_ok = []
      elif idx == 3:
        drov_ok = drov_ints.intersect(aebs_casc_ints)
        drov_ok = drov_ok.Intervals
      else:
        drov_ok = self.det_aebs_react_on_override(drov_ints, inj_pos, aebs_casc_ints)
      driver_override_ok.extend(drov_ok)
    driver_override_ok = list(set(driver_override_ok))
    driver_override_ok_ints =\
      cIntervalList.fromList(maneuver_intervals.Time, driver_override_ok)
    driver_override_ok_ints = driver_override_ok_ints.addMargin(CycleMargins=(0,3))
    return driver_override_ok_ints

class cTestCaseErrhanEvalHelpers(cTestCaseGeneralEvalHelpers):
  def select_errhan_interf_test_res(self, msg_id, inputs):
    for t_id, v_id in zip(*msg_id):
      if v_id == 0: continue
      inp_vals = []
      for inp in inputs:
        idx = np.searchsorted(inp[0], t_id)
        idx = min(idx, inp[1].size - 1)
        inp_vals.append(inp[1][idx])
      yield v_id, t_id, inp_vals
