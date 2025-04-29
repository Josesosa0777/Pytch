# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis

sgs = [
    {

        "FLI2_StateOfLDWS": ("CAN_MFC_Public_FLI2_E8","FLI2_LDWSState_E8"),

        "LaneDepartureLeft": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_left"),
        "LaneDepartureRight": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_right"),

        "FLI2_LeftWhlLaneDepDistance": ("CAN_MFC_Public_FLI2_E8","FLI2_LeftWhlLaneDepDistance_E8"),
        "FLI2_RightWhlLaneDepDistance": ("CAN_MFC_Public_FLI2_E8","FLI2_RightWhlLaneDepDistance_E8"),

        "FrontAxleSpeed": ("CAN_MFC_Public_EBC2_0B","EBC2_FrontAxleSpeed_0B"),
        "Flc25_LkInput": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_vy_lane"),

    },
    {
        "FLI2_StateOfLDWS": ("FLI2_E8", "FLI2_LDWSState_E8_sE8"),
        "LaneDepartureLeft": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_left"),
        "LaneDepartureRight": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_right"),
        "FLI2_LeftWhlLaneDepDistance": ("FLI2_E8","FLI2_LeftWhlLaneDepDistance_E8_sE8"),
        "FLI2_RightWhlLaneDepDistance": ("FLI2_E8","FLI2_RightWhlLaneDepDistance_E8_sE8"),
        "FrontAxleSpeed": ("EBC2_0B","EBC2_FrontAxleSpeed_0B_s0B"),
        "Flc25_LkInput": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_vy_lane"),

    },
{
        "FLI2_StateOfLDWS": ("FLI2_E8_CAN20","FLI2_LDWSState_E8_sE8"),
        "LaneDepartureLeft": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_left"),
        "LaneDepartureRight": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_LkOutput_hmi_output_lane_departure_imminent_right"),
        "FLI2_LeftWhlLaneDepDistance": ("FLI2_E8_CAN20","FLI2_LeftWhlLaneDepDistance_E8_sE8"),
        "FLI2_RightWhlLaneDepDistance": ("FLI2_E8_CAN20","FLI2_RightWhlLaneDepDistance_E8_sE8"),
        "FrontAxleSpeed": ("EBC2_0B_CAN20","EBC2_FrontAxleSpeed_0B_s0B"),
        "Flc25_LkInput": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_vy_lane"),

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
        pn = datavis.cPlotNavigator(title="Lane Departure Warning Event")

        ax = pn.addAxis(ylabel="LaneDepartureWarning")
        if 'FLI2_StateOfLDWS' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_StateOfLDWS")
            pn.addSignal2Axis(ax, "LaneDepartureWarning", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Left/RightLaneDepartureWarning")
        if 'LaneDepartureLeft' in group:
            time00, value00, unit00 = group.get_signal_with_unit("LaneDepartureLeft")
            pn.addSignal2Axis(ax, "LaneDepartureLeft", time00, value00, unit=unit00)

        if 'LaneDepartureRight' in group:
            time00, value00, unit00 = group.get_signal_with_unit("LaneDepartureRight")
            pn.addSignal2Axis(ax, "LaneDepartureRight", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="WhlDepartureDistance")
        if 'FLI2_LeftWhlLaneDepDistance' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_LeftWhlLaneDepDistance")
            pn.addSignal2Axis(ax, "LeftWhlLaneDepDistance", time00, value00, unit=unit00)

        if 'FLI2_RightWhlLaneDepDistance' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_RightWhlLaneDepDistance")
            pn.addSignal2Axis(ax, "RightWhlLaneDepDistance", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="FrontAxleSpeed")
        if 'FrontAxleSpeed' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FrontAxleSpeed")
            pn.addSignal2Axis(ax, "FrontAxleSpeed", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Flc25_LkInput")
        if 'Flc25_LkInput' in group:
            time00, value00, unit00 = group.get_signal_with_unit("Flc25_LkInput")
            pn.addSignal2Axis(ax, "Flc25_LkInput", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return
