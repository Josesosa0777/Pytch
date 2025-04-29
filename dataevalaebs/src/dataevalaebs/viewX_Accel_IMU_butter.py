# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import datavis
DefParam = interface.NullParam

SignalGroups   = [
{
  "X_Accel": ("IMU_XAccel_and_YawRate", "X_Accel"),
},
]
def LPF_butter_4o_5Hz(t, input_signal):
  # Low pass filter, butterworth characteristic, 4th order, corner frequency 5 Hz 
  # input:  t             time [sec] signal as np array
  #         input_signal  input signal as np array 
  # return: filtered signal as np array  
  
  import numpy as np                # array operations
  import scipy.signal as signal     # signal toolbox

  # parameters
  n_order  = 4                      # filter order of butterworth filter
  f0 = 5.0                          # -3dB corner frequency [Hz] of butterworth filter
  
  fs = 1.0/np.mean(np.diff(t))      # sampling frequency (assumption: constant sampling interval)
  f_nyq = fs/2.0                    # Nyquist frequency (= 1/2 sampling frequency)
  Wn = f0/f_nyq                     # normalized corner frequency  (related to Nyquist frequency)
  
  # calculate filter coefficients
  B,A = signal.butter(n_order, Wn)
 
  # calculate filter 
  out_signal = signal.lfilter(B,A,input_signal)
  
  return out_signal
class cView(interface.iView):
  def check(self):
    Group = interface.Source.selectSignalGroup(SignalGroups)
    return Group

  def fill(self, Group):
    return Group

  def view(self, Param, Group):
    Client = datavis.cPlotNavigator(title="PN", figureNr=None)
    interface.Sync.addClient(Client)
    offset_IMU = -0.0
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "X_Accel")
    Client.addSignal2Axis(Axis, "X_Accel", Time, ((Value*9.81)-offset_IMU), unit=u"m/ss")
    Time, Value = interface.Source.getSignalFromSignalGroup(Group, "X_Accel")
    fValue=LPF_butter_4o_5Hz(Time, Value)
    Client.addSignal2Axis(Axis, "X_Accel_butter", Time, ((fValue*9.81)-offset_IMU), unit=u"m/ss")

    return
