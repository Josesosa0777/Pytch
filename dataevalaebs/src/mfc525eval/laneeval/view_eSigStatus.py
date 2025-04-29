# -*- dataeval: init -*-

import datavis
from interface import iView

#def_param = interface.NullParam

sgs  = [
  {
    "LD_sSigHeader_eSigStatus": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_sigHeader_eSigStatus"),
    "TPF_sSigHeader_eSigStatus": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas", "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_sSigHeader_eSigStatus"),
  },
]

vehSpdSgs = [
  {
  "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
  },
  {
  "FrontAxleSpeed": ("EBC2", "FrontAxleSpeed_s0B"),
  },
  {
  "FrontAxleSpeed": ("EBC2_s0B", "FrontAxleSpeed"),
  },
  {
  "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                           "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
  },
]

class View(iView):

  def check(self):
    # select signals
    group = self.source.selectLazySignalGroup(sgs)
    veh_grp= self.source.selectLazySignalGroup(vehSpdSgs)
    if veh_grp.has_key('FrontAxleSpeed'):
      group["FrontAxleSpeed"] = veh_grp["FrontAxleSpeed"]
    # give warning for not available signals
    for alias in sgs[0]:
      if alias not in group:
        self.logger.warning("Signal for '%s' not available" % alias)
    for alias in vehSpdSgs[0]:
      if alias not in group:
        self.logger.warning("Signal for '%s' not available" % alias)
    return group

  def view(self, group):
    pn = datavis.cPlotNavigator(title="sSigHeader_eSigStatus")
    mapping_eSig = {0: 'AL_SIG_STATE_INIT', 1: 'AL_SIG_STATE_OK', 2: 'AL_SIG_STATE_INVALID'}

    if "LD_sSigHeader_eSigStatus" in group:
      axis00 = pn.addAxis(ylabel='LD_sSigHeader_eSigStatus',yticks=mapping_eSig,
                          ylim=(min(mapping_eSig) - 0.5, max(mapping_eSig) + 0.5))
      time_LD_sSigHeader, value_LD_sSigHeader, unit_LD_sSigHeader = group.get_signal_with_unit("LD_sSigHeader_eSigStatus")
      pn.addSignal2Axis(axis00, "LD_sSigHeader_eSigStatus", time_LD_sSigHeader, value_LD_sSigHeader, unit=unit_LD_sSigHeader)

    if "TPF_sSigHeader_eSigStatus" in group:
      axis01 = pn.addAxis(ylabel='TPF_sSigHeader_eSigStatus',yticks=mapping_eSig,
                          ylim=(min(mapping_eSig) - 0.5, max(mapping_eSig) + 0.5))
      time_TPF_sSigHeader, value_TPF_sSigHeader, unit_TPF_sSigHeader = group.get_signal_with_unit("TPF_sSigHeader_eSigStatus")
      pn.addSignal2Axis(axis01, "TPF_sSigHeader_eSigStatus", time_TPF_sSigHeader, value_TPF_sSigHeader,
                        unit=unit_TPF_sSigHeader)

    if "FrontAxleSpeed" in group:
      axis03 = pn.addAxis(ylabel='FrontAxleSpeed')
      time_FrontAxleSpeed, value_FrontAxleSpeed, unit_FrontAxleSpeed = group.get_signal_with_unit("FrontAxleSpeed")
      pn.addSignal2Axis(axis03, "FrontAxleSpeed", time_FrontAxleSpeed, value_FrontAxleSpeed, unit=unit_FrontAxleSpeed)

    self.sync.addClient(pn)
    return
