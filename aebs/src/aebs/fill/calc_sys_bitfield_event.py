# -*- dataeval: init -*-
import numpy as np

from interface import iCalc

sgs = [
    {
        "AEBS1_AEBSState_2A": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_AEBSState_2A"),

        "FLI2_LDWSState_E8": ("CAN_MFC_Public_FLI2_E8", "FLI2_LDWSState_E8"),

        "DM1_DTC1_E8": ("CAN_MFC_Public_DM1_E8", "DM1_DTC1_E8"),
        "DM1_DTC2_E8": ("CAN_MFC_Public_DM1_E8", "DM1_DTC2_E8"),
        "DM1_DTC3_E8": ("CAN_MFC_Public_DM1_E8", "DM1_DTC3_E8"),
        "DM1_DTC4_E8": ("CAN_MFC_Public_DM1_E8", "DM1_DTC4_E8"),
        "DM1_DTC5_E8": ("CAN_MFC_Public_DM1_E8", "DM1_DTC5_E8"),

        "FLI2_FwdLaneImagerStatus_E8": ("CAN_MFC_Public_FLI2_E8", "FLI2_FwdLaneImagerStatus_E8"),

        "DM1_DTC1_2A": ("CAN_MFC_Public_DM1_2A", "DM1_DTC1_2A"),
        "DM1_DTC2_2A": ("CAN_MFC_Public_DM1_2A", "DM1_DTC2_2A"),
        "DM1_DTC3_2A": ("CAN_MFC_Public_DM1_2A", "DM1_DTC3_2A"),
        "DM1_DTC4_2A": ("CAN_MFC_Public_DM1_2A", "DM1_DTC4_2A"),
        "DM1_DTC5_2A": ("CAN_MFC_Public_DM1_2A", "DM1_DTC5_2A"),

        # "time": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
    },
]


class cFill(iCalc):
    dep = ('calc_common_time-flr25')

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flr25')

        time_AEBSState, value_AEBSState, unit_AEBSState = group.get_signal_with_unit('AEBS1_AEBSState_2A',
                                                                                     ScaleTime=time)
        bitfield_AEBSState = (value_AEBSState == 14)

        time_LDWSState, value_LDWSState, unit_LDWSState = group.get_signal_with_unit('FLI2_LDWSState_E8',
                                                                                     ScaleTime=time)
        bitfield_LDWSState = (value_LDWSState == 14)

        time_DTC1_E8, value_DTC1_E8, unit_DTC1_E8 = group.get_signal_with_unit('DM1_DTC1_E8',
                                                                               ScaleTime=time)
        if np.any(np.isnan(value_DTC1_E8)):
            bitfield_DTC1_E8 = np.zeros(len(time), dtype=bool)
        else:
            bitfield_DTC1_E8 = (value_DTC1_E8 != 0)

        time_DTC2_E8, value_DTC2_E8, unit_DTC2_E8 = group.get_signal_with_unit('DM1_DTC2_E8',
                                                                               ScaleTime=time)
        if np.any(np.isnan(value_DTC2_E8)):
            bitfield_DTC2_E8 = np.zeros(len(time), dtype=bool)
        else:
            bitfield_DTC2_E8 = (value_DTC2_E8 != 0)

        time_DTC3_E8, value_DTC3_E8, unit_DTC3_E8 = group.get_signal_with_unit('DM1_DTC3_E8',
                                                                               ScaleTime=time)
        if np.any(np.isnan(value_DTC3_E8)):
            bitfield_DTC3_E8 = np.zeros(len(time), dtype=bool)
        else:
            bitfield_DTC3_E8 = (value_DTC3_E8 != 0)

        time_DTC4_E8, value_DTC4_E8, unit_DTC4_E8 = group.get_signal_with_unit('DM1_DTC4_E8',
                                                                               ScaleTime=time)
        if np.any(np.isnan(value_DTC4_E8)):
            bitfield_DTC4_E8 = np.zeros(len(time), dtype=bool)
        else:
            bitfield_DTC4_E8 = (value_DTC4_E8 != 0)

        time_DTC5_E8, value_DTC5_E8, unit_DTC5_E8 = group.get_signal_with_unit('DM1_DTC5_E8',
                                                                               ScaleTime=time)
        if np.any(np.isnan(value_DTC5_E8)):
            bitfield_DTC5_E8 = np.zeros(len(time), dtype=bool)
        else:
            bitfield_DTC5_E8 = (value_DTC5_E8 != 0)

        time_FwdLaneImagerStatus_E8, value_FwdLaneImagerStatus_E8, unit_FwdLaneImagerStatus_E8 = group.get_signal_with_unit(
            'FLI2_FwdLaneImagerStatus_E8',
            ScaleTime=time)

        bitfield_FwdLaneImagerStatus_E8 = (value_FwdLaneImagerStatus_E8 > 1)

        time_DTC1_2A, value_DTC1_2A, unit_DTC1_2A = group.get_signal_with_unit('DM1_DTC1_2A',
                                                                               ScaleTime=time)
        if np.any(np.isnan(value_DTC1_2A)):
            bitfield_DTC1_2A = np.zeros(len(time), dtype=bool)
        else:
            bitfield_DTC1_2A = (value_DTC1_2A != 0)

        time_DTC2_2A, value_DTC2_2A, unit_DTC2_2A = group.get_signal_with_unit('DM1_DTC2_2A',
                                                                               ScaleTime=time)
        if np.any(np.isnan(value_DTC2_2A)):
            bitfield_DTC2_2A = np.zeros(len(time), dtype=bool)
        else:
            bitfield_DTC2_2A = (value_DTC2_2A != 0)

        time_DTC3_2A, value_DTC3_2A, unit_DTC3_2A = group.get_signal_with_unit('DM1_DTC3_2A',
                                                                               ScaleTime=time)
        if np.any(np.isnan(value_DTC3_2A)):
            bitfield_DTC3_2A = np.zeros(len(time), dtype=bool)
        else:
            bitfield_DTC3_2A = (value_DTC3_2A != 0)

        time_DTC4_2A, value_DTC4_2A, unit_DTC4_2A = group.get_signal_with_unit('DM1_DTC4_2A',
                                                                               ScaleTime=time)
        if np.any(np.isnan(value_DTC4_2A)):
            bitfield_DTC4_2A = np.zeros(len(time), dtype=bool)
        else:
            bitfield_DTC4_2A = (value_DTC4_2A != 0)

        time_DTC5_2A, value_DTC5_2A, unit_DTC5_2A = group.get_signal_with_unit('DM1_DTC5_2A',
                                                                               ScaleTime=time)
        if np.any(np.isnan(value_DTC5_2A)):
            bitfield_DTC5_2A = np.zeros(len(time), dtype=bool)
        else:
            bitfield_DTC5_2A = (value_DTC5_2A != 0)

        return time, bitfield_AEBSState, bitfield_LDWSState, bitfield_DTC1_E8, bitfield_DTC2_E8, bitfield_DTC3_E8, \
               bitfield_DTC4_E8, bitfield_DTC5_E8, bitfield_FwdLaneImagerStatus_E8, bitfield_DTC1_2A, bitfield_DTC2_2A, \
               bitfield_DTC3_2A, bitfield_DTC4_2A, bitfield_DTC5_2A


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Python_Toolchain_2\Evaluation_data\sys_bitfield_event\mi5id5506__2024-06-26_09-43-26.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_sys_bitfield_event@aebs.fill', manager)
    # print flr25_egomotion.vx
