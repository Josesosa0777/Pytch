# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import numpy as np
from scipy.signal import butter, filtfilt
from scipy.signal import savgol_filter


def zero_phase_low_pass_filter(time, data,cutoff_freq=2, order=5):
    # Desired cutoff frequency
    # cutoff_freq = 2
    sampling_freq = 50  # Sampling frequency

    # Sampling Time = the time difference between two consecutive samples
    sampling_time = np.mean(np.diff(time))

    # Sampling frequency
    sampling_freq = 1.0 / sampling_time

    # The Nyquist rate or frequency is the minimum rate at which a finite bandwidth signal needs to be sampled to
    # retain all of the information. If a time series is sampled at regular time intervals dt, then the Nyquist rate
    # is just 1/(2 dt ).
    nyquist = 0.5 * sampling_freq
    normal_cutoff = cutoff_freq / nyquist

    # calculate filter coefficients
    b, a = butter(order, normal_cutoff, btype='low', analog=False)

    # apply 'zero-phase' filter
    y = filtfilt(b, a, data)

    return y
# # Ulrich's Implementation for savgol...................

# def sort_signal_by_reference_time_axis(t, x, ref_t):
#     """
#         t: time axis of the signal in seconds
#         x: signal value
#         ref_t: reference time axis in seconds
#
#         """
#
#     # ref_t = ref_t / 1e6  # convert microsecond to seconds
#
#     # checks -> only information
#
#     # check for unique values in the reference time axis
#     if len(set(ref_t)) / len(ref_t) < 1.0:
#         print("Warning - duplicate values in reference")
#
#     # check that time axis of signal cores
#     delta_t = t.max() - t.min()
#     delta_t_ref = ref_t.max() - ref_t.min()
#     print(abs((delta_t / delta_t_ref) - 1.0))
#     if abs((delta_t / delta_t_ref) - 1.0) > 0.01:
#         print("Warning - reference time axis is not ")
#
#     # sort the reference time axis and apply index to time axis and signal values
#     ref_t_idx = ref_t.argsort()
#     t_corrected = ref_t[ref_t_idx[:]]
#     x_corrected = x[ref_t_idx[:]]
#
#     # adjust start of time signal
#     t_corrected = t_corrected - t_corrected[0] + t[0]
#
#     return t_corrected, x_corrected


# calc_derivative_using_Savitzky_Golay_filter
# def savgolFilter(time, values, ref_t, window_length=9, polyorder=3):
#     t_corrected, x_corrected = sort_signal_by_reference_time_axis(time, values, ref_t)
#     dT = np.mean(np.diff(t_corrected))
#     dx = savgol_filter(x_corrected, window_length=window_length, polyorder=polyorder, deriv=1, delta=dT)
#     return dx
#...........................................................................................