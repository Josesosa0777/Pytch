# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis

sgs = [
    {
        "ASSC1_LKAStatusLeftSide": ("CAN_VEHICLE_ASSC1_E8","ASSC1_LKAStatusLeftSide_E8"),
        "ASSC1_LKAStatusRightSide": ("CAN_VEHICLE_ASSC1_E8","ASSC1_LKAStatusRightSide_E8"),
        "FLI2_LeftWhlLaneDepDistance": ("CAN_VEHICLE_FLI2_E8","FLI2_LeftWhlLaneDepDistance_E8"),
        "FLI2_RightWhlLaneDepDistance": ("CAN_VEHICLE_FLI2_E8","FLI2_RightWhlLaneDepDistance_E8"),
        "EPSI1_SteeringAngleReq_E8": ("CAN_MFC_Public_EPSI1_E8","EPSI1_SteeringAngleReq_E8"),
        "EPSO1_SteeringAngle_13": ("CAN_MFC_Public_EPSO1_13","EPSO1_SteeringAngle_13"),

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
        pn = datavis.cPlotNavigator(title="Construction Site Event")

        ax = pn.addAxis(ylabel="LKA Status")
        if 'ASSC1_LKAStatusLeftSide' in group:
            time00, value00, unit00 = group.get_signal_with_unit("ASSC1_LKAStatusLeftSide")
            pn.addSignal2Axis(ax, "ASSC1_LKAStatusLeftSide", time00, value00, unit=unit00)

        if 'ASSC1_LKAStatusRightSide' in group:
            time00, value00, unit00 = group.get_signal_with_unit("ASSC1_LKAStatusRightSide")
            pn.addSignal2Axis(ax, "ASSC1_LKAStatusRightSide", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="WhlLaneDepDis")
        if 'FLI2_LeftWhlLaneDepDistance' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_LeftWhlLaneDepDistance")
            pn.addSignal2Axis(ax, "FLI2_LeftWhlLaneDepDistance", time00, value00, unit=unit00)

        if 'FLI2_RightWhlLaneDepDistance' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_RightWhlLaneDepDistance")
            pn.addSignal2Axis(ax, "FLI2_RightWhlLaneDepDistance", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="SteeringAngle")
        if 'EPSI1_SteeringAngleReq_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("EPSI1_SteeringAngleReq_E8")
            pn.addSignal2Axis(ax, "EPSI1_SteeringAngleReq_E8", time00, value00, unit=unit00)

        if 'EPSO1_SteeringAngle_13' in group:
            time00, value00, unit00 = group.get_signal_with_unit("EPSO1_SteeringAngle_13")
            pn.addSignal2Axis(ax, "EPSO1_SteeringAngle_13", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return
