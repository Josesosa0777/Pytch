# -*- dataeval: init -*-

import numpy as np

from interface import iCalc
from aebs_c import AEBS_C_wrapper

class Calc(iCalc):
  def check(self):
    # validate necessary signals
    sg =       { name : ('CCP', 'kbaebsInaebs.%s'  %name) for name in AEBS_C_wrapper.kbaebsInputSt_t_dtype.names     }
    sg.update( { name : ('CCP', 'kbaebsParaebs.%s' %name) for name in AEBS_C_wrapper.kbaebsParameterSt_t_dtype.names } )
    group = self.source.selectSignalGroup( [sg] )
    time = group.get_time('dxv')
    inp = np.empty(time.size, dtype=AEBS_C_wrapper.kbaebsInputSt_t_dtype)
    par = np.empty(1,         dtype=AEBS_C_wrapper.kbaebsParameterSt_t_dtype)
    # fill inputs
    for name in AEBS_C_wrapper.kbaebsInputSt_t_dtype.names:
      inp[name] = group.get_value(name)
    # fill params
    for name in AEBS_C_wrapper.kbaebsParameterSt_t_dtype.names:
      par[name] = group.get_value(name)[-1]
    return time, inp, par

  def fill(self, time, inp, par):
    out_sim, internals = AEBS_C_wrapper.AEBSproc(inp, par)
    return time, inp, par, out_sim, internals
