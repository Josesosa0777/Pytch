"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: OHL evalulation '''
''' to be called by DAS_eval.py '''

import os
import pickle
import pylab as pl
import numpy as np

import measproc
import kbtools

# path where numpy backup files will be saved
measproc.NpyHomeDir = r'C:\tmp_python'

# output 
pickle_filename = 'track_list_OHL.pkl'

# Radar Device
Device = "MRR1plus-0-0"

# ==============================================================================================
class cEvalOHL():
  def __init__(self):       # constructor
    self.myname = 'EvalOHL'
    self.H4E = {}

  def __del__(self):         # destructor
    pass
      
  # ------------------------------------------------------------------------------------------
  def init(self,folder):     # general start
  
    # headline
    self.table_headline = ['Idx','t start','dura','wExistProb','dxv','dyv','FileName']

    # BL BlackList    
    self.BL_table_array = [self.table_headline]
    self.BL_table_n_track = 0

    # experimental list
    self.table_array = [self.table_headline]
    self.table_n_track = 0

    # stationary obstacles
    self.stat_obj_table_array = [self.table_headline]
    self.stat_obj_table_n_track = 0

   
  # ------------------------------------------------------------------------------------------
  def reinit(self):          # recording interrupted
    for key in self.H4E.keys():
      self.H4E[key].reinit()

  # ------------------------------------------------------------------------------------------
  def finish(self):          # end of recording
    for key in self.H4E.keys():
      self.H4E[key].finish()

  # ------------------------------------------------------------------------------------------
  def process(self,Source):  # evaluate recorded file

    # FileName to specify the origin of the track
    FileName = os.path.basename(Source.FileName)

    # -------------------------------------------------------
    # ego vehicle information
    EgoVeh = self.get_ego_vehicle_information(Source)

 
    # -------------------------------------------------------
    # extract OHL tracks
    track_list = self.extract_OHL_tracks(Source)
    print "%d OHL tracks extracted" % len(track_list)
      
    # -------------------------------------------------------
    # pickle track_list and ego vehicle information to file
    output = open(pickle_filename, 'wb')
    pickle.dump(track_list, output,-1) # -1: using the highest protocol available
    pickle.dump(EgoVeh, output,-1)     # -1: using the highest protocol available
    output.close()

    # -------------------------------------------------------
    # evaluate tracks        
    for track in track_list:
      Time           = track['t']
      t_start        = Time[0]
      t_stop         = Time[-1]
      dura           = t_stop - t_start
      valid          = track['valid'][0]
      Stand_b        = track['Stand_b']
      min_wExistProb = np.min(track['wExistProb'])
      max_wExistProb = np.max(track['wExistProb'])
      min_dxv        = np.min(track['dxv'])
      max_dxv        = np.max(track['dxv'])
      min_dyv        = np.min(track['dyv'])
      max_dyv        = np.max(track['dyv'])

      # Blacklist
      condition1 = 1
      
      if condition1 :
        self.BL_table_n_track = self.BL_table_n_track +1
        
        # plot
        #self.plot_xy(self.table_n_track,track)
        
        # add to table
        self.BL_table_array.append(['%d'%self.BL_table_n_track,'%3.2f'%t_start,'%3.2f'%dura,'[%3.2f %3.2f]'%(min_wExistProb,max_wExistProb),'[%3.2f %3.2f]'%(min_dxv,max_dxv),'[%3.2f %3.2f]'%(min_dyv,max_dyv),kbtools.esc_bl(FileName)])

      # .............................................................................
      # stationary object with existance probability greater 0.4 and duration longer 0.5 secs       
      condition1 = (dura > 0.5) 
      condition2 = (Stand_b==1).any()
      condition3 = max_wExistProb > 0.4
      
      if condition1 & condition2 & condition3 :
        self.stat_obj_table_n_track = self.stat_obj_table_n_track +1
        
        # plot
        #self.plot_xy(self.table_n_track,track)
        
        # add to table
        self.stat_obj_table_array.append(['%d'%self.stat_obj_table_n_track,'%3.2f'%t_start,'%3.2f'%dura,'[%3.2f %3.2f]'%(min_wExistProb,max_wExistProb),'[%3.2f %3.2f]'%(min_dxv,max_dxv),'[%3.2f %3.2f]'%(min_dyv,max_dyv),kbtools.esc_bl(FileName)])

      # .............................................................................
      # experimental        
      condition1 = (dura > 0.1) & (dura<5)
      condition2 = min_dxv < 20
      condition3 = min_dyv > -5
      condition4 = max_dyv < 5
      condition5 = max_wExistProb > 0.7
      
      if condition1 & condition2 & condition3 & condition4 & condition5:
        self.table_n_track = self.table_n_track +1
        
        # plot
        #self.plot_xy(self.table_n_track,track)
        
        # add to table
        self.table_array.append(['%d'%self.table_n_track,'%3.2f'%t_start,'%3.2f'%dura,'[%3.2f %3.2f]'%(min_wExistProb,max_wExistProb),'[%3.2f %3.2f]'%(min_dxv,max_dxv),'[%3.2f %3.2f]'%(min_dyv,max_dyv),kbtools.esc_bl(FileName)])
   
   
   
   

  # ------------------------------------------------------------------------------------------
  def report_init(self):     # prepare for report - input tex file to main
    self.kb_tex.tex_main('\n\\input{%s.tex}\n'%self.myname)
    self.kb_tex.workingfile('%s.tex'%self.myname)
    self.kb_tex.tex('\n\\newpage\\section{EvalOHL Overview}')

    self.kb_tex.tex_main('\n\\input{%s_details.tex}\n'%self.myname)
    self.kb_tex.workingfile('%s_details.tex'%self.myname)
    self.kb_tex.tex('\n\\newpage\\section{EvalOHL Details}')

  # ------------------------------------------------------------------------------------------
  def report(self):          # report events
      
    self.kb_tex.workingfile('%s.tex'%self.myname)

    # all OHL objects
    self.kb_tex.tex('\n\\newpage\\subsection{OHL list }')
    label = self.kb_tex.table(self.BL_table_array)
    
    # stat obj
    self.kb_tex.tex('\n\\newpage\\subsection{OHL list - stat obj }')
    label = self.kb_tex.table(self.stat_obj_table_array)
        
    # experimental
    self.kb_tex.tex('\n\\newpage\\subsection{FUS experimental}')
        
    # conditions
    table = [ ['    ', 'Condition'        ' '],
              ['   ',  '0.1 s $<$ dura $<$ 5 s'],
              ['and',  'dxv $<$ 20 m'],
              ['and',  '-5 m $<$ dyv $<$5 m'],
              ['and',  'wExistProb $>$ 0.7']]
    
    label = self.kb_tex.table(table)

    label = self.kb_tex.table(self.table_array)


     
    self.kb_tex.tex('\nEvalOHL-finished')

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # local functions  
  def get_ego_vehicle_information(self, Source):
    EgoVeh = {}
    
    EgoVeh['t'], EgoVeh['psiDtOpt'] = Source.getSignal(Device, "evi.General_TC.psiDtOpt")
    EgoVeh['psiDtDt']           = Source.getSignal(Device, "evi.General_TC.psiDtDt") [1]
    EgoVeh['vxvRef']            = Source.getSignal(Device, "evi.General_TC.vxvRef") [1]
    EgoVeh['axvRef']            = Source.getSignal(Device, "evi.General_TC.axvRef") [1]
    
    EgoVeh['tAbsPsiDt']         = Source.getSignal(Device, "evi.General_TC.tAbsPsiDt") [1]
    EgoVeh['tAbsVxvRef']        = Source.getSignal(Device, "evi.General_TC.tAbsVxvRef") [1]
    EgoVeh['tAbsMeasTimeStamp'] = Source.getSignal(Device, "dsp.LocationData_TC.tAbsMeasTimeStamp") [1]
   
    EgoVeh['kapCurvTraj']       = Source.getSignal(Device, "evi.MovementData_TC.kapCurvTraj") [1]
    EgoVeh['alpSideSlipAngle']  = Source.getSignal(Device, "evi.MovementData_TC.alpSideSlipAngle") [1]
    
    EgoVeh['dLongitudinalOffsetRearAxis']  = Source.getSignal(Device, "csi.VehicleData_T20.dLongitudinalOffsetRearAxis") [1]

    return EgoVeh
  
  
  def extract_OHL_tracks(self, Source):
    print 'extract_OHL_tracks()'

    # constants
    Device = "MRR1plus-0-0"
    N_OHL_obj = 40
    OhlObj = "ohl.ObjData_TC.OhlObj"
    
    # ----------------------------------  
    track_list = [];

    for idx in xrange(N_OHL_obj):

      # get signals of OHL objects
      t, valid      = Source.getSignal(Device, ('%s.i%d.c.c.Valid_b'   %(OhlObj,idx)))
      dxv           = Source.getSignal(Device, ('%s.i%d.dx'            %(OhlObj,idx)),ScaleTime = t)[1]
      dyv           = Source.getSignal(Device, ('%s.i%d.dy'            %(OhlObj,idx)),ScaleTime = t)[1]
      vxv           = Source.getSignal(Device, ('%s.i%d.vx'            %(OhlObj,idx)),ScaleTime = t)[1]
      vyv           = Source.getSignal(Device, ('%s.i%d.vy'            %(OhlObj,idx)),ScaleTime = t)[1]
      axv           = Source.getSignal(Device, ('%s.i%d.ax'            %(OhlObj,idx)),ScaleTime = t)[1]
      ayv           = Source.getSignal(Device, ('%s.i%d.ay'            %(OhlObj,idx)),ScaleTime = t)[1]
      Stand_b       = Source.getSignal(Device, ('%s.i%d.c.c.Stand_b'   %(OhlObj,idx)),ScaleTime = t)[1]
      wExistProb    = Source.getSignal(Device, ('%s.i%d.wExistProb'    %(OhlObj,idx)),ScaleTime = t)[1]
      wGroundReflex = Source.getSignal(Device, ('%s.i%d.wGroundReflex' %(OhlObj,idx)),ScaleTime = t)[1]
      wInterfProb   = Source.getSignal(Device, ('%s.i%d.wInterfProb'   %(OhlObj,idx)),ScaleTime = t)[1]
      probClass0    = Source.getSignal(Device, ('%s.i%d.probClass.i0'  %(OhlObj,idx)),ScaleTime = t)[1]
      probClass1    = Source.getSignal(Device, ('%s.i%d.probClass.i1'  %(OhlObj,idx)),ScaleTime = t)[1]
      probClass2    = Source.getSignal(Device, ('%s.i%d.probClass.i2'  %(OhlObj,idx)),ScaleTime = t)[1]
      probClass3    = Source.getSignal(Device, ('%s.i%d.probClass.i3'  %(OhlObj,idx)),ScaleTime = t)[1]
      probClass4    = Source.getSignal(Device, ('%s.i%d.probClass.i4'  %(OhlObj,idx)),ScaleTime = t)[1]
      
      dReflexCorrectionEff = Source.getSignal(Device, ('%s.i%d.internal.dReflexCorrectionEff' %(OhlObj,idx)),ScaleTime = t)[1]
      dReflexCorrection    = Source.getSignal(Device, ('%s.i%d.internal.dReflexCorrection'    %(OhlObj,idx)),ScaleTime = t)[1]
      maxDbPowerFilt       = Source.getSignal(Device, ('%s.i%d.internal.maxDbPowerFilt'       %(OhlObj,idx)),ScaleTime = t)[1]
      CntAlive             = Source.getSignal(Device, ('%s.i%d.internal.CntAlive'             %(OhlObj,idx)),ScaleTime = t)[1]
      PowerFiltHist_b      = Source.getSignal(Device, ('%s.i%d.internal.b.b.PowerFiltHist_b'  %(OhlObj,idx)),ScaleTime = t)[1]
      dbPowerFilt          = Source.getSignal(Device, ('%s.i%d.internal.dbPowerFilt'          %(OhlObj,idx)),ScaleTime = t)[1]


      
      
      

      # separate handles
      handle_list = kbtools.scan4handles(valid)
      
      # create tracks from handle list and append to track list
      for k in xrange(len(handle_list)):
        idx = range(handle_list[k][0],handle_list[k][1]+1,1)
        current_track = {'idx':idx,
                         't':t[idx],
                         'valid':valid[idx],
                         'dxv':dxv[idx],
                         'dyv':dyv[idx],
                         'vxv':vxv[idx],
                         'vyv':vyv[idx],
                         'axv':axv[idx],
                         'ayv':ayv[idx],
                         'Stand_b':Stand_b[idx],
                         'wExistProb':wExistProb[idx],
                         'wGroundReflex':wGroundReflex[idx],
                         'wInterfProb':wInterfProb[idx],  
                         'probClass0':probClass0[idx],
                         'probClass1':probClass1[idx],
                         'probClass2':probClass2[idx],
                         'probClass3':probClass3[idx],
                         'probClass4':probClass4[idx],
                         'dReflexCorrectionEff':dReflexCorrectionEff[idx], 
                         'dReflexCorrection':dReflexCorrection[idx],
                         'maxDbPowerFilt':maxDbPowerFilt[idx],
                         'CntAlive':CntAlive[idx],             
                         'PowerFiltHist_b':PowerFiltHist_b[idx],      
                         'dbPowerFilt':dbPowerFilt[idx]         
                        }

        current_track['angle'] = np.arctan2(current_track['dyv'],current_track['dxv'])*(180.0/np.pi)

        track_list.append(current_track)

    return track_list

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def plot_xy(self,k,track):
  
    self.kb_tex.workingfile('%s_details.tex'%self.myname)
    self.kb_tex.tex('\n\\subsection{OHL %d}'%k)
 
    #----------------------------------------------------
    # include the plot
    FigNr = 1

    f=pl.figure(FigNr)
    f.clear()
    f.suptitle('Matplotlib Example')

    sp=f.add_subplot(311)
    sp.grid()
    sp.plot(track['t'],track['wExistProb'])
    sp.set_title('wExistProb')

    sp=f.add_subplot(312)
    sp.grid()
    sp.plot(track['t'],track['dxv'])
    sp.set_title('dxv')

    sp=f.add_subplot(313)
    sp.grid()
    sp.plot(track['t'],track['dyv'])
    sp.set_title('dyv')

    f.show()
    
    name = 'Handle:%d'%track['Handle'][0]
    label = self.kb_tex.epsfig(f, '%s' % self.kb_tex.esc_bl(name) );

    #----------------------------------------------------
    # include the plot
    FigNr = 2

    f=pl.figure(FigNr)
    f.clear()
    f.suptitle('Matplotlib Example')

    sp=f.add_subplot(111)
    sp.grid()
    sp.plot(track['dyv'],track['dxv'])
    sp.set_title('xy')

    f.show()
    
    name = 'Handle:%d'%track['Handle'][0]
    label = self.kb_tex.epsfig(f, '%s' % self.kb_tex.esc_bl(name) );

    return label  
      
#-------------------------------------------------------------------------      









