import numpy as np
from collections import OrderedDict

#from rail_eval_n_ccp_meas_handler import cAcquireSignals
from rail_tc_eval_helpers import cTestCaseGeneralEvalHelpers,\
                      cTestCaseOverrideEvalHelpers, cTestCaseErrhanEvalHelpers
import measproc
from measproc.IntervalList import cIntervalList


FAULT_TYPE_4_COMMENT =\
  OrderedDict([(1, "Immediate_irrev_off_raised"),
               (2, "Immediate_rev_off_raised"),
               (3, "Controlled_irrev_off_raised"),
               (4, "Controlled_rev_off_raised"),
               (5, "Reduced_perf_rev_raised")])
FAULT_POS_4_COMMENT =\
  OrderedDict([(1, "Before AEBS cascade"),
               (5, "In AEBS warning phase"),
               (6, "In AEBS partial braking phase"),
               (7, "In AEBS emergency braking phase"),
               (9, "Inside ICB/SSB activation interval")])

# TODO: create options for changed AEBS2 source address!!!
CAN_MSG_ID_4_COMMENT =\
  OrderedDict([("0xC0B2A21", "AEBS2"),
               ("0x18FED917", "AUXIO1"),
               ("0x18FECA17", "DM1"),
               ("0x18F0010B", "EBC1"),
               ("0x18FEBF0B", "EBC2"),
               ("0x18FDC40B", "EBC5"),
               ("0xCF00400", "EEC1"),
               ("0xCF00300", "EEC2"),
               ("0x18F00503", "ETC2"),
               ("0xCFDCC21", "OEL"),
               ("0xC010021", "TC1"),
               ("0x18FE4F0B", "VDC1"),
               ("0x18F0090B", "VDC2"),
               ("0x61F", "Video_Data_General_A"),
               ("0x7FFFFFFE", "All_Video_Messages")])
CAN_SGN_ID_4_COMMENT =\
  OrderedDict([(("0xC0B2A21", 0, 2), "AEBS2_DriverActDemand_21"),
               (("0xC0B2A21", 60, 4), "AEBS2_MessageChkSum_21"),
               (("0x18FED917", 14, 2), "AuxIO1_5_TrailerConnected_17"),
               (("0x18FED917", 12, 2), "AuxIO1_6_TrailerABSDetected_17"),
               (("0x18FED917", 10, 2), "AuxIO1_7_TrailerABSFullyOper_17"),
               (("0x18F0010B", 40, 2), "EBC1_ABSFullyOp_0B"),
               (("0x18F0010B", 8, 8), "EBC1_BrkPedPos_0B"),
               (("0x18F0010B", 6, 2), "EBC1_EBSBrkSw_0B"),
               (("0x18FEBF0B", 0, 16), "EBC2_MeanSpdFA_0B"),
               (("0x18FEBF0B", 16, 8), "EBC2_RelWhlSpdFL_0B"),
               (("0x18FEBF0B", 24, 8), "EBC2_RelWhlSpdFR_0B"),
               (("0x18FEBF0B", 32, 8), "EBC2_RelWhlSpdRL1_0B"),
               (("0x18FEBF0B", 40, 8), "EBC2_RelWhlSpdRR1_0B"),
               (("0x18FDC40B", 10, 2), "EBC5_XBRSystemSt_0B"),
               (("0xCF00400", 24, 16), "EEC1_EngSpd_00"),
               (("0xCF00300", 8, 8), "EEC2_APPos1_00"),
               (("0x18F00503", 24, 8), "ETC2_CurrentGear_03"),
               (("0xCFDCC21", 8, 4), "OEL_TurnSigSw_21"),
               (("0xC010021", 16, 8), "TC1_RqGear_21"),
               (("0x18FE4F0B", 2, 2), "VDC1_FullyOp_0B"),
               (("0x18F0090B", 0, 16), "VDC2_SteerWhlAngle_0B"),
               (("0x61F", 62, 2), "Message_Counter_GenA"),
               (("0x7FFFFFFE", 62, 2), "All_Vid_Msg_Counters")])
CAN_SGN_CHG_TYPE_4_COMMENT =\
  OrderedDict([(1, "Not Available"),
               (2, "Error"),
               (3, "Invalid"),
               (4, "Min."),
               (5, "Mid."),
               (6, "Max.")])


def evaluate_test_case(tc_eval_class, test_case_id, *args, **kwargs):
  if 'report' in kwargs and kwargs['report'] is not None:
    report = kwargs['report']
  else:
    try:
      test_case_eval = tc_eval_class(test_case_id, *args)
    except ValueError:
      report = None
    else:
      report = test_case_eval(test_case_id)
  return report

def tc_eval_func(func):
  func.is_tc_eval = True
  return func


class cTestCaseEvaluator(object):
  def __new__(cls, test_case_id, *args, **kwargs):
    tc_eval = "TC%d" % test_case_id
    avail_tc_eval = []
    for method_name in dir(cls):
      method = getattr(cls, method_name, None)
      if (callable(method)
          and (hasattr(method, 'is_tc_eval') and method.is_tc_eval)):
        avail_tc_eval.append(method_name)
    
    if tc_eval in avail_tc_eval:
      return super(cTestCaseEvaluator, cls).__new__(cls)
    else:
      raise ValueError
  
  def __call__(self, test_case_id):
    method = getattr(self, "TC%d" % test_case_id, None)
    report = method()
    return report
  
  def _init_basic_data(self, test_case_id, test_session_id, batch, ref_intervals,
                       tc_eval_helper_class,
                       get_needed_signals, needed_io_signals, needed_param_signals):
    self.tceh = tc_eval_helper_class(batch)
    self.report = self.tceh.create_report(ref_intervals.Time,
                                          "Evaluation of TC %s (TS %s)"
                                          % (test_case_id, test_session_id))
    self.ref_intervals = ref_intervals
    
    sgns_4_tc_eval = get_needed_signals(*needed_io_signals,
                                        common_time=ref_intervals.Time)
    params_4_tc_eval = get_needed_signals(*needed_param_signals)
    for param_name, param_val in params_4_tc_eval.iteritems():
      params_4_tc_eval[param_name] = param_val[1][0]
    return sgns_4_tc_eval, params_4_tc_eval
  
  def _check_sgn_availability(self, sgns_4_tc_eval, params_4_tc_eval,
                              needed_io_signals, needed_param_signals):
    if (set(needed_io_signals).difference(set(sgns_4_tc_eval.keys()))
        or set(needed_param_signals).difference(set(params_4_tc_eval.keys()))):
      self.missing_signals = True
    else:
      self.missing_signals = False
    return


