# -*- dataeval: init -*-

"ACC ego/target vehicle kinematic and control signals"

import numpy as np

from pyutils.enum import enum
import datavis
from interface import iView
from measparser.signalgroup import SignalGroupError

EgoLonState = enum(
    STANDSTILL_SECURED=0,
    STANDSTILL_UNSECURED=1,
    BACKWARD=2,
    INTENTION_TO_DRIVE_FWD=3,
    FORWARD=4
)

init_params = {
    "DEVELOPER": dict(id=dict(developer=True)),
    "TESTER": dict(id=dict(tester=True)),
}

def as_yticks(myenum):
    return {v: '%s(%d)' % (k, v) for k, v in myenum._asdict().iteritems()}


RED = '#CC2529'  # red from default color cycle


class View(iView):
    def init(self, id):
        self.id = id
        return

    def check(self):
        sgs = [
            {
                "momentary_track_dx": (
                    "Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf_momentary_track_dx"),
                "acc_following_time": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_following_time"),
                "acc_vehicle_motion_v": (
                    "Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf_acc_vehicle_motion_v"),
                "im_vehicle_motion_ego_long_accel": (
                    "Rte_SWC_InputManager_RPort_postp_im_vehicle_DEP_postp_im_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_vehicle_DEP_postp_im_vehicle_Buf_vehicle_motion_ego_long_accel"),
                "acc_vehicle_motion_ego_longitudinal_state": (
                    "Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf_acc_vehicle_motion_ego_longitudinal_state"),
                "momentary_track_vx": (
                    "Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf_momentary_track_vx"),
                "acc_driver_cc_setspeed": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_cc_setspeed"),
                "momentary_track_valid": (
                    "Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf_momentary_track_valid"),
                "momentary_track_ax": (
                    "Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf_momentary_track_ax"),
                "acc_vehicle_motion_ego_curvature": (
                    "Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf_acc_vehicle_motion_ego_curvature"),
                "acc_control_output_ax_dem": (
                    "Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf_acc_control_output_ax_dem"),
                "acc_control_output_sna_ax_dem": (
                    "Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf_acc_control_output_sna_ax_dem"),
                "acc_control_output_M_perc_Eng_dem": (
                    "Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf_acc_control_output_M_perc_Eng_dem"),
                "acc_control_output_sna_M_perc_Eng_dem": (
                    "Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf_acc_control_output_sna_M_perc_Eng_dem"),
                "acc_powertrain_M_perc_eng": (
                    "Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf_acc_powertrain_M_perc_eng"),
                "om_TSC1_ReqTorqueLimit": (
                    "Rte_SWCNorm_RPort_norm_om_TSC1_DEP_om_norm_TSC1_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_TSC1_DEP_om_norm_TSC1_Buf_ReqTorqueLimit"),
                "acc_driver_cc_active": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_cc_active"),
                "acc_control_output_cc_disable": (
                    "Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf_acc_control_output_cc_disable"),
                "om_CCVS2_CruiseControlDisableCommand": (
                    "Rte_SWCNorm_RPort_norm_om_CCVS2_DEP_om_norm_CCVS2_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_CCVS2_DEP_om_norm_CCVS2_Buf_CruiseControlDisableCommand"),
                "om_CCVS2_CruiseControlPauseCommand": (
                    "Rte_SWCNorm_RPort_norm_om_CCVS2_DEP_om_norm_CCVS2_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_CCVS2_DEP_om_norm_CCVS2_Buf_CruiseControlPauseCommand"),
                "om_CCVS2_CruiseControlResumeCommand": (
                    "Rte_SWCNorm_RPort_norm_om_CCVS2_DEP_om_norm_CCVS2_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_CCVS2_DEP_om_norm_CCVS2_Buf_CruiseControlResumeCommand"),
                "om_PropXBR_HoldBrake": (
                    "Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf_HoldBrake"),
                "im_vehicle_brake_system_xbr_brake_hold_mode": (
                    "Rte_SWC_InputManager_RPort_postp_im_vehicle_DEP_postp_im_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_vehicle_DEP_postp_im_vehicle_Buf_brake_system_xbr_brake_hold_mode"),
                "om_PropXBR_ExtAccelDem": (
                    "Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf_ExtAccelDem"),

            },
            {
                "momentary_track_dx": (
                    "Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf_momentary_track_dx"),
                "acc_following_time": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_following_time"),
                "acc_vehicle_motion_v": (
                    "Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf_acc_vehicle_motion_v"),
                "im_vehicle_motion_ego_long_accel": (
                    "Rte_SWC_InputManager_RPort_postp_im_vehicle_DEP_postp_im_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_vehicle_DEP_postp_im_vehicle_Buf_vehicle_motion_ego_long_accel"),
                "acc_vehicle_motion_ego_longitudinal_state": (
                    "Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf_acc_vehicle_motion_ego_longitudinal_state"),
                "momentary_track_vx": (
                    "Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf_momentary_track_vx"),
                "acc_driver_cc_setspeed": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_cc_setspeed"),
                "momentary_track_valid": (
                    "Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf_momentary_track_valid"),
                "momentary_track_ax": (
                    "Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_sensor_DEP_im_acc_sensor_Buf_momentary_track_ax"),
                "acc_vehicle_motion_ego_curvature": (
                    "Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf_acc_vehicle_motion_ego_curvature"),
                "acc_control_output_ax_dem": (
                    "Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf_acc_control_output_acc_brake_acceleration_demand"),
                "acc_control_output_sna_ax_dem": (
                    "Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf_acc_control_output_sna_acc_brake_acceleration_demand"),
                "acc_control_output_M_perc_Eng_dem": (
                    "Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf_acc_control_output_acc_engine_torque_demand"),
                "acc_control_output_sna_M_perc_Eng_dem": (
                    "Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf_acc_control_output_sna_acc_engine_torque_demand"),
                "acc_powertrain_M_perc_eng": (
                    "Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_vehicle_DEP_im_acc_vehicle_Buf_acc_powertrain_M_perc_eng"),
                "om_TSC1_ReqTorqueLimit": (
                    "Rte_SWCNorm_RPort_norm_om_TSC1_DEP_om_norm_TSC1_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_TSC1_DEP_om_norm_TSC1_Buf_engine_requested_torque_torque_limit"),
                "acc_driver_cc_active": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_cc_active"),
                "acc_control_output_cc_disable": (
                    "Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf_acc_control_output_cc_disable"),
                "om_CCVS2_CruiseControlDisableCommand": (
                    "Rte_SWCNorm_RPort_norm_om_CCVS2_DEP_om_norm_CCVS2_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_CCVS2_DEP_om_norm_CCVS2_Buf_cc_disable_command"),
                "om_CCVS2_CruiseControlPauseCommand": (
                    "Rte_SWCNorm_RPort_norm_om_CCVS2_DEP_om_norm_CCVS2_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_CCVS2_DEP_om_norm_CCVS2_Buf_cc_pause_command"),
                "om_CCVS2_CruiseControlResumeCommand": (
                    "Rte_SWCNorm_RPort_norm_om_CCVS2_DEP_om_norm_CCVS2_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_CCVS2_DEP_om_norm_CCVS2_Buf_cc_resume_command"),
                "om_PropXBR_HoldBrake": (
                    "Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf_brake_hold_state"),
                "im_vehicle_brake_system_xbr_brake_hold_mode": (
                    "Rte_SWC_InputManager_RPort_postp_im_vehicle_DEP_postp_im_vehicle_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_InputManager_RPort_postp_im_vehicle_DEP_postp_im_vehicle_Buf_brake_system_xbr_brake_hold_mode"),
                "om_PropXBR_ExtAccelDem": (
                    "Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_PropXBR_DEP_om_norm_PropXBR_Buf_external_acceleration_demand"),
            },
        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        if 'momentary_track_valid' not in group:
            raise SignalGroupError('momentary_track_valid signal not found, object data masking not possible')
        return group

    def view(self, group):

        if self.id.get("developer"):
            pn = datavis.cPlotNavigator(title=__doc__)

            time, valid = group.get_signal("momentary_track_valid")
            valid_bool = valid.astype(np.bool)

            ax = pn.addAxis(ylabel="dist.")
            if 'momentary_track_dx' in group:
                time, dx, unit = group.get_signal_with_unit("momentary_track_dx")
                unit = 'm' if not unit else unit
                dx_masked = np.ma.masked_array(dx, mask=~valid_bool)
                pn.addSignal2Axis(ax, "momentary_track.dx", time, dx_masked, unit=unit, color='g')
            if "acc_following_time" in group:
                twinax = pn.addTwinAxis(ax, ylabel='following time', color='gray')
                time, t_follow, unit = group.get_signal_with_unit("acc_following_time")
                unit = 's' if not unit else unit
                pn.addSignal2Axis(twinax, "following_time", time, t_follow, unit=unit, color='lightgrey')

            ax = pn.addAxis(ylabel="speed")
            if 'acc_vehicle_motion_v' in group and 'momentary_track_vx' in group:
                time, acc_vehicle_motion_v, unit = group.get_signal_with_unit("acc_vehicle_motion_v")
                unit = 'm/s' if not unit else unit
                pn.addSignal2Axis(ax, "vehicle_motion.v", time, acc_vehicle_motion_v, unit=unit)
                time, track_vx, unit = group.get_signal_with_unit("momentary_track_vx")
                unit = 'm/s' if not unit else unit
                track_vx_masked = np.ma.masked_array(track_vx, mask=~valid_bool)
                track_vx_abs_masked = track_vx_masked + acc_vehicle_motion_v
                pn.addSignal2Axis(ax, "momentary_track.vx (abs)", time, track_vx_abs_masked, unit=unit, color='g')
            if 'acc_driver_cc_setspeed' in group:
                time, value, unit = group.get_signal_with_unit("acc_driver_cc_setspeed")
                unit = 'm/s' if not unit else unit
                pn.addSignal2Axis(ax, "driver.cc_setspeed", time, value, unit=unit, color='blue', ls='--')
            if "acc_vehicle_motion_ego_curvature" in group:
                twinax = pn.addTwinAxis(ax, ylabel='curvature', color='gray')
                time, curvature, unit = group.get_signal_with_unit("acc_vehicle_motion_ego_curvature")
                unit = '1/m' if not unit else unit
                pn.addSignal2Axis(twinax, "vehicle_motion.ego_curvature", time, curvature, unit=unit, color='lightgrey')

            ax = pn.addAxis(ylabel="motion st.", yticks=as_yticks(EgoLonState))
            if 'acc_vehicle_motion_ego_longitudinal_state' in group:
                time, ego_longitudinal_state = group.get_signal("acc_vehicle_motion_ego_longitudinal_state")
                pn.addSignal2Axis(ax, "vehicle_motion.ego_longitudinal_state", time, ego_longitudinal_state, color='blue')
            twinax = pn.addTwinAxis(ax, ylabel="brk. hold", color=RED)
            if 'om_PropXBR_HoldBrake' in group:
                time, value = group.get_signal("om_PropXBR_HoldBrake")
                pn.addSignal2Axis(twinax, "om_PropXBR.HoldBrake", time, value, color=RED)
            if 'im_vehicle_brake_system_xbr_brake_hold_mode' in group:
                time, value = group.get_signal("im_vehicle_brake_system_xbr_brake_hold_mode")
                pn.addSignal2Axis(twinax, "vehicle_xbr_brake_hold_mode", time, value, color='b', ls='--')
                # adjust yticks based on max value of signal (TODO: proper enum)
                yticks = range(np.max(value) + 1)
                twinax.set_yticks(yticks)
                twinax.set_yticklabels(["%s" % i for i in yticks])

            ax = pn.addAxis(ylabel="accel.")
            if 'im_vehicle_motion_ego_long_accel' in group:
                time, ax_value, unit = group.get_signal_with_unit("im_vehicle_motion_ego_long_accel")
                unit = 'm/s/s' if not unit else unit
                pn.addSignal2Axis(ax, "ego_long_accel", time, ax_value, unit=unit, color='b')
            if 'momentary_track_ax' in group:
                time, ax_value, unit = group.get_signal_with_unit("momentary_track_ax")
                unit = 'm/s/s' if not unit else unit
                ax_masked = np.ma.masked_array(ax_value, mask=~valid_bool)
                pn.addSignal2Axis(ax, "momentary_track.ax", time, ax_masked, unit=unit, color='g')
            if "acc_control_output_ax_dem" in group and "acc_control_output_sna_ax_dem" in group:
                time, xbr, unit = group.get_signal_with_unit("acc_control_output_ax_dem")
                unit = 'm/s/s' if not unit else unit
                xbr_sna = group.get_value("acc_control_output_sna_ax_dem")
                xbr_masked = np.ma.masked_array(xbr, mask=xbr_sna)
                pn.addSignal2Axis(ax, "control_output.ax_dem", time, xbr_masked, unit=unit, color='orange')
            if 'om_PropXBR_ExtAccelDem' in group:
                time, xbr, unit = group.get_signal_with_unit("om_PropXBR_ExtAccelDem")
                if (xbr.dtype == 'uint8') | (xbr.dtype == 'uint16'):
                    xbr = ((xbr * 1/2048.) + (-15.687))
                # if xbr data type is not of float, then convert back to float (optional, backward-compatible)
                unit = 'm/s/s' if not unit else unit
                xbr_masked = np.ma.masked_array(xbr, mask=xbr > 0.)
                pn.addSignal2Axis(ax, "om_PropXBR.ExtAccelDem", time, xbr_masked, unit=unit, color=RED)

            ax = pn.addAxis(ylabel="eng. trq.")
            if "acc_powertrain_M_perc_eng" in group:
                time, torque, unit = group.get_signal_with_unit("acc_powertrain_M_perc_eng")
                unit = '%' if not unit else unit
                pn.addSignal2Axis(ax, "powertrain.M_perc_eng", time, torque, unit=unit)
            if "acc_control_output_M_perc_Eng_dem" in group and "acc_control_output_sna_M_perc_Eng_dem" in group:
                time, torque, unit = group.get_signal_with_unit("acc_control_output_M_perc_Eng_dem")
                unit = '%' if not unit else unit
                torque_sna = group.get_value("acc_control_output_sna_M_perc_Eng_dem")
                torque_masked = np.ma.masked_array(torque, mask=torque_sna)
                pn.addSignal2Axis(ax, "control_output.M_perc_Eng_dem", time, torque_masked, unit=unit, color='orange')
            if "om_TSC1_ReqTorqueLimit" in group:
                time, torque, unit = group.get_signal_with_unit("om_TSC1_ReqTorqueLimit")
                if (torque.dtype == 'uint8') | (torque.dtype == 'uint16'):
                    torque = ((torque * 1.0) + (-125))
                unit = '%' if not unit else unit
                torque_masked = np.ma.masked_array(torque, mask=torque >= 125.)
                pn.addSignal2Axis(ax, "om_TSC1.ReqTorqueLimit", time, torque_masked, unit=unit, color=RED)

            ax = pn.addAxis(ylabel="eng. cc", ylim=(-0.5, 7.5))
            ax.set_yticks(range(8))
            ax.set_yticklabels([str(i) for i in (0, 1) * 4])
            if "acc_driver_cc_active" in group:
                time, value = group.get_signal("acc_driver_cc_active")
                pn.addSignal2Axis(ax, "driver.cc_active", time, value, offset=6, displayscaled=False, color='blue')
            # if "acc_control_output_cc_disable" in group:
            # time, value = group.get_signal("acc_control_output_cc_disable")
            # pn.addSignal2Axis(ax, "control_output.cc_disable", time, value, offset=4, displayscaled=False, color='orange')
            if 'om_CCVS2_CruiseControlDisableCommand' in group:
                time, value = group.get_signal("om_CCVS2_CruiseControlDisableCommand")
                pn.addSignal2Axis(ax, "om_CCVS2.CruiseControlDisableCommand", time, value, offset=4, displayscaled=False,
                                  color=RED)
            if "om_CCVS2_CruiseControlPauseCommand" in group:
                time, value = group.get_signal("om_CCVS2_CruiseControlPauseCommand")
                pn.addSignal2Axis(ax, "om_CCVS2.CruiseControlPauseCommand", time, value, offset=2, displayscaled=False,
                                  color=RED)
            if "om_CCVS2_CruiseControlResumeCommand" in group:
                time, value = group.get_signal("om_CCVS2_CruiseControlResumeCommand")
                pn.addSignal2Axis(ax, "om_CCVS2.CruiseControlResumeCommand", time, value, offset=0, displayscaled=False,
                                  color=RED)

            self.sync.addClient(pn)
            return

        if self.id.get("tester"):
            pn = datavis.cPlotNavigator(title=__doc__)

            time, valid = group.get_signal("momentary_track_valid")
            valid_bool = valid.astype(np.bool)

            ax = pn.addAxis(ylabel="dist.")
            if 'momentary_track_dx' in group:
                time, dx, unit = group.get_signal_with_unit("momentary_track_dx")
                unit = 'm' if not unit else unit
                dx_masked = np.ma.masked_array(dx, mask=~valid_bool)
                pn.addSignal2Axis(ax, "momentary_track.dx", time, dx_masked, unit=unit, color='g')
            if "acc_following_time" in group:
                twinax = pn.addTwinAxis(ax, ylabel='following time', color='gray')
                time, t_follow, unit = group.get_signal_with_unit("acc_following_time")
                unit = 's' if not unit else unit
                pn.addSignal2Axis(twinax, "following_time", time, t_follow, unit=unit, color='lightgrey')

            ax = pn.addAxis(ylabel="speed")
            if 'acc_vehicle_motion_v' in group and 'momentary_track_vx' in group:
                time, acc_vehicle_motion_v, unit = group.get_signal_with_unit("acc_vehicle_motion_v")
                unit = 'kmph' if not unit else unit
                acc_vehicle_motion_v = 3.6 * acc_vehicle_motion_v
                pn.addSignal2Axis(ax, "vehicle_motion.v", time, acc_vehicle_motion_v, unit=unit)
                time, track_vx, unit = group.get_signal_with_unit("momentary_track_vx")
                unit = 'kmph' if not unit else unit
                track_vx = 3.6 * track_vx
                track_vx_masked = np.ma.masked_array(track_vx, mask=~valid_bool)
                track_vx_abs_masked = track_vx_masked + acc_vehicle_motion_v
                pn.addSignal2Axis(ax, "momentary_track.vx (abs)", time, track_vx_abs_masked, unit=unit, color='g')
            if 'acc_driver_cc_setspeed' in group:
                time, value, unit = group.get_signal_with_unit("acc_driver_cc_setspeed")
                unit = 'kmph' if not unit else unit
                value = 3.6 * value
                pn.addSignal2Axis(ax, "driver.cc_setspeed", time, value, unit=unit, color='blue', ls='--')
            if "acc_vehicle_motion_ego_curvature" in group:
                twinax = pn.addTwinAxis(ax, ylabel='curvature', color='gray')
                time, curvature, unit = group.get_signal_with_unit("acc_vehicle_motion_ego_curvature")
                unit = '1/m' if not unit else unit
                pn.addSignal2Axis(twinax, "vehicle_motion.ego_curvature", time, curvature, unit=unit, color='lightgrey')

            ax = pn.addAxis(ylabel="motion st.", yticks=as_yticks(EgoLonState))
            if 'acc_vehicle_motion_ego_longitudinal_state' in group:
                time, ego_longitudinal_state = group.get_signal("acc_vehicle_motion_ego_longitudinal_state")
                pn.addSignal2Axis(ax, "vehicle_motion.ego_longitudinal_state", time, ego_longitudinal_state,
                                  color='blue')
            twinax = pn.addTwinAxis(ax, ylabel="brk. hold", color=RED)
            if 'om_PropXBR_HoldBrake' in group:
                time, value = group.get_signal("om_PropXBR_HoldBrake")
                pn.addSignal2Axis(twinax, "om_PropXBR.HoldBrake", time, value, color=RED)
            if 'im_vehicle_brake_system_xbr_brake_hold_mode' in group:
                time, value = group.get_signal("im_vehicle_brake_system_xbr_brake_hold_mode")
                pn.addSignal2Axis(twinax, "vehicle_xbr_brake_hold_mode", time, value, color='b', ls='--')
                # adjust yticks based on max value of signal (TODO: proper enum)
                yticks = range(np.max(value) + 1)
                twinax.set_yticks(yticks)
                twinax.set_yticklabels(["%s" % i for i in yticks])

            ax = pn.addAxis(ylabel="accel.")
            if 'im_vehicle_motion_ego_long_accel' in group:
                time, ax_value, unit = group.get_signal_with_unit("im_vehicle_motion_ego_long_accel")
                unit = 'kmph' if not unit else unit
                ax_value = 3.6 * ax_value
                pn.addSignal2Axis(ax, "ego_long_accel", time, ax_value, unit=unit, color='b')
            if 'momentary_track_ax' in group:
                time, ax_value, unit = group.get_signal_with_unit("momentary_track_ax")
                unit = 'kmph' if not unit else unit
                ax_value = 3.6 * ax_value
                ax_masked = np.ma.masked_array(ax_value, mask=~valid_bool)
                pn.addSignal2Axis(ax, "momentary_track.ax", time, ax_masked, unit=unit, color='g')
            if "acc_control_output_ax_dem" in group and "acc_control_output_sna_ax_dem" in group:
                time, xbr, unit = group.get_signal_with_unit("acc_control_output_ax_dem")
                unit = 'kmph' if not unit else unit
                xbr = 3.6 * xbr
                xbr_sna = group.get_value("acc_control_output_sna_ax_dem")
                xbr_masked = np.ma.masked_array(xbr, mask=xbr_sna)
                pn.addSignal2Axis(ax, "control_output.ax_dem", time, xbr_masked, unit=unit, color='orange')
            if 'om_PropXBR_ExtAccelDem' in group:
                time, xbr, unit = group.get_signal_with_unit("om_PropXBR_ExtAccelDem")
                if (xbr.dtype == 'uint8') | (xbr.dtype == 'uint16'):
                    xbr = ((xbr * 1 / 2048.) + (-15.687))
                # if xbr data type is not of float, then convert back to float (optional, backward-compatible)
                unit = 'kmph' if not unit else unit
                xbr = 3.6 * xbr
                xbr_masked = np.ma.masked_array(xbr, mask=xbr > 0.)
                pn.addSignal2Axis(ax, "om_PropXBR.ExtAccelDem", time, xbr_masked, unit=unit, color=RED)

            ax = pn.addAxis(ylabel="eng. trq.")
            if "acc_powertrain_M_perc_eng" in group:
                time, torque, unit = group.get_signal_with_unit("acc_powertrain_M_perc_eng")
                unit = '%' if not unit else unit
                pn.addSignal2Axis(ax, "powertrain.M_perc_eng", time, torque, unit=unit)
            if "acc_control_output_M_perc_Eng_dem" in group and "acc_control_output_sna_M_perc_Eng_dem" in group:
                time, torque, unit = group.get_signal_with_unit("acc_control_output_M_perc_Eng_dem")
                unit = '%' if not unit else unit
                torque_sna = group.get_value("acc_control_output_sna_M_perc_Eng_dem")
                torque_masked = np.ma.masked_array(torque, mask=torque_sna)
                pn.addSignal2Axis(ax, "control_output.M_perc_Eng_dem", time, torque_masked, unit=unit, color='orange')
            if "om_TSC1_ReqTorqueLimit" in group:
                time, torque, unit = group.get_signal_with_unit("om_TSC1_ReqTorqueLimit")
                if (torque.dtype == 'uint8') | (torque.dtype == 'uint16'):
                    torque = ((torque * 1.0) + (-125))
                unit = '%' if not unit else unit
                torque_masked = np.ma.masked_array(torque, mask=torque >= 125.)
                pn.addSignal2Axis(ax, "om_TSC1.ReqTorqueLimit", time, torque_masked, unit=unit, color=RED)

            ax = pn.addAxis(ylabel="eng. cc", ylim=(-0.5, 7.5))
            ax.set_yticks(range(8))
            ax.set_yticklabels([str(i) for i in (0, 1) * 4])
            if "acc_driver_cc_active" in group:
                time, value = group.get_signal("acc_driver_cc_active")
                pn.addSignal2Axis(ax, "driver.cc_active", time, value, offset=6, displayscaled=False, color='blue')
            # if "acc_control_output_cc_disable" in group:
            # time, value = group.get_signal("acc_control_output_cc_disable")
            # pn.addSignal2Axis(ax, "control_output.cc_disable", time, value, offset=4, displayscaled=False, color='orange')
            if 'om_CCVS2_CruiseControlDisableCommand' in group:
                time, value = group.get_signal("om_CCVS2_CruiseControlDisableCommand")
                pn.addSignal2Axis(ax, "om_CCVS2.CruiseControlDisableCommand", time, value, offset=4,
                                  displayscaled=False,
                                  color=RED)
            if "om_CCVS2_CruiseControlPauseCommand" in group:
                time, value = group.get_signal("om_CCVS2_CruiseControlPauseCommand")
                pn.addSignal2Axis(ax, "om_CCVS2.CruiseControlPauseCommand", time, value, offset=2, displayscaled=False,
                                  color=RED)
            if "om_CCVS2_CruiseControlResumeCommand" in group:
                time, value = group.get_signal("om_CCVS2_CruiseControlResumeCommand")
                pn.addSignal2Axis(ax, "om_CCVS2.CruiseControlResumeCommand", time, value, offset=0, displayscaled=False,
                                  color=RED)

            self.sync.addClient(pn)
            return
