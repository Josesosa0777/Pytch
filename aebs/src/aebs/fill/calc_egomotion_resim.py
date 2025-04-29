# -*- dataeval: init -*-

import numpy as np
import scipy.signal

from primitives.egomotion import EgoMotionResim
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


sgs = [{
    "vx_kmh": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),
    "yaw_rate": ("VDC2_0B", "VDC2_YawRate_0B"),
    }, {  # Iveco
        "vx_kmh": ("EBC2", "MeanFASpeed"),
        "yaw_rate": ("VDC2", "YawRate"),
    }, {  # Actros
        "vx_kmh": ("EBC2_BS", "FA_Spd_Cval"),
        "yaw_rate": ("VDC2_BS", "yaw_rate"),
    }, {  # FLR20, ARS430 combined endurance run
        "vx_kmh": ("EBC2_0B", "EBC2_MeanSpdFA_0B_C2"),
        "yaw_rate": ("VDC2_0B", "VDC2_YawRate_0B_C2"),
    },
    {
        "vx_kmh": ("EBC2_VDY_s0B", "EBC2_MeanSpdFA_0B"),
        "yaw_rate": ("VDC2_VDY_s0B", "VDC2_YawRate_0B"),
    },

    {
        "vx_kmh"  : ("EBC2_0B","EBC2_MeanSpdFA_0B"),
        "yaw_rate": ("VDC2_0B","VDC2_YawRate_0B_s0B"),

    },
    {
        "vx_kmh"  : ("EBC2_s0B","FrontAxleSpeed"),
        "yaw_rate": ("VDC2_s0B","YawRate"),
    },
    {
        "vx_kmh"  : ("EBC2_0B","FrontAxleSpeed"),
        "yaw_rate": ("VDC2_0B","VDC2_YawRate_0B_s0B"),
    },
    {
        "yaw_rate": ("VDC2_0B","VDC2_YawRate_0B_s0B"),
        "vx_kmh": ("EBC2_0B","EBC2_FrontAxleSpeed_0B_s0B"),
    }
]

optsgs = [{
    "ax": ("VDC2_0B", "VDC2_LongAccel_0B"),
    }, {  # Iveco
        "ax": ("VDC2", "LongitudinalAcc"),
    }, {  # Actros (dummy)
        "ax": ("VDC2_BS", "ax"),
    },
    {
        "ax": ("VDC2_VDY_s0B", "VDC2_LongAccel_0B"),
    }
    ,
    {
        "ax": ("VDC2_0B","VDC2_LongAccel_0B_s0B"),

    },
    {
        'ax':  ("VDC2_s0B","LongitudinalAcceleration"),
    }
]

new_sgs = [
    {
        "accped_pos": ("EEC2_00_s00", "EEC2_APPos1_00_s00"),
        "brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B_s0B"),
        "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B_s0B"),
        "dir_ind": ("OEL_32_s32", "OEL_TurnSigSw_32_s32"),
    },
    {
        "accped_pos": ("EEC2_00_s00", "EEC2_APPos1_00"),
        "brkped_pos": ("EBC1_0B_s0B", "EBC1_BrkPedPos_0B"),
        "steer_angle": ("VDC2_0B_s0B", "VDC2_SteerWhlAngle_0B"),
        "dir_ind": ("OEL_32_s32", "OEL_TurnSigSw_32"),
    },
    {

        "dir_ind"    : ("OEL_32_CAN20", "OEL_TurnSigSw_32"),
        "steer_angle": ("VDC2_0B_CAN20", "VDC2_SteerWhlAngle_0B"),
        "brkped_pos" : ("EBC1_0B_CAN20", "EBC1_BrkPedPos_0B"),
        "accped_pos" : ("EEC2_00_CAN20", "EEC2_APPos1_00"),
    }
    ,
    {
        "dir_ind"    : ("OEL_32_CAN23", "OEL_TurnSigSw_32"),
        "steer_angle": ("VDC2_0B_CAN23", "VDC2_SteerWhlAngle_0B"),
        "brkped_pos" : ("EBC1_0B_CAN23", "EBC1_BrkPedPos_0B"),
        "accped_pos" : ("EEC2_00_CAN23", "EEC2_APPos1_00"),
    },
    {
        "dir_ind"    :("OEL_32","OEL_TurnSigSw_32_s32"),
        "steer_angle":("VDC2_0B","VDC2_SteerWhlAngle_0B_s0B"),
        "brkped_pos" :("EBC1_0B","EBC1_BrkPedPos_0B"),
        "accped_pos" :("EEC2_00","EEC2_APPos1_00"),

    },
    {
        "dir_ind"    :("OEL_32","OEL_TurnSignalSwitch_32_s32"),
        "steer_angle":("VDC2_0B","VDC2_SteerWhlAngle_0B_s0B"),
        "brkped_pos" :("EBC1_0B","EBC1_BrkPedPos_0B"),
        "accped_pos" :("EEC2_00","EEC2_AccPedalPos1_00_s00"),

    },
    {

        "steer_angle" : ("VDC2_s0B", "SteerWheelAngle"),
        "accped_pos"  : ("EEC2_s00", "AccelPedalPos1"),
        "dir_ind": ("OEL_s32", "TurnSignalSwitch"),
        "brkped_pos"   : ("EBC1_s0B", "BrakePedalPos"),

    }
]

class Calc(interface.iCalc):
    def check(self):
        group = self.source.selectSignalGroup(sgs)
        new_group=self.source.selectLazySignalGroup(new_sgs)
        optgroup = self.source.selectLazySignalGroup(optsgs)
        return group, optgroup, new_group

    def fill(self, group, optgroup, new_group):
        ego_motion = {}
        # remark: update_rate(VDC2) > update_rate(EBC2)
        #         ==> rescale to VDC2 time
        time, yaw_rate = group.get_signal('yaw_rate')
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


        if 'accped_pos' in new_group:
            accped_pos = new_group.get_value("accped_pos",**rescale_kwargs)
        else:
            self.logger.debug("'accped_pos' not available")
            accped_pos = np.zeros_like(time)


        if 'brkped_pos' in new_group:
            brkped_pos = new_group.get_value("brkped_pos",**rescale_kwargs)
        else:
            self.logger.debug("'brkped_pos' not available")
            brkped_pos = np.zeros_like(time)


        if 'steer_angle' in new_group:
            steer_angle = new_group.get_value("steer_angle",**rescale_kwargs)
        else:
            self.logger.debug("'steer_angle' not available")
            steer_angle = np.zeros_like(time)


        if 'dir_ind' in new_group:
            dir_ind = new_group.get_value("dir_ind",**rescale_kwargs)
        else:
            self.logger.debug("'dir_ind' not available")
            dir_ind = np.zeros_like(time)

        ego_motion = EgoMotionResim(time, vx, yaw_rate, ax, accped_pos,brkped_pos,steer_angle,dir_ind)
        return ego_motion

if __name__=='__main__':
	from config.Config import init_dataeval
	meas_path = r"C:\KBData\__PythonToolchain\Meas\dSpace_resim\mi5id00__2021-12-16_08-38-23.h5"
	config, manager, manager_modules = init_dataeval(['-m', meas_path])
	ego_motion = manager_modules.calc('calc_egomotion_resim@aebs.fill', manager)
	print(ego_motion)