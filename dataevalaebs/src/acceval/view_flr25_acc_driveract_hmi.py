# -*- dataeval: init -*-

"ACC driver activation and HMI signals"

import numpy as np

from pyutils.enum import enum
import datavis
from interface import iView

from acceval.view_flr25_acc_kinematics_control import as_yticks, RED

Ego_TurnSignalState = enum(
    NO_TURN_SIGNAL=0,
    LEFT_TURN_SIGNAL=1,
    RIGHT_TURN_SIGNAL=2,
    BOTH_TURN_SIGNALS=3,
)

Acc_RestrictionModeType = enum(
    FULLY_OPERATIONAL=0,
    IMMEDIATE=1,
    CONTROLLED=2,
    BRAKE_ONLY=3,
    IMMEDIATE_NO_ERROR=4,
    BRAKE_ONLY_NO_ERROR=5,
    BRAKE_ONLY_EMERGENCY_FUNCTION=6,
)

Om_Acc1_Mode = enum(
    OFF=0,
    SPEED_CONTROL=1,
    DISTANCE_CONTROL=2,
    OVERTAKE_MODE=3,
    HOLD_MODE=4,
    FINISH_MODE=5,
    DISABLED=6,
    NOT_AVAILABLE=7,
)

Om_PropHmi_AccResumeState = enum(
    NOT_ALLOWED=0,
    SLOW_AND_GO=1,
    DRIVER_GO=2,
    AUTO_GO=3,
)

Om_PropHmi_AccBrakeHoldReleaseWarning = enum(
    OFF=0,
    AUDIBLE_ONLY=1,
    VISUAL_ONLY=2,
    AUDIBLE_AND_VISUAL=3,
)

init_params = {
    "DEVELOPER": dict(id=dict(developer=True)),
    "TESTER": dict(id=dict(tester=True)),
}

def get_n_plot(group, signame, pn, ax, unit_replacement=None, label_replacement=None, parameter=None, **kwargs):
    if signame in group:
        time, value, unit = group.get_signal_with_unit(signame)
        unit = unit_replacement if not unit else unit
        if parameter == 'tester':
            value = np.rad2deg(value)
        label = signame if not label_replacement else label_replacement
        pn.addSignal2Axis(ax, label, time, value, unit=unit, **kwargs)
    return