class cEvalMovObjApprTests(cTestCaseEvaluator):
  def __init__(self, test_case_id, test_session_id, batch, ref_intervals,
               get_needed_signals):
    needed_io_signals = ['Drive_b', 'Stopped_b', 'Stand_b', 'dxv', 'vxv', 'vRef',
                         'AEBS1_SystemState']
    needed_param_signals = ['dxSecure', 'vEgoMaxStartWarning',
                            'vEgoMinStartWarning', 'vRelMaxStartWarning']
    sgns_4_tc_eval, params_4_tc_eval =\
      self._init_basic_data(test_case_id, test_session_id, batch, ref_intervals,
                            cTestCaseGeneralEvalHelpers,
                            get_needed_signals,
                            needed_io_signals, needed_param_signals)
    self._check_sgn_availability(sgns_4_tc_eval, params_4_tc_eval,
                                 needed_io_signals, needed_param_signals)
    if self.missing_signals:
      return
    
    self.mov_target_ints =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['Drive_b'],
                         measproc.not_equal, 0)
    self.stopped_target_ints =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['Stopped_b'],
                         measproc.not_equal, 0)
    self.stand_target_ints = self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['Stand_b'], measproc.not_equal, 0)
    if self.stopped_target_ints.neighbour(self.stand_target_ints):
        self.stopped_stand_ints = self.stopped_target_ints.union(self.stand_target_ints)
    else:
        self.stopped_stand_ints = self.stopped_target_ints.copy()
    self.secure_dist_ints =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['dxv'],
                         measproc.greater_equal,
                         max(params_4_tc_eval['dxSecure']-1.5, 1.0))
    self.rel_vel_min_ints =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['vxv'],
                         measproc.greater_equal, -3.0/3.6)
    self.aebs_casc_pres_ints =\
      self.tceh.det_casc_flow(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'])
    self.aebs_state_1 =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 1)
    self.aebs_state_3 =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 3)
    self.rel_vel_2small =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['vxv'],
                         measproc.greater,  # vRelMaxStartWarning is negative value
                         params_4_tc_eval['vRelMaxStartWarning']) 
    self.vref_2small =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['vRef'],
                         measproc.less, params_4_tc_eval['vEgoMinStartWarning'])
    self.vref_2big =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['vRef'],
                         measproc.greater, params_4_tc_eval['vEgoMaxStartWarning'])
    return
  
  def _eval_mov_obj_tc(self):
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals, self.mov_target_ints,
                              self.aebs_casc_pres_ints, self.rel_vel_min_ints,
                              self.secure_dist_ints)
    return self.report
  
  @tc_eval_func
  def TC938592(self):
    """StopObjInLane_H80_T0"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals, self.stopped_stand_ints,
                              self.aebs_casc_pres_ints, self.rel_vel_min_ints,
                              self.secure_dist_ints)
    return self.report
  
  @tc_eval_func
  def TC910427(self):
    """MovObjInLane_H80_T32"""
    return self._eval_mov_obj_tc()
  
  @tc_eval_func
  def TC910446(self):
    """MovObjInLane_H80_T12"""
    return self._eval_mov_obj_tc()
  
  @tc_eval_func
  def TC910459(self):
    """MovObjInLane_H80_T80-32"""
    return self._eval_mov_obj_tc()
  
  @tc_eval_func
  def TC910461(self):
    """MovObjInLane_H90_T12"""
    return self._eval_mov_obj_tc()
  
  @tc_eval_func
  def TC910464(self):
    """MovObjInLane_HT_min"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals, self.mov_target_ints,
                              self.aebs_casc_pres_ints.negate(), self.aebs_state_3,
                              self.rel_vel_2small)
    return self.report
  
  @tc_eval_func
  def TC910466(self):
    """MovObjInLane_Hmin_T5"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals, self.mov_target_ints,
                              self.aebs_casc_pres_ints.negate(), self.aebs_state_1,
                              self.vref_2small)
    return self.report
  
  @tc_eval_func
  def TC910468(self):
    """MovObjInLane_Hmax_T30"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals, self.mov_target_ints,
                              self.aebs_casc_pres_ints.negate(), self.aebs_state_1,
                              self.vref_2big)
    return self.report


class cEvalStatObjApprTests(cTestCaseEvaluator):
  def __init__(self, test_case_id, test_session_id, batch, ref_intervals,
               get_needed_signals):
    needed_io_signals = ['Stand_b', 'dxv', 'vRef', 'AEBS1_SystemState']
    needed_param_signals = ['vEgoMaxStartWarning', 'vEgoMinStartWarning']
    sgns_4_tc_eval, params_4_tc_eval =\
      self._init_basic_data(test_case_id, test_session_id, batch, ref_intervals,
                            cTestCaseGeneralEvalHelpers,
                            get_needed_signals,
                            needed_io_signals, needed_param_signals)
    self._check_sgn_availability(sgns_4_tc_eval, params_4_tc_eval,
                                 needed_io_signals, needed_param_signals)
    if self.missing_signals:
      return
    target_approached = np.zeros_like(sgns_4_tc_eval['dxv'])
    target_approached[1:] = np.diff(sgns_4_tc_eval['dxv'])
    self.appr_target_ints =\
      self.tceh.def_ints(self.ref_intervals, target_approached, measproc.less, 0)
    self.stat_target_ints =\
      self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['Stand_b'],
                         measproc.not_equal, 0)
    self.aebs_casc_pres_ints =\
      self.tceh.det_casc_flow(self.ref_intervals,
                              sgns_4_tc_eval['AEBS1_SystemState'])
    self.aebs_state_1 =\
      self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 1)
    self.vref_2small =\
      self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['vRef'],
                         measproc.less, params_4_tc_eval['vEgoMinStartWarning'])
    self.vref_2big =\
      self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['vRef'],
                         measproc.greater, params_4_tc_eval['vEgoMaxStartWarning'])
    self.vref_max = params_4_tc_eval['vEgoMaxStartWarning']
    speed_red_mask = self.appr_target_ints.toMask(dtype=np.float)
    for start, end in self.appr_target_ints:
      vel_red = sgns_4_tc_eval['vRef'][start] - sgns_4_tc_eval['vRef'][end-1]
      speed_red_mask[start:end] = speed_red_mask[start:end] * vel_red
    self.suff_vel_red_ints =\
      self.tceh.def_ints(self.ref_intervals, speed_red_mask,
                         measproc.greater_equal, 20.0/3.6)
    return
  
  def _eval_stat_mov_obj_tc(self):
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals, self.stat_target_ints,
                              self.aebs_casc_pres_ints, self.suff_vel_red_ints)
    return self.report
  
  @tc_eval_func
  def TC910475(self):
    """StatObjInLane_H80"""
    return self._eval_stat_mov_obj_tc()
  
  @tc_eval_func
  def TC910477(self):
    """StatObjInLane_H50"""
    return self._eval_stat_mov_obj_tc()
  
  @tc_eval_func
  def TC910479(self):
    """StatObjInLane_H90"""
    return self._eval_stat_mov_obj_tc()
  
  @tc_eval_func
  def TC910481(self):
    """StatObjInLane_Hmin"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals, self.stat_target_ints,
                              self.aebs_casc_pres_ints.negate(),
                              self.vref_2small, self.aebs_state_1)
    return self.report
  
  @tc_eval_func
  def TC910483(self):
    """StatObjInLane_Hmax"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      # when vEgoMaxStartWarning is greater than 130 km/h than RaiL is unable to inject the object for some reason
      if self.vref_max < (130.0 / 3.6):
        self.tceh.judge_results(self.report, self.ref_intervals, self.stat_target_ints,
                                self.aebs_casc_pres_ints.negate(),
                                self.vref_2big, self.aebs_state_1)
      else:
        self.tceh.judge_results(self.report, self.ref_intervals, self.aebs_casc_pres_ints.negate(),
                                self.vref_2big, self.aebs_state_1,
                                pass_comment="AEBS system goes into temporary not available state after the host vehicle speed reaches V_EGO_MAX_START_WARNING. Behaviour is OK, test Passed.")
    return self.report


