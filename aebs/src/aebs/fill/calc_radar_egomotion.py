# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import sys

import interface
import numpy as np
import scipy.signal
from measparser.signalgroup import SignalGroupError
from primitives.egomotion import EgoMotion

EXP_UNITS = {
    'yaw_rate': ('rad/s',),
    'vx': ('m/s',),
    'ax': ('m/s^2',),
}

UNKNOWN_FRAME_MSG = 'Warning: ' \
                    'unknown FLR20 coordinate frame, assuming right=positive configuration (%s)'

init_params = {
    'flr25': dict(
        common_time="calc_common_time-flr25",
        sgs=[{
            "vx": ("VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
            "yaw_rate": ("VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Lateral_YawRate_YawRate"),
            "ax": ("VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Accel"),
        },
            {
                "vx": (
                "ARS4xx Device.AlgoVehCycle.VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Velocity"),
                "yaw_rate": (
                "ARS4xx Device.AlgoVehCycle.VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Lateral_YawRate_YawRate"),
                "ax": (
                "ARS4xx Device.AlgoVehCycle.VehDyn", "ARS4xx_Device_AlgoVehCycle_VehDyn_Longitudinal_MotVar_Accel"),
            },
            {
                "vx": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
                "yaw_rate": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Lateral_YawRate_YawRate"),
                "ax": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Accel"),
            },
            {
                "vx": ("VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
                "yaw_rate": ("VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Lateral_YawRate_YawRate"),
                "ax": ("VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Accel"),
            },
            {
                "vx": ("CAN_MFC_Public_middle_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
                "yaw_rate": ("CAN_MFC_Public_middle_VDC2_0B", "VDC2_YawRate_0B"),
                "ax": ("CAN_MFC_Public_middle_VDC2_0B", "VDC2_LongAccel_0B"),
            }
        ]
    ),
    'flc25': dict(
        common_time="calc_common_time-flc25",
        sgs=[
            {
                "vx": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
                "yaw_rate": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Lateral_YawRate_YawRate"),
                "ax": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Accel"),
            },

            {
                "vx": ("VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
                "yaw_rate": ("VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Lateral_YawRate_YawRate"),
                "ax": ("VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Accel"),
            },

            {
                "vx": ("VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Velocity"),
                "yaw_rate": ("VehDyn", "MFC5xx_Device_VDY_VehDyn_Lateral_YawRate_YawRate"),
                "ax": ("VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Accel"),
            },

            {
                "vx": ("MFC5xx Device.VDY.VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Velocity"),
                "yaw_rate": ("MFC5xx Device.VDY.VehDyn", "MFC5xx_Device_VDY_VehDyn_Lateral_YawRate_YawRate"),
                "ax": ("MFC5xx Device.VDY.VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Accel"),
            },
            {
                "vx": ("CAN_MFC_Public_middle_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
                "yaw_rate": ("CAN_MFC_Public_middle_VDC2_0B", "VDC2_YawRate_0B"),
                "ax": ("CAN_MFC_Public_middle_VDC2_0B", "VDC2_LongAccel_0B"),
            },
            {
                "vx": ("CAN_MFC_Public_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
                "yaw_rate": ("CAN_MFC_Public_VDC2_0B", "VDC2_YawRate_0B"),
                "ax": ("CAN_MFC_Public_VDC2_0B", "VDC2_LongAccel_0B"),

            }
        ]
    ),
}


class Calc(interface.iCalc):
    dep = {
        'common_time': None
    }

    def init(self, common_time, sgs):
        self.dep["common_time"] = common_time
        self.sgs = sgs
        return

    def check(self):
        commonTime = self.modules.fill(self.dep["common_time"])
        group = self.source.selectSignalGroup(self.sgs)
        return commonTime, group

    def fill(self, commonTime, group):
        # rescale_kwargs = {'ScaleTime': commonTime, 'Order': 'valid'}
        _, vx, unit = group.get_signal_with_unit('vx', ScaleTime=commonTime)
        _, ax, unit = group.get_signal_with_unit('ax', ScaleTime=commonTime)

        _, yaw_rate, unit_yawrate = group.get_signal_with_unit('yaw_rate', ScaleTime=commonTime)
        check_unit('yaw_rate', unit_yawrate)

        # yaw_rate *= -1.0 #TODO assuming left positive

        ego_motion = EgoMotion(commonTime, vx, yaw_rate, ax)
        return ego_motion


def check_unit(alias, unit):
    """
    Check whether the signal's physical unit is the expected one or not.
    Raise AssertionError in the latter case.
    """
    if unit == '':
        print >> sys.stderr, "Unit check not possible for %s." % alias
        return
    if unit not in EXP_UNITS[alias]:
        raise AssertionError('unexpected unit for %s: %s' % (alias, unit))
    return


def is_left_positive(source, exception=False):
    """
    Checks the direction of the lateral axis of the radar's coordinate frame,
    based on the radar's and a reference sensor's yaw rate signals (prefers the
    sign which gives the smaller LS error).
    """
    radar_sgs = [
        {'yawrate_radar_deg': ('General_radar_status', 'cvd_yawrate')},
    ]
    ref_sgs = [
        {'yawrate_ref': ('VDC2--Message--S_CAM_J1939_Jan_16_2013', 'YawRate')},
        {'yawrate_ref': ('VDC2--Message--H566_All_v_04', 'YawRate')},
        {'yawrate_ref': ('VDC2_0B', 'VDC2_YawRate_0B')},
        {'yawrate_ref': ('VDC2', 'YAW_Rate')},
        {'yawrate_ref': ('VDC2_0B_s0B_VDC2_0B_CAN21', 'VDC2_YawRate_0B')},
        {'yawrate_ref': ('VDC2', 'YawRate')},
        {'yawrate_ref': ('RadarFC', 'evi.General_TC.psiDtOpt')},
        {'yawrate_ref': ('MRR1plus', 'evi.General_TC.psiDtOpt')},
        {"yawrate_ref": ("CAN_MFC_Public_VDC2_0B", "VDC2_YawRate_0B")},
    ]
    left_positive = False
    try:
        radar_group = source.selectSignalGroup(radar_sgs)
        ref_group = source.selectSignalGroup(ref_sgs)
        time, yawrate_radar_deg, unit_radar = \
            radar_group.get_signal_with_unit('yawrate_radar_deg')
        # check_unit('yawrate_radar_deg', unit_radar)
        yawrate_radar = np.deg2rad(yawrate_radar_deg)
        _, yawrate_ref, unit_ref = \
            ref_group.get_signal_with_unit('yawrate_ref', ScaleTime=time)
    # check_unit('yawrate_ref', unit_ref)
    except (SignalGroupError, AssertionError), error:
        if exception:
            raise
        else:
            print >> sys.stderr, UNKNOWN_FRAME_MSG % error.message
            return left_positive
    else:
        left_positive = (np.sum((yawrate_radar - yawrate_ref) ** 2.0) <
                         np.sum((-yawrate_radar - yawrate_ref) ** 2.0))
    return left_positive


### Copied from viewAEBS_1_accelerations
### TODO: rm
def _LPF_butter_4o_5Hz(t, input_signal):
    # input:  t             time [sec] signal as np array
    #         input_signal  input signal as np array
    # return: filtered signal as np array

    # parameters
    n_order = 4  # filter order of butterworth filter
    f0 = 5.0  # -3dB corner frequency [Hz] of butterworth filter

    fs = 1.0 / np.mean(np.diff(t))  # sampling frequency (assumption: constant sampling interval)
    f_nyq = fs / 2.0  # Nyquist frequency (= 1/2 sampling frequency)
    Wn = f0 / f_nyq  # normalized corner frequency  (related to Nyquist frequency)

    # calculate filter coefficients
    B, A = scipy.signal.butter(n_order, Wn)

    # calculate filter
    out_signal = scipy.signal.lfilter(B, A, input_signal)

    return out_signal


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"\\pu2w6474\shared-drive\measurements\oncoming_for_stationary_obj_cem_tpf\mi5id5033__2022-04-26_11-53-10.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_common_time = manager_modules.calc('calc_radar_egomotion-flr25@aebs.fill', manager)
    print flr25_common_time
