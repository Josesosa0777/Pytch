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
            {  # Subplot 1
                "acc_driver_main_switch": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_main_switch"),
                "acc_driver_pause_button": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_pause_button"),
                "acc_driver_resume_button": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_resume_button"),
                "acc_driver_set_button": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_set_button"),
                "acc_driver_accel_button": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_accel_button"),
                "acc_driver_coast_button": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_coast_button"),

                # Subplot 2
                "acc_driver_pedal_pos": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_accel_pedal_pos"),
                "input_brake_pedal_position": (
                    "Rte_SWC_InputManager_RPort_im_postp_DEP_postp_im_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_im_postp_DEP_postp_im_Buf_driver_brake_pedal_position"),

                # Subplot 3
                "acc_driver_str_angle": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_str_whl_angle"),

                # Subplot 4
                "input_turn_signal_switch": (
                    "Rte_SWC_InputManager_RPort_im_postp_DEP_postp_im_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_im_postp_DEP_postp_im_Buf_driver_turn_signal_switch"),

                # Subplot 5
                "acc_brake_system_parkBrake": (
                    "Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf_acc_brake_system_parkBrake_f"),

            }
        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="ACC Driver Input")

        ax = pn.addAxis(ylabel="")

        # Subplot 1
        if 'acc_driver_main_switch' in group:
            time00, value00, unit00 = group.get_signal_with_unit("acc_driver_main_switch")
            pn.addSignal2Axis(ax, "acc_driver_main_switch.", time00, value00, unit=unit00)

        if 'acc_driver_pause_button' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_driver_pause_button")
            pn.addSignal2Axis(ax, "acc_driver_pause_button", time04, value04, unit=unit04)

        if 'acc_driver_resume_button' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_driver_resume_button")
            pn.addSignal2Axis(ax, "acc_driver_resume_button", time04, value04, unit=unit04)

        if 'acc_driver_set_button' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_driver_set_button")
            pn.addSignal2Axis(ax, "acc_driver_set_button", time04, value04, unit=unit04)

        if 'acc_driver_accel_button' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_driver_accel_button")
            pn.addSignal2Axis(ax, "acc_driver_accel_button", time04, value04, unit=unit04)

        if 'acc_driver_coast_button' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_driver_coast_button")
            pn.addSignal2Axis(ax, "acc_driver_coast_button", time04, value04, unit=unit04)

        # Subplot 2
        ax = pn.addAxis(ylabel="")
        if 'acc_driver_pedal_pos' in group:
            time00, value00, unit00 = group.get_signal_with_unit("acc_driver_pedal_pos")
            pn.addSignal2Axis(ax, "acc_driver_pedal_pos.", time00, value00, unit=unit00)

        if 'input_brake_pedal_position' in group:
            time00, value00, unit00 = group.get_signal_with_unit("input_brake_pedal_position")
            pn.addSignal2Axis(ax, "input_brake_pedal_position.", time00, value00, unit=unit00)

        # Subplot 3
        ax = pn.addAxis(ylabel="")
        if 'acc_driver_str_angle' in group:
            time00, value00, unit00 = group.get_signal_with_unit("acc_driver_str_angle")
            pn.addSignal2Axis(ax, "acc_driver_str_angle.", time00, value00, unit=unit00)

        # Subplot 4
        ax = pn.addAxis(ylabel="")
        if 'input_turn_signal_switch' in group:
            time04, value04, unit04 = group.get_signal_with_unit("input_turn_signal_switch")
            pn.addSignal2Axis(ax, "input_turn_signal_switch", time04, value04, unit=unit04)

        # Subplot 5
        ax = pn.addAxis(ylabel="")
        if 'acc_brake_system_parkBrake' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_brake_system_parkBrake")
            pn.addSignal2Axis(ax, "acc_brake_system_parkBrake", time04, value04, unit=unit04)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
