# -*- dataeval: init -*-

from collections import OrderedDict
import calc_aebs_c_sil_versions_inp_resim
from interface import iCalc
from aebseval.sim.view_driveract_aebsout_sim import shorten_dpv


init_params = calc_aebs_c_sil_versions_inp_resim.init_params

class Calc(iCalc):
  def init(self, dll, dpv):
    self.optdep = OrderedDict([
      # assumptions: CCP data gives more accurate resimulation, therefore preferred over preprocessed CAN data
      ('aebs_c_sil_ccp',
       'calc_aebs_c_sil_versions_inp_ccp-%s__%s@aebseval.sim' % (dll, 'DEV_' + shorten_dpv(dpv).replace('.', '_'))),
      ('aebs_c_sil_resim',
       'calc_aebs_c_sil_versions_inp_resim-%s__%s@aebseval.sim' % (dll, 'DEV_' + shorten_dpv(dpv).replace('.', '_'))),
      ('aebs_c_sil_mbt',
       'calc_aebs_c_sil_versions_inp_mbt-%s__%s@aebseval.sim' % (dll, 'DEV_' + shorten_dpv(dpv).replace('.', '_'))),
    ]
    )
    return

  def check(self):
    # if certain kind of data is available, it should fulfill required inputs
    assert len(self.passed_optdep) > 0, 'AEBS_C input data not available (neither CCP nor preprocessed CAN, nor MBT)'
    return

  def fill(self):
    time, inp, par, out_sim, internals = self.modules.fill(self.passed_optdep[0])
    source_type = "CCP" if "ccp" in self.passed_optdep[0] else "CAN" if "resim" in self.passed_optdep[0] else "MBT"
    return time, inp, par, out_sim, internals, source_type
