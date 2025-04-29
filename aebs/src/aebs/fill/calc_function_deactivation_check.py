# -*- dataeval: init -*-

from interface import iCalc
import numpy as np

sgs = [
    {
    "XBR_ExtAccelDem": ("XBR_2A","XBR_ExtAccelDem_2A"),
    "XBR_ExtAccelDem_1": ("XBR_2A_CAN20","XBR_ExtAccelDem_2A"),
    "XBR_ExtAccelDem_2": ("XBR_2A_CAN22","XBR_ExtAccelDem_2A"),
    "AEBSState": ("AEBS1_2A","AEBS1_AEBSState_2A"),
    "brake_acceleration_demand": ("XBR_2A","XBR_ExtAccelDem_2A"),
    },
    {
    "XBR_ExtAccelDem": ("XBR_0B_2A_d0B_s2A","XBR_ExtAccelDem_0B_2A"),
    "XBR_ExtAccelDem_1": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN20","XBR_ExtAccelDem_0B_2A"),
    "XBR_ExtAccelDem_2": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN22","XBR_ExtAccelDem_0B_2A"),
    "AEBSState": ("AEBS1_2A_s2A","AEBS1_AEBSState_2A"),
    "brake_acceleration_demand": ("Rte_SWC_OutputManager_RPort_aebs_om_control_DEP_aebs_om_control_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_aebs_om_control_DEP_aebs_om_control_Buf_eb_brake_acceleration_demand"),
    },
    {
    "XBR_ExtAccelDem": ("XBR_0B_2A_d0B_s2A","XBR_ExtAccelDem_0B_2A"),
    "XBR_ExtAccelDem_1": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN20","XBR_ExtAccelDem_0B_2A"),
    "XBR_ExtAccelDem_2": ("XBR_0B_2A_d0B_s2A_XBR_0B_2A_CAN21","XBR_ExtAccelDem_0B_2A"),
    "AEBSState": ("AEBS1_2A_s2A","AEBS1_AEBSState_2A"),
    "brake_acceleration_demand": ("Rte_SWC_OutputManager_RPort_aebs_om_control_DEP_aebs_om_control_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_aebs_om_control_DEP_aebs_om_control_Buf_eb_brake_acceleration_demand"),
    },
]

class cFill(iCalc):
    dep = ('calc_common_time-flr25')

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        valid_intervals = None
        time = self.modules.fill('calc_common_time-flr25')

        # vx
        _, XBR_ExtAccelDem, unit_vx = group.get_signal_with_unit('XBR_ExtAccelDem', ScaleTime=time)
        _, XBR_ExtAccelDem_1, unit_vx = group.get_signal_with_unit('XBR_ExtAccelDem_1', ScaleTime=time)
        _, XBR_ExtAccelDem_2, unit_vx = group.get_signal_with_unit('XBR_ExtAccelDem_2', ScaleTime=time)
        _, AEBSState, unit_vx = group.get_signal_with_unit('AEBSState', ScaleTime=time)
        _, aebs_brake_acceleration_demand, unit_vx = group.get_signal_with_unit('brake_acceleration_demand', ScaleTime=time)

        if (np.abs(XBR_ExtAccelDem) < 9).any():
            valid_intervals = (XBR_ExtAccelDem < 9)
        elif (np.abs(XBR_ExtAccelDem_1) < 9).any():
            valid_intervals = (XBR_ExtAccelDem_1 < 9)
        elif (np.abs(XBR_ExtAccelDem_2) < 9).any():
            valid_intervals = (XBR_ExtAccelDem_2 < 9)

        return time, valid_intervals, XBR_ExtAccelDem, XBR_ExtAccelDem_1, XBR_ExtAccelDem_2 , AEBSState, aebs_brake_acceleration_demand


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\aebs_test\2021-05-20\mi5id5390__2021-05-20_09-28-48.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_function_deactivation_check@aebs.fill', manager)
    # print flr25_egomotion.vx
