'''
   
   data source: EgoVeh
   
   vehicle speed, yaw rate, curavture, etc.
      
   Ulrich Guecker 2011-11-30

'''


'''
known issues:


Multiple device names:
  CVR3\2011_11_30_release_CVR3_Volvo_OI_New_OTCOHL\CVR3_B2_2011-11-30_10-23_002.mdf
  VDC2: VDC2-98F0093E-1-ESP; VDC2-98F0090B-3-BrakeSys

'''


import pickle
import numpy as np
import pylab as pl



# KB specific imports
import measparser

# --------------------------------------------------------------------------------------------
class cDataEgoVeh():

  # -------------------------------------------------------------------------------------------
  @staticmethod
  def load_EgoVeh_from_Source(Source, PickleFilename=None, Device = "MRR1plus"):
    # load signal from SignalSource
    
    # here we want to collect the signals
    EgoVeh = None
  
    # list of signals with their short names
    # "VDC2_YAW_Rate"      : ("VDC2", "YAW_Rate"),
    SignalGroups = [{"VDC2_YAW_Rate"      : ("VDC2", "YawRate"),
                     
                     "psiDtOpt"           : (Device, "evi.General_TC.psiDtOpt"),
                     "psiDtDt"            : (Device, "evi.General_TC.psiDtDt"),
                     "vxvRef"             : (Device, "evi.General_TC.vxvRef"),
                     "axvRef"             : (Device, "evi.General_TC.axvRef"),

                     "tAbsPsiDt"          : (Device, "evi.General_TC.tAbsPsiDt"),
                     "tAbsVxvRef"         : (Device, "evi.General_TC.tAbsVxvRef"),
                     "tAbsMeasTimeStamp"  : (Device, "dsp.LocationData_TC.tAbsMeasTimeStamp"),

                     "kapCurvTraj"        : (Device, "evi.MovementData_TC.kapCurvTraj"),
                     "alpSideSlipAngle"   : (Device, "evi.MovementData_TC.alpSideSlipAngle"),

                     "psiDtOptRaw"        : (Device, "evi.General_TC.psiDtOptRaw"),
                     
                     "dLongitudinalOffsetRearAxis"   : (Device, "csi.VehicleData_T20.dLongitudinalOffsetRearAxis"),
                     
                     "psiDtCAN_T20"       : (Device, "csi.VehicleData_T20.psiDt"),
                     "psiDtOpt_T20"       : (Device, "evi.General_T20.psiDtOpt"),
                     "psiDtOptRaw_T20"    : (Device, "evi.General_T20.psiDtOptRaw"),
                     "psiDtDt_T20"        : (Device, "evi.General_T20.psiDtDt"),
                     
                     "vxvRef_T20"         : (Device, "evi.General_T20.vxvRef"),
                     "kapCurvTraj_T20"    : (Device, "evi.MovementData_T20.kapCurvTraj"),
                     "kapCurvTrajRaw_T20" : (Device, "evi.MovementData_T20.kapCurvTrajRaw"),
                      
           
                     },]
  
    try:
      #Group = Source.selectSignalGroup(SignalGroups)
      Group = Source.selectFilteredSignalGroup(SignalGroups)
    except ValueError, error:
      print __file__
      print error.message
    else:
      # here we load signal to a dict
      EgoVeh = {}
      EgoVeh['FileName']                = Source.FileName
      
      try:
        EgoVeh['VDC2_YAW_Rate_Time'], EgoVeh['VDC2_YAW_Rate_Value'] = Source.getSignalFromSignalGroup(Group, "VDC2_YAW_Rate")
      except:
        pass      
        
                
      
      # TC Task
      EgoVeh['t'], EgoVeh['psiDtOpt']   = Source.getSignalFromSignalGroup(Group, "psiDtOpt")
      EgoVeh['psiDtDt']                 = Source.getSignalFromSignalGroup(Group, "psiDtDt")[1]
      EgoVeh['vxvRef']                  = Source.getSignalFromSignalGroup(Group, "vxvRef")[1]
      EgoVeh['axvRef']                  = Source.getSignalFromSignalGroup(Group, "axvRef")[1]
      
      EgoVeh['tAbsPsiDt']               = Source.getSignalFromSignalGroup(Group, "tAbsPsiDt")[1]
      EgoVeh['tAbsVxvRef']              = Source.getSignalFromSignalGroup(Group, "tAbsVxvRef")[1]
      EgoVeh['tAbsMeasTimeStamp']       = Source.getSignalFromSignalGroup(Group, "tAbsMeasTimeStamp")[1]

      EgoVeh['kapCurvTraj']             = Source.getSignalFromSignalGroup(Group, "kapCurvTraj")[1]
      EgoVeh['alpSideSlipAngle']        = Source.getSignalFromSignalGroup(Group, "alpSideSlipAngle")[1]
      
      EgoVeh['psiDtOptRaw']             = Source.getSignalFromSignalGroup(Group, "psiDtOptRaw")[1]
     
      # scalar
      EgoVeh['dLongitudinalOffsetRearAxis'] = Source.getSignalFromSignalGroup(Group, "dLongitudinalOffsetRearAxis")[1][0]

      # T20 Task
      EgoVeh['t_T20'], EgoVeh['psiDtCAN_T20'] = Source.getSignalFromSignalGroup(Group, "psiDtCAN_T20")
      EgoVeh['psiDtOpt_T20']                  = Source.getSignalFromSignalGroup(Group, "psiDtOpt_T20")[1]
      EgoVeh['psiDtOptRaw_T20']               = Source.getSignalFromSignalGroup(Group, "psiDtOptRaw_T20")[1]
      EgoVeh['psiDtDt_T20']                   = Source.getSignalFromSignalGroup(Group, "psiDtDt_T20")[1]
      EgoVeh['vxvRef_T20']                    = Source.getSignalFromSignalGroup(Group, "vxvRef_T20")[1]
      EgoVeh['kapCurvTraj_T20']               = Source.getSignalFromSignalGroup(Group, "kapCurvTraj_T20")[1]
      EgoVeh['kapCurvTrajRaw_T20']            = Source.getSignalFromSignalGroup(Group, "kapCurvTrajRaw_T20")[1]
      
      
      
            
    # save if filename given to a pickle file
    if EgoVeh and PickleFilename:
      output = open(PickleFilename, 'wb')
      pickle.dump(EgoVeh, output,-1)     # -1: using the highest protocol available
      output.close()

    return EgoVeh
    
  # -------------------------------------------------------------------------------------------
  @staticmethod
  def load_EgoVeh_from_picklefile(FileName,sig={},timebase=None):

    # load ego vehicle data from file (pickle)
    pkl_file = open(FileName, 'rb')
    EgoVeh  = pickle.load(pkl_file)
    pkl_file.close()
    
    sig['FileName']            = EgoVeh['FileName']
    
    if EgoVeh.has_key('VDC2_YAW_Rate_Time'):
      sig['VDC2_YAW_Rate_Time']  = EgoVeh['VDC2_YAW_Rate_Time']
      sig['VDC2_YAW_Rate_Value'] = EgoVeh['VDC2_YAW_Rate_Value'] 
      
            
    sig['t']                   = EgoVeh['t']             # time
    sig['psiDtOpt']            = EgoVeh['psiDtOpt']      # yaw rate
    sig['vxvRef']              = EgoVeh['vxvRef']        # ego vehicle speed
    sig['kapCurvTraj']         = EgoVeh['kapCurvTraj']   # curvature
  
    sig['t_T20']               = EgoVeh['t_T20']
    sig['psiDtCAN_T20']        = EgoVeh['psiDtCAN_T20'] 
    sig['psiDtOpt_T20']        = EgoVeh['psiDtOpt_T20']               
    sig['psiDtOptRaw_T20']     = EgoVeh['psiDtOptRaw_T20']  
    sig['psiDtDt_T20']         = EgoVeh['psiDtDt_T20']  
    sig['vxvRef_T20']          = EgoVeh['vxvRef_T20']                  
    sig['kapCurvTraj_T20']     = EgoVeh['kapCurvTraj_T20']             
    sig['kapCurvTrajRaw_T20']  = EgoVeh['kapCurvTrajRaw_T20']    
  
    return sig
    
  # -------------------------------------------------------------------------------------------
  @staticmethod
  def save_yaw_rate_as_matlab(sig,FileName='yaw_rate.mat'):
  
    import scipy.io as sio
  
    signal_list = {'VDC2_YAW_Rate_Time' :sig['VDC2_YAW_Rate_Time'],
                   'VDC2_YAW_Rate_Value':sig['VDC2_YAW_Rate_Value'],
                   't_T20'              :sig['t_T20'],
                   'psiDt_T20'          :sig['psiDtCAN_T20'],
                   'psiDtOpt_T20'       :sig['psiDtOpt_T20'],
                   'psiDtOptRaw_T20'    :sig['psiDtOptRaw_T20'],
                   'vxvRef_T20'         :sig['vxvRef_T20']
                 }
                 
    sio.savemat(FileName, signal_list, oned_as='row')


  
 
  # -------------------------------------------------------------------------------------------
  @staticmethod
  def plot_ego_vehicle_speed_and_yaw_rate(sig, FigNr=200): 

    # just the input signal
    fig=pl.figure(FigNr);   FigNr += 1
    fig.clear()
    fig.suptitle('ego vehicle speed and yaw rate')

    # ego vehicle speed
    sp=fig.add_subplot(211)
    sp.grid()
    sp.plot(sig['t_T20'],sig['vxvRef_T20']*3.6)
    sp.legend(('velocity',))
    sp.set_ylabel('[km/h]')
    
 
    # yaw rate
    sp=fig.add_subplot(212)
    sp.grid()
    sp.plot(sig['t_T20'],sig['psiDtCAN_T20'],'b')
    sp.plot(sig['t_T20'],sig['psiDtOpt_T20'],'r')
    sp.set_ylim(-0.05,0.05)
    sp.legend(('yaw rate (CAN)','yaw rate (EVI)'))
    sp.set_ylabel('[rad/s]')
    sp.set_xlabel('time [s]')
 
    fig.show()
    
  # ==========================================================
  @staticmethod
  def CalcVehTrajR(t,v0,wz,sig={}):
    # calc vehicle trajectory in R-system 
    # input:
    #   t   - time
    #   v0  - vehicle speed
    #   wz  - yaw rate
    # output:
    #    [x_ego_R, y_ego_R, psi] 

    #print " calc vehicle trajectory in R-system "
  
    
    # determine time interval
    dT = np.diff(t)
    dT = np.hstack((0.1,dT))
  
    # vehicle course angle
    psi = np.cumsum(dT*wz)
  
    # calc vehicle trajectory in R-system:  x_ego_R, y_ego_R
    x_ego_R = np.zeros_like(t)
    y_ego_R = np.zeros_like(t)
    for k in xrange(1,t.size):
      x_ego_R[k] = x_ego_R[k-1] + v0[k]*dT[k]*np.cos(psi[k]) 
      y_ego_R[k] = y_ego_R[k-1] + v0[k]*dT[k]*np.sin(psi[k])

    #print "vehicle trajectory in R-system calculated"
    
    # return
    sig['time']      = t
    sig['yaw_rate']  = wz
    sig['veh_speed'] = v0
    
    sig['x_ego_R']   = x_ego_R
    sig['y_ego_R']   = y_ego_R
    sig['psi']       = psi
    
    return sig
    
    
  # ==========================================================
  @staticmethod
  def plot_vehicle_trajectory_in_R_system(sig,FigNr=300):
    # plot vehicle trajectory sig['x_ego_R'],sig['y_ego_R'] in x-y plot
    
    fig=pl.figure(FigNr)
    fig.clear()
    fig.suptitle('fixed system R')

    sp=fig.add_subplot(111)
    sp.grid()
    sp.plot(sig['x_ego_R'],sig['y_ego_R'],'b-')
    sp.set_xlabel('x [m]')
    sp.set_ylabel('y [m]')
  
    cDataEgoVeh.TimeMarkings(sp,sig['time'],sig['x_ego_R'],sig['y_ego_R'])
  
    fig.show()
    return

  # ==========================================================
  @staticmethod
  def plot_vehicle_trajectory_and_yaw_rate_in_R_system(sig,FigNr=300): 
    # versus x-position
    
    fig=pl.figure(FigNr);  FigNr += 1
    fig.clear()
    fig.suptitle('yaw rate, yaw angle and lateral position in fixed system')

    #dx_max = 500
  
    sp=fig.add_subplot(311)
    sp.grid()
    sp.plot(sig['x_ego_R'],sig['yaw_rate'],'b')
    sp.set_ylabel('[rad/s]')
    sp.legend(('psiDt',))
    #sp.set_ylim(-0.05,0.05)
    
    sp=fig.add_subplot(312)
    sp.grid()
    sp.plot(sig['x_ego_R'],sig['psi']*180.0/np.pi,'b')
    sp.legend(('psi',))
    sp.set_ylabel('[deg]')
    #sp.set_ylim(-0.05,0.05)
      
    sp=fig.add_subplot(313)
    sp.grid()
    sp.plot(sig['x_ego_R'],sig['y_ego_R'],'b')
    sp.legend(('y in fixed system',))
    sp.set_xlabel('x [m]')
    sp.set_ylabel('[m]')
    #sp.set_ylim(-2.25,2.25)
    
    fig.show()
    
  # ==========================================================
  @staticmethod
  def plot_vehicle_trajectory_and_yaw_rate_in_R_system_vs_time(sig,FigNr=300): 
    # versus time
    
    fig=pl.figure(FigNr);  FigNr += 1
    fig.clear()
    fig.suptitle('yaw rate, yaw angle and lateral position in fixed system')

    #dx_max = 500
  
    sp=fig.add_subplot(311)
    sp.grid()
    sp.plot(sig['time'],sig['yaw_rate'],'b')
    sp.set_ylabel('[rad/s]')
    sp.legend(('psiDt',))
    #sp.set_ylim(-0.05,0.05)
    
    sp=fig.add_subplot(312)
    sp.grid()
    sp.plot(sig['time'],sig['psi']*180.0/np.pi,'b')
    sp.legend(('psi',))
    sp.set_ylabel('[deg]')
    #sp.set_ylim(-0.05,0.05)
    
  
    sp=fig.add_subplot(313)
    sp.grid()
    sp.plot(sig['time'],sig['y_ego_R'],'b')
    sp.set_xlabel('time [s]')
    sp.set_ylabel('[m]')
    sp.legend(('y in fixed system',))
  
    #sp.set_ylim(-2.25,2.25)
    #sp.set_xlim(0,dx_max)
  
    fig.show()
  # -------------------------------------------------------------------------------------------
  @staticmethod
  def TimeMarkings(sp,t,x,y,n=10): 
    # --------------------------------------
    # Zeitmarkierungen  
  
    if len(t)>2:
      idx = range(1,len(t),int(len(t)/n))
      t = t[idx]
      x = x[idx]
      y = y[idx]

    for k in xrange(len(t)):
      sp.plot(x[k],y[k],'bx');
      sp.text(x[k],y[k],' %3.0f s'%t[k])

  