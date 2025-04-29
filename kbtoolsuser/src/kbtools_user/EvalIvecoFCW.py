"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: evalulation of Iveco's FCW (Forward Collision Warning) '''

''' to be called by DAS_eval.py '''

import numpy as np
import pylab as pl

import measproc
import kbtools

# ==============================================================================================
class cEvalIvecoFCW():
    # ------------------------------------------------------------------------------------------
    def __init__(self):        # constructor
      self.myname = 'EvalIvecoFCW'   # name of this user specific evaluation

    # ------------------------------------------------------------------------------------------
    def __del__(self):         # destructor
      pass

    # ------------------------------------------------------------------------------------------
    def step2(self):     
      
      # link Iveco_FCW tex part to tex main document 
      self.kb_tex.tex_main('\n\\input{Iveco_FCW.tex}\n');

      # create Iveco FCW -> frame
      self.kb_tex.workingfile('Iveco_FCW.tex');
      self.kb_tex.tex('\n\\newpage\\section{Iveco FCW}')
      self.kb_tex.tex('\n\\input{Iveco_FCW_overview.tex}\n');
      self.kb_tex.tex('\n\\input{Iveco_FCW_details.tex}\n');

      # create Iveco FCW details
      self.kb_tex.workingfile('Iveco_FCW_details.tex');
      self.kb_tex.tex('\n\\subsection{Details Iveco FCW}')
      Iveco_FCW_table = self.calc_Iveco_FCW()
      
      self.kb_tex.tex('\n\\subsection{Details ATS4}')
      ATS4_table = self.calc_ATS4()

      self.kb_tex.tex('\n\\subsection{Details repprew}')
      repprew_table = self.calc_repprew()
      
      # create Iveco FCW overview
      self.kb_tex.workingfile('Iveco_FCW_overview.tex');
      self.kb_tex.tex('\n\\subsection{Overview Iveco FCW}')
      label = self.kb_tex.table(Iveco_FCW_table)

      self.kb_tex.tex('\n\\subsection{Overview ATS4}')
      label = self.kb_tex.table(ATS4_table)

      self.kb_tex.tex('\n\\subsection{Overview repprew}')
      label = self.kb_tex.table(repprew_table)

      pass

      
    # =============================================================================
    def calc_Iveco_FCW(self):

      # ---------------------------------------------------
      # initialisation
      
      # table
      table_headline = ['Idx','ATS4','ttc','dx','vr','ATS0','repprew','FileName']
      table_array    = [table_headline]
      table_n_track  = 0

      # Figure Numbering      
      FigNr = 1
  
  
  
      # ---------------------------------------------------
      # get and process events
      H4E       = kbtools.cHunt4Event('no','Babu',10)
      EventList = H4E.return_event('ACCDistanceAlert')
      
     
      
      for Event_No, Event in enumerate(EventList):
        Event_No += 1
        print "(%d/%d)" % (Event_No,len(EventList))
        
        self.kb_tex.tex('\n\\newpage\\subsubsection{No %d}'%Event_No)
    
        FileName = Event['FileName']
       
    
        pre_trigger  = 4
        post_trigger = 4
        t_start = Event['t_start'] 
        t_stop  = Event['t_stop']  
        
        # load measure file
        FullPath = Event['FullPath']
        Source = measproc.cEventFinder(FullPath)
   
        sig = {}
    
        # create a common time base
        #Time = Source.getSignal("ACC1_27(98FE6F27)_1_", "ACCDistanceAlertSignal")[0]
        Time = Source.getSignal("ECU_0_0", "evi.General_T20.vxvRef")[0]   # T20
     
        # select section     
        t = Time
        t = t[np.nonzero(np.logical_and((t_start-pre_trigger) < t,t < (t_start + post_trigger)))]
    
        # get signals    
        sig['ACCDistanceAlertSignal'] = Source.getSignal("ACC1_27(98FE6F27)_1_", "ACCDistanceAlertSignal",ScaleTime = t)[1]

        # LRR3
        device = 'ECU_0_0'
        sig['ATS0_Handle']  = Source.getSignal(device, "ats.Po_T20.PO.i0.Handle",ScaleTime = t)[1]
        sig['ATS4_Handle']  = Source.getSignal(device, "ats.Po_T20.PO.i4.Handle",ScaleTime = t)[1]
        sig['repprew']      = Source.getSignal(device, 'repprew.__b_Rep.__b_RepBase.status',ScaleTime = t)[1]
  
        # ACC msg to Iveco  
        sig['Iveco_ACC_dx']             = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "HighResolutionDistanceToTarget",ScaleTime = t)[1]
        sig['Iveco_ACC_vr']             = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "RelativeVelocityToTarget",ScaleTime = t)[1]
        sig['Iveco_ACC_ObjectType']     = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "ObjectType",ScaleTime = t)[1]
        sig['Iveco_ACC_TargetLossType'] = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "TargetLossType",ScaleTime = t)[1]
        sig['Iveco_ACC_StatusOfSensor'] = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "StatusOfSensor",ScaleTime = t)[1]
        sig['Iveco_ACC_PsiDt']          = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "HighResolutionYawRate",ScaleTime = t)[1]

 
        # set origin to t_start 
        sig['t'] = t - t_start
  
     
        idx = np.nonzero(np.logical_and(-0.5 < sig['t'],sig['t'] < 0.0))
        # check if it is cause by an ATS4 objects 
        x = sig['ATS4_Handle'][idx]
        if (x>0).any():
          ATS4_present = 'yes'
        else:
          ATS4_present = 'no'
          
        # check if ATS0 objects present
        x = sig['ATS0_Handle'][idx]
        if (x>0).any():
          ATS0_present = 'yes'
        else:
          ATS0_present = 'no'

        # check if ASF prewarning present
        x = sig['repprew'][idx]
        if (x==6).any():
          repprew_present = 'yes'
        else:
          repprew_present = 'no'

          
        # attributes of target object right before FCW
        idx = np.nonzero(np.logical_and(-0.5 < sig['t'],sig['t'] < 0.5))
        
        dx = sig['Iveco_ACC_dx'][idx]
        vr = sig['Iveco_ACC_vr'][idx]
        dx = np.min(dx[np.nonzero(dx < 650)])
        vr = np.max(vr[np.nonzero(vr < 260)])
                
        print dx
        print vr 
        
       
        
        # time to collision 
        ttc = dx/(vr/3.6)
        
        # ------------------------------------------------------
        # add to table
        table_n_track = table_n_track +1
        table_array.append(['%d'%table_n_track,
                            '%s'%ATS4_present,
                            '%3.2f s'%ttc,
                            '%3.2f m'%dx,
                            '%3.2f km/h'%vr,
                            '%s'%ATS0_present,
                            '%s'%repprew_present,
                            self.kb_tex.esc_bl(FileName)])

  
  
        # ------------------------------------------------------
        f=pl.figure(FigNr);   FigNr += 1
        f.clear()
        f.suptitle('ACCDistanceAlert')

        sp=f.add_subplot(711)
        sp.grid()
        sp.plot(sig['t'],sig['ACCDistanceAlertSignal'],'-')
        sp.set_title('ACCDistanceAlert')
        sp.set_ylabel('bool')
        sp.set_ylim(-0.1,1.1)
        
        sp=f.add_subplot(712)
        sp.grid()
        sp.plot(sig['t'],sig['ATS0_Handle']>0 ,'-')
        sp.set_title('ATS0_Handle present')
        sp.set_ylabel('-')
        sp.set_ylim(-0.1,1.1)
    

        sp=f.add_subplot(713)
        sp.grid()
        sp.plot(sig['t'],sig['ATS4_Handle']>0 ,'-')
        sp.set_title('ATS4_Handle present')
        sp.set_ylabel('-')
        sp.set_ylim(-0.1,1.1)


        sp=f.add_subplot(714)
        sp.grid()
        sp.plot(sig['t'],sig['repprew'] ,'-')
        sp.set_title('repprew')
        sp.set_xlabel('time [s]')
        sp.set_ylabel('-')
        sp.set_ylim(-0.1,7.1)

    
        sp=f.add_subplot(715)
        sp.grid()
        sp.plot(sig['t'],sig['Iveco_ACC_dx'] ,'-')
        sp.set_title('Iveco_ACC_dx')
        sp.set_ylabel('m')
        sp.set_ylim(0,80)

        sp=f.add_subplot(716)
        sp.grid()
        sp.plot(sig['t'],sig['Iveco_ACC_vr'] ,'-')
        sp.set_title('Iveco_ACC_vx')
        sp.set_ylabel('km/h')
        sp.set_ylim(0,80)

        sp=f.add_subplot(717)
        sp.grid()
        sp.plot(sig['t'],sig['Iveco_ACC_ObjectType']  ,'-')
        sp.set_title('Iveco_ACC_ObjectType')
        sp.set_xlabel('time relative to event[s]')
        sp.set_ylabel('-')
        sp.set_ylim(0,4)

    
        #f.show()
        s  = ''
        s += 'FileName = %s; '%self.kb_tex.esc_bl(FileName)
        s += 't\\_start = %4.2f s; '%t_start
        #s += 't\\_stop  = %4.2f s; '%t_stop
        s += 'duration  = %4.2f s'%(t_stop-t_start)
        label = self.kb_tex.epsfig(f,s)
  
      return table_array
    # =============================================================================
    def calc_ATS4(self):

      # ---------------------------------------------------
      # initialisation
      
      # table
      table_headline = ['Idx','ATS4','ttc','dx','vr','ATS0','repprew','Iveco FCW']
      table_array    = [table_headline]
      table_n_track  = 0

      # Figure Numbering      
      FigNr = 1
  
  
  
      # ---------------------------------------------------
      # get and process events
      H4E       = kbtools.cHunt4Event('no','Babu',10)
      EventList = H4E.return_event('LRR3_ATS4')
      
      
      for Event_No, Event in enumerate(EventList):
        Event_No += 1
        print "(%d/%d)" % (Event_No,len(EventList))
        
        self.kb_tex.tex('\n\\newpage\\subsubsection{No %d}'%Event_No)
    
        FileName = Event['FileName']
       
    
        pre_trigger  = 4
        post_trigger = 4
        t_start = Event['t_start'] 
        t_stop  = Event['t_stop']  
        dura = t_stop-t_start
        
        # load measure file
        FullPath = Event['FullPath']
        #Source = measproc.cEventFinder(FullPath)
        Source = cLrr3Source(FullPath)
   
        sig = {}
    
        # create a common time base
        #Time = Source.getSignal("ACC1_27(98FE6F27)_1_", "ACCDistanceAlertSignal")[0]
        Time = Source.getSignal("ECU_0_0", "evi.General_T20.vxvRef")[0]   # T20

        
        # select section     
        t = Time
        t = t[np.nonzero(np.logical_and((t_start-pre_trigger) < t,t < (t_start + post_trigger)))]
    
        # get signals    
        sig['ACCDistanceAlertSignal'] = Source.getSignal("ACC1_27(98FE6F27)_1_", "ACCDistanceAlertSignal",ScaleTime = t)[1]

        # LRR3
        device = 'ECU_0_0'
        sig['ATS0_Handle']  = Source.getSignal(device, "ats.Po_T20.PO.i0.Handle",ScaleTime = t)[1]
        sig['ATS4_Handle']  = Source.getSignal(device, "ats.Po_T20.PO.i4.Handle",ScaleTime = t)[1]
        sig['repprew']      = Source.getSignal(device, 'repprew.__b_Rep.__b_RepBase.status',ScaleTime = t)[1]
  
        sig['ATS4_dx']      = Source.getSignal(device, 'ats.Po_T20.PO.i4.dxvFilt',ScaleTime = t)[1]
        sig['ATS4_vr']      = Source.getSignal(device, 'ats.Po_T20.PO.i4.vxvFilt',ScaleTime = t)[1]
  
        #sig['Intro_Handle'] = Source.getSignal(device, 'sit.IntroFinder_TC.Intro.i0.Id',ScaleTime = t)[1]
        #tmp_t, sig['Intro_dx'] = calcByHandle(Source, 'dxv',t)
        #tmp_t, sig['Intro_vr'] = calcByHandle(Source, 'vxv',t)
  
        # ACC msg to Iveco  
        sig['Iveco_ACC_dx']             = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "HighResolutionDistanceToTarget",ScaleTime = t)[1]
        sig['Iveco_ACC_vr']             = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "RelativeVelocityToTarget",ScaleTime = t)[1]
        sig['Iveco_ACC_ObjectType']     = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "ObjectType",ScaleTime = t)[1]
        sig['Iveco_ACC_TargetLossType'] = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "TargetLossType",ScaleTime = t)[1]
        sig['Iveco_ACC_StatusOfSensor'] = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "StatusOfSensor",ScaleTime = t)[1]
        sig['Iveco_ACC_PsiDt']          = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "HighResolutionYawRate",ScaleTime = t)[1]

 
        # set origin to t_start 
        sig['t'] = t - t_start
  
  
        idx = np.nonzero(np.logical_and(0.0 < sig['t'],sig['t'] < (dura+0.5)))
        
        # check if ATS4 objects is present
        x = sig['ATS4_Handle'][idx]
        if (x>0).any():
          ATS4_present = 'yes'
        else:
          ATS4_present = 'no'
  
        # check if ACCDistanceAlertSignal present 
        x = sig['ACCDistanceAlertSignal'][idx]
        if (x>0).any():
          ACCDistanceAlertSignal_present = 'yes'
        else:
          ACCDistanceAlertSignal_present = 'no'
          
        # check if ATS0 objects present
        x = sig['ATS0_Handle'][idx]
        if (x>0).any():
          ATS0_present = 'yes'
        else:
          ATS0_present = 'no'

        # check if ASF prewarning present
        x = sig['repprew'][idx]
        if (x==6).any():
          repprew_present = 'yes'
        else:
          repprew_present = 'no'

          
        # attributes of target object right before FCW
        dx = sig['ATS4_dx'][np.nonzero(sig['t']>=0.0)][0]
        vr = sig['ATS4_vr'][np.nonzero(sig['t']>=0.0)][0]
        
        vr *= -3.6 # m/s -> km/h  and Iveco sign convention
        
        # time to collision
        if abs(vr) > 0.1:        
          ttc = dx/(vr/3.6)
          ttc_text = '%3.2f s'%ttc
        else:
          ttc = None
          ttc_text = 'n.d.'
        
          
          
        # ------------------------------------------------------
        # add to table
        table_n_track = table_n_track +1
        table_array.append(['%d'%table_n_track,
                            '%s'%ATS4_present,
                            ttc_text,
                            '%3.2f m'%dx,
                            '%3.2f km/h'%vr,
                            '%s'%ATS0_present,
                            '%s'%repprew_present,
                            '%s'%ACCDistanceAlertSignal_present])
      
        # ------------------------------------------------------
        f=pl.figure(FigNr);   FigNr += 1
        f.clear()
        f.suptitle('ACCDistanceAlert')

        
        sp=f.add_subplot(711)
        sp.grid()
        sp.plot(sig['t'],sig['ATS4_Handle']>0 ,'-')
        sp.set_title('ATS4_Handle present')
        sp.set_ylabel('-')
        sp.set_ylim(-0.1,1.1)

        sp=f.add_subplot(712)
        sp.grid()
        sp.plot(sig['t'],sig['repprew'] ,'-')
        sp.set_title('repprew')
        sp.set_xlabel('time [s]')
        sp.set_ylabel('-')
        sp.set_ylim(-0.1,7.1)
        
        sp=f.add_subplot(713)
        sp.grid()
        sp.plot(sig['t'],sig['ACCDistanceAlertSignal'],'-')
        sp.set_title('ACCDistanceAlert')
        sp.set_ylabel('bool')
        sp.set_ylim(-0.1,1.1)
        
        sp=f.add_subplot(714)
        sp.grid()
        sp.plot(sig['t'],sig['ATS0_Handle']>0 ,'-')
        sp.set_title('ATS0_Handle present')
        sp.set_ylabel('-')
        sp.set_ylim(-0.1,1.1)
   
        sp=f.add_subplot(715)
        sp.grid()
        sp.plot(sig['t'],sig['ATS4_dx'] ,'-')
        sp.set_title('dx')
        sp.set_ylabel('-')
        sp.set_ylim(0.0,40.0)
    
        sp=f.add_subplot(716)
        sp.grid()
        sp.plot(sig['t'],sig['ATS4_vr']*-3.6 ,'-')
        sp.set_title('vr')
        sp.set_ylabel('-')
        sp.set_ylim(0.0,50.0)
    
        f.show()
        s  = ''
        s += 'FileName = %s; '%self.kb_tex.esc_bl(FileName)
        s += 't\\_start = %4.2f s; '%t_start
        #s += 't\\_stop  = %4.2f s; '%t_stop
        s += 'duration  = %4.2f s'%(t_stop-t_start)
        label = self.kb_tex.epsfig(f,s)

      return table_array
      
    # =============================================================================
    def calc_repprew(self):

      # ---------------------------------------------------
      # initialisation
      
      # table
      table_headline = ['Idx','repprew','ttc','dx','vr','ATS4','ATS0','Iveco FCW']
      table_array    = [table_headline]
      table_n_track  = 0

      # Figure Numbering      
      FigNr = 1
  
  
  
      # ---------------------------------------------------
      # get and process events
      H4E       = kbtools.cHunt4Event('no','Babu',10)
      EventList = H4E.return_event('repprew_locked')
      
      for Event_No, Event in enumerate(EventList):
        Event_No += 1
        print "(%d/%d)" % (Event_No,len(EventList))
        
        self.kb_tex.tex('\n\\newpage\\subsubsection{No %d}'%Event_No)
    
        FileName = Event['FileName']
       
    
        pre_trigger  = 4
        post_trigger = 4
        t_start = Event['t_start'] 
        t_stop  = Event['t_stop']  
        dura = t_stop-t_start
        
        # load measure file
        FullPath = Event['FullPath']
        #Source = measproc.cEventFinder(FullPath)
        Source = cLrr3Source(FullPath)
   
        sig = {}
    
        # create a common time base
        #Time = Source.getSignal("ACC1_27(98FE6F27)_1_", "ACCDistanceAlertSignal")[0]
        Time = Source.getSignal("ECU_0_0", "evi.General_T20.vxvRef")[0]   # T20

        # select section     
        t = Time
        t = t[np.nonzero(np.logical_and((t_start-pre_trigger) < t,t < (t_start + post_trigger)))]
    
        # get signals    
        sig['ACCDistanceAlertSignal'] = Source.getSignal("ACC1_27(98FE6F27)_1_", "ACCDistanceAlertSignal",ScaleTime = t)[1]

        # LRR3
        device = 'ECU_0_0'
        sig['ATS0_Handle']  = Source.getSignal(device, "ats.Po_T20.PO.i0.Handle",ScaleTime = t)[1]
        sig['ATS4_Handle']  = Source.getSignal(device, "ats.Po_T20.PO.i4.Handle",ScaleTime = t)[1]
        sig['repprew']      = Source.getSignal(device, 'repprew.__b_Rep.__b_RepBase.status',ScaleTime = t)[1]
  
        sig['Intro_Handle'] = Source.getSignal(device, 'sit.IntroFinder_TC.Intro.i0.Id',ScaleTime = t)[1]
        tmp_t, sig['Intro_dx'] = calcByHandle(Source, 'dxv',t)
        tmp_t, sig['Intro_vr'] = calcByHandle(Source, 'vxv',t)
  
        # ACC msg to Iveco  
        sig['Iveco_ACC_dx']             = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "HighResolutionDistanceToTarget",ScaleTime = t)[1]
        sig['Iveco_ACC_vr']             = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "RelativeVelocityToTarget",ScaleTime = t)[1]
        sig['Iveco_ACC_ObjectType']     = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "ObjectType",ScaleTime = t)[1]
        sig['Iveco_ACC_TargetLossType'] = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "TargetLossType",ScaleTime = t)[1]
        sig['Iveco_ACC_StatusOfSensor'] = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "StatusOfSensor",ScaleTime = t)[1]
        sig['Iveco_ACC_PsiDt']          = Source.getSignal("PropA_ACC_Si_27_FC(8CEF27FC)_1_", "HighResolutionYawRate",ScaleTime = t)[1]

 
        # set origin to t_start 
        sig['t'] = t - t_start
  
      
        idx = np.nonzero(np.logical_and(0.0 < sig['t'],sig['t'] < (dura+0.5)))
        # check if ATS4 objects is present
        x = sig['ATS4_Handle'][idx]
        if (x>0).any():
          ATS4_present = 'yes'
        else:
          ATS4_present = 'no'
          
        # check if ACCDistanceAlertSignal present 
        x = sig['ACCDistanceAlertSignal'][idx]
        if (x>0).any():
          ACCDistanceAlertSignal_present = 'yes'
        else:
          ACCDistanceAlertSignal_present = 'no'
          
        # check if ATS0 objects present
        x = sig['ATS0_Handle'][idx]
        if (x>0).any():
          ATS0_present = 'yes'
        else:
          ATS0_present = 'no'

        # check if ASF prewarning present
        x = sig['repprew'][idx]
        if (x==6).any():
          repprew_present = 'yes'
        else:
          repprew_present = 'no'

          
        # attributes of target object right before FCW
        dx = sig['Intro_dx'][np.nonzero(sig['t']>=0.0)][0]
        vr = sig['Intro_vr'][np.nonzero(sig['t']>=0.0)][0]
        
        vr *= -3.6 # m/s -> km/h  and Iveco sign convention
        
        # time to collision 
        ttc = dx/(vr/3.6)
        
        
        # ------------------------------------------------------
        # add to table
        table_n_track = table_n_track +1
        table_array.append(['%d'%table_n_track,
                            '%s'%repprew_present,
                            '%3.2f s'%ttc,
                            '%3.2f m'%dx,
                            '%3.2f km/h'%vr,
                            '%s'%ATS4_present,
                            '%s'%ATS0_present,
                            '%s'%ACCDistanceAlertSignal_present])
        # self.kb_tex.esc_bl(FileName)
      
      
        # ------------------------------------------------------
        f=pl.figure(FigNr);   FigNr += 1
        f.clear()
        f.suptitle('ACCDistanceAlert')

        
        sp=f.add_subplot(711)
        sp.grid()
        sp.plot(sig['t'],sig['ATS4_Handle']>0 ,'-')
        sp.set_title('ATS4_Handle present')
        sp.set_ylabel('-')
        sp.set_ylim(-0.1,1.1)

        sp=f.add_subplot(712)
        sp.grid()
        sp.plot(sig['t'],sig['repprew'] ,'-')
        sp.set_title('repprew')
        sp.set_xlabel('time [s]')
        sp.set_ylabel('-')
        sp.set_ylim(-0.1,7.1)
        
        sp=f.add_subplot(713)
        sp.grid()
        sp.plot(sig['t'],sig['ACCDistanceAlertSignal'],'-')
        sp.set_title('ACCDistanceAlert')
        sp.set_ylabel('bool')
        sp.set_ylim(-0.1,1.1)
        
        sp=f.add_subplot(714)
        sp.grid()
        sp.plot(sig['t'],sig['ATS0_Handle']>0 ,'-')
        sp.set_title('ATS0_Handle present')
        sp.set_ylabel('-')
        sp.set_ylim(-0.1,1.1)
   
        sp=f.add_subplot(715)
        sp.grid()
        sp.plot(sig['t'],sig['Intro_dx'] ,'-')
        sp.set_title('dx')
        sp.set_ylabel('-')
        sp.set_ylim(0.0,40.0)
    
        sp=f.add_subplot(716)
        sp.grid()
        sp.plot(sig['t'],sig['Intro_vr']*-3.6 ,'-')
        sp.set_title('vr')
        sp.set_ylabel('-')
        sp.set_ylim(0.0,50.0)
    
        f.show()
        s  = ''
        s += 'FileName = %s; '%self.kb_tex.esc_bl(FileName)
        s += 't\\_start = %4.2f s; '%t_start
        #s += 't\\_stop  = %4.2f s; '%t_stop
        s += 'duration  = %4.2f s'%(t_stop-t_start)
        label = self.kb_tex.epsfig(f,s)

      return table_array
      
