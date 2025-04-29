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
                "accped_pos": ("CAN_VEHICLE_EEC2_00", "EEC2_AccPedalPos1_00"),
                "brkped_pos": ("CAN_VEHICLE_EBC1_0B", "EBC1_BrkPedPos_0B"),
                "brake_switch": ("CAN_VEHICLE_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("CAN_VEHICLE_VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("CAN_VEHICLE_OEL_32", "OEL_TurnSignalSwitch_32"),
                "aebs_state": ("CAN_VEHICLE_AEBS1_2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("CAN_VEHICLE_AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("CAN_VEHICLE_XBR_0B_2A", "XBR_ExtAccelDem_0B_2A"),
                "xbr_ctrl_mode": ("CAN_VEHICLE_XBR_0B_2A", "XBR_CtrlMode_0B_2A"),
            },
            {
                "accped_pos": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EEC2_EEC2_APPos1"),
                "brkped_pos": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC1_EBC1_BrkPedPos"),
                "brake_switch": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC1_EBC1_EBSBrkSw"),
                "steer_angle": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_VDC2_VDC2_SteerWhlAngle"),
                "dir_ind": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_OEL_OEL_TurnSigSw"),

                "aebs_state": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state"),
                "coll_warn_level": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_warning_level"),
                "xbr_demand": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_HdbOutput_control_output_hdb_xbr_accel_demand"),
                "xbr_ctrl_mode": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                  "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_HdbOutput_control_output_hdb_xbr_active"),
            },
            {
                "accped_pos": ("EEC2_00_s00", "EEC2_AccPedalPos1_00"),
                "brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B"),
                "brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf",
                            "ARS4xx_Device_SW_Every10ms_Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf_OEL_TurnSigSw"),

                "aebs_state": ("AEBS1_A0_sA0", "AEBS1_AEBSState_A0"),
                "coll_warn_level": ("AEBS1_A0_sA0", "AEBS1_CollisionWarningLevel_A0"),
                "xbr_demand": ("XBR_0B_72_d0B_s72", "XBR_ExtAccelDem_0B_72"),
                "xbr_ctrl_mode": ("XBR_0B_72_d0B_s72", "XBR_CtrlMode_0B_72"),
            },
            {
                # driver
                "accped_pos": ("EEC2_00", "EEC2_APPos1_00"),
                "brkped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
                "steer_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("OEL_21", "OEL_TurnSigSw_21"),
                # aebs
                "aebs_state": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("XBR_2A", "XBR_ExtAccelDem_2A"),
                "xbr_ctrl_mode": ("XBR_2A", "XBR_CtrlMode_2A"),
            }, {
                # driver
                "accped_pos": ("EEC2_00", "EEC2_APPos1_00"),
                "brkped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
                "steer_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("OEL_21", "OEL_TurnSigSw_21"),
                # aebs
                "aebs_state": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("AEBS1_2A", "AEBS1_ColisionWarningLevel_2A"),  # typo
                "xbr_demand": ("XBR_2A", "XBR_ExtAccelDem_2A"),
                "xbr_ctrl_mode": ("XBR_2A", "XBR_CtrlMode_2A"),
            }, {
                # driver
                "accped_pos": ("EEC2_00", "EEC2_APPos1_00"),
                "brkped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
                "steer_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("OEL_E6", "OEL_TurnSigSw_E6"),  # SA 0xE6
                # aebs
                "aebs_state": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("XBR_2A", "XBR_ExtAccelDem_2A"),
                "xbr_ctrl_mode": ("XBR_2A", "XBR_CtrlMode_2A"),
            }, {
                # driver
                "accped_pos": ("EEC2_00", "EEC2_APPos1_00"),
                "brkped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
                "steer_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("OEL_27", "OEL_TurnSigSw_27"),  # SA 0x27
                # aebs
                "aebs_state": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("XBR_2A", "XBR_ExtAccelDem_2A"),
                "xbr_ctrl_mode": ("XBR_2A", "XBR_CtrlMode_2A"),
            },
            {
                "accped_pos": ("EEC2_00", "EEC2_APPos1_00"),
                "brkped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
                "steer_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("OEL_32", "OEL_TurnSigSw_32"),
                "aebs_state": ("AEBS1_A0", "AEBS1_AEBSState_A0"),
                "coll_warn_level": ("AEBS1_A0", "AEBS1_CollisionWarningLevel_A0"),
                "xbr_demand": ("XBR", "XBR_ExtAccelDem"),
                "xbr_ctrl_mode": ("XBR", "XBR_CtrlMode"),
            },
            # FCW
            {
                "accped_pos": ("EEC2_00_s00", "EEC2_APPos1_00_s00"),
                "brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B_s0B"),
                "brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B_s0B"),
                "dir_ind": ("OEL_32_s32", "OEL_TurnSigSw_32_s32"),

                "aebs_state": ("AEBS1_A0_sA0", "AEBS1_AEBSState_A0_sA0"),
                "coll_warn_level": ("AEBS1_A0_sA0", "AEBS1_CollisionWarningLevel_A0_sA0"),
                "xbr_demand": ("XBR", "XBR_ExtAccelDem"),
                "xbr_ctrl_mode": ("XBR", "XBR_CtrlMode"),
            },
            {
                "accped_pos": ("EEC2_00_s00_EEC2_00_CAN21", "EEC2_APPos1_00"),
                "brkped_pos": ("EBC1_0B_s0B", "BrakePedalPosition"),
                "brake_switch": ("EBC1_0B_s0B", "EBSBrakeSwitch"),
                "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle"),
                "dir_ind": ("OEL_32_s32", "OEL_TurnSigSw_32"),

                "aebs_state": ("AEBS1_2A_s2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("AEBS1_2A_s2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("XBR_0B_2A_d0B_s2A", "XBR_ExtAccelDem_2A"),
                "xbr_ctrl_mode": ("XBR_0B_2A_d0B_s2A", "XBR_CtrlMode_2A"),
            },
            {
                "accped_pos": ("EEC2_00_s00", "EEC2_APPos1_00"),
                "brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B"),
                "brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrkSw_0B"),
                "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("OEL_32_s32", "OEL_TurnSigSw_32"),

                "aebs_state": ("AEBS1_2A_s2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("AEBS1_2A_s2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("XBR_0B_2A_d0B_s2A", "XBR_ExtAccelDem_2A"),
                "xbr_ctrl_mode": ("XBR_0B_2A_d0B_s2A", "XBR_CtrlMode_2A"),
            },
            {
                "accped_pos": ("EEC2_00_s00", "EEC2_AccPedalPos1_00"),
                "brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B"),
                "brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf",
                            "ARS4xx_Device_SW_Every10ms_Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf_OEL_TurnSigSw"),

                "aebs_state": ("AEBS1_2A_s2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("AEBS1_2A_s2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("XBR_0B_2A_d0B_s2A", "XBR_ExtAccelDem_0B_2A"),
                "xbr_ctrl_mode": ("XBR_0B_2A_d0B_s2A", "XBR_CtrlMode_0B_2A"),
            },
            {
                "accped_pos": ("EEC2_s00", "AccelPedalPos1"),
                "brkped_pos": ("EBC1_0B_s0B", "BrakePedalPosition"),
                "brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("VDC2_0B_s0B", "SteeringWheelAngle"),
                "dir_ind": ("OEL_s32", "TurnSignalSwitch"),

                "aebs_state": ("AEBS1_A0_sA0", "FwdCollisionAEBSSysState"),
                "coll_warn_level": ("AEBS1_A0_sA0", "CollisionWarningLevel"),
                "xbr_demand": ("XBR_2A", "XBR_ExtAccelDem_2A"),
                "xbr_ctrl_mode": ("XBR_2A", "XBR_CtrlMode_2A"),
            },
            {
                "accped_pos": ("EEC2_00", "EEC2_APPos1_00"),
                "brkped_pos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
                "brake_switch": ("EBC1_0B", "EBC1_EBSBrkSw_0B"),
                "steer_angle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B_s0B"),
                "dir_ind": ("OEL_32", "OEL_TurnSigSw_32_s32"),
                "aebs_state": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("XBR_2A", "XBR_ExtAccelDem_2A"),
                "xbr_ctrl_mode": ("XBR_2A", "XBR_CtrlMode_2A"),
            },
            {
                "accped_pos": ("CAN_MFC_Public_middle_EEC2_00", "EEC2_AccPedalPos1_00"),
                "brkped_pos": ("CAN_MFC_Public_middle_EBC1_0B", "EBC1_BrkPedPos_0B"),
                "brake_switch": ("CAN_MFC_Public_middle_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("CAN_MFC_Public_middle_VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("CAN_MFC_Public_middle_OEL_32", "OEL_TurnSignalSwitch_32"),
                "aebs_state": ("CAN_MFC_Public_middle_AEBS1_2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("CAN_MFC_Public_middle_AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("CAN_MFC_Public_middle_XBR_0B_2A", "XBR_ExtAccelDem_0B_2A"),
                "xbr_ctrl_mode": ("CAN_MFC_Public_middle_XBR_0B_2A", "XBR_CtrlMode_0B_2A"),

            },
            {
                "accped_pos": ("CAN_VEHICLE_EEC2_00", "EEC2_AccPedalPos1_00"),
                "brkped_pos": ("CAN_VEHICLE_EBC1_0B", "EBC1_BrkPedPos_0B"),
                "brake_switch": ("CAN_VEHICLE_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("CAN_MFC_Public_middle_VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("CAN_MFC_Public_middle_OEL_32", "OEL_TurnSignalSwitch_32"),
                "aebs_state": ("CAN_VEHICLE_AEBS1_2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("CAN_VEHICLE_AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("CAN_VEHICLE_XBR_0B_2A", "XBR_CtrlMode_0B_2A"),
                "xbr_ctrl_mode": ("CAN_VEHICLE_XBR_0B_2A", "XBR_ExtAccelDem_0B_2A"),
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
        pn = datavis.cPlotNavigator(title="Driver activities and AEBS outputs")

        ax = pn.addAxis(ylabel="pos.", ylim=(-5.0, 105.0))
        # accel. pedal
        if 'accped_pos' in group:
            time00, value00, unit00 = group.get_signal_with_unit("accped_pos")
            pn.addSignal2Axis(ax, "accel. p. pos.", time00, value00, unit=unit00)
        # brake pedal
        if 'brkped_pos' in group:
            time02, value02, unit02 = group.get_signal_with_unit("brkped_pos")
            pn.addSignal2Axis(ax, "brake p. pos.", time02, value02, unit=unit02)
        # brake switch
        if 'brake_switch' in group:
            time02, value02, unit02 = group.get_signal_with_unit("brake_switch")
            ax = pn.addTwinAxis(ax, ylabel='brake switch', color='g')
            pn.addSignal2Axis(ax, "brake switch", time02, value02, unit=unit02)

        # steering wheel
        ax = pn.addAxis(ylabel="angle", ylim=(-100.0, 100.0))
        if 'steer_angle' in group:
            time04, value04, unit04 = group.get_signal_with_unit("steer_angle")
            if unit04 == "rad" or not unit04:  # assuming rad if unit is empty
                value04 = np.rad2deg(value04)
                unit04 = "deg"
            pn.addSignal2Axis(ax, "steering wheel angle", time04, value04, unit=unit04)
        # direction indicator
        yticks = {0: "none", 1: "left", 2: "right", 3: "n/a"}
        yticks = dict((k, "%d (%s)" % (k, v)) for k, v in yticks.iteritems())
        ax = pn.addTwinAxis(ax, ylabel="state", ylim=(-1.0, 4.0), yticks=yticks, color='g')
        if 'dir_ind' in group:
            time05, value05, unit05 = group.get_signal_with_unit("dir_ind")
            pn.addSignal2Axis(ax, "dir. indicator", time05, value05, unit=unit05)

        # AEBS state
        yticks = {0: "not ready", 1: "temp. n/a", 2: "deact.", 3: "ready",
                  4: "override", 5: "warning", 6: "part. brk.", 7: "emer. brk.",
                  14: "error", 15: "n/a"}
        yticks = dict((k, "(%s) %d" % (v, k)) for k, v in yticks.iteritems())
        ax = pn.addAxis(ylabel="state", yticks=yticks)
        ax.set_ylim((-1.0, 8.0))
        if 'aebs_state' in group:
            time00, value00, unit00 = group.get_signal_with_unit("aebs_state")
            pn.addSignal2Axis(ax, "AEBSState", time00, value00, unit=unit00)
        # extend axis e.g. with simulated signal(s)
        self.extend_aebs_state_axis(pn, ax)
        # coll. warn. level
        ax = pn.addTwinAxis(ax, ylabel="level", ylim=(-1.0, 8.0), color='g')
        ax.set_yticks(xrange(8))
        if 'coll_warn_level' in group:
            time01, value01, unit01 = group.get_signal_with_unit("coll_warn_level")
            pn.addSignal2Axis(ax, "CollisionWarningLevel", time01, value01, unit=unit01)

        # XBR demand
        ax = pn.addAxis(ylabel="decel.", ylim=(-11.0, 11.0))
        if 'xbr_demand' in group:
            time04, value04, unit04 = group.get_signal_with_unit("xbr_demand")
            pn.addSignal2Axis(ax, "XBR_ExtAccelDem", time04, value04, unit=unit04)
        # XBR control mode
        yticks = {0: "off", 1: "add", 2: "max", 3: "n/a"}
        yticks = dict((k, "%d (%s)" % (k, v)) for k, v in yticks.iteritems())
        ax = pn.addTwinAxis(ax, ylabel="mode", ylim=(-1.0, 4.0), yticks=yticks, color='g')
        if 'xbr_ctrl_mode' in group:
            time05, value05, unit05 = group.get_signal_with_unit("xbr_ctrl_mode")
            pn.addSignal2Axis(ax, "XBR_CtrlMode", time05, value05, unit=unit05)

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
