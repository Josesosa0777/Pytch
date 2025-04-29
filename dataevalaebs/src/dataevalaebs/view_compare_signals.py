# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
This script compares signals from original(non-resim) measurement with resimulated measurement
"""

import datavis
from interface import iView
import numpy as np
from bisect import bisect_left, bisect_right
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

aebs = [
    {
        "aebs_source": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_source"),
        "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
    },
    {
        "aebs_source": ("MTSI_stKBFreeze_020ms_t",
                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_source"),
        "FrontAxleSpeed": ("EBC2_0B_s0B", "EBC2_FrontAxleSpeed_0B"),
    },
    {
        "aebs_source": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_source"),
        "FrontAxleSpeed": ("EBC2_0B_CAN20", "EBC2_FrontAxleSpeed_0B_s0B"),
    },
    {
        "aebs_source": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_aebs_object_source"),
        "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                           "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_vehicle_brake_system_front_axle_speed"),
    }
]

acc = [
    {
        "acc_object_dx": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_acc_object_dx"),
        "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
    },
    {
        "acc_object_dx": ("MTSI_stKBFreeze_020ms_t",
                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_acc_object_dx"),
        "FrontAxleSpeed": ("EBC2_0B_s0B", "EBC2_FrontAxleSpeed_0B"),
    },
    {
        "acc_object_dx": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_acc_object_dx"),
        "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                           "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_vehicle_brake_system_front_axle_speed"),
    }
]
ldws_can = [
    {
        "LDWSState": ("CAN1", "FLC25_CANController_CANChannel_FLI2_E8_FLI2_E8_LaneDepartureWarningSystemState"),
        "LeftWhlLaneDepDistance": (
            "CAN1", "FLC25_CANController_CANChannel_FLI2_E8_FLI2_E8_LeftWheelLaneDepartureDistance"),
        "RightWhlLaneDepDistance": (
            "CAN1", "FLC25_CANController_CANChannel_FLI2_E8_FLI2_E8_RightWheelLaneDepartureDistance"),
        "lane_mark_quality_on_the_left_side": (
            "CAN1", "FLC25_CANController_CANChannel_FLI3_E8_FLI3_E8_LaneMarkQualityOnLeft"),
        "lane_mark_quality_on_the_right_side": (
            "CAN1", "FLC25_CANController_CANChannel_FLI3_E8_FLI3_E8_LaneMarkQualityOnRight"),
        "road_curvature_based_on_lane_marks": (
            "CAN1", "FLC25_CANController_CANChannel_FLI3_E8_FLI3_E8_RoadCurvatureBasedOnLaneMarks"),
        "left_lane_marker_type": ("CAN1", "FLC25_CANController_CANChannel_FLI3_E8_FLI3_E8_LeftLaneMarkerType"),
        "right_lane_marker_type": ("CAN1", "FLC25_CANController_CANChannel_FLI3_E8_FLI3_E8_RightLaneMarkerType"),
        "lane_departure_angle_left": ("CAN1", "FLC25_CANController_CANChannel_FLI3_E8_FLI3_E8_LaneDepartureAngleLeft"),
        "lane_departure_angle_right": (
            "CAN1", "FLC25_CANController_CANChannel_FLI3_E8_FLI3_E8_LaneDepartureAngleRight"),
        "left_distance_to_lane_mark_from_vehicles_middle": (
            "CAN1", "FLC25_CANController_CANChannel_FLI3_E8_FLI3_E8_LeftDistanceToLaneMarkFromMiddle"),
        "right_distance_to_lane_mark_from_vehicles_middle": (
            "CAN1", "FLC25_CANController_CANChannel_FLI3_E8_FLI3_E8_RightDistanToLaneMarkFromMiddle"),
        "ConstructionArea": ("CAN2", "FLC25_CANController_CANChannel_GeneralInfo_GeneralInfo_Construction_Area"),

        "FrontAxleSpeed": ("CAN1", "FLC25_CANController_CANChannel_EBC2_0B_EBC2_0B_FrontAxleSpeed"),
    },
    {
        "LDWSState": ("FLI2_E8", "FLI2_LDWSState_E8_sE8"),
        "LeftWhlLaneDepDistance": ("FLI2_E8", "FLI2_LeftWhlLaneDepDistance_E8_sE8"),
        "RightWhlLaneDepDistance": ("FLI2_E8", "FLI2_RightWhlLaneDepDistance_E8_sE8"),
        "lane_mark_quality_on_the_left_side": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI3_lane_mark_quality_on_the_left_side"),
        "lane_mark_quality_on_the_right_side": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI3_lane_mark_quality_on_the_right_side"),
        "road_curvature_based_on_lane_marks": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI3_road_curvature_based_on_lane_marks"),
        "left_lane_marker_type": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI3_left_lane_marker_type"),
        "right_lane_marker_type": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI3_right_lane_marker_type"),
        "lane_departure_angle_left": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI3_lane_departure_angle_left"),
        "lane_departure_angle_right": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI3_lane_departure_angle_right"),
        "left_distance_to_lane_mark_from_vehicles_middle": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI3_left_distance_to_lane_mark_from_vehicles_middle"),
        "right_distance_to_lane_mark_from_vehicles_middle": (
            "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_OmLatControlMessages_FLI3_right_distance_to_lane_mark_from_vehicles_middle"),
        # "ConstructionArea": ("GeneralInfo_CAN21", "GeneralInfo_ConstructionArea_A0_sA0"),
        "FrontAxleSpeed": ("EBC2_0B_CAN20", "EBC2_FrontAxleSpeed_0B_s0B"),
    }
]

ldoutput = [
    {
        "ego_left_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_offset"),
        "ego_left_clothoidNear_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_yawAngle"),
        "ego_left_clothoidNear_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_curvature"),
        "ego_left_clothoidNear_curvatureRate": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_curvatureRate"),
        "ego_right_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_offset"),
        "ego_right_clothoidNear_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_yawAngle"),
        "ego_right_clothoidNear_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_curvature"),
        "ego_right_clothoidNear_curvatureRate": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_curvatureRate"),
        "ego_laneEvents_constructionSiteEvent_available": (
            "MFC5xx Device.LD.LdOutput",
            "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_constructionSiteEvent_available"),

        "FrontAxleSpeed": ("CAN_MFC_Public_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
    },
    {
        "ego_left_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_offset"),
        "ego_left_clothoidNear_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_yawAngle"),
        "ego_left_clothoidNear_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_curvature"),
        "ego_left_clothoidNear_curvatureRate": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_curvatureRate"),
        "ego_right_clothoidNear_offset": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_offset"),
        "ego_right_clothoidNear_yawAngle": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_yawAngle"),
        "ego_right_clothoidNear_curvature": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_curvature"),
        "ego_right_clothoidNear_curvatureRate": (
            "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_curvatureRate"),
        "ego_laneEvents_constructionSiteEvent_available": (
            "MFC5xx Device.LD.LdOutput",
            "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_constructionSiteEvent_available"),

        "FrontAxleSpeed": ("EBC2_0B_CAN20", "EBC2_FrontAxleSpeed_0B_s0B"),
    }
]

# initial parameter definition
init_params = dict(aebs=dict(compare_signals=aebs, compare_plot=1),
                   acc=dict(compare_signals=acc, compare_plot=2),
                   ldws_can=dict(compare_signals=ldws_can, compare_plot=3),
                   ldoutput=dict(compare_signals=ldoutput, compare_plot=4))


class View(iView):
    # define two measurement channel for the script
    channels = 'main', 'resim'

    # the init method gets the selected initial parameters
    def init(self, compare_signals, compare_plot):
        self.compare_signals = compare_signals
        self.compare_plot = compare_plot
        self.complete_signal_dict = {}
        self.signal_dict = {}
        self.signal_dict2 = {}
        self.offset = 0.5
        return

    def check(self):
        compare_group = self.source.selectSignalGroup(self.compare_signals)
        sources = []
        for ch in self.channels[1:]:
            sources.append(self.get_source(ch))
        meas_paths = [self.source.FileName]
        compare_groups = []
        for src in sources:
            meas_paths.append(src.FileName)
            compare_groups.append(src.selectSignalGroup(self.compare_signals))

        return compare_group, compare_groups, meas_paths

    # view method will create the plots
    def view(self, compare_group, compare_groups, meas_paths):

        pn = datavis.cPlotNavigator(title="Compare original(test0) vs resim(test1) measurements")

        if self.compare_plot == 1:
            self.add_compare_plot_min_sample_for('FrontAxleSpeed', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('aebs_source', pn, compare_group, compare_groups)

        if self.compare_plot == 2:
            self.add_compare_plot_min_sample_for('FrontAxleSpeed', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('acc_object_dx', pn, compare_group, compare_groups)

        if self.compare_plot == 3:
            self.add_compare_plot_min_sample_for('FrontAxleSpeed', pn, compare_group, compare_groups)

            self.add_compare_plot_min_sample_for('LDWSState', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('LeftWhlLaneDepDistance', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('RightWhlLaneDepDistance', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('lane_mark_quality_on_the_left_side', pn, compare_group,
                                                 compare_groups)
            self.add_compare_plot_min_sample_for('lane_mark_quality_on_the_right_side', pn, compare_group,
                                                 compare_groups)
            self.add_compare_plot_min_sample_for('road_curvature_based_on_lane_marks', pn, compare_group,
                                                 compare_groups)
            self.add_compare_plot_min_sample_for('left_lane_marker_type', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('right_lane_marker_type', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('lane_departure_angle_left', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('lane_departure_angle_right', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('left_distance_to_lane_mark_from_vehicles_middle', pn, compare_group,
                                                 compare_groups)
            self.add_compare_plot_min_sample_for('right_distance_to_lane_mark_from_vehicles_middle', pn, compare_group,
                                                 compare_groups)
            self.add_compare_plot_min_sample_for('ConstructionArea', pn, compare_group, compare_groups)

        if self.compare_plot == 4:
            self.add_compare_plot_min_sample_for('FrontAxleSpeed', pn, compare_group, compare_groups)

            self.add_compare_plot_min_sample_for('ego_left_clothoidNear_offset', pn, compare_group,
                                                 compare_groups)
            self.add_compare_plot_min_sample_for('ego_left_clothoidNear_yawAngle',
                                                 pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('ego_left_clothoidNear_curvature', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('ego_left_clothoidNear_curvatureRate', pn, compare_group,
                                                 compare_groups)
            self.add_compare_plot_min_sample_for('ego_right_clothoidNear_offset', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('ego_right_clothoidNear_yawAngle', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('ego_right_clothoidNear_curvature', pn, compare_group, compare_groups)
            self.add_compare_plot_min_sample_for('ego_right_clothoidNear_curvatureRate', pn, compare_group,
                                                 compare_groups)
            self.add_compare_plot_min_sample_for('ego_laneEvents_constructionSiteEvent_available', pn, compare_group,
                                                 compare_groups)

        # add the PlotNavigator client to the Synchronizer
        self.sync.addClient(pn)

    # fill method is needed to pass through the signal groups to the view method
    def fill(self, compare_group, compare_groups, meas_paths):
        return compare_group, compare_groups, meas_paths

    def add_compare_plot_min_sample_for(self, signal_group, pn, compare_group, compare_groups):
        offset_value = []
        time = compare_group.get_time(signal_group)
        aebs = compare_group.get_value(signal_group)

        meanspd_orig = compare_group.get_value('FrontAxleSpeed')
        meanspd_resim = compare_groups[0].get_value("FrontAxleSpeed")

        if len(meanspd_orig) > len(meanspd_resim):
            similar_element_index = np.where(meanspd_orig[:len(meanspd_resim)] >= meanspd_resim)[0][0]
            meanspd_orig = meanspd_orig[similar_element_index:]
            common_signal_length = len(meanspd_resim)
        elif len(meanspd_orig) < len(meanspd_resim):
            similar_element_index = np.where(meanspd_orig >= meanspd_resim[:len(meanspd_orig)])[0][0]
            meanspd_orig = meanspd_orig[similar_element_index:]
            common_signal_length = len(meanspd_orig)
        # similar_element_index = 98

        time = time[:common_signal_length]
        aebs = aebs[:common_signal_length]
        min_sample_length = common_signal_length

        ax = pn.addAxis(ylabel='')

        # Condition to check faulty resimulated measurements
        if abs(len(meanspd_orig) - len(meanspd_resim)) < 150:
            signal_lst = [aebs]
            for idx, grp in enumerate(compare_groups):
                signal = grp.get_value(signal_group)
                signal_lst.append(signal)
                if len(signal_lst[0]) != len(signal_lst[1]):
                    min_sample_length = min([len(s) for s in signal_lst])
                    signal_lst[0] = signal_lst[0][0:min_sample_length]
                    signal_lst[1] = signal_lst[1][0:min_sample_length]

            # min_sample_length = min([len(s) for s in signal_lst])

            if signal_group == 'FrontAxleSpeed':
                distance, path = fastdtw(signal_lst[0][0:min_sample_length], signal_lst[1][0:min_sample_length],
                                         dist=euclidean)
                offset = 0
                if np.any(
                        np.where(
                            np.subtract(signal_lst[0][0:min_sample_length], signal_lst[1][0:min_sample_length]) > 0)):
                    for i in range(0, len(path) - 1):
                        nxt = i + 1
                        try:
                            if path[nxt][0] in (0, path[i][0], path[nxt + 1][0]) or path[nxt][1] in (
                                    0, path[i][1], path[nxt + 1][1]):
                                continue
                            elif path[nxt][0] != path[nxt][1]:
                                offset = time[path[nxt][0]] - time[path[nxt][1]]
                                offset_value.append(offset)
                                # break
                        except:
                            pass
                if bool(offset_value):
                    average_offset = np.average(offset_value)
                    max_offset = max(offset_value)
                    if 2 <= (max_offset - average_offset) <= 5:
                        self.offset = max_offset
                    else:
                        self.offset = average_offset
                else:
                    matched_index = min(
                        np.subtract(signal_lst[0][0:min_sample_length], (signal_lst[1][0:min_sample_length])))
                    self.offset = abs(matched_index)
                # print "offset: ", offset_value[0]
                # print 'average offset: ', self.offset
                self.logger.info('Average offset: {}'.format(self.offset))
                pn.addSignal2Axis(ax, signal_group + "_test" + str(0), time[0:min_sample_length],
                                  signal_lst[0][0:min_sample_length])
                pn.addSignal2Axis(ax, signal_group + "_test" + str(1), time[0:min_sample_length] + self.offset,
                                  signal_lst[1][0:min_sample_length])
            else:
                pn.addSignal2Axis(ax, signal_group + "_test" + str(0), time[0:min_sample_length],
                                  signal_lst[0][0:min_sample_length])
                pn.addSignal2Axis(ax, signal_group + "_test" + str(1), time[0:min_sample_length] + self.offset,
                                  signal_lst[1][0:min_sample_length])
        else:
            self.logger.warning(
                "Can not compare signals as length difference of CAN signal is large i.e. meanspd_orig:{} "
                "meanspd_resim:{}".format(len(meanspd_orig), len(meanspd_resim)))
        return

    def add_compare_plot_original_vs_resim(self, signal_group, pn, compare_group, compare_groups):

        time = compare_group.get_time(signal_group)
        aebs = compare_group.get_value(signal_group)
        meanspd_orig = compare_group.get_value("FrontAxleSpeed")
        signal_lst = [meanspd_orig]
        meanspd_orig_time = compare_group.get_time("FrontAxleSpeed")
        meanspd_resim = compare_groups[0].get_value("FrontAxleSpeed")
        signal_lst.append(meanspd_resim)
        min_sample_length = min([len(s) for s in signal_lst])

        # to check if CAN signal is perfectly matching or not
        if not np.any(np.where(np.subtract(meanspd_orig[0:min_sample_length], meanspd_resim[0:min_sample_length]) > 0)):
            can_sig_last_index = len(meanspd_orig) - 10
            can_sig_first_index = 10

            signal_first_index = bisect_left(time, meanspd_orig_time[can_sig_first_index])
            signal_last_index = bisect_right(time, meanspd_orig_time[can_sig_last_index])
            # orig_diff = signal_last_index - signal_first_index

            time = time[signal_first_index:signal_last_index]
            aebs = aebs[signal_first_index:signal_last_index]
            ax = pn.addAxis(ylabel=signal_group)
            pn.addSignal2Axis(ax, signal_group + "_main", time, aebs)

            for idx, grp in enumerate(compare_groups):
                signal = grp.get_value(signal_group)
                signal = signal[signal_first_index:signal_last_index]
                pn.addSignal2Axis(ax, signal_group + "_test" + str(idx), time, signal)

            return
        else:
            mean_value = np.mean(meanspd_orig)
            # print('mean1 ', mean1)
            can_sig_last_index = len(meanspd_orig) - mean_value
            can_sig_first_index = mean_value

            signal_first_index = bisect_left(time, meanspd_orig_time[can_sig_first_index])
            signal_last_index = bisect_right(time, meanspd_orig_time[can_sig_last_index])
            orig_diff = signal_last_index - signal_first_index

            time = time[signal_first_index:signal_last_index]
            aebs = aebs[signal_first_index:signal_last_index]
            ax = pn.addAxis(ylabel=signal_group)
            pn.addSignal2Axis(ax, signal_group + "_main", time, aebs)

            for idx, grp in enumerate(compare_groups):
                signal = grp.get_value(signal_group)
                resim_time = grp.get_time(signal_group)
                mean_spd_time = grp.get_time("FrontAxleSpeed")
                meanspd = grp.get_value("FrontAxleSpeed")

                searchval = meanspd_orig[can_sig_first_index:can_sig_first_index + 10]
                N = len(searchval)
                possibles = np.where(meanspd == searchval[0])[0]
                solns = []
                for p in possibles:
                    check = meanspd[p:p + N]
                    if np.all(check == searchval):
                        solns.append(p)
                resim_time_sync = mean_spd_time[solns[0]]
                resim_first_index = bisect_left(resim_time, resim_time_sync)
                # resim_first_index = int(solns[0] * og_ratio)
                resim_last_index = resim_first_index + orig_diff

                signal = signal[resim_first_index:resim_last_index]
                pn.addSignal2Axis(ax, signal_group + "_test" + str(idx), time, signal)

            return
