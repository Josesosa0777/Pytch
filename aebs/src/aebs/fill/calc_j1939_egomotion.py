# -*- dataeval: init -*-

import numpy as np
import scipy.signal

from primitives.egomotion import EgoMotion
import interface


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
    Wn = np.clip(Wn, 0, 1)
    # calculate filter coefficients
    B, A = scipy.signal.butter(n_order, Wn)

    # calculate filter
    out_signal = scipy.signal.lfilter(B, A, input_signal)

    return out_signal


###

class Calc(interface.iCalc):
    def check(self):
        sgs = [
            {
                "vx_kmh": ("CAN_MFC_Public_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
                "yaw_rate": ("CAN_MFC_Public_VDC2_0B", "VDC2_YawRate_0B"),
            },
            {
                "vx_kmh": ("CAN_MFC_ARS_Private_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
                "yaw_rate": ("CAN_MFC_ARS_Private_VDC2_0B", "VDC2_YawRate_0B"),
            },
            {
                "vx_kmh": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),
                "yaw_rate": ("VDC2_0B", "VDC2_YawRate_0B"),
            },
            {  # Iveco
                "vx_kmh": ("EBC2", "MeanFASpeed"),
                "yaw_rate": ("VDC2", "YawRate"),
            },
            {  # Actros
                "vx_kmh": ("EBC2_BS", "FA_Spd_Cval"),
                "yaw_rate": ("VDC2_BS", "yaw_rate"),
            },
            {  # FLR20, ARS430 combined endurance run
                "vx_kmh": ("EBC2_0B", "EBC2_MeanSpdFA_0B_C2"),
                "yaw_rate": ("VDC2_0B", "VDC2_YawRate_0B_C2"),
            },
            {
                "vx_kmh": ("EBC2_VDY_s0B", "EBC2_MeanSpdFA_0B"),
                "yaw_rate": ("VDC2_VDY_s0B", "VDC2_YawRate_0B"),
            },
            {
                "vx_kmh": ("EBC2_0B_s0B", "AverageFrontAxleWhlSpeed"),
                "yaw_rate": ("VDC2_0B_s0B", "YawRate"),
            },
            {
                "vx_kmh": ("EBC2_0B_s0B", "EBC2_FrontAxleSpeed_0B"),
                "yaw_rate": ("VDC2_0B_s0B", "VDC2_YawRate_0B"),
            },
            {
                "vx_kmh": ("EBC2_s0B", "FrontAxleSpeed"),
                "yaw_rate": ("VDC2_0B_s0B", "VDC2_YawRate_0B"),
            },
            {
                "vx_kmh": ("EBC2_0B_s0B", "EBC2_MeanSpdFA_0B_s0B"),
                "yaw_rate": ("VDC2_0B_s0B", "VDC2_YawRate_0B_s0B"),
            },
            {
                "vx_kmh": ("EBC2", "FrontAxleSpeed_s0B"),
                "yaw_rate": ("VDC2", "YawRate_s3E"),
            },
            {
                "yaw_rate": ("VDC2_3E_s3E", "VDC2_YawRate_3E"),
                "vx_kmh": ("EBC2_0B_s0B", "EBC2_FrontAxleSpeed_0B"),
            },
            {
                "vx_kmh": ("CAN_Vehicle_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
                "yaw_rate": ("CAN_Vehicle_VDC2_3E", "VDC2_YawRate_3E"),
            },
            {
                "vx_kmh": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
                "yaw_rate": ("VDC2_0B", "VDC2_YawRate_0B_s0B"),
            },
            {
                "vx_kmh": ("CAN_Fusion_Private_EBC2_0B_Bus21_Msg18FEBF0Bx", "EBC2_MeanSpdFA_0B"),
                "yaw_rate": ("CAN_Fusion_Private_VDC2_0B_Bus21_Msg18F0090Bx", "VDC2_YawRate_0B"),
            },
            {
                "vx_kmh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
                "yaw_rate": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_VDC2_VDC2_YawRate"),
            },
            {
                "vx_kmh": ("MFC5xx_Device.KB.MTSI_stKBFreeze_020ms_t",
                           "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFdf_CanInput_EBC2_EBC2_MeanSpdFA"),
                "yaw_rate": ("MFC5xx_Device.KB.MTSI_stKBFreeze_020ms_t",
                             "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFdf_CanInput_VDC2_VDC2_YawRate"),
            },
            {
                "vx_kmh": ("CAN_ARS_MFC_EBC2_VDY", "EBC2_MeanSpdFA_0B"),
                "yaw_rate": ("CAN_MFC_Public_VDC2_0B", "VDC2_YawRate_0B"),
            },
            {
                "vx_kmh": ("CAN_MFC_Public_middle_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
                "yaw_rate": ("CAN_MFC_Public_middle_VDC2_0B", "VDC2_YawRate_0B"),
            },
            {
                "vx_kmh": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFdf_CanInput.EBC2.EBC2_MeanSpdFA"),
                "yaw_rate": ("CAN_MFC_Public_VDC2_0B", "VDC2_YawRate_0B"),
            }
        ]
        optsgs = [
            {
                "ax": ("CAN_MFC_Public_VDC2_0B", "VDC2_LongAccel_0B"),

            },
            {
                "ax": ("CAN_MFC_ARS_Private_VDC2_0B", "VDC2_LongAccel_0B"),

            },
            {
                "ax": ("VDC2_0B_s0B", "VDC2_LongitudinalAcceleration_0B"),
            },
            {
                "ax": ("VDC2_0B", "VDC2_LongAccel_0B"),
            },
            {  # Iveco
                "ax": ("VDC2", "LongitudinalAcc"),
            },
            {  # Actros (dummy)
                "ax": ("VDC2_BS", "ax"),
            },
            {
                "ax": ("VDC2_VDY_s0B", "VDC2_LongAccel_0B"),
            },
            {
                'ax': ("VDC2_0B_s0B", "VDC2_LongAccel_0B"),
            },
            {
                'ax': ("VDC2_0B_s0B", "LongitudinalAcceleration"),
            },
            {
                "ax": ("VDC2_0B_s0B", "VDC2_LongAccel_0B_s0B"),
            },
            {
                "ax": ("VDC2_3E_s3E", "VDC2_LongAccel_3E"),
            },
            {
                "ax": ("CAN_Vehicle_VDC2_3E", "VDC2_LongAccel_3E"),
            },
            {
                "ax": ("VDC2_0B", "VDC2_LongAccel_0B_s0B"),
            },
            {
                "ax": ("CAN_Fusion_Private_VDC2_0B_Bus21_Msg18F0090Bx", "VDC2_LongAccel_0B"),
            },
            {
                "ax": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_VDC2_VDC2_LongAccel"),

            },
            {
                "ax": ("MFC5xx_Device.KB.MTSI_stKBFreeze_020ms_t",
                       "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFdf_CanInput_VDC2_VDC2_LongAccel"),
            },
            {
                "ax": ("MFC5xx Device.VDY.VehDyn", "MFC5xx_Device_VDY_VehDyn_Longitudinal_Accel"),
            },
            {
                "ax": ("CAN_MFC_Public_middle_VDC2_0B", "VDC2_LongAccel_0B"),
            },
            {
                "VDC2_LongAccel_0B": ("CAN_MFC_Public_VDC2_0B", "VDC2_LongAccel_0B"),
            }
        ]
        group = self.source.selectSignalGroup(sgs)
        optgroup = self.source.selectLazySignalGroup(optsgs)
        return group, optgroup

    def fill(self, group, optgroup):
        # remark: update_rate(VDC2) > update_rate(EBC2)
        #         ==> rescale to VDC2 time
        ego_motion = None
        time, yaw_rate = group.get_signal('yaw_rate')

        if not np.any(np.diff(time) > 100):
            rescale_kwargs = {'ScaleTime': time}
            vx_kmh = group.get_value('vx_kmh', **rescale_kwargs)
            if np.any(vx_kmh > 251.0):  # limit based on J1939_DAS.dbc, rev. 1.6
                self.logger.debug("Invalid values in EBC2 speed signal")
                vx_kmh = np.ma.masked_array(vx_kmh, vx_kmh > 251.0)
            vx = vx_kmh / 3.6
            if 'ax' in optgroup:
                ax = optgroup.get_value('ax', **rescale_kwargs)
            else:
                self.logger.debug("'VDC2_LongAccel_0B' not available; calculating ax")
                d_vx = np.gradient(vx)
                d_t = np.gradient(time)
                if isinstance(vx, np.ma.MaskedArray):
                    ax = np.ma.where(d_t > 0.0, d_vx / d_t, 0.0)
                    # ax = _LPF_butter_4o_5Hz(time, ax)  # TODO: implement for MaskedArray
                else:
                    ax = np.where(d_t > 0.0, d_vx / d_t, 0.0)
                    ax = _LPF_butter_4o_5Hz(time, ax)
            ego_motion = EgoMotion(time, vx, yaw_rate, ax)
        else:
            vx = np.zeros(time.shape)
            yaw_rate = np.zeros(time.shape)
            ax = np.zeros(time.shape)

            ego_motion = EgoMotion(time, vx, yaw_rate, ax)

            self.logger.error("Invalid measurement due to high difference in time array")
        return ego_motion


if __name__ == '__main__':
    from config.Config import init_dataeval

    # meas_path = r"\\corp.knorr-bremse.com\str\measure\DAS\ConvertedMeas_Xcellis\FER\AEBS\F30\NY00_0787\FC232909_FU232840\2023-10-25\mi5id786__2023-10-25_10-46-24.h5"
    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_j1939_egomotion@aebs.fill', manager)
    # print data
