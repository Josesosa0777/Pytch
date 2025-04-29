# -*- dataeval: init -*-

from aebs_c import dpvs
import calc_aebs_c_sil_versions_inp_resim

init_params = calc_aebs_c_sil_versions_inp_resim.init_params


class Calc(calc_aebs_c_sil_versions_inp_resim.Calc):
  def check(self):
    # validate necessary signals
    sg = {name: ("sil", "kbaebsInput_" + name) for name in self.dll.kbaebsInputSt_t_dtype.names if
                                                   name is not "dt" and name is not "TORSitSubjective_b"}
    sg["dt"] = ("sil", "dt")
    sg["t"] = ("sil", "t")

    group = self.source.selectSignalGroup( [sg] )
    time = group.get_time('dt')
    # fill inputs
    inp = {name: group.get_value(name) for name in group}
    if 'TORSitSubjective_b' in self.dll.kbaebsInputSt_t_dtype.names:
      inp['TORSitSubjective_b'] = 0
    # fill params
    par = dpvs.get_dpv(self.dpv)
    return time, inp, par
