# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    dep = ('calc_common_time-flc25@aebs.fill',)

    def check(self):
        sgs = [
            {
                "right_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
                "C0_Right_A": ("Video_Lane_Right_A", "C0_Right_A"),
                "right_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                       "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_quality"),
                "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_splitOrExitEvent_available": ("MFC5xx Device.LD.LdOutput",
                            "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_splitOrExitEvent_available"),
                "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_mergeOrEntryEvent_available": ("MFC5xx Device.LD.LdOutput",
                            "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_mergeOrEntryEvent_available"),
                "MFC5xx_Device_LD_LdOutput_road_ego_right_lineEvent_event": ("MFC5xx Device.LD.LdOutput",
                            "MFC5xx_Device_LD_LdOutput_road_ego_right_lineEvent_event"),
                "LaneInfo_RH_B_Quality_A0_sA0": ("LaneInfo_RH_B_A0", "LaneInfo_RH_B_Quality_A0_sA0"),
            },
        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)

        modules = self.get_modules()
        commonTime = modules.fill('calc_common_time-flc25@aebs.fill')
        return group, commonTime

    def view(self, group, commonTime):
        pn = datavis.cPlotNavigator(title="Compare Right Lane C0 FLC25vsMFC525")
        rescale_kwargs = {'ScaleTime': commonTime}

        ax = pn.addAxis(ylabel="Compare right C0")
        if 'right_lane_marking_c0' in group:
            time_right_lane_marking_c0, value_right_lane_marking_c0, unit_right_lane_marking_c0 = group.get_signal_with_unit("right_lane_marking_c0")
            pn.addSignal2Axis(ax, "right lane marking c0", time_right_lane_marking_c0, value_right_lane_marking_c0, unit=unit_right_lane_marking_c0)

        if 'C0_Right_A' in group:
            time_C0_Right_A, value_C0_Right_A, unit_C0_Right_A = group.get_signal_with_unit("C0_Right_A")
            pn.addSignal2Axis(ax, "C0_Right_A", time_C0_Right_A, value_C0_Right_A, unit=unit_C0_Right_A)

        ax = pn.addAxis(ylabel="C0 Right Diff", ylim=(-0.5, 0.5))
        if 'C0_Right_A' in group:
            time_C0_Right_A, value_C0_Right_A, unit_C0_Right_A = group.get_signal_with_unit("C0_Right_A", **rescale_kwargs)
            if 'right_lane_marking_c0' in group:
                right_lane_time, right_lane_value, right_lane_unit = group.get_signal_with_unit("right_lane_marking_c0",
                                                                                            **rescale_kwargs)
                difference_plot = value_C0_Right_A + right_lane_value
                pn.addSignal2Axis(ax, "C0_Right_Diff.", commonTime, difference_plot, unit=right_lane_unit)

        ax = pn.addAxis(ylabel="Right Lane Quality")
        if 'right_lane_quality' in group:
            time_right_lane_quality, value_right_lane_quality, unit_right_lane_quality = group.get_signal_with_unit("right_lane_quality")
            pn.addSignal2Axis(ax, "right lane quality", time_right_lane_quality, value_right_lane_quality, unit=unit_right_lane_quality)

        if 'LaneInfo_RH_B_Quality_A0_sA0' in group:
            time_LaneInfo_RH_B_Quality, value_LaneInfo_RH_B_Quality, unit_LaneInfo_RH_B_Quality = group.get_signal_with_unit("LaneInfo_RH_B_Quality_A0_sA0")
            pn.addSignal2Axis(ax, "LaneInfo_RH", time_LaneInfo_RH_B_Quality, value_LaneInfo_RH_B_Quality, unit=unit_LaneInfo_RH_B_Quality)

        ax = pn.addAxis(ylabel=" ")
        if 'MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_splitOrExitEvent_available' in group:
            time00, value00, unit00 = group.get_signal_with_unit(
                "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_splitOrExitEvent_available")
            pn.addSignal2Axis(ax, "exit_&_stop", time00, value00, unit=unit00)
        # ax = pn.addAxis(ylabel="Entries&Stop")
        if 'MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_mergeOrEntryEvent_available' in group:
            time00, value00, unit00 = group.get_signal_with_unit(
                "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_mergeOrEntryEvent_available")
            pn.addSignal2Axis(ax, "entries_&_stop", time00, value00, unit=unit00)
        # ax = pn.addAxis(ylabel="Track_Scene&Stop")
        if 'MFC5xx_Device_LD_LdOutput_road_ego_right_lineEvent_event' in group:
            time00, value00, unit00 = group.get_signal_with_unit(
                "MFC5xx_Device_LD_LdOutput_road_ego_right_lineEvent_event")
            pn.addSignal2Axis(ax, "Unsual_Scene_&_Stop", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return

