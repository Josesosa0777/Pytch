# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

import logging
import measproc
from interface import iSearch
from ..tceval.rail_eval_n_ccp_meas_handler import cAcquireSignals
from ..tceval.rail_tc_eval import cTestCaseEvaluator, evaluate_test_case, tc_eval_func
from ..tceval.rail_tc_eval_helpers import cTestCaseOverrideEvalHelpers


class Search(iSearch, cAcquireSignals):
    def _get_basic_rail_info(self):
        test_sgn_names = ['RaIL_test_case_id', 'RaIL_test_session_id']
        test_mng_data = self.get_rail_eval_sgn(*test_sgn_names)

        test_case_id = test_mng_data['RaIL_test_case_id'][1][0]
        test_session_id = test_mng_data['RaIL_test_session_id'][1][0]

        ccp_sgn_name = self.ccp_input_group.keys()[0]
        ccp_time = self.get_ccp_input_sgn(ccp_sgn_name)[ccp_sgn_name][0]
        rail_man_sgn = self.get_rail_eval_sgn('set_new_conditions',
                                              common_time=ccp_time)
        ref_intervals = self.source.compare(ccp_time,
                                            rail_man_sgn['set_new_conditions'],
                                            measproc.not_equal, 0)
        return test_case_id, test_session_id, ref_intervals

    def search(self):
        test_case_id, test_session_id, ref_intervals = self._get_basic_rail_info()
        report = evaluate_test_case(cEvalACCTests, test_case_id, test_session_id, self.batch, ref_intervals,
                                    self.get_needed_signals)
        if report is not None:
            self.batch.add_entry(report)
        return


AEBS_SYSTEM_STATE__IS_NOT_READY = 0,
AEBS_SYSTEM_STATE__TEMP_NOT_AVAILABLE = 1,
AEBS_SYSTEM_STATE__IS_DEACTIVATED_BY_DRIVER = 2,
AEBS_SYSTEM_STATE__IS_READY = 3,
AEBS_SYSTEM_STATE__DRIVER_OVERRIDES_SYSTEM = 4,
AEBS_SYSTEM_STATE__COLLISION_WARNING_ACTIVE = 5,
AEBS_SYSTEM_STATE__COLLISION_WARNING_WITH_BRAKING = 6,
AEBS_SYSTEM_STATE__EMERGENCY_BRAKING_ACTIVE = 7,
AEBS_SYSTEM_STATE__ERROR_INDICATION = 14,
AEBS_SYSTEM_STATE__NOT_AVAILABLE = 15


class cEvalACCTests(cTestCaseEvaluator):
    def __init__(self, test_case_id, test_session_id, batch, ref_intervals,
                 get_needed_signals):
        self.logger = logging.getLogger()
        self.get_needed_signals = get_needed_signals

        needed_io_signals = ['AEBS1_SystemState', 'XBR_ExtAccelDem', 'XBR_Prio', 'XBR_Demand', 'ACC_brake_req',
                             'ACC_brake_dem']
        needed_param_signals = []
        sgns_4_tc_eval, params_4_tc_eval = \
            self._init_basic_data(test_case_id, test_session_id, batch, ref_intervals,
                                  cTestCaseOverrideEvalHelpers,
                                  get_needed_signals,
                                  needed_io_signals, needed_param_signals)
        self._check_sgn_availability(sgns_4_tc_eval, params_4_tc_eval,
                                     needed_io_signals, needed_param_signals)
        if self.missing_signals:
            self.logger.warn("Can't evaluate ACC tests because of missing signal(s): \n" + self.missing_signals)
            return

        # def_ints() returns a cIntervalList instance where the specified conditions hold true
        self.aebs_disabled = self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'], measproc.equal, 2)
        self.aebs_idle = self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'], measproc.equal, 3)
        self.aebs_override = self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'], measproc.equal, 4)
        self.aebs_warning = self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'], measproc.equal, 5)
        self.aebs_partial_brk = self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'], measproc.equal, 6)
        self.aebs_emergency = self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['AEBS1_SystemState'], measproc.equal, 7)

        self.acc_active = self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['ACC_brake_req'], measproc.equal, 4)

        # the AEBS XBR_request value needs to be converted to physical value
        # there will be rounding error between the values the maximum of 1/2048
        self.aebsXBRdem_eq_XBRextDem = \
            self.tceh.def_ints(ref_intervals,
                               sgns_4_tc_eval['XBR_ExtAccelDem'] - sgns_4_tc_eval['XBR_Demand'] / 2048.0,
                               measproc.less, 1 / 2048.0)

        self.accXBRdem_eq_XBRextDem = \
            self.tceh.def_ints(ref_intervals,
                               sgns_4_tc_eval['XBR_ExtAccelDem'] - sgns_4_tc_eval['ACC_brake_dem'],
                               measproc.less, 1 / 2048.0)

        self.XBRextDem_gt_th = \
            self.tceh.def_ints(ref_intervals,
                               sgns_4_tc_eval['XBR_ExtAccelDem'], measproc.greater_equal, -4.0)

        self.XBRextDem_non_negative = \
            self.tceh.def_ints(ref_intervals,
                               sgns_4_tc_eval['XBR_ExtAccelDem'], measproc.greater_equal, 0.0)

        minOf_ACCnAEBS_brk_dem = np.minimum(sgns_4_tc_eval['XBR_Demand'] / 2048.0, sgns_4_tc_eval['ACC_brake_dem'])
        self.accXBRdem_eq_minOfACCnAEBS = \
            self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['XBR_ExtAccelDem'] - minOf_ACCnAEBS_brk_dem,
                               measproc.less, 1 / 2048.0)

        self.XBR_high = self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['XBR_Prio'], measproc.equal, 0)
        self.XBR_not_high = self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['XBR_Prio'], measproc.not_equal, 0)
        self.XBR_low = self.tceh.def_ints(ref_intervals, sgns_4_tc_eval['XBR_Prio'], measproc.equal, 3)

    @tc_eval_func
    def TC2744402(self):
        if self.missing_signals:
            for start, end in self.ref_intervals:
                self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
        else:
            self.tceh.judge_results(self.report, self.ref_intervals, self.aebs_emergency,
                                    self.XBR_high, self.aebsXBRdem_eq_XBRextDem)
        return self.report
        pass

    @tc_eval_func
    def TC2744414(self):
        if self.missing_signals:
            for start, end in self.ref_intervals:
                self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
        else:
            self.tceh.judge_results(self.report, self.ref_intervals, self.aebs_idle, self.XBR_not_high,
                                    self.acc_active, self.accXBRdem_eq_XBRextDem, self.XBRextDem_gt_th)
        return self.report
        pass

    @tc_eval_func
    def TC2744461(self):
        if self.missing_signals:
            for start, end in self.ref_intervals:
                self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
        else:
            self.tceh.judge_results(self.report, self.ref_intervals, self.aebs_partial_brk,
                                    self.XBR_high, self.acc_active, self.XBRextDem_gt_th,
                                    self.accXBRdem_eq_minOfACCnAEBS)
        return self.report
        pass

    @tc_eval_func
    def TC2744470(self):
        if self.missing_signals:
            for start, end in self.ref_intervals:
                self.tceh.vote_intervals(self.report, (start, end), self.tceh.tc_incons)
        else:
            self.tceh.judge_results(self.report, self.ref_intervals,
                                    self.aebs_disabled.union(self.aebs_idle).union(self.aebs_override), self.XBR_low,
                                    self.XBRextDem_non_negative)
        return self.report
        pass
