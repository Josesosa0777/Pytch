"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: AEBS evalulation '''

''' to be called by DAS_eval.py '''

import measproc
import kbtools

# path where numpy backup files will be saved
measproc.NpyHomeDir = r'C:\tmp_python'

# ==============================================================================================
class cEvalAEBS():
    # ------------------------------------------------------------------------------------------
    def __init__(self):        # constructor
      self.myname = 'EvalAEBS'    # name of this user specific evaluation
      self.H4E = {}               # H4E hunt4event directory

    # ------------------------------------------------------------------------------------------
    def __del__(self):         # destructor
      pass
      
    # ------------------------------------------------------------------------------------------
    def init(self,folder):     # general start
       
      # REactions Patterns REPs of Predictive Safety Systems
      t_join = 0
      self.H4E['LRR3_repprew_locked'] = kbtools.cHunt4Event('on_phase','LRR3 repprew',t_join)
      self.H4E['LRR3_repacuw_locked'] = kbtools.cHunt4Event('on_phase','LRR3 repacuw',t_join)
      self.H4E['LRR3_repretg_locked'] = kbtools.cHunt4Event('on_phase','LRR3 repretg',t_join)
      self.H4E['LRR3_repdesu_locked'] = kbtools.cHunt4Event('on_phase','LRR3 repdesu',t_join)

      self.H4E['CVR3_repprew_locked'] = kbtools.cHunt4Event('on_phase','CVR3 repprew',t_join)
      self.H4E['CVR3_repacuw_locked'] = kbtools.cHunt4Event('on_phase','CVR3 repacuw',t_join)
      self.H4E['CVR3_repretg_locked'] = kbtools.cHunt4Event('on_phase','CVR3 repretg',t_join)
      self.H4E['CVR3_repdesu_locked'] = kbtools.cHunt4Event('on_phase','CVR3 repdesu',t_join)
    
      # Action Coordinator ACO of Predictive Safety Systems
      t_join = 0
      self.H4E['LRR3_acooptiRequest'] = kbtools.cHunt4Event('on_phase','LRR3 acoopti',t_join)
      self.H4E['LRR3_acoacoiRequest'] = kbtools.cHunt4Event('on_phase','LRR3 acoacoi',t_join)
      self.H4E['LRR3_acobrajRequest'] = kbtools.cHunt4Event('on_phase','LRR3 acobraj',t_join)
      self.H4E['LRR3_acopebpRequest'] = kbtools.cHunt4Event('on_phase','LRR3 acopebp',t_join)
      self.H4E['LRR3_acopebeRequest'] = kbtools.cHunt4Event('on_phase','LRR3 acopebe',t_join)
      self.H4E['LRR3_acopebmRequest'] = kbtools.cHunt4Event('on_phase','LRR3 acopebm',t_join)
      self.H4E['LRR3_acoxbadRequest'] = kbtools.cHunt4Event('on_phase','LRR3 acoxbad',t_join)
      
      self.H4E['CVR3_acooptiRequest'] = kbtools.cHunt4Event('on_phase','CVR3 acoopti',t_join)
      self.H4E['CVR3_acoacoiRequest'] = kbtools.cHunt4Event('on_phase','CVR3 acoacoi',t_join)
      self.H4E['CVR3_acobrajRequest'] = kbtools.cHunt4Event('on_phase','CVR3 acobraj',t_join)
      self.H4E['CVR3_acopebpRequest'] = kbtools.cHunt4Event('on_phase','CVR3 acopebp',t_join)
      self.H4E['CVR3_acopebeRequest'] = kbtools.cHunt4Event('on_phase','CVR3 acopebe',t_join)
      self.H4E['CVR3_acopebmRequest'] = kbtools.cHunt4Event('on_phase','CVR3 acopebm',t_join)
      self.H4E['CVR3_acoxbadRequest'] = kbtools.cHunt4Event('on_phase','CVR3 acoxbad',t_join)
      
      # HMI Request - Pre Warning 
      t_join = 0
      self.H4E['LRR3_HmiReq_OptInfoReq']      = kbtools.cHunt4Event('on_phase','LRR3 HmiReq OptInfoReq',t_join)
      self.H4E['LRR3_HmiReq_AcousticInfoReq'] = kbtools.cHunt4Event('on_phase','LRR3 HmiReq AcousticInfoReq',t_join)

      self.H4E['CVR3_HmiReq_OptInfoReq']      = kbtools.cHunt4Event('on_phase','CVR3 HmiReq OptInfoReq',t_join)
      self.H4E['CVR3_HmiReq_AcousticInfoReq'] = kbtools.cHunt4Event('on_phase','CVR3 HmiReq AcousticInfoReq',t_join)


      # Intro Finder 
      t_join = 0
      # Same Approach Moving - SAM  (1)
      self.H4E['LRR3_IntroFinder_SAM'] = kbtools.cHunt4Event('on_phase','LRR3 IntroFinder SAM',t_join)
   
      # Same don't care Moving - SXM  (2)
      self.H4E['LRR3_IntroFinder_SXM'] = kbtools.cHunt4Event('on_phase','LRR3 IntroFinder SXM',t_join)

      # Same Approach Stationary - SAS  (3)
      self.H4E['LRR3_IntroFinder_SAS'] = kbtools.cHunt4Event('on_phase','LRR3 IntroFinder SAS',t_join)

      # Left Approach Moving - LAM (4)
      self.H4E['LRR3_IntroFinder_LAM'] = kbtools.cHunt4Event('on_phase','LRR3 IntroFinder LAM',t_join)
  
      # Right Approach Moving - RAM (5)
      self.H4E['LRR3_IntroFinder_RAM'] = kbtools.cHunt4Event('on_phase','LRR3 IntroFinder RAM',t_join)
   
      # Same Equal Moving - SEM (6)
      self.H4E['LRR3_IntroFinder_SEM'] = kbtools.cHunt4Event('on_phase','LRR3 IntroFinder SEM',t_join)

      
      
      # Same Approach Moving - SAM  (1)
      self.H4E['CVR3_IntroFinder_SAM'] = kbtools.cHunt4Event('on_phase','CVR3 IntroFinder SAM',t_join)
   
      # Same don't care Moving - SXM  (2)
      self.H4E['CVR3_IntroFinder_SXM'] = kbtools.cHunt4Event('on_phase','CVR3 IntroFinder SXM',t_join)

      # Same Approach Stationary - SAS  (3)
      self.H4E['CVR3_IntroFinder_SAS'] = kbtools.cHunt4Event('on_phase','CVR3 IntroFinder SAS',t_join)

      # Left Approach Moving - LAM (4)
      self.H4E['CVR3_IntroFinder_LAM'] = kbtools.cHunt4Event('on_phase','CVR3 IntroFinder LAM',t_join)
  
      # Right Approach Moving - RAM (5)
      self.H4E['CVR3_IntroFinder_RAM'] = kbtools.cHunt4Event('on_phase','CVR3 IntroFinder RAM',t_join)
   
      # Same Equal Moving - SEM (6)
      self.H4E['CVR3_IntroFinder_SEM'] = kbtools.cHunt4Event('on_phase','CVR3 IntroFinder SEM',t_join)

      
      
    
    # ------------------------------------------------------------------------------------------
    def reinit(self):          # recording interrupted
      for key in self.H4E.keys():
        self.H4E[key].reinit()

    # ------------------------------------------------------------------------------------------
    def process(self,Source):  # evaluate recorded file

    
      LRR3_device = 'ECU-0-0'
      CVR3_device = 'MRR1plus-0-0'
      
      # -----------------------------------------------------------------------------------------
      # REactions Patterns REPs of Predictive Safety Systems
      #   (status == 6) means reaction pattern is locked
      
      # LRR3
      try:      
        Time, Value = Source.getSignal(LRR3_device, 'repprew.__b_Rep.__b_RepBase.status')
        self.H4E['LRR3_repprew_locked'].process(Time, (Value==6), Source)
      except:
        print "error with reaction patter LRR3 repprew_locked"   

      try:      
        Time, Value = Source.getSignal(LRR3_device, 'repacuw.__b_Rep.__b_RepBase.status')
        self.H4E['LRR3_repacuw_locked'].process(Time, (Value==6), Source)
      except:
        print "error with reaction patter LRR3 repacuw_locked"   

      try:      
        Time, Value = Source.getSignal(LRR3_device, 'repretg.__b_Rep.__b_RepBase.status')
        self.H4E['LRR3_repretg_locked'].process(Time, (Value==6), Source)
      except:
        print "error with reaction patter LRR3 repretg_locked"   

      try:      
        Time, Value = Source.getSignal(LRR3_device, 'repdesu.__b_Rep.__b_RepBase.status')
        self.H4E['LRR3_repdesu_locked'].process(Time, (Value==6), Source)
      except:
        print "error with reaction patter LRR3 repdesu_locked"   

      # CVR3 
      try:      
        Time, Value = Source.getSignal(CVR3_device, 'repprew.__b_Rep.__b_RepBase.status')
        self.H4E['CVR3_repprew_locked'].process(Time, (Value==6), Source)
      except:
        print "error with reaction patter CVR3 repprew_locked"   

      try:      
        Time, Value = Source.getSignal(CVR3_device, 'repacuw.__b_Rep.__b_RepBase.status')
        self.H4E['CVR3_repacuw_locked'].process(Time, (Value==6), Source)
      except:
        print "error with reaction patter CVR3 repacuw_locked"   

      try:      
        Time, Value = Source.getSignal(CVR3_device, 'repretg.__b_Rep.__b_RepBase.status')
        self.H4E['CVR3_repretg_locked'].process(Time, (Value==6), Source)
      except:
        print "error with reaction patter CVR3 repretg_locked"   

      try:      
        Time, Value = Source.getSignal(CVR3_device, 'repdesu.__b_Rep.__b_RepBase.status')
        self.H4E['CVR3_repdesu_locked'].process(Time, (Value==6), Source)
      except:
        print "error with reaction patter CVR3 repdesu_locked"   



      # -----------------------------------------------------------------------------------------
      # Action Coordinator ACO of Predictive Safety Systems
      
      # LRR3 
      try:  
        Time, Value = Source.getSignal(LRR3_device, 'acoopti.__b_AcoNoFb.__b_Aco.request_B')
        self.H4E['LRR3_acooptiRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator LRR3 acooptiRequest"

      try:  
        Time, Value = Source.getSignal(LRR3_device, 'acoacoi.__b_AcoNoFb.__b_Aco.request_B')
        self.H4E['LRR3_acoacoiRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator LRR3 acoacoiRequest"

      try:  
        Time, Value = Source.getSignal(LRR3_device, 'acobraj.__b_AcoCoFb.__b_Aco.request_B')
        self.H4E['LRR3_acobrajRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator LRR3 acobrajRequest"
      
      try:  
        Time, Value = Source.getSignal(LRR3_device, 'acopebp.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B')
        self.H4E['LRR3_acopebpRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator LRR3 acopebpRequest"

      try:  
        Time, Value = Source.getSignal(LRR3_device, 'acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B')
        self.H4E['LRR3_acopebeRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator LRR3 acopebeRequest"

      try:  
        Time, Value = Source.getSignal(LRR3_device, 'acopebm.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B')
        self.H4E['LRR3_acopebmRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator LRR3 acopebmRequest"
      
      try:  
        Time, Value = Source.getSignal(LRR3_device, 'acoxbad.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B')
        self.H4E['LRR3_acoxbadRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator LRR3 acoxbadRequest"

      # CVR3 
      try:  
        Time, Value = Source.getSignal(CVR3_device, 'acoopti.__b_AcoNoFb.__b_Aco.request_B')
        self.H4E['CVR3_acooptiRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator CVR3 acooptiRequest"

      try:  
        Time, Value = Source.getSignal(CVR3_device, 'acoacoi.__b_AcoNoFb.__b_Aco.request_B')
        self.H4E['CVR3_acoacoiRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator CVR3 acoacoiRequest"

      try:  
        Time, Value = Source.getSignal(CVR3_device, 'acobraj.__b_AcoCoFb.__b_Aco.request_B')
        self.H4E['CVR3_acobrajRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator CVR3 acobrajRequest"
      
      try:  
        Time, Value = Source.getSignal(CVR3_device, 'acopebp.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B')
        self.H4E['CVR3_acopebpRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator CVR3 acopebpRequest"

      try:  
        Time, Value = Source.getSignal(CVR3_device, 'acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B')
        self.H4E['CVR3_acopebeRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator CVR3 acopebeRequest"

      try:  
        Time, Value = Source.getSignal(CVR3_device, 'acopebm.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B')
        self.H4E['CVR3_acopebmRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator CVR3 acopebmRequest"
      
      try:  
        Time, Value = Source.getSignal(CVR3_device, 'acoxbad.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B')
        self.H4E['CVR3_acoxbadRequest'].process(Time, (Value==1), Source)
      except:
        print "error with action coordinator CVR3 acoxbadRequest"

      # -----------------------------------------------------------------------------------------
      # HMI Request - Pre Warning 
      
      # LRR3
      try:  
        Time, Value = Source.getSignal(LRR3_device, 'asf.HmiReq_TC.requestFlags.l.OptInfoReq_b')
        self.H4E['LRR3_HmiReq_OptInfoReq'].process(Time, (Value==1), Source)
      except:
        print "error with HMI request LRR3 HmiReq_OptInfoReq"

      try:  
        Time, Value = Source.getSignal(LRR3_device, 'asf.HmiReq_TC.requestFlags.l.AcousticInfoReq_b')
        self.H4E['LRR3_HmiReq_AcousticInfoReq'].process(Time, (Value==1), Source)
      except:
        print "error with HMI request LRR3 HmiReq_AcousticInfoReq"

      # CVR3
      try:  
        Time, Value = Source.getSignal(CVR3_device, 'asf.HmiReq_TC.requestFlags.l.OptInfoReq_b')
        self.H4E['CVR3_HmiReq_OptInfoReq'].process(Time, (Value==1), Source)
      except:
        print "error with HMI request CVR3 HmiReq_OptInfoReq"

      try:  
        Time, Value = Source.getSignal(CVR3_device, 'asf.HmiReq_TC.requestFlags.l.AcousticInfoReq_b')
        self.H4E['CVR3_HmiReq_AcousticInfoReq'].process(Time, (Value==1), Source)
      except:
        print "error with HMI request CVR3 HmiReq_AcousticInfoReq"

      # -----------------------------------------------------------------------------------------
      # Intro Finder 
      
      # LRR3 
      try:
        Time, Value = Source.getSignal(LRR3_device, 'sit.IntroFinder_TC.Intro.i0.Id')
        # Same Approach Moving - SAM  (1)
        self.H4E['LRR3_IntroFinder_SAM'].process(Time, (Value==1), Source)
        # Same don't care Moving - SXM  (2)
        self.H4E['LRR3_IntroFinder_SXM'].process(Time, (Value==2), Source)
        # Same Approach Stationary - SAS  (3)
        self.H4E['LRR3_IntroFinder_SAS'].process(Time, (Value==3), Source)
        # Left Approach Moving - LAM (4)
        self.H4E['LRR3_IntroFinder_LAM'].process(Time, (Value==4), Source)
        # Right Approach Moving - RAM (5)
        self.H4E['LRR3_IntroFinder_RAM'].process(Time, (Value==5), Source)
        # Same Equal Moving - SEM (6)
        self.H4E['LRR3_IntroFinder_SEM'].process(Time, (Value==6), Source)
      except:
        print "error with LRR3 Intro Finder"

      try:
        Time, Value = Source.getSignal(CVR3_device, 'sit.IntroFinder_TC.Intro.i0.Id')
        # Same Approach Moving - SAM  (1)
        self.H4E['CVR3_IntroFinder_SAM'].process(Time, (Value==1), Source)
        # Same don't care Moving - SXM  (2)
        self.H4E['CVR3_IntroFinder_SXM'].process(Time, (Value==2), Source)
        # Same Approach Stationary - SAS  (3)
        self.H4E['CVR3_IntroFinder_SAS'].process(Time, (Value==3), Source)
        # Left Approach Moving - LAM (4)
        self.H4E['CVR3_IntroFinder_LAM'].process(Time, (Value==4), Source)
        # Right Approach Moving - RAM (5)
        self.H4E['CVR3_IntroFinder_RAM'].process(Time, (Value==5), Source)
        # Same Equal Moving - SEM (6)
        self.H4E['CVR3_IntroFinder_SEM'].process(Time, (Value==6), Source)
      except:
        print "error with CVR3 Intro Finder"

      
      
      
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
      
      
      self.kb_tex.tex('\n\\newpage\\section{EvalAEBS}')
      
      # REactions Patterns REPs of Predictive Safety Systems
      self.kb_tex.tex('\n\\subsection{Reaction Pattern REP}')
 
      self.kb_tex.tex('\n\\subsubsection{Prewarning - locked}')
      label = self.kb_tex.table(self.H4E['LRR3_repprew_locked'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_repprew_locked'].table_array())

      self.kb_tex.tex('\n\\subsubsection{Acute Warning - locked}')
      label = self.kb_tex.table(self.H4E['LRR3_repacuw_locked'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_repacuw_locked'].table_array())
      
      self.kb_tex.tex('\n\\subsubsection{Reaction Time Gain - locked}')
      label = self.kb_tex.table(self.H4E['LRR3_repretg_locked'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_repretg_locked'].table_array())

      self.kb_tex.tex('\n\\subsubsection{Deceleration Support - locked}')
      label = self.kb_tex.table(self.H4E['LRR3_repdesu_locked'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_repdesu_locked'].table_array())
 
 
 
      # Action Coordinator ACO of Predictive Safety Systems
      self.kb_tex.tex('\n\\newpage\\subsection{Action Coordinator ACO}')

      self.kb_tex.tex('\n\\subsubsection{acoopti - request}')
      label = self.kb_tex.table(self.H4E['LRR3_acooptiRequest'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_acooptiRequest'].table_array())

      self.kb_tex.tex('\n\\subsubsection{acoacoi - request}')
      label = self.kb_tex.table(self.H4E['LRR3_acoacoiRequest'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_acoacoiRequest'].table_array())

      self.kb_tex.tex('\n\\subsubsection{acobraj - request}')
      label = self.kb_tex.table(self.H4E['LRR3_acobrajRequest'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_acobrajRequest'].table_array())

      self.kb_tex.tex('\n\\subsubsection{acopebp - request}')
      label = self.kb_tex.table(self.H4E['LRR3_acopebpRequest'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_acopebpRequest'].table_array())

      self.kb_tex.tex('\n\\subsubsection{acopebe - request}')
      label = self.kb_tex.table(self.H4E['LRR3_acopebeRequest'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_acopebeRequest'].table_array())

      self.kb_tex.tex('\n\\subsubsection{acopebm - request}')
      label = self.kb_tex.table(self.H4E['LRR3_acopebmRequest'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_acopebmRequest'].table_array())
      
      self.kb_tex.tex('\n\\subsubsection{acoxbad - request}')
      label = self.kb_tex.table(self.H4E['LRR3_acoxbadRequest'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_acoxbadRequest'].table_array())

      # HMI Request - Pre Warning 
      self.kb_tex.tex('\n\\newpage\\subsection{HMI Request - Pre Warning}')
      # OptInfo
      self.kb_tex.tex('\n\\subsubsection{HmiReq OptInfoReq}')
      label = self.kb_tex.table(self.H4E['LRR3_HmiReq_OptInfoReq'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_HmiReq_OptInfoReq'].table_array())
      
      # AcousticInfo
      self.kb_tex.tex('\n\\subsubsection{HmiReq AcousticInfoReq}')
      label = self.kb_tex.table(self.H4E['LRR3_HmiReq_AcousticInfoReq'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_HmiReq_AcousticInfoReq'].table_array())
      
      # Intros 
      self.kb_tex.tex('\n\\newpage\\subsection{IntroFinder}')
      # Same Approach Moving - SAM  (1)
      self.kb_tex.tex('\n\\subsubsection{Same Approach Moving - SAM}')
      label = self.kb_tex.table(self.H4E['LRR3_IntroFinder_SAM'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_IntroFinder_SAM'].table_array())
     
      # Same don't care Moving - SXM  (2)
      self.kb_tex.tex('\n\\subsubsection{Same don''t care Moving - SXM}')
      label = self.kb_tex.table(self.H4E['LRR3_IntroFinder_SXM'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_IntroFinder_SXM'].table_array())

      # Same Approach Stationary - SAS  (3)
      self.kb_tex.tex('\n\\subsubsection{Same Approach Stationary - SAS}')
      label = self.kb_tex.table(self.H4E['LRR3_IntroFinder_SAS'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_IntroFinder_SAS'].table_array())

      # Left Approach Moving - LAM (4)
      self.kb_tex.tex('\n\\subsubsection{Left Approach Moving - LAM}')
      label = self.kb_tex.table(self.H4E['LRR3_IntroFinder_LAM'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_IntroFinder_LAM'].table_array())

      # Right Approach Moving - RAM (5)
      self.kb_tex.tex('\n\\subsubsection{Right Approach Moving - RAM}')
      label = self.kb_tex.table(self.H4E['LRR3_IntroFinder_RAM'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_IntroFinder_RAM'].table_array())

      # Same Equal Moving - SEM (6)
      self.kb_tex.tex('\n\\subsubsection{Same Equal Moving - SEM}')
      label = self.kb_tex.table(self.H4E['LRR3_IntroFinder_SEM'].table_array())
      label = self.kb_tex.table(self.H4E['CVR3_IntroFinder_SEM'].table_array())

   
      self.kb_tex.tex('\nEvalAEBS-finished')

#-------------------------------------------------------------------------      









