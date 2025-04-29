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
                # Subplot 1 (Change all Signals after getting new measurement)
                "tg_lon_planner_ego_vx": (
                    "Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf_AccEventLogTriggerRequest"),
                "bp_mate_final_vx_set": (
                    "Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf_AccEventLogTriggerRequest"),
                "tg_lon_planner_v0_obj": (
                    "Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf_conf_LONC_p_sp_const"),
                "tg_lon_planner_orig_v0": (
                    "Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf_conf_LONC_p_v_const"),

                # Subplot 2 (Change all Signal)
                "*tg_lon_planner_ego_ax": (
                    "Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf_conf_LONC_p_v_const"),
                "tg_lon_planner_a0_obj": (
                    "ort_om_acc_control_DEP_acc_om_control_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_om_acc_control_DEP_acc_om_control_Buf_ax_dem"),
                "*tg_lon_planner_orig_a0": (
                    "Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf_conf_LONC_p_v_const"),
                "ax_dem_LONC": (
                    "ort_om_acc_control_DEP_acc_om_control_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_om_acc_control_DEP_acc_om_control_Buf_ax_dem"),
                "*ax_tracMinAdj_TC": (
                    "Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_nvm_DEP_nvm_acc_Buf_conf_LONC_p_v_const"),

                # Subplot 3 (Change All Signals)
                "tg_lon_planner_dx0_obj": (
                    "ort_om_acc_control_DEP_acc_om_control_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_om_acc_control_DEP_acc_om_control_Buf_M_perc_Eng_dem"),
                "tg_lon_planner_dist_follow_momentary": (
                    "ort_om_acc_control_DEP_acc_om_control_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_om_acc_control_DEP_acc_om_control_Buf_M_perc_Eng_dem"),

                # Subplot 4
                "tg_lon_planner_lon_ctrl_mode": (
                    "ort_om_acc_control_DEP_acc_om_control_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_om_acc_control_DEP_acc_om_control_Buf_sna_ax_dem"),
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
        pn = datavis.cPlotNavigator(title="ACC Kinematics")

        ax = pn.addAxis(ylabel="")

        # Subplot 1
        if 'tg_lon_planner_ego_vx' in group:
            time00, value00, unit00 = group.get_signal_with_unit("tg_lon_planner_ego_vx")
            pn.addSignal2Axis(ax, "tg_lon_planner_ego_vx.", time00, value00, unit=unit00)
        if 'bp_mate_final_vx_set' in group:
            time00, value00, unit00 = group.get_signal_with_unit("bp_mate_final_vx_set")
            pn.addSignal2Axis(ax, "bp_mate_final_vx_set.", time00, value00, unit=unit00)
        if 'tg_lon_planner_v0_obj' in group:
            time00, value00, unit00 = group.get_signal_with_unit("tg_lon_planner_v0_obj")
            pn.addSignal2Axis(ax, "tg_lon_planner_v0_obj.", time00, value00, unit=unit00)
        if 'tg_lon_planner_orig_v0' in group:
            time00, value00, unit00 = group.get_signal_with_unit("tg_lon_planner_orig_v0")
            pn.addSignal2Axis(ax, "tg_lon_planner_orig_v0.", time00, value00, unit=unit00)

        # Subplot 2
        ax = pn.addAxis(ylabel="")
        if 'tg_lon_planner_ego_ax' in group:
            time00, value00, unit00 = group.get_signal_with_unit("tg_lon_planner_ego_ax")
            pn.addSignal2Axis(ax, "tg_lon_planner_ego_ax.", time00, value00, unit=unit00)
        if 'tg_lon_planner_a0_obj' in group:
            time04, value04, unit04 = group.get_signal_with_unit("tg_lon_planner_a0_obj")
            pn.addSignal2Axis(ax, "tg_lon_planner_a0_obj", time04, value04, unit=unit04)
        if 'tg_lon_planner_orig_a0' in group:
            time04, value04, unit04 = group.get_signal_with_unit("tg_lon_planner_orig_a0")
            pn.addSignal2Axis(ax, "tg_lon_planner_orig_a0", time04, value04, unit=unit04)
        if 'ax_dem_LONC' in group:
            time04, value04, unit04 = group.get_signal_with_unit("ax_dem_LONC")
            pn.addSignal2Axis(ax, "ax_dem_LONC", time04, value04, unit=unit04)
        if 'ax_tracMinAdj_TC' in group:
            time04, value04, unit04 = group.get_signal_with_unit("ax_tracMinAdj_TC")
            pn.addSignal2Axis(ax, "ax_tracMinAdj_TC", time04, value04, unit=unit04)

        # Subplot 3
        ax = pn.addAxis(ylabel="")
        if 'tg_lon_planner_dx0_obj' in group:
            time04, value04, unit04 = group.get_signal_with_unit("tg_lon_planner_dx0_obj")
            pn.addSignal2Axis(ax, "tg_lon_planner_dx0_obj", time04, value04, unit=unit04)
        if 'tg_lon_planner_dist_follow_momentary' in group:
            time04, value04, unit04 = group.get_signal_with_unit("tg_lon_planner_dist_follow_momentary")
            pn.addSignal2Axis(ax, "tg_lon_planner_dist_follow_momentary", time04, value04, unit=unit04)

        # Subplot 4
        ax = pn.addAxis(ylabel="")
        if 'tg_lon_planner_lon_ctrl_mode' in group:
            time04, value04, unit04 = group.get_signal_with_unit("tg_lon_planner_lon_ctrl_mode")
            pn.addSignal2Axis(ax, "tg_lon_planner_lon_ctrl_mode", time04, value04, unit=unit04)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
