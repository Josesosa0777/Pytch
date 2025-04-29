"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: Obstacle Classifier evalulation '''

''' to be called by DAS_eval.py '''

import numpy as np
import pylab as pl

import kbtools
import measparser

def getSignalByHandle(Source, DeviceName, Handle, SignalName, **kwargs):    
    """
    Get the signal via its handle and name.
    
    :Parameters:
      Handle : int
        Handle of the requested signal.
      DeviceName : str
      SignalName : str
        The end of the requested signal name eg dxv.
    :Keywords:
      Keywords are passed to `cSignalSource.getSignal`
    :ReturnType: two element list of `ndarray`
    :Return:
      Requested signal in time, value numpy array pairs.      
    """
    
    HandleName = 'fus.ObjData_TC.FusObj.i%d.%s'

    Time, Value = Source.getSignal(DeviceName, HandleName %(0, SignalName),**kwargs)
    Value = np.zeros_like(Value) # * np.NaN
    Idx   = 255.0*np.ones_like(Value) # * np.NaN
    for FusObjNr in xrange(33):
      Mask = np.logical_and(Source.getSignal(DeviceName, HandleName %(FusObjNr, 'Handle'), **kwargs)[1] == Handle, Handle>0)
      Value[Mask] = Source.getSignal(DeviceName, HandleName %(FusObjNr, SignalName),**kwargs)[1][Mask]
      Idx[Mask]   = FusObjNr
           
    return Time, Value, Idx

# -------------------------------------------------------------------------------------------------------------
def getIntervalAroundEvent(t,t_center,bool_signal):
   # determine interval around an event given by time instand t:center
   #
   #    bool_signal =  00000000111111111000000
   #                                ^ t_center
   #                           ^       ^     start_idx and stop_idx
   verbose = 0

   start_tmp = np.diff(np.hstack([0,np.logical_and(t < t_center,bool_signal)]))
   
   if verbose:
     print "start_tmp", start_tmp          
     print "nonzero(start_tmp)", np.nonzero(start_tmp)
     print "nonzero(start_tmp)[0]", np.nonzero(start_tmp)[0]
     print "start_idx = nonzero(start_tmp)[0][-2]", np.nonzero(start_tmp)[0][-2]

   start_idx = np.nonzero(start_tmp)[0][-2]

        
   stop_tmp = np.diff(np.hstack([np.logical_and(t_center < t, bool_signal),0]))
   if verbose:
     print "stop_tmp", start_tmp          
     print "nonzero(stop_tmp)", np.nonzero(start_tmp)
     print "nonzero(stop_tmp)[0]", np.nonzero(start_tmp)[0]
     print "start_idx = nonzero(stop_tmp)[0][1]", np.nonzero(start_tmp)[0][1]
                
   
   stop_idx   = np.nonzero(stop_tmp)[0][1]

   return start_idx, stop_idx 
   
# ====================================================================================================================
'''
  res["IntroFusHandle"]  
  res["IntroFusIdx"]       
  res["IntroOhlIdx"] 
  res["OHLObj_start_idx"] 
  res["OHLObj_stop_idx"]  
  res["OHLObj_t_start"]   
  res["OHLObj_t_stop"]    

  res["CMS0_wObstacle_thres"] 
  res["CMS3_wObstacle_thres"] 
  res["CMS5_wObstacle_thres"] 
  res["CMS7_wObstacle_thres"] 
  
   res["CMS0_dx"] 
   res["CMS3_dx"] 
   res["CMS5_dx"] 
   res["CMS7_dx"] 
   
           print "CMS0 %3.1f %3.1f m"%(CMS0_wObstacle_thres, CMS0_dx)
        print "CMS3 %3.1f %3.1f m"%(CMS3_wObstacle_thres, CMS3_dx)
        print "CMS5 %3.1f %3.1f m"%(CMS5_wObstacle_thres, CMS5_dx)
        print "CMS7 %3.1f %3.1f m"%(CMS7_wObstacle_thres, CMS7_dx)

'''        
   
