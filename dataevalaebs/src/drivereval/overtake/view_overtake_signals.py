# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import numpy as np
import scipy.signal as signal
import interface
import datavis
import measparser
def_param = interface.NullParam

sgs  = [
{
  "EBC1_BrkPedPos_0B": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
  "VDC2_SteerWhlAngle_0B": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
  "actual_vehicle_speed": ("General_radar_status", "actual_vehicle_speed"),
  "EEC2_APPos1_00": ("EEC2_00", "EEC2_APPos1_00"),
  #"OEL_TurnSigSw_21": ("OEL_21", "OEL_TurnSigSw_21"),
  "C0_Left_A": ("Video_Lane_Left_A", "C0_Left_A"),
  "C1_Left_A": ("Video_Lane_Left_A", "C1_Left_A"),
  #"EEC1_ActEngPercTrq_00": ("EEC1_00", "EEC1_ActEngPercTrq_00"),
  #"EEC1_EngSpd_00": ("EEC1_00", "EEC1_EngSpd_00"),
  "tr0_range": ("Tracks", "tr0_range"),
  "tr0_relative_velocitiy": ("Tracks", "tr0_relative_velocitiy"),
  "View_Range_Left_B": ("Video_Lane_Left_B", "View_Range_Left_B"),
  "AEBS1_AEBSState_2A": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
  "track_acc": ("Tracks", "tr0_acceleration_over_ground"),
  "tr0_lateral_position": ("Tracks", "tr0_lateral_position"),
  "tr0_video_confidence": ("Tracks", "tr0_video_confidence"),
  "tr0_is_video_associated": ("Tracks", "tr0_is_video_associated"),
  "tr0_corrected_lateral_distance": ("Tracks", "tr0_corrected_lateral_distance"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    return group
    
  def filter(self, data, time, T):
    filtered = np.zeros_like(data)
    filtered[0] = data[0]
    const = np.mean(np.diff(time))/T
    for i in xrange(1,data.size):
      filtered[i] = const*(data[i] - filtered[i-1]) + filtered[i-1]
    return filtered
    
  def LPF_butter_4o_5Hz(self, t, input_signal):
  # input:  t             time [sec] signal as np array
  #         input_signal  input signal as np array 
  # return: filtered signal as np array 

    # parameters
    n_order  = 4                      # filter order of butterworth filter
    f0 = 20.0                          # -3dB corner frequency [Hz] of butterworth filter
  
    fs = 1.0/np.mean(np.diff(t))      # sampling frequency (assumption: constant sampling interval)
    f_nyq = fs/2.0                    # Nyquist frequency (= 1/2 sampling frequency)
    Wn = f0/f_nyq                     # normalized corner frequency  (related to Nyquist frequency)
  
    # calculate filter coefficients
    B,A = signal.butter(n_order, Wn)
  
    # calculate filter 
    out_signal = signal.lfilter(B,A,input_signal)
  
    return out_signal

  def view(self, param, group):
    client00 = datavis.cPlotNavigator(title="", figureNr=None)
    self.sync.addClient(client00)
    client01 = datavis.cPlotNavigator(title="", figureNr=None)
    self.sync.addClient(client01)
    axis00 = client00.addAxis()
    time00, value00, unit00 = group.get_signal_with_unit("actual_vehicle_speed")
    client00.addSignal2Axis(axis00, "actual_vehicle_speed", time00, value00, unit='m/s')
    axis01 = client00.addAxis()
    time01, value01, unit01 = group.get_signal_with_unit("EBC1_BrkPedPos_0B")
    client00.addSignal2Axis(axis01, "BrkPedPos", time01, value01, unit='%')
    time02, value02, unit02 = group.get_signal_with_unit("EEC2_APPos1_00")
    client00.addSignal2Axis(axis01, "APPos", time02, value02, unit='%')
    axis02 = client00.addAxis()
    client00.addSignal2Axis(axis02, "deriv_appos", time02, measparser.signalproc.backwardderiv(value02,time02), unit='%/s')
    axis03 = client00.addAxis()
    time03, value03, unit03 = group.get_signal_with_unit("VDC2_SteerWhlAngle_0B")
    T = 0.5 #filter time const
    filtered = self.filter(value03, time03, T)
    filter_butter = self.LPF_butter_4o_5Hz(time03, value03)
    client00.addSignal2Axis(axis03, "SteerWhlAngle", time03, value03, unit='rad')
    client00.addSignal2Axis(axis03, 'filtered', time03, filter_butter, unit='rad')
    axis04 = client00.addAxis()
    client00.addSignal2Axis(axis04, "deriv_steerwhlangle", time03, measparser.signalproc.backwardderiv(value03,time03), unit='rad/s')
    axis08 = client00.addAxis()
    time07, value07, unit07 = group.get_signal_with_unit("tr0_range")
    client00.addSignal2Axis(axis08, "tr0_range", time07, value07, unit='m')
    axis09 = client00.addAxis()
    time08, value08, unit08 = group.get_signal_with_unit("tr0_relative_velocitiy")
    client00.addSignal2Axis(axis09, "tr0_rel_vel", time08, value08, unit='m/s')
    axis10 = client00.addAxis()
    time10, value10, unit10 = group.get_signal_with_unit("C0_Left_A")
    client00.addSignal2Axis(axis10, "left_line", time10, value10 + 1.25, unit='m')
    axis05 = client00.addAxis()
    time05, value05, unit05 = group.get_signal_with_unit('C1_Left_A')
    client00.addSignal2Axis(axis05, 'head angle', time05, value05, unit=unit05)
    client00.addSignal2Axis(axis05, 'filtered', time05, self.filter(value05, time05, T), unit=unit05)
    axis11 = client00.addAxis()
    time11, value11, unit11 = group.get_signal_with_unit( "View_Range_Left_B" )
    client00.addSignal2Axis(axis11,  "View_Range", time11, value11, unit='m')
    axis12 = client00.addAxis()
    time12, value12, unit12 = group.get_signal_with_unit("AEBS1_AEBSState_2A")
    client00.addSignal2Axis(axis12, "AEBSState", time12, value12, unit=unit12)
    axis13 = client00.addAxis()
    time13, value13, unit13 = group.get_signal_with_unit('track_acc')
    client00.addSignal2Axis(axis13, 'track_acc', time13, value13, unit='m/s^2')
    axis06 = client01.addAxis()
    time14, value14, unit14 = group.get_signal_with_unit("tr0_lateral_position")
    client01.addSignal2Axis(axis06, "tr0_lateral_position", time14, value14, unit=unit14)
    time15, value15, unit15 = group.get_signal_with_unit("tr0_corrected_lateral_distance")
    client01.addSignal2Axis(axis06, "tr0_corrected_lateral_distance", time15, value15, unit=unit15)
    axis07 = client01.addAxis()
    time16, value16, unit16 = group.get_signal_with_unit("tr0_is_video_associated")
    client01.addSignal2Axis(axis07, "tr0_is_video_associated", time16, value16, unit=unit16)
    time17, value17, unit17 = group.get_signal_with_unit("tr0_video_confidence")
    client01.addSignal2Axis(axis07, "tr0_video_confidence", time17, value17, unit=unit17)
    
    return
