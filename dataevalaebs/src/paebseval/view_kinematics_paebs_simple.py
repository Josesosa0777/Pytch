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
                {   "XBR_CtrlMod": ("XBR_0B_2A_d0B_s2A","XBR_CtrlMode_0B_2A"),
                    "XBR_ExtAccelDem": ("XBR_0B_2A_d0B_s2A","XBR_ExtAccelDem_0B_2A"),
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
                    "paebs_obj_0_dx": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI0I_dx"),
                    "paebs_obj_0_dy": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI0I_dy"),
                    "paebs_obj_0_vx_rel": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI0I_vx_rel"),
                    "paebs_obj_0_vy_abs": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI0I_vy_abs"),
                },
                {
                    "XBR_CtrlMod"                     : ("XBR_0B_2A","XBR_CtrlMode_0B_2A_d0B_s2A"),
                    "XBR_ExtAccelDem"                 :  ("XBR_0B_2A","XBR_ExtAccelDem_0B_2A_d0B_s2A"),
                    "control_xbr_demand"              : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_control_paebs_brake_acceleration_demand"),
                    "control_engine_torque_limitation": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_control_paebs_engine_torque_demand_perc"),
                    "hmi_system_state"                : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                    "hmi_relevant_object_detected"    : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_detected"),
                    "hmi_ttc"                         : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_ttc"),
                    "paebs_obj_0_dx"                  : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI0I_dx"),
                    "paebs_obj_0_dy"                  : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI0I_dy"),
                    "paebs_obj_0_vx_rel"              : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI0I_vx_rel"),
                    "paebs_obj_0_vy_abs"              : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objectsI0I_vy_abs"),
                },
                {
                    "XBR_CtrlMod"                     : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC5_EBC5_XBR_ActiveCntrlMod"),
                    "XBR_ExtAccelDem"                 :  ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_HdbOutput_control_output_hdb_xbr_accel_demand"),
                    "control_xbr_demand"              : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_control_paebs_brake_acceleration_demand"),
                    "control_engine_torque_limitation": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_control_paebs_engine_torque_demand_perc"),
                    "hmi_system_state"                : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
                    "hmi_relevant_object_detected"    : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_detected"),
                    "hmi_ttc"                         : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_relevant_object_ttc"),
                    "paebs_obj_0_dx"                  : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects0_dx"),
                    "paebs_obj_0_dy"                  : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects0_dy"),
                    "paebs_obj_0_vx_rel"              : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects0_vx_rel"),
                    "paebs_obj_0_vy_abs"              : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_paebs_objects0_vy_abs"),
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
            if 'XBR_ExtAccelDem' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("XBR_ExtAccelDem")
                pn.addSignal2Axis(ax, "XBR_ExtAccelDem.", time00, value00, unit=unit00, color=RED)
            
            if 'XBR_CtrlMod' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("XBR_CtrlMod")
                ax = pn.addTwinAxis(ax, ylabel="XBR_CtrlMod", color = 'b')
                pn.addSignal2Axis(ax, "XBR_CtrlMod", time00, value00, unit=unit00, color='b')

            # PAEBS state
            yticks = {0: "not ready", 1: "temp. n/a", 2: "deact.", 3: "ready",
                      4: "override", 5: "warning", 6: "part. brk.", 7: "emer. brk.",
                      14: "error", 15: "n/a"}
            yticks = dict((k, "(%s) %d" % (v, k)) for k, v in yticks.iteritems())
            ax = pn.addAxis(ylabel="system_state", yticks=yticks)
            if 'hmi_system_state' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("hmi_system_state")
                pn.addSignal2Axis(ax, "hmi_system_state.", time00, value00, unit=unit00, color='g')

            #ax = pn.addAxis(ylabel="RelevantObjectDetected")
            if 'hmi_relevant_object_detected' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("hmi_relevant_object_detected")
                ax = pn.addTwinAxis(ax, ylabel="RelevanObjDet", color = 'b', ylim=(0,2))
                pn.addSignal2Axis(ax, "hmi_relevant_object_detected.", time00, value00, unit=unit00, color='b')

            ax = pn.addAxis(ylabel="dx")
            if 'paebs_obj_0_dx' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("paebs_obj_0_dx")
                pn.addSignal2Axis(ax, "paebs_obj_0_dx.", time00, value00, unit=unit00, color='g')

            if 'paebs_obj_0_dy' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("paebs_obj_0_dy")
                ax = pn.addTwinAxis(ax, ylabel="dy", color = 'b')
                pn.addSignal2Axis(ax, "paebs_obj_0_dy.", time00, value00, unit=unit00, color='b')

            ax = pn.addAxis(ylabel="vx_rel")
            if 'paebs_obj_0_vx_rel' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("paebs_obj_0_vx_rel")
                pn.addSignal2Axis(ax, "paebs_obj_0_vx_rel.", time00, value00, unit=unit00, color='g')

            if 'paebs_obj_0_vy_abs' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("paebs_obj_0_vy_abs")
                ax = pn.addTwinAxis(ax, ylabel="vy_abs", color = 'b')
                pn.addSignal2Axis(ax, "paebs_obj_0_vy_abs.", time00, value00, unit=unit00, color='b')


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
