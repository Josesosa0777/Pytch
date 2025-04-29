# -*- dataeval: init -*-

"""
Plot basic driver activities and AEBS outputs

AEBS-relevant driver activities (pedal activation, steering etc.) and
AEBS outputs (in AEBS1 and XBR messages) are shown.
"""

import numpy as np

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                # Sensor_State
                # "sensorRadar_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                #                       "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state"),
                # "sensorCamera_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                #                        "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state"),
                # # CEM_State
                # "CemState": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas",
                #              "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState"),

                # ACTL signals
                # "ACTL": (
                #     "MFC5xx Device.ACTL.EcuOmc_FreezeData",
                #     "MFC5xx_Device_ACTL_EcuOmc_FreezeData_Status_CurrentState_u_StateId"),

                # Sys_bitfield_signals

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

                "time": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
            },
        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="Sys Bitfield event")

        # mapping = {0: 'FAILED', 1: 'DEGRADED', 2: 'AVAILABLE'}
        #
        # if "sensorRadar_state" in group and "sensorCamera_state" in group:
        #     axis00 = pn.addAxis(ylabel='SensorState', yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
        #     time_sensorRadar_state, value_sensorRadar_state, unit_sensorRadar_state = group.get_signal_with_unit(
        #         "sensorRadar_state")
        #     pn.addSignal2Axis(axis00, "sensorRadar_state", time_sensorRadar_state, value_sensorRadar_state,
        #                       unit=unit_sensorRadar_state)
        #
        #     time_sensorCamera_state, value_sensorCamera_state, unit_sensorCamera_state = group.get_signal_with_unit(
        #         "sensorCamera_state")
        #     pn.addSignal2Axis(axis00, "sensorCamera_state", time_sensorCamera_state, value_sensorCamera_state,
        #                       unit=unit_sensorCamera_state)
        #
        # mapping_cem = {0: 'OFF', 1: 'INIT', 2: 'NORMAL', 3: 'FAILURE'}
        #
        # if "CemState" in group:
        #     axis01 = pn.addAxis(ylabel='CemState', yticks=mapping_cem,
        #                         ylim=(min(mapping_cem) - 0.5, max(mapping_cem) + 0.5))
        #     time_CemState, value_CemState, unit_CemState = group.get_signal_with_unit("CemState")
        #     pn.addSignal2Axis(axis01, "CemState", time_CemState, value_CemState, unit=unit_CemState)
        #
        # mapping_actl = {0: 'e_Orphan', 1: 'OPMODE_STARTUP_IU', 3: 'OPMODE_INFRASTRUCTURE_RUNNING',
        #                 4: 'OPMODE_LIMITED_START', 5: 'LIMITED_ERROR_HANDLER', 6: 'VIDEOPROC_ON',
        #                 7: 'OPMODE_NORMAL',
        #                 8: 'STARTUP_IMGPROC', 9: 'DPU_APPL_LOADING', 10: 'DPU_INITIALIZATION',
        #                 11: 'IMAGE_PENDING', 12: 'GS_CONFIRM_PENDING',
        #                 13: 'LIMITED_FATAL_ERROR', 14: 'LIMITED_DPU_DEG', 15: 'LIMITED_DPUBOOT_ERROR',
        #                 16: 'FUNCTION_OFF', 17: 'SENSOR_NOT_CALIBRATED',
        #                 18: 'IDLE_PENDING', 19: 'IDLE_REQUESTED',
        #                 20: 'SENSOR_MISALIGNED', 21: 'CALIBRATION', 22: 'EOL',
        #                 23: 'ACAL', 24: 'GS_RESET'}
        #
        # axis02 = pn.addAxis(ylabel='ACTL', yticks=mapping_actl, ylim=(min(mapping_actl) - 1.0, max(mapping_actl) + 1.0))
        #
        # time_ACTL, value_ACTL, unit_ACTL = group.get_signal_with_unit("ACTL")
        # pn.addSignal2Axis(axis02, "ACTL", time_ACTL, value_ACTL, unit=unit_ACTL)

        axis03 = pn.addAxis(ylabel="")

        commonTime = group.get_time('time')

        # Subplot 1
        if 'AEBS1_AEBSState_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("AEBS1_AEBSState_2A", ScaleTime=commonTime)
            value_2 = (value00 == 14).astype(int)
            pn.addSignal2Axis(axis03, "AEBS1_AEBSState_2A", time00, value_2, unit=unit00)

        if 'FLI2_LDWSState_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_LDWSState_E8", ScaleTime=commonTime)
            value_2 = (value00 == 14).astype(int)
            pn.addSignal2Axis(axis03, "FLI2_LDWSState_E8", time00, value_2, unit=unit00)

        if 'DM1_DTC1_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC1_E8", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                value_2 = np.zeros(len(commonTime), dtype=int)
            else:
                value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(axis03, "DM1_DTC1_E8", time00, value_2, unit=unit00)

        if 'DM1_DTC2_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC2_E8", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                value_2 = np.zeros(len(commonTime), dtype=int)
            else:
                value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(axis03, "DM1_DTC2_E8", time00, value_2, unit=unit00)

        if 'DM1_DTC3_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC3_E8", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                value_2 = np.zeros(len(commonTime), dtype=int)
            else:
                value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(axis03, "DM1_DTC3_E8", time00, value_2, unit=unit00)

        if 'DM1_DTC4_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC4_E8", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                value_2 = np.zeros(len(commonTime), dtype=int)
            else:
                value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(axis03, "DM1_DTC4_E8", time00, value_2, unit=unit00)

        if 'DM1_DTC5_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC5_E8", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                value_2 = np.zeros(len(commonTime), dtype=int)
            else:
                value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(axis03, "DM1_DTC5_E8", time00, value_2, unit=unit00)

        if 'FLI2_FwdLaneImagerStatus_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_FwdLaneImagerStatus_E8", ScaleTime=commonTime)
            value_2 = (value00 > 1).astype(int)
            pn.addSignal2Axis(axis03, "FLI2_FwdLaneImagerStatus_E8", time00, value_2, unit=unit00)

        if 'DM1_DTC1_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC1_2A", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                value_2 = np.zeros(len(commonTime), dtype=int)
            else:
                value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(axis03, "DM1_DTC1_2A", time00, value_2, unit=unit00)

        if 'DM1_DTC2_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC2_2A", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                value_2 = np.zeros(len(commonTime), dtype=int)
            else:
                value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(axis03, "DM1_DTC2_2A", time00, value_2, unit=unit00)

        if 'DM1_DTC3_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC3_2A", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                value_2 = np.zeros(len(commonTime), dtype=int)
            else:
                value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(axis03, "DM1_DTC3_2A", time00, value_2, unit=unit00)

        if 'DM1_DTC4_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC4_2A", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                value_2 = np.zeros(len(commonTime), dtype=int)
            else:
                value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(axis03, "DM1_DTC4_2A", time00, value_2, unit=unit00)

        if 'DM1_DTC5_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC5_2A", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                value_2 = np.zeros(len(commonTime), dtype=int)
            else:
                value_2 = (value00 != 0).astype(int)
            pn.addSignal2Axis(axis03, "DM1_DTC5_2A", time00, value_2, unit=unit00)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
