# -*- dataeval: init -*-

"""
Plot basic driver and vehicle paebs plots.

"""

import numpy as np

import datavis
from interface import iView

RED = "#CC2529"  # red from default color cycle


class View(iView):
    def check(self):
        sgs = [
            {
                # Driver
                "driver_gas_pedal_position_perc": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_accel_pedal_position_perc",
                ),
                "driver_gas_pedal_kickdown_switch": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_accel_pedal_kickdown_switch_pressed",
                ),
                "driver_brake_pedal_position_perc": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_brake_pedal_position_perc",
                ),
                "driver_brake_pedal_switch": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_brake_pedal_switch",
                ),
                "source_control_device": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC1_EBC1_SourceAddressOfControllingDevice",
                ),
                "turn_indicator_switch": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_turn_signal_switch",
                ),
                "driver_steering_wheel_angle": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle",
                ),
                # Vehicle
                "vehicle_motion_ego_long_accel": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_vehicle_vehicle_motion_ego_long_accel",
                ),
                "vehicle_motion_ego_speed": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_vehicle_vehicle_motion_ego_speed",
                ),
            },
            {
                "driver_gas_pedal_position_perc": ("CAN_VEHICLE_EEC2_00", "EEC2_AccPedalPos1_00"),

                "driver_gas_pedal_kickdown_switch": ("CAN_VEHICLE_EEC2_00", "EEC2_AccPedalKickdownSwitch_00"),

                "driver_brake_pedal_position_perc": ("CAN_VEHICLE_EBC1_0B", "EBC1_BrkPedPos_0B"),

                "source_control_device": ("CAN_VEHICLE_EBC1_0B", "EBC1_SrcAddOfCtrlDevFrBrkCtrl_0B"),

                "turn_indicator_switch": ("CAN_VEHICLE_OEL_32", "OEL_TurnSignalSwitch_32"),

                "driver_steering_wheel_angle": ("CAN_VEHICLE_VDC2_0B", "VDC2_SteerWhlAngle_0B"),

                # Vehicle

                "vehicle_motion_ego_long_accel": ("CAN_VEHICLE_VDC2_0B", "VDC2_LongAccel_0B"),

                "vehicle_motion_ego_speed": ("CAN_VEHICLE_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),

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
        pn = datavis.cPlotNavigator(title="Driver and Vehicle Plots for Paebs")

        # Plot 1: Gas Pedal
        ax = pn.addAxis(ylabel="Position")
        # Axis left: Gas Pedal Position
        if "driver_gas_pedal_position_perc" in group:
            time, value, unit = group.get_signal_with_unit(
                "driver_gas_pedal_position_perc"
            )
            pn.addSignal2Axis(
                ax, "Gas Pedal Position", time, value.astype(int), unit="%", color="b"
            )
        # Axis right: Gas Pedal Switch
        if "driver_gas_pedal_kickdown_switch" in group:
            time, value, unit = group.get_signal_with_unit(
                "driver_gas_pedal_kickdown_switch"
            )
            mapping = {0: "False", 1: "True"}
            ax = pn.addTwinAxis(
                ax,
                ylabel='Switch Flag',
                yticks=mapping,
                ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
                color="g",
            )
            pn.addSignal2Axis(
                ax, "Gas Pedal Switch", time, value, unit='', color="g"
            )

        # Plot 2: Brake Pedal
        ax = pn.addAxis(ylabel="Position")
        # Axis left: Brake Pedal Position
        if "driver_brake_pedal_position_perc" in group:
            time, value, unit = group.get_signal_with_unit(
                "driver_brake_pedal_position_perc"
            )
            pn.addSignal2Axis(
                ax, "Brake Pedal Position", time, value.astype(int), unit='%', color='b'
            )
        # Axis right: Brake Pedal Switch
        if "driver_brake_pedal_switch" in group:
            time, value, unit = group.get_signal_with_unit(
                "driver_brake_pedal_switch"
            )
            mapping = {0: "False", 1: "True"}
            ax = pn.addTwinAxis(
                ax,
                ylabel='Switch Flag',
                yticks=mapping,
                ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
                color="g",
            )
            pn.addSignal2Axis(
                ax, "Brake Pedal Switch", time, value, unit='', color="g"
            )

        # Plot 3: Steering Wheel Angle and Turn Indicator
        ax = pn.addAxis(ylabel="Angle")
        # Axis left: Steering Wheel Angle
        if "driver_steering_wheel_angle" in group:
            time, value, unit = group.get_signal_with_unit(
                "driver_steering_wheel_angle"
            )
            data = value * 180 / np.pi
            pn.addSignal2Axis(
                ax, "Steering Wheel Angle", time, data.astype(int), unit='Degree', color="b"
            )
        # Axis right: Turn Indicator
        if "turn_indicator_switch" in group:
            time, value, unit = group.get_signal_with_unit(
                "turn_indicator_switch"
            )
            mapping = {0: "False", 1: "True"}
            ax = pn.addTwinAxis(
                ax,
                ylabel='Switch Flag',
                yticks=mapping,
                ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
                color="g",
            )
            pn.addSignal2Axis(
                ax, "Turn Indicator Switch", time, value, unit='', color="g"
            )

        # Plot 4: Source of Controlling Device
        ticks = {42: hex(42), 160: hex(160), 11: hex(11), 33: hex(33)}  # known Source Addresses
        ax = pn.addAxis(ylabel="Device", yticks=ticks)
        if "source_control_device" in group:
            time, value, unit = group.get_signal_with_unit(
                "source_control_device"
            )

            pn.addSignal2Axis(
                ax, "Source of Controlling Device", time, value, unit='', color="b"
            )

        # Plot 5: Ego Vehicle Kinematics
        ax = pn.addAxis(ylabel="Speed")
        # Axis left: Ego Speed
        if "vehicle_motion_ego_speed" in group:
            time, value, unit = group.get_signal_with_unit(
                "vehicle_motion_ego_speed"
            )
            pn.addSignal2Axis(
                ax, "Ego lon. Speed", time, value, unit='m/s', color="b"
            )
            # Axis right: Ego Acceleration
        if "vehicle_motion_ego_long_accel" in group:
            time, value, unit = group.get_signal_with_unit(
                "vehicle_motion_ego_long_accel"
            )
            ax = pn.addTwinAxis(
                ax,
                ylabel='Acceleration',
                color="g",
            )
            pn.addSignal2Axis(
                ax, "Ego lon. Acceleration", time, value, unit='m/s^2', color="g"
            )

        self.sync.addClient(pn)
        return

    def extend_aebs_state_axis(self, pn, ax):
        return
