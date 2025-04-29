# -*- dataeval: init -*-

from interface import iCalc

from aebseval.sim.view_driveract_aebsout_sim import shorten_dpv

init_params = dict(
  AEBS_C_7_0_vs_7_1__DEV_GENERAL_8_17_BRAKING= dict(dll_old='AEBS_C_7_0', dll_new = 'AEBS_C_7_1', dpv = 'DEV_GENERAL_8.17_BRAKING.DPV'),
  AEBS_C_6_1_vs_7_0__DEV_GENERAL_8_17_BRAKING = dict(dll_old='AEBS_C_6_1', dll_new = 'AEBS_C_7_0', dpv = 'DEV_GENERAL_8.17_BRAKING.DPV'),
  AEBS_C_6_1_vs_7_0__DEV_FORD_7_11_BRAKING = dict(dll_old='AEBS_C_6_1', dll_new = 'AEBS_C_7_0', dpv = 'DEV_FORD_7.11_BRAKING.DPV'),
)

class Calc(iCalc):
  def init(self, dll_old, dll_new, dpv):
    self.dep = {
      'calc_arbitration_old': 'calc_aebs_c_sil_versions_inp_arb-%s__%s@aebseval.sim' %(dll_old, 'DEV_'+shorten_dpv(dpv).replace('.', '_')),
      'calc_arbitration_new': 'calc_aebs_c_sil_versions_inp_arb-%s__%s@aebseval.sim' %(dll_new, 'DEV_'+shorten_dpv(dpv).replace('.', '_')),
    }
    return

  def check(self):
    t, inp_old, par, out_sim_old, internals_old, source_type_old = self.modules.fill(self.dep['calc_arbitration_old'])
    _, inp_new, ___, out_sim_new, internals_new, source_type_new = self.modules.fill(self.dep['calc_arbitration_new'])
    assert source_type_new == source_type_old, "Inconsistent input source types, old: %s new: %s" % (source_type_old,
                                                                                                     source_type_new)
    return t, inp_new, par, out_sim_old, out_sim_new, internals_old, internals_new, source_type_old