#============================================================================================================
# stolen from python\func\lrr3\viewFUSoverlay.py
def calcByHandle(Source, Name, t):
  """
  :Parameters:
    Source : `aebs.proc.cLrr3Source`
    Name : str
  :ReturnType: numpy.ndarray, numpy.ndarray
  :Return:
    time
    value
  """
  # Indicate SIT intro object  
  handle = Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.ObjectList.i0',ScaleTime = t)[1]
  signal = np.zeros(len(handle))
  for h in np.unique(handle):
    time, value = Source.getSignalByHandle(h, Name, ScaleTime = t)
    mask = handle == h
    signal[mask] = value[mask]
  return time, signal
  

#============================================================================================================
# stolen from python\func\aebs\proc\Lrr3Source.py
class cLrr3Source(measproc.cEventFinder):
  """Signal source for LRR3 porpuces."""
  Yticks = {'SIT_Intro'    : {   1 : 'SAM',
                                 2 : 'SXM',
                                 3 : 'SAS',
                                 4 : 'LAM',
                                 5 : 'RAM'},
            'SIT_Relation' : {  16 : 'LAM',     
                                12 : 'LAS',     
                                15 : 'LEM',             
                                11 : 'LES',           
                                14 : 'LLM',          
                                10 : 'LLS',          
                                17 : 'LOM',    
                                36 : 'RAM',          
                                32 : 'RAS',          
                                35 : 'REM',          
                                31 : 'RES',          
                                34 : 'RLM',          
                                30 : 'RLS',          
                                37 : 'ROM',          
                                26 : 'SAM',          
                                22 : 'SAS',          
                                25 : 'SEM',            
                                21 : 'SES',          
                                24 : 'SLM',          
                                20 : 'SLS',          
                                27 : 'SOM',          
                                64 : 'UNCORRELATED',      
                               128 : 'UNKNOWN', 
                               255 : 'INVALID'}} 
  """:type: dict
  Collect the meaning of the signal values."""
  Iterators = {'SIT_IntroFinderObjList' : xrange( 8),
               'SIT_RelGraphObjList'    : xrange(33)}  
  """:type: dict
  Collect one place the number of the signals in the lists."""
  Invalids = {'sit.IntroFinder_TC.Intro.i0.Id'             : 0,
              'sit.IntroFinder_TC.Intro.i0.ObjectList.i%d' : 0}
  """:type: dict
  Collect the invalid values of the signals."""
  HandleName = 'fus.ObjData_TC.FusObj.i%d.%s'
  """:type: str
  Name pattern for handle signal name."""
  HandleSaveName = 'fus.ObjData_TC.FusObj.h%d.%s'
  """:type: str
  Name pattern to save handle signals."""  
  Status = {"LRR3_LOC" : [{'dummy': ['ECU', 'rmp.D2lLocationData_TC.Location.i0.dMeas']}],
            "LRR3_OHL" : [{'dummy': ['ECU', 'ohl.ObjData_TC.OhlObj.i0.dx']}],
            "LRR3_FUS" : [{'dummy': ['ECU', 'fus.ObjData_TC.FusObj.i0.dxv']}],
            "LRR3_ATS" : [{'dummy': ['ECU', 'ats.Po_T20.PO.i0.dxvFilt']}],
            "LRR3_POS" : [{'dummy': ['ECU', 'fus.ObjData_TC.FusObj.i0.Handle']}],
            "LRR3_SIT" : [{'dummy': ['ECU', 'sit.RelationGraph_TC.ObjectList.i0']}],
            "CVR3_LOC" : [{'dummy': ['MRR1', 'dsp.LocationData_TC.Location.i0.dMeas']}],
            "CVR3_OHL" : [{'dummy': ['MRR1', 'ohl.ObjData_TC.OhlObj.i0.dx']}],
            "CVR3_FUS" : [{'dummy': ['MRR1', 'fus.ObjData_TC.FusObj.i0.dxv']}],
            "CVR3_SIT" : [{'dummy': ['MRR1', 'sit.RelationGraph_TC.ObjectList.i0']}],
            "CVR3_ATS" : [{'dummy': ['MRR1', 'ats.Po_T20.PO.i0.dxvFilt']}],
            "CVR3_POS" : [{'dummy': ['MRR1', 'fus.ObjData_TC.FusObj.i0.Handle']}],
            "AC100"    : [{'dummy': ['Tracks', 'tr0_track_selection_status']}],
            "ESR"      : [{'dummy': ['ESR_Track01', 'CAN_TX_TRACK_RANGE_01']}],
            "IBEO"     : [{'dummy': ['Ibeo_List_header', 'Ibeo_Number_of_objects']}],
            "Iteris"   : [{'dummy': ['Iteris_object_follow', 'PO_target_range_OFC']}],
            "VFP"      : [{'dummy': ['VISION_OBSTACLE_MSG1', 'CAN_VIS_OBS_RANGE']}],
            "MobilEye" : [{'dummy': ['obstacle_0_info','Distance_to_Obstacle_0']}]}
  """:type: dict
  Dict with signals for different Sensors, to check if MDF contains signal"""
  def __init__(self, Measurement, ECU='ECU_0_0'):
    """
    :Parameter:
      ECU : str
        Name of the ECU device on mdf
      Measurement : str
        Path of the selected file.
    """
    measproc.cEventFinder.__init__(self, Measurement)
    self.ECU = ECU
    """:type: str
    Name of the ECU device on mdf"""
    
    self.Status.update(self.__class__.Status)    
    pass
  
  def getSignalFromECU(self, SignalName, **kwargs):
    """
    Get the requested signal in time, value numpy array pairs from the default 
    `ECU` device.
    
    :Parameters:
      SignalName : str
        Name of the requested signal.
    """
    return self.getSignal(self.ECU, SignalName, **kwargs)
    
  
  def getSignalByHandle(self, Handle, SignalName, **kwargs):    
    """
    Get the signal via its handle and name.
    
    :Parameters:
      Handle : int
        Handle of the requested signal.
      SignalName : str
        The end of the requested signal name eg dxv.
    :Keywords:
      Keywords are passed to `cSignalSource.getSignal`
    :ReturnType: two element list of `ndarray`
    :Return:
      Requested signal in time, value numpy array pairs.      
    """
    FullSignalName = self.HandleSaveName %(Handle, SignalName)
    if not self.isSignalLoaded(self.ECU, FullSignalName):
      self.__calcSignalByHandle(Handle, SignalName)          
    return self.getSignalFromECU(FullSignalName, **kwargs)    
    pass
  
  def __calcSignalByHandle(self, Handle, SignalName):
    """
    Calculate the requested signal via `Handle` and store in `cSignalSource`.
    
    :Parameters:
      Handle : int
        Handle of the requested signal.
      SignalName : str
        The end of the requested signal name eg dxv.
    """
    
    Value = self.getSignalFromECU(self.HandleName %(0, SignalName))[1]
    Value = np.zeros_like(Value) * np.NaN
    for FusObjNr in cLrr3Source.Iterators['SIT_RelGraphObjList']:
      Mask = self.getSignalFromECU(self.HandleName %(FusObjNr, 'Handle'))[1] == Handle
      Value[Mask] = self.getSignalFromECU(self.HandleName %(FusObjNr, SignalName))[1][Mask]
    self.addSignal(self.ECU,
                   self.HandleSaveName %(Handle, SignalName), 
                   self.getTimeKey(self.ECU, self.HandleName %(0, SignalName)),
                   Value)
    pass
  
  def getFUSIndexMode(self, Handle):
    """
    Get the mode of the FUS index.
    
    :Parameters:
      Handle : int
        Number of ObjectList handle.
    :ReturnType: int    
    """    
    NaN   = 42
    Time, Intro = self.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.ObjectList.i%d' %(Handle,))
    Value = np.ones_like(Intro) * NaN
    for i in cLrr3Source.Iterators['SIT_RelGraphObjList']:
      Time, RelGraph = self.getSignalFromECU('sit.RelationGraph_TC.ObjectList.i%d' %i)
      MaskZero = RelGraph != 0
      Mask     = Intro == RelGraph
      Mask = np.logical_and(MaskZero, Mask)
      Value[Mask] = i
    return self.mode(Value, NaN)  
      
  def getIntroObjects(self, Time, Pos):
    """
    Get the FUS object handles of the actual SIT intro objects and their 
    realations, too.
    
    :Parameters:
      Time : `ndarray`
        Time of the sit.IntroFinder_TC.Intro.i0.Id signal.
      Pos : int
        `Time` index where the FUS objects are looked for.
    :ReturnType: list
    :Return: 
      List of the FUS handle and relation pairs of the actual SIT intro 
      objects.   
    """
    Objects = []
    for IntroObj in cLrr3Source.Iterators['SIT_IntroFinderObjList']:
      IntroObjHandle = self.getSignalAtPos(self.ECU, 'sit.IntroFinder_TC.Intro.i0.ObjectList.i%d' %(IntroObj,), Time, Pos)
      if IntroObjHandle != cLrr3Source.Invalids['sit.IntroFinder_TC.Intro.i0.ObjectList.i%d']:
        SITObjRel = self.getSignalAtPos(self.ECU, 'sit.IntroFinder_TC.Intro.i0.ObjectRelation.i%d' %(IntroObj,), Time, Pos)
        SITObjRel = cLrr3Source.Yticks['SIT_Relation'][SITObjRel]
        for RelGraphObj in cLrr3Source.Iterators['SIT_RelGraphObjList']:
          RelGraphObjHandle = self.getSignalAtPos(self.ECU, 'sit.RelationGraph_TC.ObjectList.i%d' %(RelGraphObj,), Time, Pos)
          if RelGraphObjHandle == IntroObjHandle:
            Objects.append([RelGraphObj, SITObjRel])
            break
    return Time, Objects
  
  def getSITIntroIntervals(self, IntroTime, IntroValue):
    """
    Get the intervals of SIT intro ID where doesn't have invalid value.
    
    :Parameters:
      IntroTime : `ndarray`
        Time of the sit.IntroFinder_TC.Intro.i0.Id signal.
      IntroValue : `ndarray`
        Value of the sit.IntroFinder_TC.Intro.i0.Id signal.
    :ReturnType: `cIntervalList`
    """
    IntroName = 'sit.IntroFinder_TC.Intro.i0.Id'
    Intervals = self.compare(IntroTime, IntroValue, 
                             measproc.not_equal, 
                             cLrr3Source.Invalids[IntroName])     
    Intervals = Intervals.intersect(self.getDomains(IntroTime, IntroValue))
    return Intervals
  
  def getSITIntroObjects(self, IntroTime, IntroValue, Intervals):    
    """
    Merge the `Intervals`, where the same SIT intro objects are.
    
    :Parameters:
      IntroTime : `ndarray`
        Time of the sit.IntroFinder_TC.Intro.i0.Id signal.
      IntroValue : `ndarray`
        Value of the sit.IntroFinder_TC.Intro.i0.Id signal.
      Intervals : `cIntervalList`
        Selected intervals where the objects are looked for.
    :ReturnType: list
    :Return:
      [[LowerBound, UpperBound, IntroID, [[FUS_ObjHandle, SIT_ObjRel],...],...]
    """
    SIT_Intros = []
    Objects    = []
    for Lower, Upper in Intervals:
      Object = [cLrr3Source.Yticks['SIT_Intro'][IntroValue[Lower]],
                self.getIntroObjects(IntroTime, Lower)]
      try:
        Index = Objects.index(Object)
        SIT_Intros[Index][1] = Upper
      except ValueError:
        Objects.append(Object)
        SIT_Intros.append([Lower, Upper])
    
    for i in xrange(len(SIT_Intros)):
      SIT_Intros[i] += Objects[i]
    return SIT_Intros
 
