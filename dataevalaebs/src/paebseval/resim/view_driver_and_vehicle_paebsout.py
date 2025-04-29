# -*- dataeval: init -*-

"""
Plot basic driver and vehicle paebs plots.

"""

import numpy as np

import datavis
from interface import iView
from measparser.signalproc import rescale
from measparser.filenameparser import FileNameParser
from measproc.IntervalList import maskToIntervals

RED = '#CC2529'  # red from default color cycle


class View(iView):
    dep = ('calc_paebs_resim_output@aebs.fill')

    def check(self):
        sgs = [
            {
            # Driver
            "driver_gas_pedal_position_perc": ("MTSI_stKBFreeze_020ms_t",
                                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_gas_pedal_position_perc"),
            "driver_gas_pedal_kickdown_switch": ("MTSI_stKBFreeze_020ms_t",
                                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_gas_pedal_kickdown_switch"),
            "driver_brake_pedal_position_perc": ("MTSI_stKBFreeze_020ms_t",
                                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_brake_pedal_position_perc"),
            "driver_brake_pedal_switch": ("MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_brake_pedal_switch"),
            "driver_steering_wheel_angle": ("MTSI_stKBFreeze_020ms_t",
                                            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            "driver_paebs_act_demand": ("MTSI_stKBFreeze_020ms_t",
                                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_paebs_act_demand"),
            # Vehicle
            "vehicle_motion_ego_long_accel": ("MTSI_stKBFreeze_020ms_t",
                                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_vehicle_vehicle_motion_ego_long_accel"),
            "vehicle_motion_ego_speed": ("MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_vehicle_vehicle_motion_ego_speed"),

            #AEBS
            "AEBS1_AEBSState_A1": ("AEBS1_A1_sA1", "AEBS1_AEBSState_A1"),
        },
            {
            # Driver
            "driver_gas_pedal_position_perc": ("MTSI_stKBFreeze_020ms_t",
                                               "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_accel_pedal_position_perc"),
            "driver_gas_pedal_kickdown_switch": ("MTSI_stKBFreeze_020ms_t",
                                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_accel_pedal_kickdown_switch_pressed"),
            "driver_brake_pedal_position_perc": ("MTSI_stKBFreeze_020ms_t",
                                                 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_brake_pedal_position_perc"),
            "driver_brake_pedal_switch": ("MTSI_stKBFreeze_020ms_t",
                                          "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_brake_pedal_switch"),
            "driver_steering_wheel_angle": ("MTSI_stKBFreeze_020ms_t",
                                            "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            "driver_paebs_act_demand": ("MTSI_stKBFreeze_020ms_t",
                                        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_driver_engine_torque_demand_perc"),
            # Vehicle
            "vehicle_motion_ego_long_accel": ("MTSI_stKBFreeze_020ms_t",
                                              "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_vehicle_vehicle_motion_ego_long_accel"),
            "vehicle_motion_ego_speed": ("MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_vehicle_vehicle_motion_ego_speed"),

            #AEBS
            "AEBS1_AEBSState_A1": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
        },
            {
                # Driver
                "driver_gas_pedal_position_perc"  : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_accel_pedal_position_perc"),
                "driver_gas_pedal_kickdown_switch": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_accel_pedal_kickdown_switch_pressed"),
                "driver_brake_pedal_position_perc": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_brake_pedal_position_perc"),
                "driver_brake_pedal_switch"       : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_brake_pedal_switch"),
                "driver_steering_wheel_angle"     : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
                "driver_paebs_act_demand"         : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_driver_engine_torque_demand_perc"),
                # Vehicle
                "vehicle_motion_ego_long_accel"   : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_vehicle_vehicle_motion_ego_long_accel"),
                "vehicle_motion_ego_speed"        : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_vehicle_vehicle_motion_ego_speed"),


                # AEBS
                "AEBS1_AEBSState_A1"              : ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                                     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_PaebsOutput_hmi_paebs_system_state"),
            },
        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)

        paebs_resim_event, time, total_mileage = self.modules.fill(self.dep)
        return group, paebs_resim_event, time

    def view(self, group, paebs_resim_event, time):
        pn = datavis.cPlotNavigator(title="Driver and Vehicle Plots for Paebs")

        ax = pn.addAxis(ylabel="pos.")
        # gas pedal position
        if 'driver_gas_pedal_position_perc' in group:
            time00, value00, unit00 = group.get_signal_with_unit("driver_gas_pedal_position_perc")
            pn.addSignal2Axis(ax, "gas p. pos.", time00, value00, unit=unit00, color=RED)
        if 'driver_gas_pedal_kickdown_switch' in group:
            time02, value02, unit02 = group.get_signal_with_unit("driver_gas_pedal_kickdown_switch")
            pn.addSignal2Axis(ax, "gas p. switch", time02, value02, unit=unit02, color='g')

        # pedal switch
        ax = pn.addAxis(ylabel="switch")
        # brake pedal position
        if 'driver_brake_pedal_position_perc' in group:
            time02, value02, unit02 = group.get_signal_with_unit("driver_brake_pedal_position_perc")
            pn.addSignal2Axis(ax, "brake p. pos.", time02, value02, unit=unit02, color=RED)
        if 'driver_brake_pedal_switch' in group:
            time02, value02, unit02 = group.get_signal_with_unit("driver_brake_pedal_switch")
            pn.addSignal2Axis(ax, "brake p. switch", time02, value02, unit=unit02, color='blue')

        # steering wheel angle
        ax = pn.addAxis(ylabel="angle")
        if 'driver_steering_wheel_angle' in group:
            time02, value02, unit02 = group.get_signal_with_unit("driver_steering_wheel_angle")
            pn.addSignal2Axis(ax, "steering wheel angle", time02, value02, unit=unit02, color='orange')

        # paebs act demand
        ax = pn.addAxis(ylabel="act_demand")
        if 'driver_paebs_act_demand' in group:
            time02, value02, unit02 = group.get_signal_with_unit("driver_paebs_act_demand")
            pn.addSignal2Axis(ax, "paebs act demand", time02, value02, unit=unit02, color='g')

        # vehicle ego long. accel.
        ax = pn.addAxis(ylabel="accel.")
        if 'vehicle_motion_ego_long_accel' in group:
            time02, value02, unit02 = group.get_signal_with_unit("vehicle_motion_ego_long_accel")
            pn.addSignal2Axis(ax, "ego long. accel.", time02, value02, unit=unit02, color='DarkCyan')

        # vehicle motion ego speed
        ax = pn.addAxis(ylabel="speed.")
        if 'vehicle_motion_ego_speed' in group:
            time02, value02, unit02 = group.get_signal_with_unit("vehicle_motion_ego_speed")

            try:
                file_name = FileNameParser(self.source.BaseName).date_underscore
            except:
                file_name = self.source.BaseName.replace('.', '-').replace('_at_', '_').rsplit('_', 2)[0]
            valid_paebs_resim_data = self.get_data_from_csv(file_name, paebs_resim_event)
            delta_data_array = np.zeros(time02.shape, dtype=float)
            masked_aray = np.ones(time02.shape, dtype=bool)

            for item in valid_paebs_resim_data:
                interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), time00)
                delta_data_array[(interval[0] - 10):((interval[0] + 10))] = float(item['ego_velocity_x'])
                masked_aray[(interval[0] - 10):((interval[0] + 10))] = False

            pn.addSignal2Axis(ax, "motion ego speed", time02, value02, unit=unit02, color='DarkGreen')
            pn.addSignal2Axis(ax, 'resim ego speed', time02, np.ma.array(delta_data_array, mask=masked_aray), color=RED)

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
