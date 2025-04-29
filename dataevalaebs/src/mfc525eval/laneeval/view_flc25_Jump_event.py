# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis

sgs = [
    {
        "Lane_Width": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_ego_lane_width"),
        "FrontAxleSpeed": ("CAN_MFC_Public_EBC2_0B","EBC2_FrontAxleSpeed_0B"),
        "LKASState": ("CAN_MFC_Public_ASSC1_E8","ASSC1_LKASystemState_E8"),
        "LDWSState": ("CAN_MFC_Public_FLI2_E8","FLI2_LDWSState_E8"),
    },
    {
        "Lane_Width": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_ego_lane_width"),
        "FrontAxleSpeed": ("CAN_VEHICLE_EBC2_0B","EBC2_FrontAxleSpeed_0B"),
        "LKASState": ("CAN_VEHICLE_ASSC1_E8","ASSC1_LKASystemState_E8"),
        "LDWSState": ("CAN_VEHICLE_FLI2_E8","FLI2_LDWSState_E8"),
    },
    {
        "Lane_Width": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_ego_lane_width"),
        "FrontAxleSpeed": ("CAN_MFC_ARS_EBC2_0B","EBC2_FrontAxleSpeed_0B"),
        "LKASState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_ASSC1_lane_keeping_assist_system_state"),
        "LDWSState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI2_lane_departure_warning_system_state"),
    },

]


class View(interface.iView):
    def check(self):
        group = self.source.selectLazySignalGroup(sgs)
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="Lane Width Jump Event")

        ax = pn.addAxis(ylabel="Lane Width Jump Event")
        if 'Lane_Width' in group:
            time00, value00, unit00 = group.get_signal_with_unit("Lane_Width")
            pn.addSignal2Axis(ax, "Lane_Width", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="FrontAxleSpeed")
        if 'FrontAxleSpeed' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FrontAxleSpeed")
            pn.addSignal2Axis(ax, "FrontAxleSpeed", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="LDW & LKA State")
        if 'LDWSState' in group:
            time00, value00, unit00 = group.get_signal_with_unit("LDWSState")
            pn.addSignal2Axis(ax, "LDWSState", time00, value00, unit=unit00)

        if 'LKASState' in group:
            time00, value00, unit00 = group.get_signal_with_unit("LKASState")
            pn.addSignal2Axis(ax, "LKASState", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return
