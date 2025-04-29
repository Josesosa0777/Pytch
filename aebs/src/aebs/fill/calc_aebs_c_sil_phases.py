# -*- dataeval: init -*-

import calc_flr20_aebs_phases

import calc_aebs_c_sil

init_params = calc_aebs_c_sil.init_params

class Calc(calc_flr20_aebs_phases.Calc):
  def init(self, dpv):
    self.dep = {
      'aebs_sim': 'calc_aebs_c_sil-%s@aebs.fill' %dpv,
    }
    return

  def check(self):
    time, inp, par, out_sim = self.modules.fill(self.dep['aebs_sim'])
    # get necessary output signals
    status = out_sim['AEBS1_SystemState']
    level  = out_sim['AEBS1_WarningLevel']
    return time, status, level
