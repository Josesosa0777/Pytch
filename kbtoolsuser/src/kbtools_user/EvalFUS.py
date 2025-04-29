"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: FUS evalulation '''
''' to be called by DAS_eval.py '''

''' currently used to check that all FUS objects has an existance probability greater 0.4; 
    this was recommended by Bosch to present only reliable objects to the customer
'''

import os
import pickle
import pylab as pl
import numpy as np

import kbtools

# ==============================================================================================
class cEvalFUS():
  def __init__(self):       # constructor
    self.myname = 'EvalFUS'
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

   
  # ------------------------------------------------------------------------------------------
  def reinit(self):          # recording interrupted
    for key in self.H4E.keys():
      self.H4E[key].reinit()

  # ------------------------------------------------------------------------------------------
  def process(self,Source):  # evaluate recorded file

    # FileName to specify the origin of the track
    FileName = os.path.basename(Source.FileName)

    # extract FUS tracks
    track_list = self.extract_FUS_tracks(Source)
    print len(track_list)
    
    # ................................................    
    # pickle track_list to 
    output = open('track_list_FUS.pkl', 'wb')
    pickle.dump(track_list, output,-1) # -1: using the highest protocol available
    output.close()
      
    # evaluate tracks        
    for track in track_list:
      Time           = track['t']
      t_start        = Time[0]
      t_stop         = Time[-1]
      dura           = t_stop - t_start
      Handle         = track['Handle'][0]
      min_wExistProb = np.min(track['wExistProb'])
      max_wExistProb = np.max(track['wExistProb'])
      min_dxv        = np.min(track['dxv'])
      max_dxv        = np.max(track['dxv'])
      min_dyv        = np.min(track['dyv'])
      max_dyv        = np.max(track['dyv'])

      # Blacklist
      condition1 = max_wExistProb < 0.4
      
      if condition1 :
        self.BL_table_n_track = self.BL_table_n_track +1
        
        # plot
        #self.plot_xy(self.table_n_track,track)
        
        # add to table
        self.BL_table_array.append(['%d'%self.BL_table_n_track,'%3.2f'%t_start,'%3.2f'%dura,'[%3.2f %3.2f]'%(min_wExistProb,max_wExistProb),'[%3.2f %3.2f]'%(min_dxv,max_dxv),'[%3.2f %3.2f]'%(min_dyv,max_dyv),kbtools.esc_bl(FileName)])

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
  def finish(self):          # end of recording
    for key in self.H4E.keys():
      self.H4E[key].finish()
   

  # ------------------------------------------------------------------------------------------
  def report_init(self):     # prepare for report - input tex file to main
    self.kb_tex.tex_main('\n\\input{%s.tex}\n'%self.myname)
    self.kb_tex.workingfile('%s.tex'%self.myname)
    self.kb_tex.tex('\n\\newpage\\section{EvalFUS Overview}')

    self.kb_tex.tex_main('\n\\input{%s_details.tex}\n'%self.myname)
    self.kb_tex.workingfile('%s_details.tex'%self.myname)
    self.kb_tex.tex('\n\\newpage\\section{EvalFUS Details}')

  # ------------------------------------------------------------------------------------------
  def report(self):          # report events
      
    self.kb_tex.workingfile('%s.tex'%self.myname)

    self.kb_tex.tex('\n\\newpage\\subsection{FUS Blacklist (wExistProb $<$ 0.4)}')
    label = self.kb_tex.table(self.BL_table_array)
    
    
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


     
    self.kb_tex.tex('\nEvalFUS-finished')

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # local functions  
  def extract_FUS_tracks(self, Source):
    print 'extract_FUS_tracks()'

    # constants
    N_LRR3_FUS_obj = 33
    FusObj = "fus.ObjData_TC.FusObj"
    #FusObj = "ohl.ObjData_TC.OhlObj"

    # check with device is present LRR3 or CVR3
    # quick and dirty
    try:    
      Device = 'ECU-0-0'
      Time, Value = Source.getSignal(Device, '%s.i0.Handle'%FusObj)
    except:
      try:
        Device = 'MRR1plus-0-0'
        Time, Value = Source.getSignal(Device, '%s.i0.Handle'%FusObj)
      except:
         print "no device found"
         return

    
    # ----------------------------------  
    track_list = [];

    for FUSidx in xrange(N_LRR3_FUS_obj):

      # get signals
      t, Handle = Source.getSignal(Device, ('%s.i%d.Handle'     %(FusObj,FUSidx)))
      dxv       = Source.getSignal(Device, ('%s.i%d.dxv'        %(FusObj,FUSidx)),ScaleTime = t)[1]
      dyv       = Source.getSignal(Device, ('%s.i%d.dyv'        %(FusObj,FUSidx)),ScaleTime = t)[1]
      vxv       = Source.getSignal(Device, ('%s.i%d.vxv'        %(FusObj,FUSidx)),ScaleTime = t)[1]
      vyv       = Source.getSignal(Device, ('%s.i%d.vyv'        %(FusObj,FUSidx)),ScaleTime = t)[1]
      axv       = Source.getSignal(Device, ('%s.i%d.axv'        %(FusObj,FUSidx)),ScaleTime = t)[1]
      ayv       = Source.getSignal(Device, ('%s.i%d.ayv'        %(FusObj,FUSidx)),ScaleTime = t)[1]
      Stand_b   = Source.getSignal(Device, ('%s.i%d.b.b.Stand_b'%(FusObj,FUSidx)),ScaleTime = t)[1]
      wExistProb = Source.getSignal(Device, ('%s.i%d.wExistProb'%(FusObj,FUSidx)),ScaleTime = t)[1]

            
      # separate handles
      handle_list = kbtools.scan4handles(Handle)
      
      # create tracks from handle list and append to track list
      for k in xrange(len(handle_list)):
        idx = range(handle_list[k][0],handle_list[k][1]+1,1)
        current_track = {'t':t[idx],
                         'Handle':Handle[idx],
                         'dxv':dxv[idx],
                         'dyv':dyv[idx],
                         'vxv':vxv[idx],
                         'vyv':vyv[idx],
                         'axv':axv[idx],
                         'ayv':ayv[idx],
                         'Stand_b':Stand_b[idx],
                         'wExistProb':wExistProb[idx]
                        }

        current_track['angle'] = np.arctan2(current_track['dyv'],current_track['dxv'])*(180.0/np.pi)

        track_list.append(current_track)

    return track_list

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def plot_xy(self,k,track):
  
    self.kb_tex.workingfile('%s_details.tex'%self.myname)
    self.kb_tex.tex('\n\\subsection{FUS %d}'%k)
 
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









