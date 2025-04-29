"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: Video Benchmark '''
''' to be called by DAS_eval.py '''

'''  Comparison of Video Systems:
     Delphi IFV 
 
'''

import os
import pickle
import pylab as pl
import numpy as np

# ======================================================================================================
def calc_signal_valid(t,t1,t_threshold=0.1):

  valid = np.ones(t.size)
  x = np.diff(t1)
  x = np.nonzero(x> t_threshold)[0]
  #print x

  # cut away start
  valid[np.nonzero(t<t1[0])] = 0
  
  # cut away end
  valid[np.nonzero(t>t1[-1])] = 0
  
  for idx in x:
    t_start = t1[idx]
    t_stop  = t1[idx+1]
    #print idx,  t_start, t_stop
    valid[np.nonzero((t>=t_start)&(t<=t_stop))] = 0
 
  #print t
  #print valid
  return valid
# ======================================================================================================

#==========================================================================================
# sorty 
# sort list <mylist> according to attribute <attribite>
# arguments: mylist unsorted (dictionary)
#            attribute
# return :   mylist sorted (dictionary)
#
# example: track_list = sorty (track_list,'t')

def sorty (mylist, attribute):
  n = len(mylist)
  for k in xrange(0,n-1):
    for m in xrange(k+1,n):
      if mylist[k][attribute][0] > mylist[m][attribute][0]:
        tmp_element = mylist[k]
        mylist[k] = mylist[m]
        mylist[m] = tmp_element

  return mylist
# ======================================================================================================




