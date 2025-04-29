# -*- dataeval: init -*-

from aebs_c import dpvs
import calc_aebs_c_sil_versions_inp_resim

init_params = calc_aebs_c_sil_versions_inp_resim.init_params

class Calc(calc_aebs_c_sil_versions_inp_resim.Calc):
  def check(self):
    # validate necessary signals
    sg = { name : ('CCP', 'kbaebsInaebs.%s'  %name) for name in self.dll.kbaebsInputSt_t_dtype.names if name is not 'TORSitSubjective_b' } # TOR removed in 7.0
    group = self.source.selectSignalGroup( [sg] )
    time = group.get_time('dxv')
    # fill inputs
    inp = {}
    for name in group:
      value = group.get_value(name)
      if name in self.dll.kbaebsInputSt_t_norms:
        value = self.dll.FixedPointArray(value, name).float_value
      inp[name] = value
    if 'TORSitSubjective_b' in self.dll.kbaebsInputSt_t_dtype.names:
      inp['TORSitSubjective_b'] = 0
    # fill params
    par = dpvs.get_dpv(self.dpv)
    return time, inp, par
