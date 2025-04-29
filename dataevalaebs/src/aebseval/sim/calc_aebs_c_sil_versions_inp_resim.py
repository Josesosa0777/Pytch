# -*- dataeval: init -*-
import os
import imp

from interface import iCalc
from aebs_c import dpvs, AEBS_C_wrapper

init_params = dict(
  AEBS_C_6_1__DEV_GENERAL_8_17_BRAKING = dict(dll='AEBS_C_6_1', dpv='DEV_GENERAL_8.17_BRAKING.DPV'),
  AEBS_C_7_0__DEV_GENERAL_8_17_BRAKING = dict(dll='AEBS_C_7_0', dpv='DEV_GENERAL_8.17_BRAKING.DPV'),
  AEBS_C_7_1__DEV_GENERAL_8_17_BRAKING = dict(dll='AEBS_C_7_1', dpv='DEV_GENERAL_8.17_BRAKING.DPV'),
)

class Calc(iCalc):
  def init(self, dll, dpv):
    self.dll = imp.load_dynamic(dll, os.path.join(os.path.dirname(AEBS_C_wrapper.__file__), dll+'.pyd'))
    self.dpv = dpv
    return

  def check(self):
    # validate necessary signals
    sg = {name : ("kbaebsInput", name) for name in self.dll.kbaebsInputSt_t_dtype.names}
    group = self.source.selectSignalGroup( [sg] )
    # fill inputs
    time = group.get_time("dxv")
    inp = {name : group.get_value(name) for name in group}
    ### Ebc2_cycle_time_apv misconfig patch (50ms instead of 100ms)
    # inp["aRef"] = inp["aRef"]/2.
    # inp["axv"] = inp["aRef"] + inp["axv"]
    ###
    # patch missing signals
    par = dpvs.get_dpv(self.dpv)
    return time, inp, par

  def fill(self, time, inp, par):
    out_sim, internals = self.dll.AEBSproc_float(time, inp, par, typecheck=False)
    return time, inp, par, out_sim, internals