class cEvalConfChTests(cTestCaseEvaluator):
  def __init__(self, test_case_id, test_session_id, batch, ref_intervals,
               get_needed_signals):
    needed_io_signals = ['dxv', 'AEBS1_SystemState', 'XBR_request',
                         'XBR_Demand', 'TSC1_request']
    needed_param_signals = ['axvBrakingLimit', 'axvPartialBraking']
    sgns_4_tc_eval, params_4_tc_eval =\
      self._init_basic_data(test_case_id, test_session_id, batch, ref_intervals,
                            cTestCaseGeneralEvalHelpers,
                            get_needed_signals,
                            needed_io_signals, needed_param_signals)
    self._check_sgn_availability(sgns_4_tc_eval, params_4_tc_eval,
                                 needed_io_signals, needed_param_signals)
    if self.missing_signals:
      return
    
    target_approached = np.zeros_like(sgns_4_tc_eval['dxv'])
    target_approached[1:] = np.diff(sgns_4_tc_eval['dxv'])
    self.appr_target_ints = self.tceh.def_ints(ref_intervals, target_approached,
                                               measproc.less, 0)
    self.aebs_state_15 =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 15)
    self.aebs_state_1 =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 1)
    self.aebs_state_3 =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 3)
    self.warn_pres_ints =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 5)
    self.part_pres_ints =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 6)
    self.emer_pres_ints =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 7)
    self.aebs_casc_pres_ints =\
      self.tceh.det_casc_flow(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'])
    
    self.tsc1_req_on =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['TSC1_request'],
                         measproc.not_equal, 0)
    self.tsc1_req_off =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['TSC1_request'],
                         measproc.equal, 0)
    self.xbr_req_on =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['XBR_request'],
                         measproc.not_equal, 0)
    self.xbr_req_off =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['XBR_request'],
                         measproc.equal, 0)
    self.xbr_dem_part =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['XBR_Demand'],
                         measproc.equal, params_4_tc_eval['axvPartialBraking'])
    xbr_dem_emer =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['XBR_Demand'],
                         measproc.less, params_4_tc_eval['axvPartialBraking'])
    emer_braking =\
      self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['XBR_Demand'],
                         measproc.greater_equal,
                         params_4_tc_eval['axvBrakingLimit'])
    self.xbr_dem_emer = xbr_dem_emer.intersect(emer_braking)
    
    self.warn_phase_len = self.warn_pres_ints.sumTime()
    self.part_phase_len = self.part_pres_ints.sumTime()
    self.margin_t_len = self.warn_phase_len + (self.part_phase_len / 3.0)
    self.casc_len = self.aebs_casc_pres_ints.sumTime()
    return
  
  @tc_eval_func
  def TC938532(self):
    """ConfigChannel_0"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals, self.aebs_state_15,
                              self.appr_target_ints.intersect(self.tsc1_req_off),
                              self.appr_target_ints.intersect(self.xbr_req_off))
    return self.report
  
  @tc_eval_func
  def TC938561(self):
    """ConfigChannel_1"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals,
                              self.aebs_casc_pres_ints,
                              self.appr_target_ints.intersect(self.tsc1_req_off),
                              self.appr_target_ints.intersect(self.xbr_req_off),
                              self.aebs_state_1.addMargin(TimeMargins=(0,self.margin_t_len)))
    return self.report
  
  @tc_eval_func
  def TC938576(self):
    """ConfigChannel_2"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals,
                              self.aebs_casc_pres_ints,
                              self.appr_target_ints.intersect(self.xbr_req_off),
                              self.part_pres_ints.intersect(self.tsc1_req_on),
                              self.aebs_state_1.addMargin(TimeMargins=(0,self.margin_t_len)))
    return self.report
  
  @tc_eval_func
  def TC938578(self):
    """ConfigChannel_3"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals,
                              self.aebs_casc_pres_ints,
                              self.part_pres_ints.intersect(self.tsc1_req_on),
                              self.part_pres_ints.intersect(self.xbr_req_on),
                              self.part_pres_ints.intersect(self.xbr_dem_part),
                              self.aebs_state_1.addMargin(TimeMargins=(0,self.margin_t_len)))
    return self.report
  
  @tc_eval_func
  def TC938580(self):
    """ConfigChannel_4"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      partb_tsc1_on = self.part_pres_ints.intersect(self.tsc1_req_on)
      partb_tsc1_on = partb_tsc1_on.addMargin(TimeMargins=(0,0.1))
      partb_xbr_on = self.part_pres_ints.intersect(self.xbr_req_on)
      partb_xbr_on = partb_xbr_on.addMargin(TimeMargins=(0,0.1))
      partb_dem = self.part_pres_ints.intersect(self.xbr_dem_part)
      partb_dem = partb_dem.addMargin(TimeMargins=(0,0.1))
      emerb_tsc1_on = self.emer_pres_ints.intersect(self.tsc1_req_on)
      emerb_tsc1_on = emerb_tsc1_on.addMargin(TimeMargins=(0,0.1))
      emerb_xbr_on = self.emer_pres_ints.intersect(self.xbr_req_on)
      emerb_xbr_on = emerb_xbr_on.addMargin(TimeMargins=(0,0.1))
      emerb_dem = self.emer_pres_ints.intersect(self.xbr_dem_emer)
      emerb_dem = emerb_dem.addMargin(TimeMargins=(0,0.1))
      self.tceh.judge_results(self.report, self.ref_intervals,
                              self.aebs_casc_pres_ints,
                              partb_tsc1_on, partb_xbr_on, partb_dem,
                              emerb_tsc1_on, emerb_xbr_on, emerb_dem,
                              self.aebs_state_3.addMargin(TimeMargins=(0,self.casc_len)))
    return self.report


class cEvalOtherTests(cTestCaseEvaluator):
  """
  Evaluate tests that have no separate groups or are "alone in their groups".
  """
  def __init__(self, test_case_id, test_session_id, batch, ref_intervals,
               get_needed_signals):
    needed_io_signals = ['dxv', 'vxv', 'AEBS1_SystemState', 'sim_ta2_angle',
                         'sim_ta2_range', 'sim_ta3_angle', 'sim_ta3_range',
                         'EEC1_EngSpd', 'eval_inj_cascade_pos']
    needed_param_signals = ['EngineSpeedMinEnable', 'dxStartICB',
                            'vRelStartICB', 'dxSecure']
    sgns_4_tc_eval, params_4_tc_eval =\
      self._init_basic_data(test_case_id, test_session_id, batch, ref_intervals,
                            cTestCaseGeneralEvalHelpers,
                            get_needed_signals,
                            needed_io_signals, needed_param_signals)
    self._check_sgn_availability(sgns_4_tc_eval, params_4_tc_eval,
                                 needed_io_signals, needed_param_signals)
    if self.missing_signals:
      return
    
    self.aebs_with_icb_ints =\
      self.tceh.det_icb(self.ref_intervals, sgns_4_tc_eval['dxv'],
                        sgns_4_tc_eval['vxv'], params_4_tc_eval['dxStartICB'],
                        params_4_tc_eval['vRelStartICB'],
                        sgns_4_tc_eval['AEBS1_SystemState'])
    
    self.aebs_ready_ints =\
      self.tceh.def_ints(self.ref_intervals,
                         sgns_4_tc_eval['AEBS1_SystemState'], measproc.equal, 3)
    self.aebs_tmp_na_ints =\
      self.tceh.def_ints(self.ref_intervals,
                         sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 1)
    self.aebs_warn_pres_ints =\
      self.tceh.def_ints(self.ref_intervals,
                         sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 5)
    self.aebs_part_pres_ints =\
      self.tceh.def_ints(self.ref_intervals,
                         sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 6)
    self.aebs_emer_pres_ints =\
      self.tceh.def_ints(self.ref_intervals,
                         sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 7)
    self.warn_then_part_ints =\
      self.aebs_warn_pres_ints.neighbour(self.aebs_part_pres_ints,
                                         CycleMargins=(3,3))
    self.part_then_emer_ints =\
      self.aebs_part_pres_ints.neighbour(self.aebs_emer_pres_ints,
                                         CycleMargins=(3,3))
    self.aebs_casc_pres_ints =\
      self.tceh.det_casc_flow(self.ref_intervals,
                              sgns_4_tc_eval['AEBS1_SystemState'])
    
    alley_way_appr = np.zeros_like(sgns_4_tc_eval['sim_ta2_range'])
    alley_way_appr[1:] = np.diff(sgns_4_tc_eval['sim_ta2_range'])
    alley_way_appr_ints = self.tceh.def_ints(self.ref_intervals, alley_way_appr,
                                             measproc.less, 0)
    same_range =\
      np.abs(sgns_4_tc_eval['sim_ta3_range'] - sgns_4_tc_eval['sim_ta2_range']) <= 0.1
    on_opposite_sides =\
      np.abs(sgns_4_tc_eval['sim_ta2_angle'] + sgns_4_tc_eval['sim_ta3_angle']) <= 0.05
    same_range = np.logical_and(same_range, on_opposite_sides)
    same_range_ints = self.tceh.def_ints(self.ref_intervals, same_range,
                                         measproc.not_equal, 0)
    self.alley_way_appr_ints = alley_way_appr_ints.intersect(same_range_ints)
    
    self.min_rpm_inj_pos = []
    for casc_pos in [1, 5, 6, 7]:
      inj_pos = self.tceh.def_ints(self.ref_intervals,
                                   sgns_4_tc_eval['eval_inj_cascade_pos'],
                                   measproc.equal, casc_pos)
      self.min_rpm_inj_pos.append(inj_pos)
    min_rpm_icb = self.tceh.def_ints(self.ref_intervals,
                                     sgns_4_tc_eval['eval_inj_cascade_pos'],
                                     measproc.equal, 0)
    min_rpm_icb =\
      cIntervalList(min_rpm_icb.Time, Intervals=[min_rpm_icb.Intervals[-1]])
    self.min_rpm_inj_pos.append(min_rpm_icb)
    self.engine_below_min_rpm_ints =\
      self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['EEC1_EngSpd'],
                         measproc.less, params_4_tc_eval['EngineSpeedMinEnable'])

    # Test makes sense only if parameters allow override to happen
    self.engine_below_testable =\
      params_4_tc_eval['EngineSpeedMinEnable'] > 0.0
    
    self.secure_dist_ints =\
      self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['dxv'],
                         measproc.greater_equal,
                         max(params_4_tc_eval['dxSecure']-1.5, 1.0))
    
    self.rel_vel_min_ints =\
      self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['vxv'],
                         measproc.greater_equal, -3.0/3.6)
    return
  
  @tc_eval_func
  def TC938585(self):
    """CascConsisCheck"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      all_warn_ok = self.ref_intervals.intersect(self.aebs_warn_pres_ints)
      all_part_ok = self.ref_intervals.intersect(self.aebs_part_pres_ints)
      all_emer_ok = self.ref_intervals.intersect(self.aebs_emer_pres_ints)
      all_casc_ok = all_warn_ok.union(all_part_ok)
      all_casc_ok = all_casc_ok.union(all_emer_ok)
      
      all_w_p_trans_ok = self.ref_intervals.intersect(self.warn_then_part_ints)
      all_w_e_trans_ok = self.ref_intervals.intersect(self.part_then_emer_ints)
      all_trans_ok = all_w_p_trans_ok.Intervals
      all_trans_ok.extend(all_w_e_trans_ok.Intervals)
      all_trans_ok = [int((start + end) / 2) for start, end in all_trans_ok]
      
      cascs_complete = []
      for mid_idx in all_trans_ok:
        cascs_complete.append(all_casc_ok.findInterval(mid_idx))
      cascs_complete_ints = cIntervalList.fromList(self.ref_intervals.Time,
                                                   cascs_complete)
      self.tceh.judge_results(self.report, self.ref_intervals, cascs_complete_ints)
    return self.report
  
  @tc_eval_func
  def TC910471(self):
    """MovObjCutIn"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals,
                              self.aebs_casc_pres_ints,
                              self.rel_vel_min_ints, self.secure_dist_ints)
    return self.report
  
  @tc_eval_func
  def TC910473(self):
    """MovObjCutOut"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals,
                              self.aebs_casc_pres_ints.negate(),
                              fail_comment="Simulated target comes back after cut out. This causes a warning in short distance. Behaviour is OK, test Passed.")
    return self.report
  
  @tc_eval_func
  def TC910485(self):
    """AlleyWay"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals, self.alley_way_appr_ints,
                              self.aebs_ready_ints)
    return self.report
  
  @tc_eval_func
  def TC938590(self):
    """EnterICB"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals, self.aebs_with_icb_ints)
    return self.report
  
  @tc_eval_func
  def TC951027(self):
    """TestAEBSMinEngRPM"""
    # Test makes sense only if parameters allow override to happen
    if self.missing_signals or not self.engine_below_testable:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      min_eng_rpm_ok = []
      for idx, inj_pos in enumerate(self.min_rpm_inj_pos):
        if idx == 0:
          min_rpm_ok =\
            self.tceh.det_aebs_react_on_override(self.engine_below_min_rpm_ints,
                                                 inj_pos, self.aebs_ready_ints)
        else:
          min_rpm_ok =\
            self.tceh.det_aebs_react_on_override(self.engine_below_min_rpm_ints,
                                                 inj_pos,
                                                 self.aebs_casc_pres_ints)
        min_eng_rpm_ok.extend(min_rpm_ok)
      min_eng_rpm_ok = list(set(min_eng_rpm_ok))
      min_eng_rpm_ok_ints =\
        cIntervalList.fromList(self.ref_intervals.Time, min_eng_rpm_ok)
      self.tceh.judge_results(self.report, self.ref_intervals,
                              min_eng_rpm_ok_ints.addMargin(CycleMargins=(0,3)),
                              self.engine_below_min_rpm_ints.intersect(self.aebs_tmp_na_ints))
    return self.report
  
  @tc_eval_func
  def TC951033(self):
    """NCAP_CCRb_a-2d40"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals,
                              self.aebs_casc_pres_ints,
                              self.rel_vel_min_ints, self.secure_dist_ints)
    return self.report
  
  @tc_eval_func
  def TC951035(self):
    """NCAP_CCRb_a-2d40"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals,
                              self.aebs_warn_pres_ints)
    return self.report
  
  @tc_eval_func
  def TC951037(self):
    """NCAP_CCRb_a-2d40"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals,
                              self.aebs_warn_pres_ints)
    return self.report
  
  @tc_eval_func
  def TC951039(self):
    """NCAP_CCRb_a-2d40"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals,
                              self.aebs_warn_pres_ints)
    return self.report


