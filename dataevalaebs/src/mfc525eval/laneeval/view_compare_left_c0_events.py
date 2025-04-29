# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


class View(iView):
    dep = ('calc_common_time-flc25@aebs.fill',)

    def check(self):
        sgs = [
            {
                "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
                "C0_Left_A": ("Video_Lane_Left_A", "C0_Left_A"),
                "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
                "left_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
                "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_splitOrExitEvent_available": ("MFC5xx Device.LD.LdOutput",
                    "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_splitOrExitEvent_available"),
                "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_mergeOrEntryEvent_available": ("MFC5xx Device.LD.LdOutput",
                    "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_mergeOrEntryEvent_available"),
                "MFC5xx_Device_LD_LdOutput_road_ego_right_lineEvent_event": ("MFC5xx Device.LD.LdOutput",
                    "MFC5xx_Device_LD_LdOutput_road_ego_right_lineEvent_event"),
                "LaneInfo_LH_B_Quality_A0_sA0": ("LaneInfo_LH_B_A0", "LaneInfo_LH_B_Quality_A0_sA0"),
            },
            {
                "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
                "C0_Left_A": ("Video_Lane_Left_A", "C0_Left_A"),
                "FrontAxleSpeed": ("EBC2", "FrontAxleSpeed_s0B"),
                "left_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
                "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_splitOrExitEvent_available": ("MFC5xx Device.LD.LdOutput",
                    "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_splitOrExitEvent_available"),
                "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_mergeOrEntryEvent_available": ("MFC5xx Device.LD.LdOutput",
                    "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_mergeOrEntryEvent_available"),
                "MFC5xx_Device_LD_LdOutput_road_ego_right_lineEvent_event": ("MFC5xx Device.LD.LdOutput",
                    "MFC5xx_Device_LD_LdOutput_road_ego_right_lineEvent_event"),
                "LaneInfo_LH_B_Quality_A0_sA0": ("LaneInfo_LH_B_A0", "LaneInfo_LH_B_Quality_A0_sA0"),

            },
            {
                "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
                "C0_Left_A": ("Video_Lane_Left_A", "C0_Left_A"),
                "FrontAxleSpeed": ("EBC2_s0B", "FrontAxleSpeed"),
                "left_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
                "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_splitOrExitEvent_available": ("MFC5xx Device.LD.LdOutput",
                    "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_splitOrExitEvent_available"),
                "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_mergeOrEntryEvent_available": ("MFC5xx Device.LD.LdOutput",
                    "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_mergeOrEntryEvent_available"),
                "MFC5xx_Device_LD_LdOutput_road_ego_right_lineEvent_event": ("MFC5xx Device.LD.LdOutput",
                    "MFC5xx_Device_LD_LdOutput_road_ego_right_lineEvent_event"),
                "LaneInfo_LH_B_Quality_A0_sA0": ("LaneInfo_LH_B_A0", "LaneInfo_LH_B_Quality_A0_sA0"),

            },
            {
                "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
                "C0_Left_A": ("Video_Lane_Left_A", "C0_Left_A"),
                "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                   "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
                "left_lane_quality": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                      "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_quality"),
                "LaneInfo_LH_B_Quality_A0_sA0": ("LaneInfo_LH_B_A0", "LaneInfo_LH_B_Quality_A0_sA0"),
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
        pn = datavis.cPlotNavigator(title="Compare Left Lane C0 FLC25vsMFC525")
        rescale_kwargs = {'ScaleTime': commonTime}

        ax = pn.addAxis(ylabel="Compare left C0")
        if 'left_lane_marking_c0' in group:
            time_left_lane_marking_c0, value_left_lane_marking_c0, unit_left_lane_marking_c0 = group.get_signal_with_unit(
                "left_lane_marking_c0")
            pn.addSignal2Axis(ax, "left lane marking c0", time_left_lane_marking_c0, value_left_lane_marking_c0,
                              unit=unit_left_lane_marking_c0)

        if 'C0_Left_A' in group:
            time_C0_Left_A, value_C0_Left_A, unit_C0_Left_A = group.get_signal_with_unit("C0_Left_A")
            pn.addSignal2Axis(ax, "C0_Left_A", time_C0_Left_A, value_C0_Left_A, unit=unit_C0_Left_A)

        ax = pn.addAxis(ylabel="C0 Diff", ylim=(-0.5, 0.5))
        if 'C0_Left_A' in group:
            time_C0_Left_A, value_C0_Left_A, unit_C0_Left_A = group.get_signal_with_unit("C0_Left_A", **rescale_kwargs)
            if 'left_lane_marking_c0' in group:
                left_lane_time, left_lane_value, left_lane_unit = group.get_signal_with_unit("left_lane_marking_c0",
                                                                                             **rescale_kwargs)
                difference_plot = value_C0_Left_A + left_lane_value
                pn.addSignal2Axis(ax, "C0_Left_Diff.", commonTime, difference_plot, unit=left_lane_unit)

        ax = pn.addAxis(ylabel="Lane Quality")
        if 'left_lane_quality' in group:
            time_left_lane_quality, value_left_lane_quality, unit_left_lane_quality = group.get_signal_with_unit(
                "left_lane_quality")
            pn.addSignal2Axis(ax, "left lane quality", time_left_lane_quality, value_left_lane_quality,
                              unit=unit_left_lane_quality)

        if 'LaneInfo_LH_B_Quality_A0_sA0' in group:
            time_LaneInfo_LH_B_Quality, value_LaneInfo_LH_B_Quality, unit_LaneInfo_LH_B_Quality = group.get_signal_with_unit(
                "LaneInfo_LH_B_Quality_A0_sA0")
            pn.addSignal2Axis(ax, "LaneInfo_LH", time_LaneInfo_LH_B_Quality, value_LaneInfo_LH_B_Quality,
                              unit=unit_LaneInfo_LH_B_Quality)

        ax = pn.addAxis(ylabel="Ego Speed")
        if 'FrontAxleSpeed' in group:
            time_ego_speed, value_ego_speed, unit_ego_speed = group.get_signal_with_unit("FrontAxleSpeed")
            pn.addSignal2Axis(ax, "Ego Speed", time_ego_speed, value_ego_speed, unit=unit_ego_speed)

        self.sync.addClient(pn)
        return
