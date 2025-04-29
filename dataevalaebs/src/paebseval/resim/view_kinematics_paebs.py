6# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView, iParameter
from measparser.signalproc import rescale
from measparser.filenameparser import FileNameParser
from measproc.IntervalList import maskToIntervals

init_params = {
    "PAEBS_OUTPUT": dict(id=dict(paebs_output=True)),
    "VEHICLE_CAN": dict(id=dict(vehicle_can=True)),
}

RED = '#CC2529'  # red from default color cycle


class View(iView):
    dep = ('calc_paebs_resim_output@aebs.fill')

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

        paebs_resim_event, time, total_mileage = self.modules.fill(self.dep)

        return paebs_resim_event, time, paebs_group, vehicle_can_group

    def view(self, paebs_resim_event, time, paebs_group=None, vehicle_can_group=None):
        try:
            file_name = FileNameParser(self.source.BaseName).date_underscore
        except:
            file_name = self.source.BaseName.replace('.', '-').replace('_at_', '_').rsplit('_', 2)[0]
        valid_paebs_resim_data = self.get_data_from_csv(file_name, paebs_resim_event)

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

                delta_data_array = np.zeros(time00.shape, dtype=float)
                masked_aray = np.ones(time00.shape, dtype=bool)

                for item in valid_paebs_resim_data:
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
                    delta_data_array[(interval[0] - 10):((interval[0] + 10))] = float(item["event type"])
                    masked_aray[(interval[0] - 10):((interval[0] + 10))] = False

                pn.addSignal2Axis(ax, "hmi_system_state.", time00, value00, unit=unit00, color='g')
                pn.addSignal2Axis(ax, 'resim_system_state', time00, np.ma.array(delta_data_array, mask=masked_aray))

            #ax = pn.addAxis(ylabel="RelevantObjectDetected")
            if 'hmi_relevant_object_detected' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("hmi_relevant_object_detected")
                ax = pn.addTwinAxis(ax, ylabel="RelevanObjDet", color = 'b', ylim=(0,2))
                pn.addSignal2Axis(ax, "hmi_relevant_object_detected.", time00, value00, unit=unit00, color='b')

            ax = pn.addAxis(ylabel="dx")
            delta_dx_array = np.zeros(time00.shape, dtype=float)
            # masked_dx_array = np.ones(t.shape, dtype=bool)
            delta_dy_array = np.zeros(time00.shape, dtype=float)

            counter_for_loop_iteration = 0
            for item in valid_paebs_resim_data:
                counter_for_loop_iteration = counter_for_loop_iteration + 1
                if counter_for_loop_iteration >= 2:
                    interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), time00)
                    if 'obj_distance_x' in item:
                        delta_dx_array[(interval[0] + 10):((interval[0] + 40))] = float(item["obj_distance_x"])
                    elif 'obj_distance_x_start' in item:
                        delta_dx_array[(interval[0] + 10):((interval[0] + 40))] = float(item["obj_distance_x_start"])
                    masked_aray[(interval[0] + 10):((interval[0] + 40))] = False
                else:
                    interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), time00)
                    if 'obj_distance_x' in item:
                        delta_dx_array[(interval[0] - 10):((interval[0] + 40))] = float(item["obj_distance_x"])
                    elif 'obj_distance_x_start' in item:
                        delta_dx_array[(interval[0] - 10):((interval[0] + 40))] = float(item["obj_distance_x_start"])
                    masked_aray[(interval[0] - 10):((interval[0] + 40))] = False

            counter_for_loop_iteration = 0
            # Create dy signal from csv data
            for item in valid_paebs_resim_data:
                counter_for_loop_iteration = counter_for_loop_iteration + 1
                if counter_for_loop_iteration >= 2:
                    interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), time00)
                    if 'obj_distance_y' in item:
                        delta_dy_array[(interval[0] + 10):((interval[0] + 40))] = float(item["obj_distance_y"])
                    elif 'obj_distance_y_start' in item:
                        delta_dy_array[(interval[0] + 10):((interval[0] + 40))] = float(item["obj_distance_y_start"])
                    masked_aray[(interval[0] + 10):((interval[0] + 40))] = False
                else:
                    interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), time00)
                    if 'obj_distance_y' in item:
                        delta_dy_array[(interval[0] - 10):((interval[0] + 40))] = float(item["obj_distance_y"])
                    elif 'obj_distance_y_start' in item:
                        delta_dy_array[(interval[0] - 10):((interval[0] + 40))] = float(item["obj_distance_y_start"])
                    masked_aray[(interval[0] - 10):((interval[0] + 40))] = False

            if 'paebs_obj_0_dx' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("paebs_obj_0_dx")
                pn.addSignal2Axis(ax, "paebs_obj_0_dx.", time00, value00, unit=unit00, color='g')
                pn.addSignal2Axis(ax, 'dx resim', time00, np.ma.array(delta_dx_array, mask=masked_aray), unit='m')

            if 'paebs_obj_0_dy' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("paebs_obj_0_dy")
                ax = pn.addTwinAxis(ax, ylabel="dy", color = 'b')
                pn.addSignal2Axis(ax, "paebs_obj_0_dy.", time00, value00, unit=unit00, color='b')
                pn.addSignal2Axis(ax, 'dy resim', time00, np.ma.array(delta_dy_array, mask=masked_aray), unit='m')

            ax = pn.addAxis(ylabel="vx_rel")
            delta_vx_rel_array = np.zeros(time00.shape, dtype=float)
            # masked_dx_array = np.ones(t.shape, dtype=bool)
            delta_vy_abs_array = np.zeros(time00.shape, dtype=float)

            counter_for_loop_iteration = 0
            # Create dy signal from csv data
            for item in valid_paebs_resim_data:
                counter_for_loop_iteration = counter_for_loop_iteration + 1
                if counter_for_loop_iteration >= 2:
                    interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), time00)
                    if 'obj_relative_velocity_x' in item:
                        delta_vx_rel_array[(interval[0] + 10):((interval[0] + 40))] = float(item["obj_relative_velocity_x"])
                    elif 'obj_relative_velocity_x_start' in item:
                        delta_vx_rel_array[(interval[0] + 10):((interval[0] + 40))] = float(item["obj_relative_velocity_x_start"])
                    masked_aray[(interval[0] + 10):((interval[0] + 40))] = False
                else:
                    interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), time00)
                    if 'obj_relative_velocity_x' in item:
                        delta_vx_rel_array[(interval[0] - 10):((interval[0] + 40))] = float(item["obj_relative_velocity_x"])
                    elif 'obj_relative_velocity_x_start' in item:
                        delta_vx_rel_array[(interval[0] - 10):((interval[0] + 40))] = float(item["obj_relative_velocity_x_start"])
                    masked_aray[(interval[0] - 10):((interval[0] + 40))] = False

            counter_for_loop_iteration = 0
            # Create dy signal from csv data
            for item in valid_paebs_resim_data:
                counter_for_loop_iteration = counter_for_loop_iteration + 1
                if counter_for_loop_iteration >= 2:
                    interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), time00)
                    if 'obj_absolute_velocity_y' in item:
                        delta_vy_abs_array[(interval[0] + 10):((interval[0] + 40))] = float(item["obj_absolute_velocity_y"])
                    elif 'obj_absolute_velocity_y_start' in item:
                        delta_vy_abs_array[(interval[0] + 10):((interval[0] + 40))] = float(item["obj_absolute_velocity_y_start"])
                    masked_aray[(interval[0] + 10):((interval[0] + 40))] = False
                else:
                    interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), time00)
                    if 'obj_absolute_velocity_y' in item:
                        delta_vy_abs_array[(interval[0] - 10):((interval[0] + 40))] = float(item["obj_absolute_velocity_y"])
                    elif 'obj_absolute_velocity_y_start' in item:
                        delta_vy_abs_array[(interval[0] - 10):((interval[0] + 40))] = float(item["obj_absolute_velocity_y_start"])
                    masked_aray[(interval[0] - 10):((interval[0] + 40))] = False

            if 'paebs_obj_0_vx_rel' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("paebs_obj_0_vx_rel")
                pn.addSignal2Axis(ax, "paebs_obj_0_vx_rel.", time00, value00, unit=unit00, color='g')
                pn.addSignal2Axis(ax, 'vx_rel_resim', time00, np.ma.array(delta_vx_rel_array, mask=masked_aray))

            if 'paebs_obj_0_vy_abs' in paebs_group:
                time00, value00, unit00 = paebs_group.get_signal_with_unit("paebs_obj_0_vy_abs")
                ax = pn.addTwinAxis(ax, ylabel="vy_abs", color = 'b')
                pn.addSignal2Axis(ax, "paebs_obj_0_vy_abs.", time00, value00, unit=unit00, color='b')
                pn.addSignal2Axis(ax, 'vy_abs_resim', time00, np.ma.array(delta_vy_abs_array, mask=masked_aray))


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

    def get_data_from_csv(self, file_name, paebs_resim_data):
        valid_data = []

        for files in paebs_resim_data:
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