class cEvalExitICBTests(cTestCaseEvaluator):
  def __init__(self, test_case_id, test_session_id, batch, ref_intervals,
               get_needed_signals):
    needed_io_signals = ['AEBS1_SystemState', 'BPPos', 'GPPos',
                         'alpSteeringWheel', 'DirIndL_b', 'DirIndR_b',
                         'DriverActivationDemand_b', 'GPKickdown_B',
                         'vxv', 'dxv']
    needed_param_signals = ['pAccelMinStopICB', 'pAccelDeltaMinStop',
                            'pDtAccelMinStop', 'pBrakeMinStop',
                            'vRelStartICB', 'dxStartICB',
                            'alpSteeringWheelDeltaMinStop',
                            'alpDtSteeringWheelMinStop']
    sgns_4_tc_eval, params_4_tc_eval =\
      self._init_basic_data(test_case_id, test_session_id, batch, ref_intervals,
                            cTestCaseOverrideEvalHelpers,
                            get_needed_signals,
                            needed_io_signals, needed_param_signals)
    self._check_sgn_availability(sgns_4_tc_eval, params_4_tc_eval,
                                 needed_io_signals, needed_param_signals)
    if self.missing_signals:
      return
    
    self.aebs_with_icb =\
      self.tceh.det_icb(self.ref_intervals, sgns_4_tc_eval['dxv'],
                        sgns_4_tc_eval['vxv'], params_4_tc_eval['dxStartICB'],
                        params_4_tc_eval['vRelStartICB'],
                        sgns_4_tc_eval['AEBS1_SystemState'])
    
    self.gp_kickdown_on =\
      self.tceh.get_gp_kick_override_ints(self.ref_intervals,
                                          sgns_4_tc_eval['GPPos'],
                                          sgns_4_tc_eval['GPKickdown_B'])
    self.bp_pressed =\
      self.tceh.get_bp_override_ints(self.ref_intervals,
                                     sgns_4_tc_eval['BPPos'],
                                     params_4_tc_eval['pBrakeMinStop'])

    self.dir_ind_l_active = self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['DirIndL_b'], measproc.not_equal, 0)
    self.dir_ind_r_active = self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['DirIndR_b'], measproc.not_equal, 0)

    self.aebs_not_active =\
      self.tceh.get_aebs_deact_override_ints(self.ref_intervals,
                                             sgns_4_tc_eval['DriverActivationDemand_b'])
    self.gp_no_kickdown =\
      self.tceh.get_gp_no_kick_override_ints(self.ref_intervals,
                                             sgns_4_tc_eval['GPPos'],
                                             sgns_4_tc_eval['GPKickdown_B'],
                                             params_4_tc_eval['pAccelMinStopICB'])
    self.gp_gradient_ok =\
      self.tceh.get_gradient_override_ints(self.ref_intervals,
                                           sgns_4_tc_eval['GPPos'],
                                           params_4_tc_eval['pAccelMinStopICB'],
                                           params_4_tc_eval['pDtAccelMinStop'],
                                           params_4_tc_eval['pAccelDeltaMinStop'])
                                           
    # Test makes sense only if parameters allow override to happen
    self.gp_gradient_testable =\
      params_4_tc_eval['pAccelMinStopICB'] > params_4_tc_eval['pAccelDeltaMinStop']
      
    self.steering_large_enough =\
      self.tceh.get_gradient_override_ints(self.ref_intervals,
                                           abs(sgns_4_tc_eval['alpSteeringWheel']),
                                           None,
                                           params_4_tc_eval['alpDtSteeringWheelMinStop'],
                                           params_4_tc_eval['alpSteeringWheelDeltaMinStop'])
    return
  
  @tc_eval_func
  def TC910524(self):
    """ExitICB_AccelPedal_KickDown"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      react_ok = self.tceh.det_aebs_react_on_override(self.gp_kickdown_on,
                                                      self.gp_kickdown_on,
                                                      self.aebs_with_icb)
      react_ok_ints = cIntervalList.fromList(self.ref_intervals.Time, react_ok)
      self.tceh.judge_results(self.report, self.ref_intervals, react_ok_ints)
    return self.report
  
  @tc_eval_func
  def TC910526(self):
    """ExitICB_AccelPedal_NoKickDown"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      react_ok = self.tceh.det_aebs_react_on_override(self.gp_no_kickdown,
                                                      self.gp_no_kickdown,
                                                      self.aebs_with_icb)
      react_ok_ints = cIntervalList.fromList(self.ref_intervals.Time, react_ok)
      self.tceh.judge_results(self.report, self.ref_intervals, react_ok_ints)
    return self.report
  
  @tc_eval_func
  def TC910528(self):
    """ExitICB_AccelPedal_Gradient"""
    # Test makes sense only if parameters allow override to happen
    if self.missing_signals or not self.gp_gradient_testable:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      react_ok = self.tceh.det_aebs_react_on_override(self.gp_gradient_ok,
                                                      self.gp_gradient_ok,
                                                      self.aebs_with_icb)
      react_ok_ints = cIntervalList.fromList(self.ref_intervals.Time, react_ok)
      self.tceh.judge_results(self.report, self.ref_intervals, react_ok_ints)
    return self.report
  
  @tc_eval_func
  def TC910530(self):
    """ExitICB_BrakePedal"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals,
                              self.aebs_with_icb, self.bp_pressed)
    return self.report
  
  def _eval_exit_icb_steering(self):
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals, self.aebs_with_icb,
                              self.steering_large_enough)
    return self.report
  
  @tc_eval_func
  def TC910532(self):
    """ExitICB_SteeringWheel_Left"""
    return self._eval_exit_icb_steering()
  
  @tc_eval_func
  def TC910535(self):
    """ExitICB_SteeringWheel_Right"""
    return self._eval_exit_icb_steering()
  
  def _eval_exit_icb_turn_ind(self, direction="left"):
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      self.tceh.judge_results(self.report, self.ref_intervals, self.aebs_with_icb,
                              self.dir_ind_l_active if direction == "left" else self.dir_ind_r_active)
    return self.report
  
  @tc_eval_func
  def TC910537(self):
    """ExitICB_TurnIndicator_Left"""
    return self._eval_exit_icb_turn_ind()
  
  @tc_eval_func
  def TC910539(self):
    """ExitICB_TurnIndicator_Right"""
    return self._eval_exit_icb_turn_ind(direction="right")
  
  @tc_eval_func
  def TC910541(self):
    """ExitICB_MainSwitch"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      react_ok = self.tceh.det_aebs_react_on_override(self.aebs_not_active,
                                                      self.aebs_not_active,
                                                      self.aebs_with_icb)
      react_ok_ints = cIntervalList.fromList(self.ref_intervals.Time, react_ok)
      self.tceh.judge_results(self.report, self.ref_intervals, react_ok_ints)
    return self.report


