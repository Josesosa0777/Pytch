# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView

sgs = [
            {
            "ldws_system_state": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI2_lane_departure_warning_system_state"),
            "hmi_output_lka_system_state": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_keeping_assist_system_state"),
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
  "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
  },
]
class View(iView):
    def check(self):
        group = self.source.selectSignalGroupOrEmpty(sgs)
        veh_grp = self.source.selectLazySignalGroup(vehSpdSgs)

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

    def view(self,  group):
        pn = datavis.cPlotNavigator(title="LDW-State + LK-State")
        if "ldws_system_state" in group:
            axis00 = pn.addAxis(ylabel='ldws_system_state')
            time_ldws_system_state, value_ldws_system_state, unit_ldws_system_state = group.get_signal_with_unit("ldws_system_state")
            pn.addSignal2Axis(axis00, "ldws_system_state", time_ldws_system_state, value_ldws_system_state, unit=unit_ldws_system_state)

        if "hmi_output_lka_system_state" in group:
            axis01 = pn.addAxis(ylabel='lka_system_state')
            time_hmi_output_lka_system_state, value_hmi_output_lka_system_state, unit_hmi_output_lka_system_state = group.get_signal_with_unit(
                "hmi_output_lka_system_state")
            pn.addSignal2Axis(axis01, "hmi_output_lka_system_state", time_hmi_output_lka_system_state, value_hmi_output_lka_system_state,
                              unit=unit_hmi_output_lka_system_state)
        if "FrontAxleSpeed" in group:
            axis03 = pn.addAxis(ylabel='FrontAxleSpeed')
            time_FrontAxleSpeed, value_FrontAxleSpeed, unit_FrontAxleSpeed = group.get_signal_with_unit(
                "FrontAxleSpeed")
            pn.addSignal2Axis(axis03, "FrontAxleSpeed", time_FrontAxleSpeed, value_FrontAxleSpeed,
                              unit=unit_FrontAxleSpeed)

        self.sync.addClient(pn)
        return
