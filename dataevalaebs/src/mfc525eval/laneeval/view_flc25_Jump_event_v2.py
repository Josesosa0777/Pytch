# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis

sgs = [
    {
        "left_lane_marking_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
        "left_lane_marking_type": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_type"),
        "right_lane_marking_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
        "right_lane_marking_type": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_type"),
        # "ASSC1_LKAStatusLeftSide": ("CAN_VEHICLE_ASSC1_E8","ASSC1_LKAStatusLeftSide_E8"),
        # "ASSC1_LKAStatusRightSide": ("CAN_VEHICLE_ASSC1_E8","ASSC1_LKAStatusRightSide_E8"),
        "FLI2_LeftWhlLaneDepDistance": ("CAN_VEHICLE_FLI2_E8","FLI2_LeftWhlLaneDepDistance_E8"),
        "FLI2_RightWhlLaneDepDistance": ("CAN_VEHICLE_FLI2_E8","FLI2_RightWhlLaneDepDistance_E8"),
        # "EPSI1_SteeringAngleReq_E8": ("CAN_MFC_Public_EPSI1_E8","EPSI1_SteeringAngleReq_E8"),
#        "EPSO1_SteeringAngle_13": ("CAN_MFC_Public_EPSO1_13","EPSO1_SteeringAngle_13"),
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

        ax = pn.addAxis(ylabel="Lane Quality")
        if 'left_lane_marking_quality' in group:
            time00, value00, unit00 = group.get_signal_with_unit("left_lane_marking_quality")
            pn.addSignal2Axis(ax, "left_lane_marking_quality", time00, value00, unit=unit00)

        if 'right_lane_marking_quality' in group:
            time00, value00, unit00 = group.get_signal_with_unit("right_lane_marking_quality")
            pn.addSignal2Axis(ax, "right_lane_marking_quality", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="WhlLaneDepDis")
        if 'FLI2_LeftWhlLaneDepDistance' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_LeftWhlLaneDepDistance")
            pn.addSignal2Axis(ax, "FLI2_LeftWhlLaneDepDistance", time00, value00, unit=unit00)

        if 'FLI2_RightWhlLaneDepDistance' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_RightWhlLaneDepDistance")
            pn.addSignal2Axis(ax, "FLI2_RightWhlLaneDepDistance", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Lane Type")
        if 'left_lane_marking_type' in group:
            time00, value00, unit00 = group.get_signal_with_unit("left_lane_marking_type")
            pn.addSignal2Axis(ax, "left_lane_marking_type", time00, value00, unit=unit00)

        if 'right_lane_marking_type' in group:
            time00, value00, unit00 = group.get_signal_with_unit("right_lane_marking_type")
            pn.addSignal2Axis(ax, "right_lane_marking_type", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return