class cEvalDriverOverrTests(cTestCaseEvaluator):
  def __init__(self, test_case_id, test_session_id, batch, ref_intervals,
               get_needed_signals):
    needed_io_signals = ['AEBS1_SystemState', 'BPPos', 'GPPos',
                         'alpSteeringWheel', 'DirIndL_b', 'DirIndR_b',
                         'DriverActivationDemand_b', 'GPKickdown_B',
                         'dxv', 'OEL_HazardLightSw', 'eval_inj_cascade_pos']
    needed_param_signals = ['pAccelMinStop', 'pAccelDeltaMinStop',
                            'pDtAccelMinStop', 'pBrakeMinStop',
                            'alpSteeringWheelDeltaMinStop',
                            'alpDtSteeringWheelMinStop',
                            'tDirIndMaxSuppress']
    sgns_4_tc_eval, params_4_tc_eval =\
      self._init_basic_data(test_case_id, test_session_id, batch, ref_intervals,
                            cTestCaseOverrideEvalHelpers,
                            get_needed_signals,
                            needed_io_signals, needed_param_signals)
    self._check_sgn_availability(sgns_4_tc_eval, params_4_tc_eval,
                                 needed_io_signals, needed_param_signals)
    if self.missing_signals:
      return
    
    self.gp_kickdown_on =\
      self.tceh.get_gp_kick_override_ints(self.ref_intervals,
                                          sgns_4_tc_eval['GPPos'],
                                          sgns_4_tc_eval['GPKickdown_B'])
    self.bp_pressed =\
      self.tceh.get_bp_override_ints(self.ref_intervals,
                                     sgns_4_tc_eval['BPPos'],
                                     params_4_tc_eval['pBrakeMinStop'])

    self.dir_ind_l_active = self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['DirIndL_b'], measproc.not_equal, 0)
    self.dir_ind_r_active = self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['DirIndR_b'], measproc.not_equal, 0)

    self.aebs_not_active =\
      self.tceh.get_aebs_deact_override_ints(self.ref_intervals,
                                             sgns_4_tc_eval['DriverActivationDemand_b'])
    self.gp_no_kickdown =\
      self.tceh.get_gp_no_kick_override_ints(self.ref_intervals,
                                             sgns_4_tc_eval['GPPos'],
                                             sgns_4_tc_eval['GPKickdown_B'],
                                             params_4_tc_eval['pAccelMinStop'])
    self.gp_gradient_ok =\
      self.tceh.get_gradient_override_ints(self.ref_intervals,
                                           sgns_4_tc_eval['GPPos'],
                                           params_4_tc_eval['pAccelMinStop'],
                                           params_4_tc_eval['pDtAccelMinStop'],
                                           params_4_tc_eval['pAccelDeltaMinStop'])
    self.steering_large_enough =\
      self.tceh.get_gradient_override_ints(self.ref_intervals,
                                           abs(sgns_4_tc_eval['alpSteeringWheel']),
                                           None,
                                           params_4_tc_eval['alpDtSteeringWheelMinStop'],
                                           params_4_tc_eval['alpSteeringWheelDeltaMinStop'])
    
    self.hazard_lights_on =\
      self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['OEL_HazardLightSw'],
                         measproc.not_equal, 0)
    
    self.aebs_in_override =\
      self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 4)
    aebs_sys_state_2 = self.tceh.def_ints(self.ref_intervals,
                                          sgns_4_tc_eval['AEBS1_SystemState'],
                                          measproc.equal, 2)
    self.aebs_in_override_or_inact = self.aebs_in_override.union(aebs_sys_state_2)
    
    self.aebs_casc_ints =\
      self.tceh.det_casc_flow(self.ref_intervals,
                              sgns_4_tc_eval['AEBS1_SystemState'])
    self.aebs_standby_ints =\
      self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 3)
    aebs_casc_with_standby = self.aebs_casc_ints.union(self.aebs_standby_ints)
    self.aebs_casc_with_standby = aebs_casc_with_standby.join(IndexLimit=2)
    
    target_approached = np.zeros_like(sgns_4_tc_eval['dxv'])
    target_approached[1:] = np.diff(sgns_4_tc_eval['dxv'])
    self.appr_target_ints =\
      self.tceh.def_ints(self.ref_intervals, target_approached, measproc.less, 0)
    
    full_meas_ints = cIntervalList.fromList(self.ref_intervals.Time,
                                            [(0, len(self.ref_intervals.Time))])

    dir_ind_l_act_full_meas = self.tceh.def_ints(full_meas_ints, sgns_4_tc_eval['DirIndL_b'], measproc.not_equal, 0)
    dir_ind_r_act_full_meas = self.tceh.def_ints(full_meas_ints, sgns_4_tc_eval['DirIndR_b'], measproc.not_equal, 0)

    aebs_in_override_full_meas =\
      self.tceh.def_ints(full_meas_ints, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 4)
    gp_kickdown_on_full_meas =\
      self.tceh.get_gp_kick_override_ints(full_meas_ints, sgns_4_tc_eval['GPPos'],
                                          sgns_4_tc_eval['GPKickdown_B'])

    dir_ind_l_act_with_aebs_drov = dir_ind_l_act_full_meas.intersect(gp_kickdown_on_full_meas.negate())
    dir_ind_r_act_with_aebs_drov = dir_ind_r_act_full_meas.intersect(gp_kickdown_on_full_meas.negate())

    self.dir_ind_l_act_with_aebs_drov = dir_ind_l_act_with_aebs_drov.intersect(aebs_in_override_full_meas)
    self.dir_ind_r_act_with_aebs_drov = dir_ind_r_act_with_aebs_drov.intersect(aebs_in_override_full_meas)

    self.drov_inj_pos = []
    for casc_pos in [1, 5, 6, 7]:
      inj_casc_pos =\
        self.tceh.def_ints(self.ref_intervals,
                           sgns_4_tc_eval['eval_inj_cascade_pos'],
                           measproc.equal, casc_pos)
      self.drov_inj_pos.append(inj_casc_pos)
    
    self.t_dir_ind_max_suppr = params_4_tc_eval['tDirIndMaxSuppress']
    return
  
  @tc_eval_func
  def TC938594(self):
    """NoDriverOverride_HazardLightActive"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      chk_ints = cIntervalList(self.ref_intervals.Time)
      for inj_pos in self.drov_inj_pos:
        chk_ints = chk_ints.union(self.hazard_lights_on.intersect(inj_pos))
      self.tceh.judge_results(self.report, self.ref_intervals,
                              self.aebs_casc_with_standby, chk_ints)
    return self.report
  
  def _calc_dir_ind_time_bounds(self, direction="left"):
    # assuming that no other intervals are present in these interval lists
    dir_ind_act_with_aebs_drov = self.dir_ind_l_act_with_aebs_drov if direction == "left" else self.dir_ind_r_act_with_aebs_drov
    drov_start, _ = dir_ind_act_with_aebs_drov[0]
    t_drov_start = dir_ind_act_with_aebs_drov.Time[drov_start]
    appr_start, _ = self.appr_target_ints[0]
    t_appr_start = self.appr_target_ints.Time[appr_start]
    return t_appr_start, t_drov_start
  
  def _eval_turn_ind_from_sim_start(self, direction="left"):
    t_appr_start, t_drov_start = self._calc_dir_ind_time_bounds(direction=direction)
    ref_ints_for_tc = (self.dir_ind_l_act_with_aebs_drov.union(self.ref_intervals) if direction == "left" else
                       self.dir_ind_r_act_with_aebs_drov.union(self.ref_intervals))
    ref_ints_for_tc = ref_ints_for_tc.merge(DistLimit=1.0)
    ge_t_dir_ind_max_suppr =\
      measproc.greater_equal(t_appr_start - t_drov_start, self.t_dir_ind_max_suppr)
    if ge_t_dir_ind_max_suppr:
      self.tceh.judge_results(self.report, ref_ints_for_tc, self.aebs_casc_ints)
    else:
      failed_test_ints =\
        cIntervalList.fromList(self.ref_intervals.Time, [(0,1)])
      self.tceh.judge_results(self.report, ref_ints_for_tc, failed_test_ints)
    return self.report
  
  @tc_eval_func
  def TC910490(self):
    """DO_TurnIndi_L_FromSimStart"""
    return self._eval_turn_ind_from_sim_start()
  
  @tc_eval_func
  def TC910492(self):
    """DO_TurnIndi_R_FromSimStart"""
    return self._eval_turn_ind_from_sim_start(direction="right")
  
  def _eval_turn_ind_from_inj_start(self, direction="left"):
    t_appr_start, t_drov_start = self._calc_dir_ind_time_bounds(direction=direction)
    ref_ints_for_tc = (self.dir_ind_l_act_with_aebs_drov.union(self.ref_intervals) if direction == "left" else
                       self.dir_ind_r_act_with_aebs_drov.union(self.ref_intervals))
    l_t_dir_ind_max_suppr =\
      measproc.less(t_appr_start - t_drov_start, self.t_dir_ind_max_suppr)
    if l_t_dir_ind_max_suppr:
      self.tceh.judge_results(self.report, ref_ints_for_tc, self.aebs_in_override,
                              self.aebs_casc_ints.negate())
    else:
      failed_test_ints =\
        cIntervalList.fromList(self.ref_intervals.Time, [(0,1)])
      self.tceh.judge_results(self.report, ref_ints_for_tc, failed_test_ints)
    return self.report
  
  @tc_eval_func
  def TC910494(self):
    """DO_TurnIndi_L_FromInjStart"""
    return self._eval_turn_ind_from_inj_start()
  
  @tc_eval_func
  def TC910496(self):
    """DO_TurnIndi_R_FromInjStart"""
    return self._eval_turn_ind_from_inj_start(direction="right")
  
  def _eval_turn_ind_around_inj_start(self, direction="left"):
    ref_ints_for_tc = (self.dir_ind_l_act_with_aebs_drov.union(self.ref_intervals) if direction == "left" else
                       self.dir_ind_r_act_with_aebs_drov.union(self.ref_intervals))
    self.tceh.judge_results(self.report, ref_ints_for_tc, self.aebs_casc_ints)
    return self.report
  
  @tc_eval_func
  def TC910498(self):
    """DO_TurnIndi_L_AroundInjStart"""
    return self._eval_turn_ind_around_inj_start()
  
  @tc_eval_func
  def TC910500(self):
    """DO_TurnIndi_R_AroundInjStart"""
    return self._eval_turn_ind_around_inj_start(direction="right")
  
  @tc_eval_func
  def TC910504(self):
    """DriverOverride_AccelPedal_KickDown"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      driver_override_ok_ints =\
        self.tceh.override_eval_bwpe(self.ref_intervals, self.drov_inj_pos,
                                     self.gp_kickdown_on,
                                     self.aebs_standby_ints, self.aebs_casc_ints)
      drov_effect_ok =\
        self.gp_kickdown_on.intersect(self.aebs_in_override_or_inact)
      self.tceh.judge_results(self.report, self.ref_intervals,
                              driver_override_ok_ints, drov_effect_ok)
    return self.report
  
  @tc_eval_func
  def TC910506(self):
    """DriverOverride_AccelPedal_NoKickDown"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      driver_override_ok_ints =\
        self.tceh.override_eval_bwpe(self.ref_intervals, self.drov_inj_pos,
                                     self.gp_no_kickdown,
                                     self.aebs_standby_ints, self.aebs_casc_ints, no_kickdown=True)
      drov_effect_ok =\
        self.gp_no_kickdown.intersect(self.aebs_in_override_or_inact)
      self.tceh.judge_results(self.report, self.ref_intervals,
                              driver_override_ok_ints, drov_effect_ok,
                              pass_comment="AEBS state goes to override only in case it should be warning in this override. Behaviour is OK, test PASSED.")
    return self.report
  
  @tc_eval_func
  def TC910508(self):
    """DriverOverride_AccelPedal_Gradient"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      driver_override_ok_ints =\
        self.tceh.override_eval_wp(self.ref_intervals, self.drov_inj_pos,
                                   self.gp_gradient_ok, self.aebs_casc_ints)
      # Expected effect here is:
      # override after cascade state in warning and partial
      # ready after cascade state in before and emergency 
      drov_effect_ok = cIntervalList(self.ref_intervals.Time)
      for ind, interval in enumerate(self.ref_intervals):
        filter = cIntervalList(self.ref_intervals.Time, [interval])
        if ind in [0, 3]:
          drov_effect_ok = drov_effect_ok.union(
            filter.intersect(self.aebs_casc_ints))
        else:
          drov_effect_ok = drov_effect_ok.union(
            filter.intersect(self.gp_gradient_ok).intersect(
              filter.intersect(self.aebs_in_override_or_inact)))
      # drov_effect_ok =\
        # self.gp_gradient_ok.intersect(self.aebs_in_override_or_inact)
      self.tceh.judge_results(self.report, self.ref_intervals,
                          driver_override_ok_ints, drov_effect_ok)
    return self.report
  
  @tc_eval_func
  def TC910510(self):
    """DriverOverride_BrakePedal"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      driver_override_ok_ints =\
        self.tceh.override_eval_bwp(self.ref_intervals, self.drov_inj_pos,
                                    self.bp_pressed, self.aebs_standby_ints,
                                    self.aebs_casc_ints)
      drov_effect_on = self.bp_pressed.intersect(self.aebs_in_override_or_inact)
      self.tceh.judge_results(self.report, self.ref_intervals, 
                              driver_override_ok_ints, drov_effect_on)
    return self.report
  
  def _eval_steering_wheel(self):
    driver_override_ok_ints =\
      self.tceh.override_eval_wp(self.ref_intervals, self.drov_inj_pos,
                                 self.steering_large_enough, self.aebs_casc_ints)
    # Expected effect here is:
    # override after cascade state in warning and partial
    # ready after cascade state in before and emergency 
    drov_effect_ok = cIntervalList(self.ref_intervals.Time)
    for ind, interval in enumerate(self.ref_intervals):
      filter = cIntervalList(self.ref_intervals.Time, [interval])
      if ind in [0, 3]:
        drov_effect_ok = drov_effect_ok.union(
          filter.intersect(self.aebs_casc_ints))
      else:
        drov_effect_ok = drov_effect_ok.union(
          filter.intersect(self.steering_large_enough).intersect(
            filter.intersect(self.aebs_in_override_or_inact)))
    # drov_effect_ok =\
      # self.steering_large_enough.intersect(self.aebs_in_override_or_inact)
    self.tceh.judge_results(self.report, self.ref_intervals,
                        driver_override_ok_ints, drov_effect_ok)
    return self.report
  
  @tc_eval_func
  def TC910512(self):
    """DriverOverride_SteeringWheel_Left"""
    return self._eval_steering_wheel()
  
  @tc_eval_func
  def TC910514(self):
    """DriverOverride_SteeringWheel_Right"""
    return self._eval_steering_wheel()
  
  def _eval_turn_indicator(self, direction="left"):
    driver_override_ok_ints =\
      self.tceh.override_eval_bwp(self.ref_intervals, self.drov_inj_pos,
                                  self.dir_ind_l_active if direction == "left" else self.dir_ind_r_active,
                                  self.aebs_standby_ints, self.aebs_casc_ints)
    drov_effect_ok = (self.dir_ind_l_active.intersect(self.aebs_in_override_or_inact) if direction == "left" else
                      self.dir_ind_r_active.intersect(self.aebs_in_override_or_inact))
    self.tceh.judge_results(self.report, self.ref_intervals,
                            driver_override_ok_ints, drov_effect_ok)
    return self.report
  
  @tc_eval_func
  def TC910516(self):
    """DriverOverride_TurnIndicator_Left"""
    return self._eval_turn_indicator()
  
  @tc_eval_func
  def TC910518(self):
    """DriverOverride_TurnIndicator_Right"""
    return self._eval_turn_indicator(direction="right")
  
  @tc_eval_func
  def TC910520(self):
    """DriverOverride_MainSwitch"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      driver_override_ok_ints =\
        self.tceh.override_eval_bwpe(self.ref_intervals, self.drov_inj_pos,
                                     self.aebs_not_active, self.aebs_standby_ints,
                                     self.aebs_casc_ints)
      drov_effect_ok =\
        self.aebs_not_active.intersect(self.aebs_in_override_or_inact)
      self.tceh.judge_results(self.report, self.ref_intervals,
                              driver_override_ok_ints, drov_effect_ok)
    return self.report


