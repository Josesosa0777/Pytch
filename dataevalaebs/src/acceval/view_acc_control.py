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
                "AccEventLogTriggerRequest": (
                    "Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf_AccEventLogTriggerRequest"),

                # Subplot 2 (Change both Signal after getting new measurement)
                "LONC_p_sp_const": (
                    "Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf_conf_LONC_p_sp_const"),
                "LONC_p_v_const": (
                    "Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf_conf_LONC_p_v_const"),

                # Subplot 3 (Change First Signal)
                "*ax_desired_LONC": (
                    "Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf_conf_LONC_p_v_const"),
                "acc_control_output_ax_dem": (
                    "ort_om_acc_control_DEP_acc_om_control_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_om_acc_control_DEP_acc_om_control_Buf_ax_dem"),

                # Subplot 4
                "acc_control_output_M_perc_Eng_dem": (
                    "ort_om_acc_control_DEP_acc_om_control_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_om_acc_control_DEP_acc_om_control_Buf_M_perc_Eng_dem"),

                # Subplot 5
                "acc_control_output_sna_ax_dem": (
                    "ort_om_acc_control_DEP_acc_om_control_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_om_acc_control_DEP_acc_om_control_Buf_sna_ax_dem"),
                "acc_control_output_sna_M_perc_Eng_dem ": (
                    "ort_om_acc_control_DEP_acc_om_control_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_om_acc_control_DEP_acc_om_control_Buf_sna_M_perc_Eng_dem"),

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
        pn = datavis.cPlotNavigator(title="ACC Controller")

        ax = pn.addAxis(ylabel="")

        # Subplot 1
        if 'AccEventLogTriggerRequest' in group:
            time00, value00, unit00 = group.get_signal_with_unit("AccEventLogTriggerRequest")
            pn.addSignal2Axis(ax, "AccEventLogTriggerRequest.", time00, value00, unit=unit00)

        # Subplot 2
        ax = pn.addAxis(ylabel="")
        if 'LONC_p_sp_const' in group:
            time00, value00, unit00 = group.get_signal_with_unit("LONC_p_sp_const")
            pn.addSignal2Axis(ax, "LONC_p_sp_const.", time00, value00, unit=unit00)
        if 'LONC_p_v_const' in group:
            time00, value00, unit00 = group.get_signal_with_unit("LONC_p_v_const")
            pn.addSignal2Axis(ax, "LONC_p_v_const.", time00, value00, unit=unit00)

        # Subplot 3
        ax = pn.addAxis(ylabel="")
        if 'ax_desired_LONC' in group:
            time00, value00, unit00 = group.get_signal_with_unit("ax_desired_LONC")
            pn.addSignal2Axis(ax, "ax_desired_LONC.", time00, value00, unit=unit00)
        if 'acc_control_output_ax_dem' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_control_output_ax_dem")
            pn.addSignal2Axis(ax, "acc_control_output_ax_dem", time04, value04, unit=unit04)

        # Subplot 4
        ax = pn.addAxis(ylabel="")
        if 'acc_control_output_M_perc_Eng_dem' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_control_output_M_perc_Eng_dem")
            pn.addSignal2Axis(ax, "acc_control_output_M_perc_Eng_dem", time04, value04, unit=unit04)

        # Subplot 5
        ax = pn.addAxis(ylabel="")
        if 'acc_control_output_sna_ax_dem' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_control_output_sna_ax_dem")
            pn.addSignal2Axis(ax, "acc_control_output_sna_ax_dem", time04, value04, unit=unit04)
        if 'acc_control_output_sna_M_perc_Eng_dem' in group:
            time04, value04, unit04 = group.get_signal_with_unit("acc_control_output_sna_M_perc_Eng_dem")
            pn.addSignal2Axis(ax, "acc_control_output_sna_M_perc_Eng_dem", time04, value04, unit=unit04)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
