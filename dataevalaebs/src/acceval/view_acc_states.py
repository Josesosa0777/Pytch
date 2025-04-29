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
                # Subplot 1 (Change Signal after getting new measurement)
                "bp_state_coordinator_lon_ctrl_state": (
                    "Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf_AccEventLogTriggerRequest"),

                # Subplot 2 (Change Signal)
                "mode_in_LONC": (
                    "Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf_conf_LONC_p_v_const"),

                # Subplot 3
                "acc_hmi_output_acc_mode": (
                    "Rte_SWC_OutputManager_RPort_om_acc_hmi_DEP_acc_om_hmi_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_om_acc_hmi_DEP_acc_om_hmi_Buf_acc_mode"),

                # Subplot 4
                "acc_system_shutoff_warning": (
                    "Rte_SWC_OutputManager_RPort_om_acc_hmi_DEP_acc_om_hmi_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_om_acc_hmi_DEP_acc_om_hmi_Buf_acc_system_shutoff_warning"),
                "acc_distance_alert_signal": (
                    "Rte_SWC_OutputManager_RPort_om_acc_hmi_DEP_acc_om_hmi_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_om_acc_hmi_DEP_acc_om_hmi_Buf_acc_distance_alert_signal"),

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
        pn = datavis.cPlotNavigator(title="ACC States")

        ax = pn.addAxis(ylabel="")

        # Subplot 1
        if 'bp_state_coordinator_lon_ctrl_state' in group:
            time00, value00, unit00 = group.get_signal_with_unit("bp_state_coordinator_lon_ctrl_state")
            pn.addSignal2Axis(ax, "bp_state_coordinator_lon_ctrl_state.", time00, value00, unit=unit00)

        # Subplot 2
        ax = pn.addAxis(ylabel="")
        if 'mode_in_LONC' in group:
            time00, value00, unit00 = group.get_signal_with_unit("mode_in_LONC")
            pn.addSignal2Axis(ax, "mode_in_LONC.", time00, value00, unit=unit00)

        # Subplot 3
        ax = pn.addAxis(ylabel="")
        if 'acc_hmi_output_acc_mode' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_hmi_output_acc_mode")
            pn.addSignal2Axis(ax, "acc_hmi_output_acc_mode", time04, value04, unit=unit04)

        # Subplot 4
        ax = pn.addAxis(ylabel="")
        if 'acc_system_shutoff_warning' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_system_shutoff_warning")
            pn.addSignal2Axis(ax, "acc_system_shutoff_warning", time04, value04, unit=unit04)
        if 'acc_distance_alert_signal' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_distance_alert_signal")
            pn.addSignal2Axis(ax, "acc_distance_alert_signal", time04, value04, unit=unit04)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
