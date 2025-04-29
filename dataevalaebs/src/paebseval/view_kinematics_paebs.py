6# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView, iParameter

init_params = {
    "PAEBS_OUTPUT": dict(id=dict(paebs_output=True)),
    "VEHICLE_CAN": dict(id=dict(vehicle_can=True)),
}

RED = '#CC2529'  # red from default color cycle


class View(iView):
    def init(self, id):
        self.id = id
        return

    def check(self):
        PAEBS_OUTPUT = [{}]
        VEHICLE_CAN = [{}]
        if self.id.get("vehicle_can"):
            VEHICLE_CAN = [
                {
                    "XBR_ExtAccelDem_2A": ("XBR_2A", "XBR_ExtAccelDem_2A"),
                    "XBR_ExtAccelDem_A0_0B": ("XBR_A0_0B", "XBR_ExtAccelDem_A0_0B"),
                    "AEBS1_AEBSState_2A": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
                    "AEBS1_RelevantObjectDetected_2A": ("AEBS1_2A", "AEBS1_RelevantObjectDetected_2A"),
                    "AEBS1_TimeToCollision_2A": ("AEBS1_2A", "AEBS1_TimeToCollision_2A"),
                },
                {
                    "XBR_ExtAccelDem_2A": ("XBR_0B_2A_d0B_s2A", "XBR_ExtAccelDem_0B_2A"),
                    "XBR_ExtAccelDem_A0_0B": ("XBR_0B_72_d0B_s72", "XBR_ExtAccelDem_0B_72"),
                    "AEBS1_AEBSState_2A": ("AEBS1_2A_s2A", "AEBS1_AEBSState_2A"),
                    "AEBS1_RelevantObjectDetected_2A": ("AEBS1_2A_s2A", "AEBS1_RelevantObjectDetected_2A"),
                    "AEBS1_TimeToCollision_2A": ("AEBS1_2A_s2A", "AEBS1_TimeToCollision_2A"),
                }
            ]

        if self.id.get("paebs_output"):
            PAEBS_OUTPUT = [
                {
                    "control_xbr_demand": ("MTSI_stKBFreeze_020ms_t",
                                           "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_control_paebs_brake_acceleration_demand"),
                    "control_engine_torque_limitation": ("MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_control_paebs_engine_torque_demand_perc"),
                    "hmi_system_state": ("MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                    "hmi_relevant_object_detected": ("MTSI_stKBFreeze_020ms_t",
                                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_detected"),
                    "hmi_ttc": ("MTSI_stKBFreeze_020ms_t",
                                "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_ttc"),
                },
                {
                    "control_xbr_demand": ("MTSI_stKBFreeze_040ms_t",
                                           "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsOutput_control_xbr_demand"),
                    "control_engine_torque_limitation": ("MTSI_stKBFreeze_040ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsOutput_control_engine_torque_limitation"),
                    "hmi_system_state": ("MTSI_stKBFreeze_040ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsOutput_hmi_system_state"),
                    "hmi_relevant_object_detected": ("MTSI_stKBFreeze_040ms_t",
                                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsOutput_hmi_relevant_object_detected"),
                    "hmi_ttc": ("MTSI_stKBFreeze_040ms_t",
                                "MFC5xx_Device_KB_MTSI_stKBFreeze_040ms_t_sFlc25_PaebsOutput_hmi_ttc"),
                }
            ]

        # paebs_group
        paebs_group = self.source.selectLazySignalGroup(PAEBS_OUTPUT)
        # give warning for not available signals
        for alias in PAEBS_OUTPUT[0]:
            if alias not in paebs_group:
                self.logger.warning("Signal for '%s' not available" % alias)

        # vehicle_CAN
        vehicle_can_group = self.source.selectLazySignalGroup(VEHICLE_CAN)
        # give warning for not available signals
        for alias in VEHICLE_CAN[0]:
            if alias not in vehicle_can_group:
                self.logger.warning("Signal for '%s' not available" % alias)

        return paebs_group, vehicle_can_group

    def view(self, paebs_group=None, vehicle_can_group=None):

        if self.id.get("paebs_output"):

            pn = datavis.cPlotNavigator(title="PAEBS Output")

            ax = pn.addAxis(ylabel="xbr_demand")

            # Subplot 1
            if 'control_xbr_demand' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("control_xbr_demand")
                pn.addSignal2Axis(ax, "control_xbr_demand.", time00, value00, unit=unit00, color=RED)

            ax = pn.addAxis(ylabel="engine_torque_limitation")
            if 'control_engine_torque_limitation' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("control_engine_torque_limitation")
                pn.addSignal2Axis(ax, "control_engine_torque_limitation.", time00, value00, unit=unit00, color='blue')

            ax = pn.addAxis(ylabel="system_state")
            if 'hmi_system_state' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("hmi_system_state")
                pn.addSignal2Axis(ax, "hmi_system_state.", time00, value00, unit=unit00, color='g')

            ax = pn.addAxis(ylabel="RelevantObjectDetected")
            if 'hmi_relevant_object_detected' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("hmi_relevant_object_detected")
                pn.addSignal2Axis(ax, "hmi_relevant_object_detected.", time00, value00, unit=unit00, color='Orange')

            ax = pn.addAxis(ylabel="ttc")
            if 'hmi_ttc' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("hmi_ttc")
                pn.addSignal2Axis(ax, "hmi_ttc.", time00, value00, unit=unit00, color='DarkGreen')

            self.sync.addClient(pn)
            return

        if self.id.get("vehicle_can"):
            pn = datavis.cPlotNavigator(title="Vehicle CAN")

            ax = pn.addAxis(ylabel="ExtAccelDem")

            # Subplot 1
            if 'XBR_ExtAccelDem_2A' in vehicle_can_group:
                time00, value00, unit00 = vehicle_can_group.get_signal_with_unit("XBR_ExtAccelDem_2A")
                pn.addSignal2Axis(ax, "XBR_ExtAccelDem_2A.", time00, value00, unit=unit00, color=RED)
            if 'XBR_ExtAccelDem_A0_0B' in vehicle_can_group:
                time00, value00, unit00 = vehicle_can_group.get_signal_with_unit("XBR_ExtAccelDem_A0_0B")
                pn.addSignal2Axis(ax, "XBR_ExtAccelDem_A0_0B.", time00, value00, unit=unit00, color='blue')

            ax = pn.addAxis(ylabel="AEBSState")
            if 'AEBS1_AEBSState_2A' in vehicle_can_group:
                time00, value00, unit00 = vehicle_can_group.get_signal_with_unit("AEBS1_AEBSState_2A")
                pn.addSignal2Axis(ax, "AEBS1_AEBSState_2A.", time00, value00, unit=unit00, color='g')

            ax = pn.addAxis(ylabel="RelevantObjectDetected")
            if 'AEBS1_RelevantObjectDetected_2A' in vehicle_can_group:
                time00, value00, unit00 = vehicle_can_group.get_signal_with_unit("AEBS1_RelevantObjectDetected_2A")
                pn.addSignal2Axis(ax, "AEBS1_RelevantObjectDetected_2A.", time00, value00, unit=unit00, color='Orange')

            ax = pn.addAxis(ylabel="TimeToCollision")
            if 'AEBS1_TimeToCollision_2A' in vehicle_can_group:
                time00, value00, unit00 = vehicle_can_group.get_signal_with_unit("AEBS1_TimeToCollision_2A")
                pn.addSignal2Axis(ax, "AEBS1_TimeToCollision_2A.", time00, value00, unit=unit00, color='DarkGreen')

            self.sync.addClient(pn)
            return

    def extend_aebs_state_axis(self, pn, ax):
        return