class View(iView):
    def init(self, id):
        self.id = id
        return

    def check(self):
        sgs = [
            {
                "acc_driver_main_switch": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_main_switch"),
                "acc_driver_set_button": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_set_button"),
                "acc_driver_pause_button": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_pause_button"),
                "acc_driver_resume_button": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_resume_button"),
                "acc_driver_accel_pedal_pos": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_accel_pedal_pos"),
                "acc_driver_brake_pedal_switch": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_brake_pedal_switch"),
                "acc_driver_str_whl_angle": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_str_whl_angle"),
                "acc_driver_turn_indicator": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_turn_indicator"),
                "acc_pedestrian_status_auto_go_cancelled_by_pedestrian": (
                    "Rte_SWC_ACC_RPort_acc_msm_DEP_msm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_msm_DEP_msm_acc_Buf_acc_pedestrian_status_auto_go_cancelled_by_pedestrian"),
                "acc_restriction_mode_restriction_mode": (
                    "Rte_SWC_ACC_RPort_acc_msm_DEP_msm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_msm_DEP_msm_acc_Buf_acc_restriction_mode_restriction_mode"),
                "acc_hmi_output_acc_mode": (
                    "Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf_acc_hmi_output_acc_mode"),
                "om_ACC1_Mode": (
                    "Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf_Mode"),
                "om_ACC1_SystemShutoffWarning": (
                    "Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf_SystemShutoffWarning"),
                "om_ACC1_ForwardCollisionWarning": (
                    "Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf_ForwardCollisionWarning"),
                "om_ACC1_DistanceAlertSignal": (
                    "Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf_DistanceAlertSignal"),
                "om_PropHMI_AccBrakeHoldReleaseWarning": (
                    "Rte_SWCNorm_RPort_norm_om_PropHMI_DEP_om_norm_PropHMI_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_PropHMI_DEP_om_norm_PropHMI_Buf_AccBrakeHoldReleaseWarning"),
                "om_PropHMI_AccResumeState": (
                    "Rte_SWCNorm_RPort_norm_om_PropHMI_DEP_om_norm_PropHMI_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_PropHMI_DEP_om_norm_PropHMI_Buf_AccResumeState"),
            },
            {
                "acc_driver_main_switch": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_main_switch"),
                "acc_driver_set_button": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_set_button"),
                "acc_driver_pause_button": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_pause_button"),
                "acc_driver_resume_button": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_resume_button"),
                "acc_driver_accel_pedal_pos": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_accel_pedal_pos"),
                "acc_driver_brake_pedal_switch": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_brake_pedal_switch"),
                "acc_driver_str_whl_angle": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_str_whl_angle"),
                "acc_driver_turn_indicator": (
                    "Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_im_driver_DEP_im_acc_driver_Buf_turn_indicator"),
                "acc_pedestrian_status_auto_go_cancelled_by_pedestrian": (
                    "Rte_SWC_ACC_RPort_acc_msm_DEP_msm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_msm_DEP_msm_acc_Buf_acc_pedestrian_status_auto_go_cancelled_by_pedestrian"),
                "acc_restriction_mode_restriction_mode": (
                    "Rte_SWC_ACC_RPort_acc_msm_DEP_msm_acc_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_ACC_RPort_acc_msm_DEP_msm_acc_Buf_acc_restriction_mode_restriction_mode"),
                "acc_hmi_output_acc_mode": (
                    "Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWC_OutputManager_RPort_acc_om_DEP_acc_om_Buf_acc_hmi_output_acc_mode"),
                "om_ACC1_Mode": (
                    "Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf_acc_mode"),
                "om_ACC1_SystemShutoffWarning": (
                    "Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf_acc_system_shutoff_warning"),
                "om_ACC1_ForwardCollisionWarning": (
                    "Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf_forward_collision_warning"),
                "om_ACC1_DistanceAlertSignal": (
                    "Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_ACC1_DEP_om_norm_ACC1_Buf_acc_distance_alert_signal"),
                "om_PropHMI_AccBrakeHoldReleaseWarning": (
                    "Rte_SWCNorm_RPort_norm_om_PropHMI_DEP_om_norm_PropHMI_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_PropHMI_DEP_om_norm_PropHMI_Buf_acc_brake_hold_release_warning"),
                "om_PropHMI_AccResumeState": (
                    "Rte_SWCNorm_RPort_norm_om_PropHMI_DEP_om_norm_PropHMI_Buf",
                    "ARS4xx_Device_SW_Every10ms_Rte_SWCNorm_RPort_norm_om_PropHMI_DEP_om_norm_PropHMI_Buf_acc_resume_state"),
            },
        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        if self.id.get("developer"):

            pn = datavis.cPlotNavigator(title=__doc__)

            ax = pn.addAxis(ylabel="buttons", ylim=(-0.5, 7.5))
            ax.set_yticks(range(8))
            ax.set_yticklabels([str(i) for i in (0, 1) * 4])
            if "acc_driver_main_switch" in group:
                time, value = group.get_signal("acc_driver_main_switch")
                pn.addSignal2Axis(ax, "driver.main_switch", time, value, offset=6, displayscaled=False)
            if "acc_driver_set_button" in group:
                time, value = group.get_signal("acc_driver_set_button")
                pn.addSignal2Axis(ax, "driver.set_button", time, value, offset=4, displayscaled=False)
            if 'acc_driver_pause_button' in group:
                time, value = group.get_signal("acc_driver_pause_button")
                pn.addSignal2Axis(ax, "driver.pause_button", time, value, offset=2, displayscaled=False)
            if "acc_driver_resume_button" in group:
                time, value = group.get_signal("acc_driver_resume_button")
                pn.addSignal2Axis(ax, "driver.resume_button", time, value, offset=0, displayscaled=False)

            ax = pn.addAxis(ylabel="pedals")
            get_n_plot(group, 'acc_driver_accel_pedal_pos', pn, ax, label_replacement='driver.accel_pedal_pos')
            get_n_plot(group, 'acc_driver_brake_pedal_switch', pn, ax, label_replacement='driver.brake_pedal_switch')

            ax = pn.addAxis(ylabel="steering")

            get_n_plot(group, 'acc_driver_str_whl_angle', pn, ax, label_replacement='driver.str_whl_angle',
                       unit_replacement='rad', parameter='developer')
            twinax = pn.addTwinAxis(ax, yticks=as_yticks(Ego_TurnSignalState), color='g')
            get_n_plot(group, 'acc_driver_turn_indicator', pn, twinax, label_replacement='driver.turn_indicator', color='g')

            ax = pn.addAxis(ylabel="mode", yticks=as_yticks(Om_Acc1_Mode))
            get_n_plot(group, 'acc_hmi_output_acc_mode', pn, ax, label_replacement='hmi_output.acc_mode')
            get_n_plot(group, 'om_ACC1_Mode', pn, ax, label_replacement='om_ACC1.Mode')
            twinax = pn.addTwinAxis(ax, yticks=as_yticks(Acc_RestrictionModeType), color='g')
            get_n_plot(group, 'acc_restriction_mode_restriction_mode', pn, twinax,
                       label_replacement='status.restriction_mode', color='g')

            ax = pn.addAxis(ylabel="warning", ylim=(-0.5, 9.5))
            ax.set_yticks(range(10))
            enum_ticks = ['%s(%d)' % (k, v) for k, v in Om_PropHmi_AccBrakeHoldReleaseWarning._asdict().iteritems()]
            ax.set_yticklabels(enum_ticks + [str(i) for i in (0, 1) * 3])
            if "om_ACC1_SystemShutoffWarning" in group:
                time, value = group.get_signal("om_ACC1_SystemShutoffWarning")
                pn.addSignal2Axis(ax, "om_ACC1.SystemShutoffWarning", time, value, offset=8, displayscaled=False)
            if "om_ACC1_ForwardCollisionWarning" in group:
                time, value = group.get_signal("om_ACC1_ForwardCollisionWarning")
                pn.addSignal2Axis(ax, "om_ACC1.ForwardCollisionWarning", time, value, offset=6, displayscaled=False)
            if 'om_ACC1_DistanceAlertSignal' in group:
                time, value = group.get_signal("om_ACC1_DistanceAlertSignal")
                pn.addSignal2Axis(ax, "om_ACC1.DistanceAlertSignal", time, value, offset=4, displayscaled=False)
            if "om_PropHMI_AccBrakeHoldReleaseWarning" in group:
                time, value = group.get_signal("om_PropHMI_AccBrakeHoldReleaseWarning")
                pn.addSignal2Axis(ax, "om_PropHMI.AccBrakeHoldReleaseWarning", time, value, offset=0, displayscaled=False)

            ax = pn.addAxis(ylabel="resume st.", yticks=as_yticks(Om_PropHmi_AccResumeState))
            get_n_plot(group, 'om_PropHMI_AccResumeState', pn, ax, label_replacement='om_PropHMI.AccResumeState')

            self.sync.addClient(pn)
            return

        if self.id.get("tester"):

            pn = datavis.cPlotNavigator(title=__doc__)

            ax = pn.addAxis(ylabel="buttons", ylim=(-0.5, 7.5))
            ax.set_yticks(range(8))
            ax.set_yticklabels([str(i) for i in (0, 1) * 4])
            if "acc_driver_main_switch" in group:
                time, value = group.get_signal("acc_driver_main_switch")
                pn.addSignal2Axis(ax, "driver.main_switch", time, value, offset=6, displayscaled=False)
            if "acc_driver_set_button" in group:
                time, value = group.get_signal("acc_driver_set_button")
                pn.addSignal2Axis(ax, "driver.set_button", time, value, offset=4, displayscaled=False)
            if 'acc_driver_pause_button' in group:
                time, value = group.get_signal("acc_driver_pause_button")
                pn.addSignal2Axis(ax, "driver.pause_button", time, value, offset=2, displayscaled=False)
            if "acc_driver_resume_button" in group:
                time, value = group.get_signal("acc_driver_resume_button")
                pn.addSignal2Axis(ax, "driver.resume_button", time, value, offset=0, displayscaled=False)

            ax = pn.addAxis(ylabel="pedals")
            get_n_plot(group, 'acc_driver_accel_pedal_pos', pn, ax, label_replacement='driver.accel_pedal_pos')
            get_n_plot(group, 'acc_driver_brake_pedal_switch', pn, ax, label_replacement='driver.brake_pedal_switch')

            ax = pn.addAxis(ylabel="steering")

            get_n_plot(group, 'acc_driver_str_whl_angle', pn, ax, label_replacement='driver.str_whl_angle',
                       unit_replacement='deg', parameter='tester')
            twinax = pn.addTwinAxis(ax, yticks=as_yticks(Ego_TurnSignalState), color='g')
            get_n_plot(group, 'acc_driver_turn_indicator', pn, twinax, label_replacement='driver.turn_indicator', color='g')

            ax = pn.addAxis(ylabel="mode", yticks=as_yticks(Om_Acc1_Mode))
            get_n_plot(group, 'acc_hmi_output_acc_mode', pn, ax, label_replacement='hmi_output.acc_mode')
            get_n_plot(group, 'om_ACC1_Mode', pn, ax, label_replacement='om_ACC1.Mode')
            twinax = pn.addTwinAxis(ax, yticks=as_yticks(Acc_RestrictionModeType), color='g')
            get_n_plot(group, 'acc_restriction_mode_restriction_mode', pn, twinax,
                       label_replacement='status.restriction_mode', color='g')

            ax = pn.addAxis(ylabel="warning", ylim=(-0.5, 9.5))
            ax.set_yticks(range(10))
            enum_ticks = ['%s(%d)' % (k, v) for k, v in Om_PropHmi_AccBrakeHoldReleaseWarning._asdict().iteritems()]
            ax.set_yticklabels(enum_ticks + [str(i) for i in (0, 1) * 3])
            if "om_ACC1_SystemShutoffWarning" in group:
                time, value = group.get_signal("om_ACC1_SystemShutoffWarning")
                pn.addSignal2Axis(ax, "om_ACC1.SystemShutoffWarning", time, value, offset=8, displayscaled=False)
            if "om_ACC1_ForwardCollisionWarning" in group:
                time, value = group.get_signal("om_ACC1_ForwardCollisionWarning")
                pn.addSignal2Axis(ax, "om_ACC1.ForwardCollisionWarning", time, value, offset=6, displayscaled=False)
            if 'om_ACC1_DistanceAlertSignal' in group:
                time, value = group.get_signal("om_ACC1_DistanceAlertSignal")
                pn.addSignal2Axis(ax, "om_ACC1.DistanceAlertSignal", time, value, offset=4, displayscaled=False)
            if "om_PropHMI_AccBrakeHoldReleaseWarning" in group:
                time, value = group.get_signal("om_PropHMI_AccBrakeHoldReleaseWarning")
                pn.addSignal2Axis(ax, "om_PropHMI.AccBrakeHoldReleaseWarning", time, value, offset=0, displayscaled=False)

            ax = pn.addAxis(ylabel="resume st.", yticks=as_yticks(Om_PropHmi_AccResumeState))
            get_n_plot(group, 'om_PropHMI_AccResumeState', pn, ax, label_replacement='om_PropHMI.AccResumeState')

            self.sync.addClient(pn)
            return