# ==============================================================================================
class cEvalVideoBM():
  def __init__(self):       # constructor
    self.myname = 'EvalVideoBM'

  def __del__(self):         # destructor
    pass
      
  # ------------------------------------------------------------------------------------------
  def init(self,folder):     # general start
    pass  
   
  # ------------------------------------------------------------------------------------------
  def reinit(self):          # recording interrupted
    pass
    
  # ------------------------------------------------------------------------------------------
  def process(self,Source):  # evaluate recorded file

    # FileName to specify the origin of the track
    FileName = os.path.basename(Source.FileName)

    # scaletime
    Time, Value = Source.getSignal("MRR1plus_0_0", "csi.VehicleData_T20.nMot")
    print "T20 dT = %3.1f ms" % (np.mean(np.diff(Time))*1000.0)
    scaletime = Time


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if 1:    
      # extract VFP tracks
      TrackList_VFP = self.extract_VFP_tracks(Source, scaletime)
      print "TrackList_VFP %d entries" % len(TrackList_VFP)
      #TrackList_VFP = sorty (TrackList_VFP,'t')
    
      # ................................................    
      # pickle track_list to file
      if 1:
        output = open('TrackList_VFP.pkl', 'wb')
        pickle.dump(TrackList_VFP, output,-1) # -1: using the highest protocol available
        output.close()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if 1:    
      # extract IFV tracks
      TrackList_IFV = self.extract_IFV_tracks(Source, scaletime)
      print "track_list %d entries" % len(TrackList_IFV)
      #TrackList_IFV = sorty (TrackList_IFV,'t')
    
      # ................................................    
      # pickle track_list to file
      if 1:
        output = open('TrackList_IFV.pkl', 'wb')
        pickle.dump(TrackList_IFV, output,-1) # -1: using the highest protocol available
        output.close()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if 1:
      FigNr = 100
      Time = TrackList_VFP[0]['t']
      self.visual_cmp_systems_magnify(FileName, Time, TrackList_VFP, TrackList_IFV, FigNr)

  # ------------------------------------------------------------------------------------------
  def finish(self):          # end of recording
    pass   

  # ------------------------------------------------------------------------------------------
  def report_init(self):     # prepare for report - input tex file to main
    self.kb_tex.tex_main('\n\\input{%s.tex}\n'%self.myname)
    self.kb_tex.workingfile('%s.tex'%self.myname)
    self.kb_tex.tex('\n\\newpage\\section{EvalVideoBM Overview}')

    self.kb_tex.tex_main('\n\\input{%s_details.tex}\n'%self.myname)
    self.kb_tex.workingfile('%s_details.tex'%self.myname)
    self.kb_tex.tex('\n\\newpage\\section{EvalVideoBM Details}')

  # ------------------------------------------------------------------------------------------
  def report(self):          # report events
      
    self.kb_tex.workingfile('%s.tex'%self.myname)

    self.kb_tex.tex('\nEvalVideoBM-finished')

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # local functions  
  def extract_VFP_tracks(self, Source, scaletime):
    print 'extract_VFP_tracks()'

    # ----------------------------------  
    track_list = [];

    len_scaletime = len(scaletime)
    
    #multiplexed data with always 10 objects sended (value=0 for non objects)
    # VISION_OBSTACLE_MSG1
    time_VFP, MsgCnt_VFP = Source.getSignal('VISION_OBSTACLE_MSG1(675)_4_VFP','CAN_MESSAGE_COUNTER_MSG1')
    range_VFP            = Source.getSignal('VISION_OBSTACLE_MSG1(675)_4_VFP','CAN_VIS_OBS_RANGE')[1]
    angle_VFP            = Source.getSignal('VISION_OBSTACLE_MSG1(675)_4_VFP','CAN_VIS_OBS_ANGLE_CENTROID')[1]
    range_rate           = Source.getSignal('VISION_OBSTACLE_MSG1(675)_4_VFP','CAN_VIS_OBS_RANGE_RATE')[1]
    angle_rate           = Source.getSignal('VISION_OBSTACLE_MSG1(675)_4_VFP','CAN_VIS_OBS_ANGLE_RATE')[1]
    lateral_rate         = Source.getSignal('VISION_OBSTACLE_MSG1(675)_4_VFP','CAN_VIS_OBS_LATERAL_RATE')[1]
    count1               = Source.getSignal('VISION_OBSTACLE_MSG1(675)_4_VFP','CAN_VIS_OBS_COUNT_MSG1')[1]
    
    #print MsgCnt
    #print count1
    
    #motion           = Source.getSignal('VISION_OBSTACLE_MSG2(676)_4_',   'CAN_VIS_OBS_MOTION_TYPE')[1]
    #classification   = Source.getSignal('VISION_OBSTACLE_MSG2(676)_4_',   'CAN_VIS_OBS_CLASSIFICATION')[1]
    

    '''
    print "time_VFP %d" % len(time_VFP)
    print "motion %d" % len(motion)
    
    tmp_length = np.min((len(range),len(motion)))
    print "tmp_length %d" % tmp_length

    len_o=tmp_length/10
    print "len_o %d" % len_o
    #len_o -=1
    '''
    len_o=int(len(time_VFP)/10)
    print "len_o %3.2f" % len_o

    o={}
    o["time"]       =np.zeros(len_o)
    o["dx"]         =np.zeros(len_o)
    o["dy"]         =np.zeros(len_o)
    #o["motion"]     =np.zeros(len_o)
    #o["class"]      =np.zeros(len_o)
    #o["rangerate"]  =np.zeros(len_o)

    N = np.max(count1)
    print "N %d" % N

    for k in xrange(10):
      idx = count1==(k+1)
      t      = time_VFP[idx]
      MsgCnt = MsgCnt_VFP[idx]
      range  = range_VFP[idx]
      angle  = angle_VFP[idx]
      valid  = np.zeros(len(t))
      valid[range>0.0] = 1
      dx     =  range_VFP[idx]*np.cos(angle_VFP[idx]*(np.pi/180.0))
      dy     = -range_VFP[idx]*np.sin(angle_VFP[idx]*(np.pi/180.0))
      #o["rangerate"][j] = rangerate[idx]
      #o["motion"][j]    = motion[idx]
      #o["class"][j]     = classification[idx]
      
      #rescale:
      #dx        = measparser.cSignalSource.rescale(o["time"], o["dx"],        scaletime)[1]
      #dy        = measparser.cSignalSource.rescale(o["time"], o["dy"],        scaletime)[1]
      #motion    = measparser.cSignalSource.rescale(o["time"], o["motion"],    scaletime)[1]
      #rangerate = measparser.cSignalSource.rescale(o["time"], o["rangerate"], scaletime)[1]
      #classify  = measparser.cSignalSource.rescale(o["time"], o["class"],     scaletime)[1]
          
      current_track = {'t':t,
                       'valid':valid,
                       'MsgCnt':MsgCnt,
                       'range':range,
                       'angle':angle,
                       'dxv':dx,
                       'dyv':dy
                      }

      track_list.append(current_track)
          
          
    return track_list     

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # local functions  

  def extract_IFV_tracks(self, Source, scaletime):
    print 'extract_IFV_tracks()'

    Device_list = Source.getDeviceNames("fcw_cartesian_x")
    #print "Device_list", len(Device_list)
    
    # ----------------------------------  
    track_list = [];
      
    for DevNr, Device in enumerate(Device_list):
      t1, x1 = Source.getSignal(Device, 'fcw_cartesian_x')
      if len(t1) > 0:
        t_threshold=0.1
        valid = calc_signal_valid(scaletime,t1,t_threshold)
        t      = scaletime
        dx     = Source.getSignal(Device,'fcw_cartesian_x', ScaleTime=scaletime)[1]
        dy     = Source.getSignal(Device,'fcw_cartesian_y', ScaleTime=scaletime)[1]
        ID     = Source.getSignal(Device,'fcw_object_ID', ScaleTime=scaletime)[1]
        #abs_vx = Source.getSignal(Device,'fcw_cartesian_abs_vx', ScaleTime=scaletime)
        #abs_vy = Source.getSignal(Device,'fcw_cartesian_abs_vy', ScaleTime=scaletime)
      
        dy = -dy*valid
        
        current_track = {'t':t,
                         'ID':ID,
                         'dxv':dx,
                         'dyv':dy,
                         'valid': valid,
                         #'vxv':vxv[idx],
                         #'vyv':vyv[idx],
                         #'axv':axv[idx],
                         #'ayv':ayv[idx],
                         #'Stand_b':Stand_b[idx],
                         #'wExistProb':wExistProb[idx]
                        }

        current_track['range'] = current_track['dxv']
        
        current_track['angle'] = np.arctan2(current_track['dyv'],current_track['dxv'])*(180.0/np.pi)

        track_list.append(current_track)

    return track_list


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  def visual_cmp_systems_magnify(self,FileName, Time, TrackList1, TrackList2, FigNr):
  
    # in which sheet to write
    self.kb_tex.workingfile('%s_details.tex'%self.myname)
    
    # measurement is subsection
    self.kb_tex.tex('\n\\newpage\\subsection{%s}'%self.kb_tex.esc_bl(FileName))
 
 
    # magnification are subsubsections 
    t_start = Time[0]
    t_stop  = Time[-1]
    dura = t_stop-t_start
    display_width = 40.0
    n = np.fix(dura/display_width+1)
  
    for k in xrange(n):
      t_range = (t_start+display_width*(k-0.1),t_start+display_width*(k+1.1))
      f = self.visual_cmp_systems(TrackList1, TrackList2, FigNr,t_range)
      self.kb_tex.tex('\n\\newpage\\subsubsection{section %d}'%k)
      label = self.kb_tex.epsfig(f, 'Time %3.1f .. %3.1fs  %s' % (t_range[0], t_range[1],self.kb_tex.esc_bl(FileName)) );

    
  #-----------------------------------------------------------
  def visual_cmp_systems(self, TrackList1, TrackList2, FigNr, t_range):
  
    f=pl.figure(FigNr);   FigNr += 1
    f.clear()
    f.suptitle('VFP: blue bold, IFV: red thin')
  
    sp1=f.add_subplot(211)
    sp1.grid()
    sp1.set_title('dx')
    sp1.set_ylim(0,160)
    sp1.set_xlim(t_range)
    sp1.set_ylabel('[m]')
  
    sp2=f.add_subplot(212)
    sp2.grid()
    sp2.set_title('dy')
    sp2.set_ylim(-15,15)
    sp2.set_xlim(t_range)
    sp2.set_ylabel('[m]')
    sp2.set_xlabel('time [s]')
 
    # TrackList1 
    for k,track in enumerate(TrackList1):
      Time       = track['t']
      valid      = track['valid']
      dx         = track['dxv']
      dy         = track['dyv']
      range      = track['range']
      angle      = track['angle']
        
      if any(valid):
        # kick out invalid points
        dx[valid==False] = -10
        dy[valid==False] = -20
        sp1.plot(Time,dx,'b.')
        sp2.plot(Time,dy,'b.')
     
    # TrackList2
    for k,track in enumerate(TrackList2):
      Time       = track['t']
      valid      = track['valid']
      dx         = track['dxv']
      dy         = track['dyv']
      range      = track['range']
      angle      = track['angle']
    
      if any(valid):
        # kick out invalid points
        dx[valid==False] = -10
        dy[valid==False] = -20
        sp1.plot(Time,dx,'r,')
        sp2.plot(Time,dy,'r,')

    # label for VFP and IFV ?
    #sp1.legend(('VFP','IFV'))
    #sp2.legend(('VFP','IFV'))
  
    #f.show()  # not required for creating eps 
    return f
#-------------------------------------------------------------------------      









