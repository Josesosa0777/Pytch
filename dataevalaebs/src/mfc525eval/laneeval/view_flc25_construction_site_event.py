# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis

sgs = [
    {
        "constructionZoneDetected": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_construction_zone_detected"),
        "constructionSiteEventAvailable": (
            "MFC5xx Device.LD.LdOutput",
            "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_constructionSiteEvent_available"),
        "FrontAxleSpeed": ("EBC2", "FrontAxleSpeed_s0B"),
        "TunnelState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sHLA_HeadLightControlRed_Common_TunnelState"),
        "ASSC1_LKASystemState": ("CAN_VEHICLE_ASSC1_E8","ASSC1_LKASystemState_E8"),

    },
    {
        "constructionZoneDetected": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_construction_zone_detected"),
        "constructionSiteEventAvailable": (
            "MFC5xx Device.LD.LdOutput",
            "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_constructionSiteEvent_available"),
        "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
        "TunnelState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sHLA_HeadLightControlRed_Common_TunnelState"),
        "ASSC1_LKASystemState": ("CAN_VEHICLE_ASSC1_E8","ASSC1_LKASystemState_E8"),

    },
    {
        "constructionZoneDetected": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_construction_zone_detected"),
        "constructionSiteEventAvailable": (
            "MFC5xx Device.LD.LdOutput",
            "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_constructionSiteEvent_available"),
        "FrontAxleSpeed": ("CAN_VEHICLE_EBC2_0B","EBC2_FrontAxleSpeed_0B"),
        "TunnelState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sHLA_HeadLightControlRed_Common_TunnelState"),
        "ASSC1_LKASystemState": ("CAN_VEHICLE_ASSC1_E8","ASSC1_LKASystemState_E8"),

    },
    {
        "constructionZoneDetected": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.construction_zone_detected"),
        "constructionSiteEventAvailable": ("MFC5xx Device.LD.LdOutput","MFC5xx Device.LD.LdOutput.road.ego.laneEvents.constructionSiteEvent.available"),
        "FrontAxleSpeed": ("CAN_VEHICLE_EBC2_0B","EBC2_FrontAxleSpeed_0B"),
        "TunnelState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sHLA_HeadLightControlRed_Common_TunnelState"),
        "ASSC1_LKASystemState": ("CAN_VEHICLE_ASSC1_E8","ASSC1_LKASystemState_E8"),
    },
    {
        "constructionZoneDetected": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_AoaOutput.im_input_sensor.construction_zone_detected"),
        "constructionSiteEventAvailable": ("MFC5xx Device.LD.LdOutput","MFC5xx Device.LD.LdOutput.road.ego.laneEvents.constructionSiteEvent.available"),
        "FrontAxleSpeed": ("CAN_VEHICLE_EBC2_0B","EBC2_FrontAxleSpeed_0B"),
        "TunnelState": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sHLA_HeadLightControlRed.Common.TunnelState"),
        "ASSC1_LKASystemState": ("CAN_VEHICLE_ASSC1_E8","ASSC1_LKASystemState_E8"),
    }
]


class View(interface.iView):
    def check(self):
        group = self.source.selectLazySignalGroup(sgs)
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="Construction Site Event")

        ax = pn.addAxis(ylabel="constructionSiteEvent")
        if 'constructionSiteEventAvailable' in group:
            time00, value00, unit00 = group.get_signal_with_unit("constructionSiteEventAvailable")
            pn.addSignal2Axis(ax, "constructionSiteEventAvailable", time00, value00, unit=unit00)

        if 'constructionZoneDetected' in group:
            time00, value00, unit00 = group.get_signal_with_unit("constructionZoneDetected")
            pn.addSignal2Axis(ax, "constructionZoneDetected", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="FrontAxleSpeed")
        if 'FrontAxleSpeed' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FrontAxleSpeed")
            pn.addSignal2Axis(ax, "FrontAxleSpeed", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="TunnelState")
        if 'TunnelState' in group:
            time00, value00, unit00 = group.get_signal_with_unit("TunnelState")
            pn.addSignal2Axis(ax, "TunnelState", time00, value00, unit=unit00)

        if 'ASSC1_LKASystemState' in group:
            time00, value00, unit00 = group.get_signal_with_unit("ASSC1_LKASystemState")
            pn.addSignal2Axis(ax, "ASSC1_LKASystemState", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return
