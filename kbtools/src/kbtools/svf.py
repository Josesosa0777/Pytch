'''
    State Variable Filter
    
    calculates filtered time derivatives 

    Same delay for calculated time derivatives and low pass filtered input signal.
       
'''
import numpy as np
import kbtools

#=================================================================================
def svf_1o(t,x, T=0.1, valid=None):  
    '''
    State Variable Filter of 1st Order 
    
    Calculates the time derivative of a given input signal x and a corresponding time vector t.
      
    inputs: 
        t      time vector
        x      signal 
    parameters:
        T      time constants [s]
    outputs:
        df_x2  time derivative of x
        f_x2   filtered x
    
    '''   
    
    '''
    todo:  
       - variant for fix sampling rate (dT = const)
    '''
    
    '''
    Copyright Knorr Bremse 
    folgender Algorithmus wurde von Falk Hecker unter ASCET implementiert:
      
    /* zunaechst Differenz Eingang-Ausgang bilden    */
    /* (weitgehend unbeeinflusst von Quantisierung), */
    D_xfx = x - f_x;

    /* Ableitung von  x  speichern */
    df_x = D_xfx / T;

    /* Summe fuer Integration berechnen,  */
    /* dabei alte Fehler beruecksichtigen */
    f_x = f_x + (D_xfx + D_xfx_old) * dT / (2 * T);

    /* alte Eingangsdifferenz merken */
    D_xfx_old = D_xfx;
    '''
    
    if t is None or x is None:
        return None, None

    if valid is None:
        
        # outputs
        f_x2  = np.zeros_like(x)     # filtered output
        df_x2 = np.zeros_like(x)     # filfered derivative

        # filter state
        f_x   = x[0]      # filtered output   
        df_x  = 0.0       # filtered dervative
        t_old = t[0]      # previous time stamp
        
        # set output for first time instance
        df_x2[0] = f_x
        f_x2[0]  = df_x
        
        for k in xrange(1,x.size):
            dT       = t[k] - t_old
            tmp      = (x[k] - f_x)/T
            f_x      = f_x + (tmp  + df_x) * dT/2.0
            df_x     = tmp
            t_old    = t[k]
            f_x2[k]  = f_x
            df_x2[k] = df_x


    else:
        
        # outputs
        f_x2  = np.zeros_like(x)     # filtered output
        df_x2 = np.zeros_like(x)     # filfered derivative
        
        # ---------------------------------
        # 1. instanciate, inititialize 
        iMultitState = kbtools.CMultiState()
    
        # 2. calc
        iMultitState.calc(t,valid,default_value=0)
      
        for _,(t_start,dura) in enumerate(zip(iMultitState.t_starts,iMultitState.dura)):
            t_stop = t_start + dura
            idx = np.logical_and(t_start<=t,t<(t_stop))
            t_tmp = t[idx]
            x_tmp = x[idx]
            
            # filter state
            f_x   = x_tmp[0]      # filtered output   
            df_x  = 0.0           # filtered dervative
            t_old = t_tmp[0]      # previous time stamp
            
            f_x2_tmp  = np.zeros_like(x_tmp) 
            df_x2_tmp = np.zeros_like(x_tmp) 

            
            # set output for first time instance
            f_x2_tmp[0] = f_x
            df_x2_tmp[0]  = df_x
            
            for k in xrange(1,x_tmp.size):
                dT       = t_tmp[k] - t_old
                tmp      = (x_tmp[k] - f_x)/T
                f_x      = f_x + (tmp  + df_x) * dT/2.0
                df_x     = tmp
                t_old    = t_tmp[k]
                f_x2_tmp[k]  = f_x
                df_x2_tmp[k] = df_x

            
            f_x2[idx]  = f_x2_tmp     # filtered output
            df_x2[idx] = df_x2_tmp     # filfered derivative


        

    return df_x2, f_x2    # filfered derivative, filtered output
#=================================================================================
