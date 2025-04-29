# -*- dataeval: init -*-
# -*- coding: utf-8 -*-


import measproc
from interface import iSearch
from tceval.rail_eval_n_ccp_meas_handler import cAcquireSignals
from tceval.rail_tc_eval import cEvalConfChTests, cEvalDriverOverrTests,\
                                cEvalErrorHandlerFunc, cEvalErrorHandlerInterface,\
                                cEvalExitICBTests, cEvalMovObjApprTests,\
                                cEvalOtherTests, cEvalStatObjApprTests, evaluate_test_case


class Search(iSearch, cAcquireSignals):
  def _get_basic_rail_info(self):
    test_management_sgn_names = ['RaIL_test_case_id', 'RaIL_test_session_id']
    test_mng_data = self.get_rail_eval_sgn(*test_management_sgn_names)
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
    report = evaluate_test_case(cEvalMovObjApprTests, test_case_id,
                                test_session_id, self.batch, ref_intervals,
                                self.get_needed_signals)
    report = evaluate_test_case(cEvalStatObjApprTests, test_case_id,
                                test_session_id, self.batch, ref_intervals,
                                self.get_needed_signals, report=report)
    report = evaluate_test_case(cEvalConfChTests, test_case_id,
                                test_session_id, self.batch, ref_intervals,
                                self.get_needed_signals, report=report)
    report = evaluate_test_case(cEvalDriverOverrTests, test_case_id,
                                test_session_id, self.batch, ref_intervals,
                                self.get_needed_signals, report=report)
    report = evaluate_test_case(cEvalExitICBTests, test_case_id,
                                test_session_id, self.batch, ref_intervals,
                                self.get_needed_signals, report=report)
    report = evaluate_test_case(cEvalOtherTests, test_case_id,
                                test_session_id, self.batch, ref_intervals,
                                self.get_needed_signals, report=report)
    report = evaluate_test_case(cEvalErrorHandlerFunc, test_case_id,
                                test_session_id, self.batch, ref_intervals,
                                self.get_needed_signals, report=report)
    report = evaluate_test_case(cEvalErrorHandlerInterface, test_case_id,
                                test_session_id, self.batch, ref_intervals,
                                self.get_needed_signals, report=report)
    if report is not None:
      self.batch.add_entry(report)
    return
