# -*- dataeval: init -*-

from interface import iCalc

init_params = {
    'flr25': dict(
        sgn_group=[
            {
                "time": ("VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
            },
            {
                "time": (
                    "ARS4xx Device.AlgoVehCycle.VehDyn",
                    "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
            },
            {
                "time": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx Device.FCU.VehDynSync.Longitudinal.Velocity"),
            },
            {
                "time": ("VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
            },
            {
                "time": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
            },
            {
                "time": ("EBS12_Tx_TICAN", "VehWhlSpeed"),
            },
            {
                "time": ("VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Velocity"),
            },
            {
                "time": ("MFC5xx Device.VDY.VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Velocity"),
            },
            {
                "time": ("ACC1_2A", "SpeedOfForwardVehicle"),
            },
            {
                "time": ("EBC2", "FrontAxleSpeed_s0B"),
            },
            {
                "time": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
            },
            {
                "time": ("CAN_MFC_Public_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
            },
            {
                "time": ("CAN_Fusion_Private_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
            },
            {
                "time": (
                    "ARS4xx Device.AlgoVehCycle.VehDyn",
                    "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
            },
            {
                "time": ("ARS620.Task_AlgoVeh_Cycle.VDY_VehDynMeas",
                         "ARS620_Task_AlgoVeh_Cycle_VDY_VehDynMeas_Longitudinal_Velocity"),
            },
            {
                "time": ("CAN_VEHICLE_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
            },
        ]),
    'flc25': dict(
        sgn_group=[
            {
                "time": ("VehDynSync",
                         "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
            },
            {
                "time": ("VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Velocity"),
            },
            {
                "time": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx Device.FCU.VehDynSync.Longitudinal.Velocity"),
            },
            {
                "time": ("MFC5xx Device.VDY.VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Velocity"),
            },
            {
                "time": ("VehDyn",
                         "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
            },
            {
                "time": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
            },
            {
                "time": ("VehDyn", "SRR520_RightFrontBackwards_AlgoVehCycle_VehDyn_Longitudinal_Velocity"),
            },
            {
                "time": ("EBC2", "FrontAxleSpeed_s0B"),
            },
            {
                "time": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
            },
            {
                "time": ("CAN_MFC_Public_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
            },
            {
                "time": (
                    "ARS4xx Device.AlgoVehCycle.VehDyn",
                    "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
            },
            {
                "time": ("ARS620.Task_AlgoVeh_Cycle.VDY_VehDynMeas",
                         "ARS620_Task_AlgoVeh_Cycle_VDY_VehDynMeas_Longitudinal_Velocity"),
            },
            {
                "time": ("CAN_VEHICLE_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
            },
        ]),
    'slr25': dict(
        sgn_group=[
            {
                "time": ("VehDyn", "SRR520_RightFrontBackwards_AlgoVehCycle_VehDyn_Longitudinal_Velocity"),
            },
            {
                "time": ("SRR520_Front.AlgoVehCycle.VehDyn", "SRR520_Front_AlgoVehCycle_VehDyn_Longitudinal_Velocity"),
            },
            {
                "time": ("VehDyn", "SRR520_RightFrontFrontwards_AlgoVehCycle_VehDyn_Longitudinal_Velocity"),
            },
            {
                "time": ("MFC5xx Device.VDY.VehDyn", "MFC5xx Device.VDY.VehDyn.Longitudinal.Velocity"),
            },
            {
                "time": ("MFC5xx Device.VDY.VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Velocity"),
            },
            {
                "time": ("CAN_Fusion_Private_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
            },
            {
                "time": (
                    "ARS4xx Device.AlgoVehCycle.VehDyn",
                    "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
            },
            {
                "time": ("ARS620.Task_AlgoVeh_Cycle.VDY_VehDynMeas",
                         "ARS620_Task_AlgoVeh_Cycle_VDY_VehDynMeas_Longitudinal_Velocity"),
            },
        ]),
    'postmarker': dict(
        sgn_group=[{
            "time": ("ACC1_2A", "ACC1_SetSpeed_2A"),
        }, ]),
    'aebsresimcsvoutputeval': dict(
        sgn_group=[{
            "time": ("VDC2_0B", "VDC2_LatAccel_0B"),
        },
        ]),
    'trailer_eval': dict(
        sgn_group=[{
            "time": ("EBS21_Tx_TICAN_Bus1", "WhSpeedDiff"),
        },
        ]),
    'fcwresim': dict(
        sgn_group=[{
            "time": ("VDC2_0B_s0B", "VDC2_LatAccel_0B_s0B"),
        },
            {
                "time": ("CAN_MFC_Public_VDC2_0B", "VDC2_LatAccel_0B"),
            },
        ]),  #
    'tsrresim': dict(
        sgn_group=[
            {
                "time": ("EEC1_00_s00", "EngineSpeed"),
            },
            {
                "time": ("CAN_MFC_Public_EEC1_00", "EEC1_EngSpd_00"),
            },
            {
                "time": ("CAN_MFC_ARS_EEC1_00", "EEC1_EngSpd_00"),

            },
            {
                "time": ("EEC1_00_s00", "EEC1_EngSpd_00"),
            },
            {
                "time": ("EEC1_s00", "EngSpeed"),
            },
            {
                "time": ("EEC1", "EngSpeed_s00"),
            },
            {
                "time": ("EEC1_00_s00_EEC1_00_CAN20_4_4_idx84006", "EngineSpeed"),
            },
            {
                "time": ("EEC1_00", "EngineSpeed_s00"),
            },
            {
                "time": ("EEC1_00", "EEC1_EngSpd_00_s00"),
            },
            {
                "time": ("EEC1_00_s00_EEC1_00_CAN20_4_4_idx83560", "EngineSpeed"),
            },
            {
                "time": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EEC1_EEC1_EngSpd"),
            },
            {
                "time": ("CAN_Vehicle_EEC1_00", "EEC1_EngSpd_00"),
            },
        ]),
}


class cFill(iCalc):
    def init(self, sgn_group):
        self.sgn_group = sgn_group
        return

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(self.sgn_group)
        return group

    def fill(self, group):
        commonTime = group.get_time('time')
        return commonTime


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_common_time = manager_modules.calc('calc_common_time-flr25@aebs.fill', manager)
    print (flr25_common_time)
