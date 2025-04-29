# -*- dataeval: init -*-


import calc_aebs_c_sil
from aebs_c import AEBS_C_wrapper

# DPV file names (e.g. 'DEV_FORD_AREL_5.2_NON-BRAKING.DPV')
init_params = calc_aebs_c_sil.init_params


class Calc(calc_aebs_c_sil.Calc):
  def init(self, dpv):
    self.dpv = dpv
    self.sg = {name: ("sil", "kbaebsInput_" + name) for name in AEBS_C_wrapper.kbaebsInputSt_t_dtype.names if
          name is not "dt"}
    self.sg["dt"] = ("sil", "dt")
    self.sg["t"] = ("sil", "t")
    return
