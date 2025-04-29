'''

  Butterworth Low Pass Filter (4th order)
  corner frequency: 5Hz
  
  acceleration filtering for AEBS tests
  
'''

import numpy as np                # array operations
import scipy.signal as signal     # signal toolbox

def LPF_butter(t, input_signal, f0 = 5.0, n_order  = 4):
  '''
  Low pass filter, butterworth characteristic, 4th order, corner frequency 5 Hz 
  input:  t             time [sec] signal as np array
          input_signal  input signal as np array 
          n_order  = 4  filter order of butterworth filter
          f0 = 5.0      -3dB corner frequency [Hz] of butterworth filter
  return: filtered signal as np array  
  '''
  
  fs = 1.0/np.mean(np.diff(t))      # sampling frequency (assumption: constant sampling interval)
  f_nyq = fs/2.0                    # Nyquist frequency (= 1/2 sampling frequency)
  Wn = f0/f_nyq                     # normalized corner frequency  (related to Nyquist frequency)
  
  # calculate filter coefficients
  B,A = signal.butter(n_order, Wn)
 
  # calculate filter 
  out_signal = signal.lfilter(B,A,input_signal)
  
  return out_signal
#==================================================================================