# ====================================================================================================================
def ProcObstClas(Event):

   res = {}

   if Event['Radar'] == "CVR3":
      device = "MRR1plus-0-0"
   elif Event['Radar'] == "LRR3":
      device = 'ECU-0-0'    
       
   # parameters  
   pre_trigger  = 20
   post_trigger = 4
   
   # ------------------------------------------------
   # Figure Numbering      
   FigNr = 1

   # ------------------------------------------------
   # load measure file
   
   t_start = Event['t_start'] - pre_trigger
   t_stop  = Event['t_stop'] + post_trigger 
        
   Source = measparser.cSignalSource(Event['FullPath'])
   
   sig = {}
    
   # get signals
   # getSignal has Tmin, Tmax and Imin, Imax optional parameters  
   sig['t'], sig['Intro.Id'] = Source.getSignal(device, 'sit.IntroFinder_TC.Intro.i0.Id', Tmin=t_start, Tmax=t_stop)
   sig['Intro.Handle'] = Source.getSignal(device, "sit.IntroFinder_TC.Intro.i0.ObjectList.i0", Tmin=t_start, Tmax=t_stop)[1]
        
   # Handle only during SAS intro
   sig['Intro.Handle'] = sig['Intro.Handle'] * (sig['Intro.Id']==3)
           
   # get elements of SIT object
   sig['Intro.SIT.dxv'],FusIdx   = getSignalByHandle(Source, device, sig['Intro.Handle'] , 'dxv', Tmin=t_start, Tmax=t_stop)[1:3]
   sig['Intro.SIT.dyv']          = getSignalByHandle(Source, device, sig['Intro.Handle'] , 'dyv', Tmin=t_start, Tmax=t_stop)[1]
   sig['Intro.SIT.wObstacle']    = getSignalByHandle(Source, device, sig['Intro.Handle'] , 'wObstacle', Tmin=t_start, Tmax=t_stop)[1]
   sig['Intro.SIT.Handle']       = getSignalByHandle(Source, device, sig['Intro.Handle'] , 'Handle', Tmin=t_start, Tmax=t_stop)[1]
        
   # determine one IntroFusHandle and one IntroFusIdx
   IntroFusHandle =  np.median(sig['Intro.Handle'][:,np.nonzero(sig['Intro.Handle'])])
   res["IntroFusHandle"] =  IntroFusHandle    
 
   #print "FusIdx", FusIdx 
   IntroFusIdx = np.median(FusIdx[:,np.nonzero(FusIdx<255)])
   res["IntroFusIdx"] = IntroFusIdx
  
   # FUS Object
   sig['Intro.FUS.dxv']       = Source.getSignal(device, "fus.ObjData_TC.FusObj.i%d.dxv"%IntroFusIdx, Tmin=t_start, Tmax=t_stop)[1]
   sig['Intro.FUS.dyv']       = Source.getSignal(device, "fus.ObjData_TC.FusObj.i%d.dyv"%IntroFusIdx, Tmin=t_start, Tmax=t_stop)[1]
   sig['Intro.FUS.wObstacle'] = Source.getSignal(device, "fus.ObjData_TC.FusObj.i%d.wObstacle"%IntroFusIdx, Tmin=t_start, Tmax=t_stop)[1]

   # OHL Objects
   sig['Intro.LrrObjIdx'] = Source.getSignal(device, "fus_asso_mat.LrrObjIdx.i%d"%IntroFusIdx, Tmin=t_start, Tmax=t_stop, ScaleTime = sig['t'])[1]
   IntroOhlIdx = np.median(sig['Intro.LrrObjIdx'][:,np.nonzero(sig['Intro.LrrObjIdx']<255)])
   res["IntroOhlIdx"] = IntroOhlIdx
    
   sig['Intro.OHL.Valid_b']      = Source.getSignal(device,  "ohl.ObjData_TC.OhlObj.i%d.c.c.Valid_b"%IntroOhlIdx, Tmin=t_start, Tmax=t_stop)[1]
   sig['Intro.OHL.dx']           = Source.getSignal(device,  "ohl.ObjData_TC.OhlObj.i%d.dx"%IntroOhlIdx, Tmin=t_start, Tmax=t_stop)[1]
   sig['Intro.OHL.dy']           = Source.getSignal(device,  "ohl.ObjData_TC.OhlObj.i%d.dy"%IntroOhlIdx, Tmin=t_start, Tmax=t_stop)[1]
   sig['Intro.OHL.dbPowerFilt']  = (Source.getSignal(device, "ohl.ObjData_TC.OhlObj.i%d.internal.dbPowerFilt"%IntroOhlIdx, Tmin=t_start, Tmax=t_stop)[1])
   sig['Intro.OHL.probClass.i0'] = (Source.getSignal(device, "ohl.ObjData_TC.OhlObj.i%d.probClass.i0"%IntroOhlIdx, Tmin=t_start, Tmax=t_stop)[1])/32768.0
   sig['Intro.OHL.probClass.i1'] = (Source.getSignal(device, "ohl.ObjData_TC.OhlObj.i%d.probClass.i1"%IntroOhlIdx, Tmin=t_start, Tmax=t_stop)[1])/32768.0
   sig['Intro.OHL.probClass.i2'] = (Source.getSignal(device, "ohl.ObjData_TC.OhlObj.i%d.probClass.i2"%IntroOhlIdx, Tmin=t_start, Tmax=t_stop)[1])/32768.0
   sig['Intro.OHL.probClass.i3'] = (Source.getSignal(device, "ohl.ObjData_TC.OhlObj.i%d.probClass.i3"%IntroOhlIdx, Tmin=t_start, Tmax=t_stop)[1])/32768.0
   sig['Intro.OHL.probClass.i4'] = (Source.getSignal(device, "ohl.ObjData_TC.OhlObj.i%d.probClass.i4"%IntroOhlIdx, Tmin=t_start, Tmax=t_stop)[1])/32768.0

   sig['Intro.OHL.wInterfProb']   = (Source.getSignal(device, "ohl.ObjData_TC.OhlObj.i%d.wInterfProb"%IntroOhlIdx, Tmin=t_start, Tmax=t_stop)[1])
   sig['Intro.OHL.wGroundReflex'] = (Source.getSignal(device, "ohl.ObjData_TC.OhlObj.i%d.wGroundReflex"%IntroOhlIdx, Tmin=t_start, Tmax=t_stop)[1])
   sig['Intro.OHL.wExistProb']    = (Source.getSignal(device, "ohl.ObjData_TC.OhlObj.i%d.wExistProb"%IntroOhlIdx, Tmin=t_start, Tmax=t_stop)[1])

   # Ego Vehicle    
   sig['EgoVeh.psiDtOpt']    = Source.getSignal(device, "evi.General_TC.psiDtOpt", Tmin=t_start, Tmax=t_stop)[1]
   sig['EgoVeh.psiDtDt']     = Source.getSignal(device, "evi.General_TC.psiDtDt", Tmin=t_start, Tmax=t_stop) [1]
   sig['EgoVeh.vxvRef']      = Source.getSignal(device, "evi.General_TC.vxvRef", Tmin=t_start, Tmax=t_stop) [1]
   sig['EgoVeh.axvRef']      = Source.getSignal(device, "evi.General_TC.axvRef", Tmin=t_start, Tmax=t_stop) [1]
   sig['EgoVeh.kapCurvTraj'] = Source.getSignal(device, "evi.MovementData_TC.kapCurvTraj", Tmin=t_start, Tmax=t_stop) [1]
    

        
   # all signals read from SignalSource 
   Source.save()
        
   #-------------------------------------------------------
   # section No 2 s2 - only that OHL object included in the intro
        
   start_idx, stop_idx = getIntervalAroundEvent(sig['t'],Event['t_start'],sig['Intro.OHL.Valid_b'])
    
   res["OHLObj_start_idx"] = start_idx
   res["OHLObj_stop_idx"]  = stop_idx
    
   res["OHLObj_t_start"]   = sig['t'][start_idx]
   res["OHLObj_t_stop"]    = sig['t'][start_idx]
    
   sig['s2:t']                      = sig['t'][start_idx+1:stop_idx+1]
   sig['s2:Intro.OHL.dx']           = sig['Intro.OHL.dx'][start_idx+1:stop_idx+1]
   sig['s2:Intro.OHL.dy']           = sig['Intro.OHL.dy'][start_idx+1:stop_idx+1]
   sig['s2:Intro.OHL.dbPowerFilt']  = sig['Intro.OHL.dbPowerFilt'][start_idx+1:stop_idx+1]
   sig['s2:Intro.OHL.probClass.i0'] = sig['Intro.OHL.probClass.i0'][start_idx+1:stop_idx+1]
   sig['s2:Intro.OHL.probClass.i1'] = sig['Intro.OHL.probClass.i1'][start_idx+1:stop_idx+1]
   sig['s2:Intro.OHL.probClass.i2'] = sig['Intro.OHL.probClass.i2'][start_idx+1:stop_idx+1]
   sig['s2:Intro.OHL.probClass.i3'] = sig['Intro.OHL.probClass.i3'][start_idx+1:stop_idx+1]
   sig['s2:Intro.OHL.probClass.i4'] = sig['Intro.OHL.probClass.i4'][start_idx+1:stop_idx+1]
        
   sig['s2:Intro.OHL.wInterfProb']   = sig['Intro.OHL.wInterfProb'][start_idx+1:stop_idx+1]
   sig['s2:Intro.OHL.wGroundReflex'] = sig['Intro.OHL.wGroundReflex'][start_idx+1:stop_idx+1]
   sig['s2:Intro.OHL.wExistProb']    = sig['Intro.OHL.wExistProb'][start_idx+1:stop_idx+1]

   # FUS
   sig['s2:Intro.FUS.dxv']           = sig['Intro.FUS.dxv'][start_idx+1:stop_idx+1]
   sig['s2:Intro.FUS.dyv']           = sig['Intro.FUS.dyv'][start_idx+1:stop_idx+1]
   sig['s2:Intro.FUS.wObstacle']     = sig['Intro.FUS.wObstacle'][start_idx+1:stop_idx+1]
        
   # SIT
   sig['s2:Intro.SIT.dxv']           = sig['Intro.SIT.dxv'][start_idx+1:stop_idx+1]
   sig['s2:Intro.SIT.dyv']           = sig['Intro.SIT.dyv'][start_idx+1:stop_idx+1]
   sig['s2:Intro.SIT.wObstacle']     = sig['Intro.SIT.wObstacle'][start_idx+1:stop_idx+1]
        
   # EgoVeh
   sig['s2:EgoVeh.psiDtOpt']    = sig['EgoVeh.psiDtOpt'][start_idx+1:stop_idx+1]
   sig['s2:EgoVeh.psiDtDt']     = sig['EgoVeh.psiDtDt'][start_idx+1:stop_idx+1]
   sig['s2:EgoVeh.vxvRef']      = sig['EgoVeh.vxvRef'][start_idx+1:stop_idx+1]
   sig['s2:EgoVeh.axvRef']      = sig['EgoVeh.axvRef'][start_idx+1:stop_idx+1]
   sig['s2:EgoVeh.kapCurvTraj'] = sig['EgoVeh.kapCurvTraj'][start_idx+1:stop_idx+1]

        
   # ------------------------------
   # start with to t=0
   sig['s2:t:new_origin'] =  sig['s2:t'] - sig['s2:t'] [0] 

   '''
        'probClass[0]-obstacle',
        'probClass[1]-underpassable',
        'probClass[2]-overrunable',
        'probClass[3]-interference',
        'probClass[4]-unknown',
   '''
        
        
   # CMS Level
   '''
     wObstacle   >0.1    >=0.3   >=0.6   >=0.8
     CMSLevel    0       3       5       7 
   '''
        
   #   stop_tmp = np.diff(np.hstack([np.logical_and(t_center < t, bool_signal),0]))
   # sig['s2:Intro.OHL.probClass.i0']
   # sig['s2:Intro.OHL.dx']
        
   CMS0_wObstacle_thres = 0.1
   CMS3_wObstacle_thres = 0.3
   CMS5_wObstacle_thres = 0.6
   CMS7_wObstacle_thres = 0.8
    
   res["CMS0_wObstacle_thres"] =  CMS0_wObstacle_thres
   res["CMS3_wObstacle_thres"] =  CMS3_wObstacle_thres
   res["CMS5_wObstacle_thres"] =  CMS5_wObstacle_thres
   res["CMS7_wObstacle_thres"] =  CMS7_wObstacle_thres
  
   try:  
     CMS0_dx =  sig['s2:Intro.OHL.dx'][:,np.nonzero(sig['s2:Intro.OHL.probClass.i0'] >= CMS0_wObstacle_thres)][0][0]
   except:
     CMS0_dx = 0.0
   
   try:
     CMS3_dx =  sig['s2:Intro.OHL.dx'][:,np.nonzero(sig['s2:Intro.OHL.probClass.i0'] >= CMS3_wObstacle_thres)][0][0]
   except:
     CMS3_dx = 0.0

   try:     
     CMS5_dx =  sig['s2:Intro.OHL.dx'][:,np.nonzero(sig['s2:Intro.OHL.probClass.i0'] >= CMS5_wObstacle_thres)][0][0]
   except:
     CMS5_dx = 0.0
     
   try:
     CMS7_dx =  sig['s2:Intro.OHL.dx'][:,np.nonzero(sig['s2:Intro.OHL.probClass.i0'] >= CMS7_wObstacle_thres)][0][0]
   except:
     CMS7_dx = 0.0
          
   res["CMS0_dx"] =  CMS0_dx
   res["CMS3_dx"] =  CMS3_dx
   res["CMS5_dx"] =  CMS5_dx
   res["CMS7_dx"] =  CMS7_dx
        
        
      
        
        
   # ------------------------------------------------------
   # time history
        
   f=pl.figure(FigNr);   FigNr += 1
   f.clear()
   f.suptitle('file: %s'%Event['FileName'])

   sp=f.add_subplot(411)
   sp.set_title('OHL - Obstacle Classifier (versus time)')
   sp.grid()
   sp.plot(sig['s2:t:new_origin'],sig['s2:Intro.OHL.dx'],'-')
   sp.legend(('dx',),loc="lower left")
   sp.set_ylabel('[m]')
   #sp.set_xlabel('time [s]')
   sp.set_ylim(0.0,180.0)
        
        
   sp=f.add_subplot(412)
   sp.grid()
   sp.plot(sig['s2:t:new_origin'],sig['s2:Intro.OHL.dbPowerFilt'],'-')
   sp.legend(('dbPowerFilt',),loc="lower left")
   sp.set_ylabel('[dB]')
   #sp.set_xlabel('time [s]')
   sp.set_ylim(0.0,350.0)

   sp=f.add_subplot(413)
   sp.grid()
   sp.plot(sig['s2:t:new_origin'],sig['s2:Intro.OHL.probClass.i0'],'b-')
   sp.plot(sig['s2:t:new_origin'],sig['s2:Intro.OHL.probClass.i1'],'r-')
   sp.plot(sig['s2:t:new_origin'],sig['s2:Intro.OHL.probClass.i2'],'g-')
   sp.plot(sig['s2:t:new_origin'],sig['s2:Intro.OHL.probClass.i3'],'c-')
   sp.plot(sig['s2:t:new_origin'],sig['s2:Intro.OHL.probClass.i4'],'m-')
   sp.legend(('wObstacle','wUnderpassable','wOverrunable','wInterference','wUnknown'),loc="upper left")      
   sp.set_ylabel('[-]')
   #sp.set_xlabel('time [s]')
   sp.set_ylim(-0.1,1.1)

   sp=f.add_subplot(414)
   sp.grid()
   sp.plot(sig['s2:t:new_origin'],sig['s2:Intro.OHL.wInterfProb'],'b-')
   sp.plot(sig['s2:t:new_origin'],sig['s2:Intro.OHL.wGroundReflex'],'r-')
   sp.plot(sig['s2:t:new_origin'],sig['s2:Intro.OHL.wExistProb'],'k-')
   sp.legend(('wInterfProb','wGroundReflex','wExistProb'),loc="upper left")
   sp.set_ylabel('[-]')
   sp.set_xlabel('time [s]')
   sp.set_ylim(-0.1,1.1)

   
   s  = ''
   s += 'FileName = %s; '%kbtools.esc_bl(Event['FileName'])
   s += 't\\_start = %4.2f s; '%t_start
   #s += 't\\_stop  = %4.2f s; '%t_stop
   s += 'duration  = %4.2f s'%(t_stop-t_start)
   res["Plot1_ObstClas:figure"] = f
   res["Plot1_ObstClas:caption"] = s
   
   
   
 
   # ------------------------------------------------------
   # signals related to distance to target dx
        
   f=pl.figure(FigNr);   FigNr += 1
   f.clear()
   f.suptitle('file: %s'%Event['FileName'])


   sp=f.add_subplot(311)
   sp.set_title('OHL - Obstacle Classifier (versus distance to target)')
   sp.grid()
   sp.plot(-sig['s2:Intro.OHL.dx'],sig['s2:Intro.OHL.dbPowerFilt'],'-')
   sp.legend(('dbPowerFilt',),loc="lower left")
   sp.set_ylabel('[db]')
   #sp.set_xlabel('dx [m]')
   sp.set_ylim(-0.1,350.0)
   sp.set_xlim(-160.0,0.0)
        
   sp=f.add_subplot(312)
   sp.grid()
   sp.plot(-sig['s2:Intro.OHL.dx'],sig['s2:Intro.OHL.probClass.i0'],'b-')
   sp.plot(-sig['s2:Intro.OHL.dx'],sig['s2:Intro.OHL.probClass.i1'],'r-')
   sp.plot(-sig['s2:Intro.OHL.dx'],sig['s2:Intro.OHL.probClass.i2'],'g-')
   sp.plot(-sig['s2:Intro.OHL.dx'],sig['s2:Intro.OHL.probClass.i3'],'c-')
   sp.plot(-sig['s2:Intro.OHL.dx'],sig['s2:Intro.OHL.probClass.i4'],'m-')
   sp.legend(('wObstacle','wUnderpassable','wOverrunable','wInterference','wUnknown'),loc="upper left")      
   sp.set_ylabel('[-]')
   sp.set_xlabel('dx [m]')
   sp.set_ylim(-0.1,1.1)
   sp.set_xlim(-160.0,0.0)

   sp=f.add_subplot(313)
   sp.grid()
   sp.plot(-sig['s2:Intro.OHL.dx'],sig['s2:Intro.OHL.wInterfProb'],'b-')
   sp.plot(-sig['s2:Intro.OHL.dx'],sig['s2:Intro.OHL.wGroundReflex'],'r-')
   sp.plot(-sig['s2:Intro.OHL.dx'],sig['s2:Intro.OHL.wExistProb'],'k-')
   sp.legend(('wInterfProb','wGroundReflex','wExistProb'),loc="upper left")
   sp.set_ylabel('[-]')
   sp.set_xlabel('dx [m]')
   sp.set_ylim(-0.1,1.1)
   sp.set_xlim(-160.0,0.0)
        
   s  = ''
   s += 'FileName = %s; '%kbtools.esc_bl(Event['FileName'])
   s += 't\\_start = %4.2f s; '%t_start
   #s += 't\\_stop  = %4.2f s; '%t_stop
   s += 'duration  = %4.2f s'%(t_stop-t_start)
   res["Plot2_ObstClas:figure"] = f
   res["Plot2_ObstClas:caption"] = s
   
  
   # ------------------------------------------------------
   # only wObstacle
        
   f=pl.figure(FigNr);   FigNr += 1
   f.clear()
   f.suptitle('file: %s'%Event['FileName'])

   sp=f.add_subplot(111)
   sp.grid()
   sp.plot(-sig['s2:Intro.OHL.dx'],sig['s2:Intro.OHL.probClass.i0'],'b-')
   sp.plot(-CMS0_dx,CMS0_wObstacle_thres,'rx')
   sp.plot(-CMS3_dx,CMS3_wObstacle_thres,'rx')
   sp.plot(-CMS5_dx,CMS5_wObstacle_thres,'rx')
   sp.plot(-CMS7_dx,CMS7_wObstacle_thres,'rx')
   sp.plot([-160,0],[CMS0_wObstacle_thres,CMS0_wObstacle_thres],'r--')
   sp.plot([-160,0],[CMS3_wObstacle_thres,CMS3_wObstacle_thres],'r--')
   sp.plot([-160,0],[CMS5_wObstacle_thres,CMS5_wObstacle_thres],'r--')
   sp.plot([-160,0],[CMS7_wObstacle_thres,CMS7_wObstacle_thres],'r--')

   sp.plot([-CMS0_dx,-CMS0_dx],[0,CMS0_wObstacle_thres],'r--')
   sp.plot([-CMS3_dx,-CMS3_dx],[0,CMS3_wObstacle_thres],'r--')
   sp.plot([-CMS5_dx,-CMS5_dx],[0,CMS5_wObstacle_thres],'r--')
   sp.plot([-CMS7_dx,-CMS7_dx],[0,CMS7_wObstacle_thres],'r--')
                
   sp.text(-CMS0_dx,CMS0_wObstacle_thres,'%3.1fm'%CMS0_dx)
   sp.text(-CMS3_dx,CMS3_wObstacle_thres,'%3.1fm'%CMS3_dx)
   sp.text(-CMS5_dx,CMS5_wObstacle_thres,'%3.1fm'%CMS5_dx)
   sp.text(-CMS7_dx,CMS7_wObstacle_thres,'%3.1fm'%CMS7_dx)
        
   sp.legend(('wObstacle',),loc="upper left")      
   sp.set_ylabel('[-]')
   sp.set_xlabel('dx [m]')
   sp.set_ylim(-0.1,1.1)
   sp.set_xlim(-160.0,0.0)
        

   s  = ''
   s += 'FileName = %s; '%kbtools.esc_bl(Event['FileName'])
   s += 't\\_start = %4.2f s; '%t_start
   #s += 't\\_stop  = %4.2f s; '%t_stop
   s += 'duration  = %4.2f s'%(t_stop-t_start)
   res["Plot3_ObstClas:figure"] = f
   res["Plot3_ObstClas:caption"] = s
  
       
   # ------------------------------------------------------
   # SIT, FUS, OHL
        
   f=pl.figure(FigNr);   FigNr += 1
   f.clear()
   f.suptitle('file: %s'%Event['FileName'])

   sp=f.add_subplot(611)
   sp.grid()
   sp.plot(sig['t'],sig['EgoVeh.vxvRef']*3.6,'b-')
   sp.set_title('ego vehicle velocity')
   #sp.legend(('SIT','FUS','OHL'),loc="upper right")  
   sp.set_ylabel('[km/h]')
   #sp.set_xlabel('time [s]')
   sp.set_ylim(0.0,100.0)
   sp.set_xlim(t_start,t_stop)

   sp=f.add_subplot(612)
   sp.grid()
   sp.plot(sig['t'],sig['EgoVeh.axvRef'],'b-')
   sp.set_title('ego vehicle acceleration')
   #sp.legend(('SIT','FUS','OHL'),loc="upper right")  
   sp.set_ylabel('[m/s^2]')
   #sp.set_xlabel('time [s]')
   #sp.set_ylim(0.0,100.0)
   sp.set_xlim(t_start,t_stop)

   sp=f.add_subplot(613)
   sp.grid()
   sp.plot(sig['t'],sig['EgoVeh.kapCurvTraj'],'b-')
   sp.set_title('ego vehicle trajectory curvature ')
   #sp.legend(('SIT','FUS','OHL'),loc="upper right")  
   sp.set_ylabel('[1/m]')
   #sp.set_xlabel('time [s]')
   #sp.set_ylim(0.0,100.0)
   sp.set_xlim(t_start,t_stop)
              
        
   sp=f.add_subplot(614)
   sp.grid()
   sp.plot(sig['s2:t'],sig['s2:Intro.SIT.dxv'],'r-')
   sp.plot(sig['s2:t'],sig['s2:Intro.FUS.dxv'],'g-')
   sp.plot(sig['s2:t'],sig['s2:Intro.OHL.dx'],'b-')
   sp.set_title('dx')
   sp.legend(('SIT','FUS','OHL'),loc="upper right")  
   sp.set_ylabel('[m]')
   #sp.set_xlabel('time [s]')
   sp.set_ylim(0.0,180.0)
   sp.set_xlim(t_start,t_stop)

   sp=f.add_subplot(615)
   sp.grid()
   sp.plot(sig['s2:t'],sig['s2:Intro.SIT.dyv'],'r-')
   sp.plot(sig['s2:t'],sig['s2:Intro.FUS.dyv'],'g-')
   sp.plot(sig['s2:t'],sig['s2:Intro.OHL.dy'],'b-')
   sp.set_title('dy')
   sp.legend(('SIT','FUS','OHL'),loc="upper left")  
   sp.set_ylabel('[m]')
   #sp.set_xlabel('time [s]')
   #sp.set_ylim(0.0,180.0)
   sp.set_xlim(t_start,t_stop)

   sp=f.add_subplot(616)
   sp.grid()
   sp.plot(sig['s2:t'],sig['s2:Intro.SIT.wObstacle'],'r-')
   sp.plot(sig['s2:t'],sig['s2:Intro.FUS.wObstacle'],'g-')
   sp.plot(sig['s2:t'],sig['s2:Intro.OHL.probClass.i0'],'b-')
   sp.set_title('Intro.wObstacle')
   sp.legend(('SIT','FUS','OHL'),loc="upper left")  
   sp.set_ylabel('-')
   sp.set_xlabel('time [s]')
   sp.set_ylim(-0.1,1.1)
   sp.set_xlim(t_start,t_stop)

   s  = ''
   s += 'FileName = %s; '%kbtools.esc_bl(Event['FileName'])
   s += 't\\_start = %4.2f s; '%t_start
   #s += 't\\_stop  = %4.2f s; '%t_stop
   s += 'duration  = %4.2f s'%(t_stop-t_start)
   res["Plot4_ObstClas:figure"] = f
   res["Plot4_ObstClas:caption"] = s

  
   return res
   

