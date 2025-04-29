
'''

  Butterworth Low Pass Filter (4th order)
  corner frequency: 5Hz
  
  acceleration filtering for AEBS tests
  
'''

import numpy as np
import matplotlib.pyplot as plt

import kbtools

# this just an example how to use the filter
def example1():
  
  # create signals
  N = 200
  dT = 0.01

  # time signal
  t = np.arange(0,N*dT,dT)

  # 5 Hz sinus signal  (corner frequency; filter shall attentuate signal by 3dB = 0.707)
  f0 = 5.0
  input_signal = np.sin(2*np.pi*f0*t)
  
  # filter sinus signal
  output_signal = kbtools.LPF_butter(t, input_signal)

  # plot results
  fig = plt.figure(1)
  
  sp = fig.add_subplot(111)
  sp.set_title('Example Low Pass Filter 5 Hz (Butterworth 4th order)')
  sp.plot(t,input_signal,'b')
  sp.plot(t,output_signal,'r')
  sp.plot(t,np.ones_like(t)*1.0/np.sqrt(2.0),'m-')    # -3dB = 1/sqrt(2) = 0.707
  sp.plot(t,np.ones_like(t)*-1.0/np.sqrt(2.0),'m-')   # -3dB = 1/sqrt(2) = 0.707

  sp.set_ylim((-1.1,1.1))
  sp.grid()
  sp.set_xlabel('time [sec]')
  sp.set_ylabel(' input/output signal ')
  sp.legend(('input','output','3dB threshold'))
  
  fig.show()
  
  
# this just an example how to use the filter
def example2():
  
  # create signals
  N = 200
  dT = 0.005

  # time signal
  t = np.arange(0,N*dT,dT)

  # 5 Hz sinus signal  (corner frequency; filter shall attentuate signal by 3dB = 0.707)
  t_start_step = 0.1
  
  input_signal = np.zeros_like(t)
  input_signal[t>0.1] = 1.0
  
  # filter sinus signal
  output_signal = kbtools.LPF_butter(t, input_signal)

  t_10 = t[output_signal>=0.1][0]-t_start_step
  print "t_10", t_10
  t_50 = t[output_signal>=0.5][0]-t_start_step
  print "t_50", t_50
  t_90 = t[output_signal>=0.9][0]-t_start_step
  print "t_90", t_90
  
  
  
  # plot results
  fig = plt.figure(1)
  
  sp = fig.add_subplot(111)
  sp.set_title('Example Low Pass Filter 5 Hz (Butterworth 4th order)')
  sp.plot(t-t_start_step,input_signal,'b')
  sp.plot(t-t_start_step,output_signal,'r')
  sp.plot(t-t_start_step,np.ones_like(t)*0.1,'m:')    # 50%
  sp.plot(t-t_start_step,np.ones_like(t)*0.5,'m:')    # 50%
  sp.plot(t-t_start_step,np.ones_like(t)*0.9,'m:')    # 50%
  #sp.plot(t,np.ones_like(t)*-1.0/np.sqrt(2.0),'m-')   # -3dB = 1/sqrt(2) = 0.707

  sp.set_ylim((-0.1,1.5))
  sp.grid()
  sp.set_xlabel('time [sec]')
  sp.set_ylabel(' input/output signal ')
  sp.legend(('input','output','50%'))
  
  fig.show()

#--------------------------------------------------------------------------
if __name__=='__main__':
  example1()
  raw_input()
    
