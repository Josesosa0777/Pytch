"""
:Organization: Knorr-Bremse SfN GmbH T/CES3.2 (BU2) Budapest Schwieberdingen T/CES3.2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import numpy as np
import scipy.signal as signal

import datavis
import measparser
import interface

DefParam = interface.NullParam

SignalGroups = [{"CurrentAEBSActivationThreshold": ("PGNFFB2", "CurrentAEBSActivationThreshold"),
                 "Ext_Acceleration_Demand": ("XBR-8C040B2A", "Ext_Acceleration_Demand"),
                 "ReqAEBSActivationThreshold": ("PGNFFBA", "ReqAEBSActivationThreshold"),
                 "X_Accel": ("IMU_XAccel_and_YawRate", "X_Accel"),
                 #"Y_Accel": ("IMU_YAccel_and_Temp", "Y_Accel"),
                 #"Yaw_Rate": ("IMU_XAccel_and_YawRate", "Yaw_Rate"),
                 "padasf_x_par_a.REPaEmergencyBrake": ("ECU", "padasf_x_par_a.REPaEmergencyBrake"),
                 "repretg.aAvoid_DEBUG": ("ECU", "repretg.aAvoid_DEBUG"),},]

#############################################################
#Calculation of Low pass filter, butterworth characteristic,#
#4th order, corner frequency 5 Hz                           #
#regarding "Data processing for the AEBS" specification     #
#############################################################
def LPF_butter_4o_5Hz(t, input_signal):
# input:  t             time [sec] signal as np array
#         input_signal  input signal as np array 
# return: filtered signal as np array 

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
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      #############################
      # acceleration-, IMU-signals#
      #############################
      Client = datavis.cPlotNavigator(title="acceleration", figureNr=101)
      interface.Sync.addClient(Client)
      Client.addsignal('aAvoid [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "repretg.aAvoid_DEBUG"),
                       'aEmergency [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "padasf_x_par_a.REPaEmergencyBrake"),
                       'CurrActThresh [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "CurrentAEBSActivationThreshold"),
                       'ExtAccDem [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "Ext_Acceleration_Demand"),
                       'ReqActThresh [m/ss]', interface.Source.getSignalFromSignalGroup(Group, "ReqAEBSActivationThreshold"))
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "X_Accel")
      f_Value = LPF_butter_4o_5Hz(Time, Value)
      Client.addSignal2Axis(Axis, "X_Accel", Time, Value, unit="g")
      Client.addSignal2Axis(Axis, "X_Accel_butter_filt", Time, f_Value, unit="g")    
      # Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Y_Accel")
      # Client.addSignal2Axis(Axis, "Y_Accel", Time, Value, unit="g")
      # Axis = Client.addAxis()
      # Time, Value = interface.Source.getSignalFromSignalGroup(Group, "Yaw_Rate")
      # Client.addSignal2Axis(Axis, "Yaw_Rate", Time, Value, unit="/s")                 
      
      return []