# ==============================================================================================
class cEvalObstClas():
    # ------------------------------------------------------------------------------------------
    def __init__(self):       # constructor
      self.myname = 'EvalObstClas'   # name of this user specific evaluation
      self.H4E = {}                  # H4E hunt4event directory


    # ------------------------------------------------------------------------------------------
    def __del__(self):         # destructor
      pass
      
    # ------------------------------------------------------------------------------------------
    def init(self,folder):     # general start
       
      t_join = 0 
      
      # IntroFinder - Same Approach Stationary - SAS  (3)
      self.H4E['LRR3_IntroFinder_SAS'] = kbtools.cHunt4Event('on_phase','LRR3 IntroFinder SAS',t_join)
      self.H4E['CVR3_IntroFinder_SAS'] = kbtools.cHunt4Event('on_phase','CVR3 IntroFinder SAS',t_join)

    # ------------------------------------------------------------------------------------------
    def reinit(self):          # recording interrupted
      for key in self.H4E.keys():
        self.H4E[key].reinit()

    # ------------------------------------------------------------------------------------------
    def process(self,Source):  # evaluate recorded file
      
      # ---------------------------------------  
      # LRR3
      device = 'ECU-0-0'

      try:    
        # Intro Finder 
        Time, Value = Source.getSignal(device, 'sit.IntroFinder_TC.Intro.i0.Id')
        # Same Approach Stationary - SAS  (3)
        self.H4E['LRR3_IntroFinder_SAS'].process(Time, (Value==3), Source)
        
      except:
        pass
        
      # ---------------------------------------      
      # CVR3 
      device = 'MRR1plus-0-0'

      try:    
        # Intro Finder 
        Time, Value = Source.getSignal(device, 'sit.IntroFinder_TC.Intro.i0.Id')
        # Same Approach Stationary - SAS  (3)
        self.H4E['CVR3_IntroFinder_SAS'].process(Time, (Value==3), Source)
        
      except:
        pass

      
    # ------------------------------------------------------------------------------------------
    def finish(self):          # end of recording
      for key in self.H4E.keys():
        self.H4E[key].finish()
      
      # save events   
      for key in self.H4E.keys():
        self.H4E[key].save_event(key)

      
    # ------------------------------------------------------------------------------------------
    def report_init(self):     # prepare for report - input tex file to main
      self.kb_tex.tex_main('\n\\input{%s.tex}\n'%self.myname)
      pass  

    # ------------------------------------------------------------------------------------------
    def report(self):          # report events
      self.kb_tex.workingfile('%s.tex'%self.myname)
      
      # Eval ObstClas - main section
      self.kb_tex.tex('\n\\newpage\\section{EvalObstClas}')
      
      # LRR3 
      self.kb_tex.tex('\n\\subsection{LRR3}')
 
      self.kb_tex.tex('\n\\subsubsection{IntroFinder SAS}')
      label = self.kb_tex.table(self.H4E['LRR3_IntroFinder_SAS'].table_array())

      
      # CVR3
      self.kb_tex.tex('\n\\subsection{CVR3}')
 
      self.kb_tex.tex('\n\\subsubsection{IntroFinder SAS}')
      label = self.kb_tex.table(self.H4E['CVR3_IntroFinder_SAS'].table_array())
     
      self.kb_tex.tex('\nEvalObstClas-step1-finished')
      
    # ------------------------------------------------------------------------------------------
    def step2(self):
      # ---------------------------------------------------
      # initialisation
      print "step2 EvalObstClas"
      
      self.kb_tex.tex_main('\n\\input{%s.tex}\n'%self.myname)
      
      self.kb_tex.workingfile('%s.tex'%self.myname)
      
      # Eval ObstClas - main section
      self.kb_tex.tex('\n\\newpage\\section{EvalObstClas}')

     
      #  path where numpy backup files will be saved
      #measproc.NpyHomeDir = r'C:\tmp_python'
      measparser.SignalSource.NpyHomeDir = r'C:\tmp_python' # cfg['NpyHomeDir']
      
      self.kb_tex.tex('\n\\newpage\\subsection{CVR3 IntroFinder SAS}')

      # ---------------------------------------------------
      # get and process events
      H4E       = kbtools.cHunt4Event('no','Babu',10)
      EventList_all = H4E.return_event('CVR3_IntroFinder_SAS')
      #EventList = EventList_all[0:1]
      #EventList = EventList_all[1:2]
      #EventList = EventList_all[2:3]
      #EventList = EventList_all[3:4]
      EventList = EventList_all
      print EventList_all
      
      
      for Event_No, Event in enumerate(EventList):
        Event_No += 1
        print "(%d/%d)" % (Event_No,len(EventList))
        
        Event['Radar'] = "CVR3"
        
        self.kb_tex.tex('\n\\newpage\\subsubsection{No %d/%d}'%(Event_No,len(EventList)))

        res = ProcObstClas(Event)
        
        self.kb_tex.tex('\n\\newpage\\paragraph{wObstacle}')
        label = self.kb_tex.epsfig(res["Plot3_ObstClas:figure"],res["Plot3_ObstClas:caption"])

        self.kb_tex.tex('\n\\newpage\\paragraph{vs. dx}')
        label = self.kb_tex.epsfig(res["Plot2_ObstClas:figure"],res["Plot2_ObstClas:caption"])

        self.kb_tex.tex('\n\\newpage\\paragraph{vs. time}')
        label = self.kb_tex.epsfig(res["Plot1_ObstClas:figure"],res["Plot1_ObstClas:caption"])

        self.kb_tex.tex('\n\\newpage\\paragraph{Intro}')
        label = self.kb_tex.epsfig(res["Plot4_ObstClas:figure"],res["Plot4_ObstClas:caption"])

      self.kb_tex.tex('\nEvalObstClas-step2-finished')



#-------------------------------------------------------------------------      











