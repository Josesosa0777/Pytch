# -*- dataeval: init -*-

from aebs.fill import calc_flr20_aebs_phases
import calc_aebs_c_sil_versions_inp_resim
from aebseval.sim.view_driveract_aebsout_sim import shorten_dpv

init_params = calc_aebs_c_sil_versions_inp_resim.init_params

class Calc(calc_flr20_aebs_phases.Calc):
  def init(self, dll, dpv):
    self.dep = {
      'calc_arbitration': 'calc_aebs_c_sil_versions_inp_arb-%s__%s@aebseval.sim' % (
                                                   dll, 'DEV_' + shorten_dpv(dpv)),
    }
    return

  def check(self):
    time, inp, par, out_sim, internals, source_type = self.modules.fill(self.dep['calc_arbitration'])
    # get necessary output signals
    status = out_sim['AEBS1_SystemState']
    level = out_sim['AEBS1_WarningLevel']
    return time, status, level
