# -*- dataeval: init -*-

from interface import iCalc
from aebs_c import dpvs, AEBS_C_wrapper

# DPV file names (e.g. 'DEV_FORD_AREL_5.2_NON-BRAKING.DPV')
init_params = { k : dict(dpv=k) for k in dpvs._dpvs }

class Calc(iCalc):
  def init(self, dpv):
    self.dpv = dpv
    self.sg = {name: ("kbaebsInput", name) for name in AEBS_C_wrapper.kbaebsInputSt_t_dtype.names}
    return

  def check(self):
    # validate necessary signals
    group = self.source.selectSignalGroup([self.sg])
    # fill inputs
    time = group.get_time("dxv")
    inp = {name : group.get_value(name) for name in group}
    # patch missing signals
    par = dpvs.get_dpv(self.dpv)
    return time, inp, par

  def fill(self, time, inp, par):
    out_sim, internals = AEBS_C_wrapper.AEBSproc_float(time, inp, par, typecheck=False)
    return time, inp, par, out_sim, internals
