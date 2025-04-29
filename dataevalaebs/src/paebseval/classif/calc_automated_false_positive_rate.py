# -*- dataeval: init -*-

import numpy as np
import matplotlib as mpl
import datavis
from interface import iCalc
from measproc.IntervalList import intervalsToMask, maskToIntervals


class Calc(iCalc):

    def init(self):

        self.sgn_group_names = [
            {
                "PAEBS Activation": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_system_state"),
                "Vehicle Deceleration": ("CAN_MFC_Public_VDC2_0B", "VDC2_LongAccel_0B"),
                "TTC_object": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_relevant_object_ttc"),
                "Ego Speed": ("CAN_MFC_Public_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
                "Driver Footbrake": ("CAN_MFC_Public_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),
            },
            {
                "PAEBS Activation": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                "Vehicle Deceleration": ("VDC2", "LongitudinalAcceleration_s3E"),
                "TTC_object": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_ttc"),
                "Ego Speed": ("EBC2", "FrontAxleSpeed_s0B"),
                "Driver Footbrake": ("EBC1", "EBSBrakeSwitch_s0B"),
            },
            {
                "PAEBS Activation": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                "Vehicle Deceleration": ("VDC2_0B", "VDC2_LongAccel_0B_s0B"),
                "TTC_object": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_ttc"),
                "Ego Speed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
                "Driver Footbrake": ("EBC1_0B", "EBC1_EBSBrakeSwitch_0B_s0B"),
            },
            {
                "PAEBS Activation": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                "Vehicle Deceleration": ("CAN_MFC_Public_VDC2_0B", "VDC2_LongAccel_0B"),
                "TTC_object": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_ttc"),
                "Ego Speed": ("CAN_Vehicle_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
                "Driver Footbrake": ("CAN_Vehicle_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),
            },
            {
                "PAEBS Activation": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_system_state"),
                "Vehicle Deceleration": ("CAN_MFC_Public_VDC2_0B", "VDC2_LongAccel_0B"),
                "TTC_object": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_relevant_object_ttc"),
                "Ego Speed": ("CAN_MFC_Public_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
                "Driver Footbrake": ("CAN_MFC_Public_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),
            },
            {
                "PAEBS Activation": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                "Vehicle Deceleration": ("CAN_VEHICLE_VDC2", "LongitudinalAcceleration"),
                "TTC_object": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_ttc"),
                "Ego Speed": ("CAN_VEHICLE_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
                "Driver Footbrake": ("CAN_VEHICLE_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),

            },
            {
                "PAEBS Activation": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                "Vehicle Deceleration": ("CAN_MFC_Public_left_VDC2_0B", "VDC2_LongAccel_0B"),
                "TTC_object": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_ttc"),
                "Ego Speed": ("CAN_VEHICLE_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
                "Driver Footbrake": ("CAN_VEHICLE_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),

            }
        ]

    def check(self):
        A_EGO_ASSUME = 2.0  # m/s^2
        self.group = self.source.selectLazySignalGroup(self.sgn_group_names).items()
        group = self.source.selectSignalGroup(self.sgn_group_names)
        time, activation = group.get_signal('PAEBS Activation')
        deceleration = group.get_value('Vehicle Deceleration', ScaleTime=time)
        ttc_object = group.get_value('TTC_object', ScaleTime=time)
        ttc_calculated = group.get_value('Ego Speed', ScaleTime=time) / A_EGO_ASSUME
        footbrake = group.get_value('Driver Footbrake', ScaleTime=time)
        return time, activation, deceleration, ttc_object, ttc_calculated, footbrake

    def fill(self, time, activation, deceleration, ttc_object, ttc_calculated, footbrake):

        DECELERATION_THRESHOLD = -1.5  # in [m/s^2]
        LATENCY = 1.2  # in [s]
        TTC_MAX = 1.4  # in [s]

        footbrake_bool = np.where(footbrake == 0, False, True)
        deceleration_flag = np.where((deceleration < DECELERATION_THRESHOLD), True, False)
        braking_start_flag = np.where((activation == 6) | (activation == 7), True, False)
        res = deceleration_flag & braking_start_flag

        intervals = maskToIntervals(res)
        intervals_valid = []

        for interval in intervals:
            start, stop = interval
            idx_latency_end = np.argmax(time >= time[start] + LATENCY)
            if (ttc_object[start] > TTC_MAX) or (ttc_calculated[stop] > TTC_MAX) or (
            not any(footbrake_bool[start:idx_latency_end])):
                intervals_valid.append(interval)

        return intervals_valid, time
