# -*- dataeval: init -*-

"""
:Name:
	view_driveract_aebsout.py

:Type:
	View script

:Visualization Type:
	Plot

:Full Path:
	dataevalaebs/src/aebseval/resim/view_driveract_aebsout.py

:Sensors:
	FLR25

:Short Description:
	AEBS-relevant driver activities (pedal activation, steering etc.) and
  AEBS outputs (in AEBS1 and XBR messages) are shown.

:Large Description:
	Usage:
		- Plot basic driver activities and AEBS outputs

:Dependencies:
	- calc_aebs_resim_output@aebs.fill

:Output Data Image/s:
	.. image:: ../images/view_driveract_aebsout_1.png

"""

import numpy as np
from numpy import rad2deg
import datavis
from interface import iView
from measparser.signalproc import rescale
from measparser.filenameparser import FileNameParser
from measproc.IntervalList import maskToIntervals


class View(iView):
    dep = ('calc_aebs_resim_output@aebs.fill')

    def check(self):
        sgs = [
            # Delta
            {
                "accped_pos": ("EEC2_00_s00", "EEC2_APPos1_00"),
                "brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B"),
                "brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrkSw_0B"),
                "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B"),
                "turn_signal_right": ("Rte_SWC_AEBS_RPort_im_eb_driver_DEP_im_eb_driver_Buf",
                "ARS4xx_Device_SW_Every10ms_Rte_SWC_AEBS_RPort_im_eb_driver_DEP_im_eb_driver_Buf_turn_signal_right"),
                "turn_signal_left": ("Rte_SWC_AEBS_RPort_im_eb_driver_DEP_im_eb_driver_Buf",
                "ARS4xx_Device_SW_Every10ms_Rte_SWC_AEBS_RPort_im_eb_driver_DEP_im_eb_driver_Buf_turn_signal_left"),

                "aebs_state": ("AEBS1_2A_s2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("AEBS1_2A_s2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("PropXBR_d0B_s2A", "ExtAccelDem"),
                "xbr_ctrl_mode": ("PropXBR_d0B_s2A", "CtrlMode"),
            },
            {
                "accped_pos": ("EEC2_00_s00", "EEC2_AccelPedalPos1_00"),
                "brkped_pos": ("EBC1_0B_s0B", "EBC1_BrakePedalPos_0B"),
                "brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWheelAngle_0B"),
                "turn_signal_right": ("Rte_SWC_AEBS_RPort_im_eb_driver_DEP_im_eb_driver_Buf",
                "ARS4xx_Device_SW_Every10ms_Rte_SWC_AEBS_RPort_im_eb_driver_DEP_im_eb_driver_Buf_turn_signal_right"),
                "turn_signal_left": ("Rte_SWC_AEBS_RPort_im_eb_driver_DEP_im_eb_driver_Buf",
                "ARS4xx_Device_SW_Every10ms_Rte_SWC_AEBS_RPort_im_eb_driver_DEP_im_eb_driver_Buf_turn_signal_left"),

                "aebs_state": ("AEBS1_s2A", "AdvncdEmrgencyBrakingSystemState"),
                "coll_warn_level": ("AEBS1_s2A", "CollisionWarningLevel"),
                "xbr_demand": (
                    "Rte_SWCNorm_RPort_norm_om_XBR_DEP_om_norm_XBR_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_XBR_DEP_om_norm_XBR_Buf_external_acceleration_demand"),
                "xbr_ctrl_mode": (
                    "Rte_SWCNorm_RPort_norm_om_XBR_DEP_om_norm_XBR_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_XBR_DEP_om_norm_XBR_Buf_xbr_control_mode"),
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
                "brake_switch": ("EBC1_0B_s0B","EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B_s0B"),
                "dir_ind": ("OEL_32_s32", "OEL_TurnSigSw_32_s32"),

                "aebs_state": ("AEBS1_A0_sA0", "AEBS1_AEBSState_A0_sA0"),
                "coll_warn_level": ("AEBS1_A0_sA0", "AEBS1_CollisionWarningLevel_A0_sA0"),
                "xbr_demand": ("XBR", "XBR_ExtAccelDem"),
                "xbr_ctrl_mode": ("XBR", "XBR_CtrlMode"),
            },
            {
                "accped_pos": ("EEC2_00_s00","EEC2_AccPedalPos1_00"),
                "brkped_pos": ("EBC1_0B_s0B","EBC1_BrkPedPos_0B"),
                "brake_switch": ("EBC1_0B_s0B","EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("VDC2_0B_s0B","VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf_OEL_TurnSigSw"),

                "aebs_state": ("AEBS1_A0_sA0","AEBS1_AEBSState_A0"),
                "coll_warn_level": ("AEBS1_A0_sA0","AEBS1_CollisionWarningLevel_A0"),
                "xbr_ctrl_mode": ("XBR_0B_2A_d0B_s2A","XBR_CtrlMode_0B_2A"),
                "xbr_demand": ("XBR_0B_2A_d0B_s2A","XBR_ExtAccelDem_0B_2A"),
            },
            {
                "accped_pos": ("EEC2_00_s00", "EEC2_AccPedalPos1_00"),
                "brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B"),
                "brake_switch": ("EBC1_0B_s0B", "EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf","ARS4xx_Device_SW_Every10ms_Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf_OEL_TurnSigSw"),

                "aebs_state": ("AEBS1_2A_s2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("AEBS1_2A_s2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("XBR_0B_2A_d0B_s2A", "XBR_ExtAccelDem_0B_2A"),
                "xbr_ctrl_mode": ("XBR_0B_2A_d0B_s2A", "XBR_CtrlMode_0B_2A"),
            },
            #
            {
                "accped_pos": ("EEC2_00_s00_EEC2_00", "EEC2_AccPedalPos1_00"),
                "brkped_pos": ("EBC1_0B_s0B_EBC1_0B", "EBC1_BrkPedPos_0B"),
                "brake_switch": ("EBC1_0B_s0B_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("VDC2_0B_s0B_VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                "dir_ind": ("Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf",
                "ARS4xx_Device_SW_Every10ms_Rte_SWC_Preprocessor_RPort_prep_norm_OEL_DEP_norm_prep_postp_OEL_Buf_OEL_TurnSigSw"),

                "aebs_state": ("AEBS1_2A_s2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("AEBS1_2A_s2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand":("XBR_0B_2A_d0B_s2A_XBR_0B_2A", "XBR_ExtAccelDem_0B_2A") ,
                "xbr_ctrl_mode":("XBR_0B_2A_d0B_s2A_XBR_0B_2A", "XBR_CtrlMode_0B_2A") ,
            },
            {
                "accped_pos": ("EEC2_s00", "AccelPedalPos1"),
                "brkped_pos": ("EBC1_0B_s0B", "BrakePedalPosition"),
                "brake_switch": ("EBC1_0B_s0B","EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("VDC2_0B_s0B", "SteeringWheelAngle"),
                "dir_ind": ("OEL_s32", "TurnSignalSwitch"),

                "aebs_state": ("AEBS1_A0_sA0", "FwdCollisionAEBSSysState"),
                "coll_warn_level": ("AEBS1_A0_sA0", "CollisionWarningLevel"),
                "xbr_demand": ("XBR_2A", "XBR_ExtAccelDem_2A"),
                "xbr_ctrl_mode": ("XBR_2A", "XBR_CtrlMode_2A"),
            },
            {
                "accped_pos": ("CAN_Vehicle_EEC2", "AccelPedalPos1"),
                "brkped_pos": ("CAN_Vehicle_EBC1", "BrakePedalPos"),
                "brake_switch": ("CAN_Vehicle_EBC1_0B", "EBC1_EBSBrakeSwitch_0B"),
                "steer_angle": ("CAN_Vehicle_VDC2", "SteerWheelAngle"),
                "dir_ind": ("CAN_MFC_Public_OEL_32", "OEL_TurnSignalSwitch_32"),

                "aebs_state": ("CAN_Vehicle_AEBS1_2A", "AEBS1_AEBSState_2A"),
                "coll_warn_level": ("CAN_Vehicle_AEBS1_2A", "AEBS1_CollisionWarningLevel_2A"),
                "xbr_demand": ("CAN_Vehicle_XBR_0B_2A", "XBR_ExtAccelDem_0B_2A"),
                "xbr_ctrl_mode":("CAN_Vehicle_XBR_0B_2A", "XBR_CtrlMode_0B_2A") ,
            }
        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)

        aebs_resim_data, time, total_mileage = self.modules.fill(self.dep)
        return group, aebs_resim_data, time

    def view(self, group, aebs_resim_data, time):
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
            ax = pn.addTwinAxis(ax, ylabel = 'brake switch', color = 'g')
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
        if 'turn_signal_right' and 'turn_signal_left' in group:
            time05, value05, unit05 = group.get_signal_with_unit("turn_signal_right")
            time06, value06, unit06 = group.get_signal_with_unit("turn_signal_left")
            dir_ind = np.zeros(time05.shape, dtype=float)
            right_turn_interval_list = maskToIntervals(value05 == 1)
            for interval in right_turn_interval_list:
                dir_ind[interval[0]:interval[1]] = 2
            left_turn_interval_list = maskToIntervals(value06 == 1)
            for interval in left_turn_interval_list:
                dir_ind[interval[0]:interval[1]] = 1
            pn.addSignal2Axis(ax, "dir. indicator", time05, dir_ind, unit=unit05)
        else:
            if 'dir_ind' in group:
                time07, value07, unit07 = group.get_signal_with_unit("dir_ind")
                pn.addSignal2Axis(ax, "dir. indicator", time07, value07, unit=unit07)

        # AEBS state
        yticks = {0: "not ready", 1: "temp. n/a", 2: "deact.", 3: "ready",
                  4: "override", 5: "warning", 6: "part. brk.", 7: "emer. brk.",
                  14: "error", 15: "n/a"}
        yticks = dict((k, "(%s) %d" % (v, k)) for k, v in yticks.iteritems())
        ax = pn.addAxis(ylabel="state", yticks=yticks)
        ax.set_ylim((-1.0, 8.0))

        if 'aebs_state' in group:
            time00, value00, unit00 = group.get_signal_with_unit("aebs_state")

            try:
                file_name = FileNameParser(self.source.BaseName).date_underscore
            except:
                file_name = self.source.BaseName.replace('.', '-').replace('_at_', '_').rsplit('_', 2)[0]
            valid_aebs_resim_data = self.get_data_from_csv(file_name, aebs_resim_data)
            delta_data_array = np.zeros(time00.shape, dtype=float)
            masked_aray = np.ones(time00.shape, dtype=bool)

            for item in valid_aebs_resim_data:
                if item["event type"] == '0':
                    item["event type"] = '5'
                elif item["event type"] == '1':
                    item["event type"] = '6'
                elif item["event type"] == '2':
                    item["event type"] = '7'
                elif item["event type"] == '3':
                    item["event type"] = '5'
                elif item["event type"] == '4':
                    item["event type"] = '6'
                elif item["event type"] == '5':
                    item["event type"] = '7'

                interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), time00)
                delta_data_array[(interval[0]-10):((interval[0]+10))] = float(item["event type"])
                masked_aray[(interval[0]-10):((interval[0]+10))] = False

            pn.addSignal2Axis(ax, "AEBSState", time00, value00, unit=unit00)
            pn.addSignal2Axis(ax, 'AEBSState resim', time00, np.ma.array(delta_data_array, mask=masked_aray))
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

    def get_data_from_csv(self, file_name, aebs_resim_data):
        valid_data = []

        for files in aebs_resim_data:
            name = ""
            if 'camera' in files['Measurement File']:
                name = files['Measurement File'].replace('.', '-').split('_camera')[0].replace('_at_', '_')
            elif 'radar' in files['Measurement File']:
                name = files['Measurement File'].replace('.', '-').split('_radar')[0].replace('_at_', '_')
            if name == file_name:
                valid_data.append(files)
        return valid_data

    def get_index(self, interval, time):
        st_time, ed_time = interval
        st_time = st_time / 1000000.0
        ed_time = ed_time / 1000000.0
        start_index = (np.abs(time - st_time)).argmin()
        end_index = (np.abs(time - ed_time)).argmin()
        if start_index == end_index:
            end_index += 1
        return (start_index, end_index)