class cEvalErrorHandlerFunc(cTestCaseEvaluator):
  def __init__(self, test_case_id, test_session_id, batch, ref_intervals,
               get_needed_signals):
    needed_io_signals = ['AEBS1_SystemState', 'ControlledIrrevOffRaised_b',
                         'ControlledRevOffRaised_b', 'ImmediateIrrevOffRaised_b',
                         'ImmediateRevOffRaised_b', 'ReducedPerformance_b',
                         'eval_inj_cascade_pos', 'eval_inj_fault_type']
    needed_param_signals = ['WarningEnabledInReducedPerformaceSAM']
    sgns_4_tc_eval, params_4_tc_eval =\
      self._init_basic_data(test_case_id, test_session_id, batch, ref_intervals,
                            cTestCaseErrhanEvalHelpers,
                            get_needed_signals,
                            needed_io_signals, needed_param_signals)
    self._check_sgn_availability(sgns_4_tc_eval, params_4_tc_eval,
                                 needed_io_signals, needed_param_signals)
    if self.missing_signals:
      return
    
    self.set_error_flags = {}
    self.set_error_flags[1] =\
      self.tceh.def_ints(self.ref_intervals,
                         sgns_4_tc_eval['ImmediateIrrevOffRaised_b'],
                         measproc.not_equal, 0)
    self.set_error_flags[2] =\
      self.tceh.def_ints(self.ref_intervals,
                         sgns_4_tc_eval['ImmediateRevOffRaised_b'],
                         measproc.not_equal, 0)
    self.set_error_flags[3] =\
      self.tceh.def_ints(self.ref_intervals,
                         sgns_4_tc_eval['ControlledIrrevOffRaised_b'],
                         measproc.not_equal, 0)
    self.set_error_flags[4] =\
      self.tceh.def_ints(self.ref_intervals,
                         sgns_4_tc_eval['ControlledRevOffRaised_b'],
                         measproc.not_equal, 0)
    self.set_error_flags[5] =\
      self.tceh.def_ints(self.ref_intervals,
                         sgns_4_tc_eval['ReducedPerformance_b'],
                         measproc.not_equal, 0)
    
    self.inj_faults_with_pos = {}
    for inj_pos in [1, 5, 6, 7, 9]:
      inj_fault_ints =\
        self.tceh.def_ints(self.ref_intervals,
                           sgns_4_tc_eval['eval_inj_cascade_pos'],
                           measproc.equal, inj_pos)
      self.inj_faults_with_pos[inj_pos] = inj_fault_ints
    
    self.inj_faults_with_type = {}
    for fault_type in range(1, 6):
      inj_fault_type_ints =\
        self.tceh.def_ints(self.ref_intervals,
                           sgns_4_tc_eval['eval_inj_fault_type'],
                           measproc.equal, fault_type)
      self.inj_faults_with_type[fault_type] = inj_fault_type_ints
    
    self.aebs_casc_pres_ints =\
      self.tceh.det_casc_flow(self.ref_intervals,
                              sgns_4_tc_eval['AEBS1_SystemState'])
    self.aebs_in_error_ints =\
      self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'],
                         measproc.equal, 14)

    self.aebs_in_lim_perf_ints = self.tceh.def_ints(self.ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'], measproc.equal, 8)

    self.limited_perf_en_flag = params_4_tc_eval["WarningEnabledInReducedPerformaceSAM"]
    return
  
  def _eval_func_err_handler(self, inj_positions, mov_obj=True):
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      for inj_pos in inj_positions:
        for fault_type in range(1, 6):
          if fault_type == 3: continue # don't eval for Controlled_irrev_off_raised faults
          inj_fault_ints = self.inj_faults_with_pos[inj_pos]
          if inj_fault_ints:
            # As test cases are split to separate measurements based on inj_positions
            # continue only if the given measurement contains results in this cycle
            inj_fault_ints =\
              inj_fault_ints.intersect(self.inj_faults_with_type[fault_type])
            inj_mid_idx = int(sum(inj_fault_ints.findLongestIntervals()[0]) / 2)
            if not self.set_error_flags[fault_type].isEmpty():
              try:
                err_start, err_end =\
                  self.set_error_flags[fault_type].findInterval(inj_mid_idx)
              except ValueError:
                coinc_set_err_flag_ints =\
                  cIntervalList(self.set_error_flags[fault_type].Time)
              else:
                coinc_set_err_flag_ints =\
                  cIntervalList.fromList(self.set_error_flags[fault_type].Time,
                                         [(err_start, err_end)])
            else:
              coinc_set_err_flag_ints =\
                cIntervalList(self.set_error_flags[fault_type].Time)
            err_set_delay_ints =\
              inj_fault_ints.intersect(coinc_set_err_flag_ints.negate())
            rep_interval = self.ref_intervals.findInterval(inj_mid_idx)
            rep_comment = "%s | %s" % (FAULT_TYPE_4_COMMENT[fault_type],
                                       FAULT_POS_4_COMMENT[inj_pos])

            if self.limited_perf_en_flag == 1 and fault_type == 5:
              # when the WarningEnabledInReducedPerformaceSAM is enabled, the AEBS
              # will change to limitied performance state (AEBS state = 8)
              if mov_obj:
                if ((inj_pos != 1 or (inj_pos == 1 and err_set_delay_ints.sumTime() <= 0.4)) and
                    self.aebs_casc_pres_ints.intersect(coinc_set_err_flag_ints) and
                    self.aebs_in_lim_perf_ints.intersect(coinc_set_err_flag_ints)):
                  self.tceh.vote_intervals(self.report, rep_interval, self.tceh.tc_passed, rep_comment)
                else:
                  self.tceh.vote_intervals(self.report, rep_interval, self.tceh.tc_failed, rep_comment)
              else:
                if ((inj_pos == 1 and self.aebs_in_lim_perf_ints.intersect(coinc_set_err_flag_ints) and
                     err_set_delay_ints.sumTime() <= 0.4 and not self.aebs_casc_pres_ints.intersect(coinc_set_err_flag_ints)) or
                    (inj_pos != 1 and self.aebs_casc_pres_ints.intersect(coinc_set_err_flag_ints))):
                  self.tceh.vote_intervals(self.report, rep_interval, self.tceh.tc_passed, rep_comment)
                else:
                  self.tceh.vote_intervals(self.report, rep_interval, self.tceh.tc_failed, rep_comment)
            else:
              if fault_type in [1, 2] or inj_pos == 1:
                # fault is of immediate type or it is injected before the AEBS cascade
                if (err_set_delay_ints.sumTime() <= (0.4 if fault_type == 5 else 0.1)
                    and not self.aebs_casc_pres_ints.intersect(coinc_set_err_flag_ints)
                    and self.aebs_in_error_ints.intersect(coinc_set_err_flag_ints)):
                  # Reduced_perf_rev_raised fault will only be set 200-250ms later,
                  # when stopping video message 0.4 second will allow to pass
                  self.tceh.vote_intervals(self.report, rep_interval,
                                           self.tceh.tc_passed, rep_comment)
                else:
                  self.tceh.vote_intervals(self.report, rep_interval,
                                           self.tceh.tc_failed, rep_comment)
              else:
                if (self.aebs_casc_pres_ints.intersect(coinc_set_err_flag_ints)
                    and self.aebs_in_error_ints.intersect(coinc_set_err_flag_ints)):
                  self.tceh.vote_intervals(self.report, rep_interval,
                                           self.tceh.tc_passed, rep_comment)
                else:
                  self.tceh.vote_intervals(self.report, rep_interval,
                                           self.tceh.tc_failed, rep_comment)
    return self.report
  
  @tc_eval_func
  def TC893451(self):
    """MovObj_ErrorHandlerTest"""
    inj_positions = [1, 5, 6, 7]
    return self._eval_func_err_handler(inj_positions)
  
  @tc_eval_func
  def TC951017(self):
    """StatObj_ErrorHandlerTest"""
    inj_positions = [1, 5, 6, 7, 9]
    return self._eval_func_err_handler(inj_positions, mov_obj=False)


class cEvalErrorHandlerInterface(cTestCaseEvaluator):
  def __init__(self, test_case_id, test_session_id, batch, ref_intervals,
               get_needed_signals):
    needed_io_signals = ['CAN_sgn_to_chg_length', 'CAN_sgn_to_chg_startbit']
    needed_param_signals = []
    sgns_4_tc_eval, params_4_tc_eval =\
      self._init_basic_data(test_case_id, test_session_id, batch, ref_intervals,
                            cTestCaseErrhanEvalHelpers,
                            get_needed_signals,
                            needed_io_signals, needed_param_signals)
    additional_io_sgn_names = ['CAN_ID_msg_to_sgn_chg', 'CAN_ID_msg_to_timeout',
                               'eval_inj_fault_dtc_id_ok', 'eval_inj_fault_flag_ok',
                               'CAN_sgn_chg_type']
    additional_io_sgns = get_needed_signals(*additional_io_sgn_names)
    sgns_4_tc_eval.update(additional_io_sgns)
    needed_io_signals.extend(additional_io_sgn_names)
    self._check_sgn_availability(sgns_4_tc_eval, params_4_tc_eval,
                                 needed_io_signals, needed_param_signals)
    if self.missing_signals:
      return
    
    self.timeout_inputs = [sgns_4_tc_eval['eval_inj_fault_dtc_id_ok'],
                           sgns_4_tc_eval['eval_inj_fault_flag_ok']]
    self.timeout_can_ids = sgns_4_tc_eval['CAN_ID_msg_to_timeout']
    self.sgn_chg_inputs = [(ref_intervals.Time,
                            sgns_4_tc_eval['CAN_sgn_to_chg_startbit']),
                           (ref_intervals.Time,
                            sgns_4_tc_eval['CAN_sgn_to_chg_length']),
                           sgns_4_tc_eval['eval_inj_fault_dtc_id_ok'],
                           sgns_4_tc_eval['eval_inj_fault_flag_ok'],
                           sgns_4_tc_eval['CAN_sgn_chg_type']]
    self.sgn_chg_can_ids = sgns_4_tc_eval['CAN_ID_msg_to_sgn_chg']
    return
  
  @tc_eval_func
  def TC893448(self):
    """Interface_ErrorHandlerTest"""
    if self.missing_signals:
      for start, end in self.ref_intervals:
        self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
    else:
      for test_res in self.tceh.select_errhan_interf_test_res(self.timeout_can_ids,
                                                              self.timeout_inputs):
        v_msg_id, t_msg_id, vals = test_res
        dtc_id_ok, flag_ok = vals
        msg_id_ints =\
          self.tceh.def_ints_from_mask(self.timeout_can_ids[0],
                                       self.timeout_can_ids[1],
                                       measproc.equal, v_msg_id)
        t_idx = msg_id_ints.getTimeIndex(t_msg_id)
        interval = msg_id_ints.findInterval(t_idx)
        id_in_hex = hex(v_msg_id)[:2] + hex(v_msg_id)[2:].upper()
        id_in_hex = id_in_hex[:-1]
        rep_comment = "Timeout | %s" % CAN_MSG_ID_4_COMMENT[id_in_hex]
        if dtc_id_ok == 1 and flag_ok == 1:
          self.tceh.vote_intervals(self.report, interval, self.tceh.tc_passed,
                                   rep_comment)
        else:
          self.tceh.vote_intervals(self.report, interval, self.tceh.tc_failed,
                                   rep_comment)
      
      for test_res in self.tceh.select_errhan_interf_test_res(self.sgn_chg_can_ids,
                                                              self.sgn_chg_inputs):
        v_msg_id, t_msg_id, vals = test_res
        sgn_start, sgn_len, dtc_id_ok, flag_ok, chg_type = vals
        msg_id_ints =\
          self.tceh.def_ints_from_mask(self.sgn_chg_can_ids[0],
                                       self.sgn_chg_can_ids[1],
                                       measproc.equal, v_msg_id)
        t_idx = msg_id_ints.getTimeIndex(t_msg_id)
        interval = msg_id_ints.findInterval(t_idx)
        id_in_hex = hex(v_msg_id)[:2] + hex(v_msg_id)[2:].upper()
        id_in_hex = id_in_hex[:-1]
        sgn_start = int(sgn_start)
        sgn_len = int(sgn_len)
        chg_type = int(chg_type)
        rep_comment = "%s | %s" % (CAN_SGN_CHG_TYPE_4_COMMENT[chg_type],
                                   CAN_SGN_ID_4_COMMENT[(id_in_hex, sgn_start, sgn_len)])
        if dtc_id_ok in [1, 3] and flag_ok in [1, 3]:
          self.tceh.vote_intervals(self.report, interval, self.tceh.tc_passed,
                                   rep_comment)
        elif dtc_id_ok == 2:
          self.tceh.vote_intervals(self.report, interval, self.tceh.tc_incons,
                                   rep_comment)
        else:
          self.tceh.vote_intervals(self.report, interval, self.tceh.tc_failed,
                                   rep_comment)
    return self.report
