'''
  xp = ugdiff(x,t_abst,verfahren) 

  Numerisches Differenzieren des Vektors x
  
  x         : Spaltenvektor (Zeitreihe)
  t_abst    : Abtastzeit
  verfahren : 1 : Differenzenquotient (Backwardifferenz)
              2 : Polynomapproximation             

  xp        : differenzierte Zeitreihe


  ug 5.5.99

'''

import numpy as np                # array operations
import scipy.signal as signal     # signal toolbox

def ugdiff(t, input_signal, verfahren=2):

    if t is None or input_signal is None:
        out_signal = None
        return None

    diff_t = np.diff(t)
    t_abst_delta = diff_t.max()-diff_t.min()
    t_abst = np.mean(diff_t)
    print "t_abst", t_abst,diff_t.min(),diff_t.max()
   
    if  t_abst_delta > 0.01*t_abst:
        print "t is not equidistant" 
        
        out_signal = np.zeros_like(t)
        out_signal[1:] = np.diff(input_signal)/np.diff(t)
        return out_signal

    
    if 1 == verfahren :
        # Backwarddifferenz 
        B = np.array([1.0, -1.0])
        A = np.array([t_abst])
        # calculate filter 
        out_signal = signal.lfilter(B,A,input_signal)
        return out_signal

    elif 2 == verfahren:
        # Polynomapproximation   
        B = np.array([-1, 8, 0, -8, 1])
        A = np.array([t_abst*12])
        out_signal = signal.lfilter(B,A,input_signal)
        out_signal[0:-2] = out_signal[2:]   # xp = [xp(3:length(xp))',0,0]';
        return out_signal

