"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis
import pylab as pl
import numpy as np
from ugtools import scan4handles

# used for signal filtering but not compatible with pyglet
#from scipy.signal import butter
#from filtfilt import filtfilt



# tbd.
#  all_dict['LRR3_ATS']['dxvFilt']   = Source.getSignalFromECU('ats.Po_TC.PO.i0.dxvFilt')[1]


#==========================================================================================
# extract VBOX signal 
# return : (dictionary)
#  ['t']                         - t
#  ['time_since_midnight']       - [s]
#  ['Velocity_Kmh']              - [km/h]
#  ['Longitudinal_acceleration'] - [G]

def extract_VBOX(Source,FigNr,Comment):

  print 'extract_VBOX("%s")' % Comment

  enable_plots = 1
  
  VBOX_sig = {}

  if Source == None:
    print 'no Source'
    return None

  # VBOX_III_16bit.dbc
  try:  

    Source.loadParser()
    # VBOX1 e.g. 'VBOX_1(301)_x_VBOX_III'   x=1,2
    #  UTC:               Time_since_midnight_hi_byte, Time_Since_Midnight_lo_bytes : unit 10ms 
    #  Latitude:          Latitude_hi_bytes, Latitude_lo_bytes
    #  No. of Satellites: Sats
    Device_VBOX_1, =   Source.Parser.getDeviceNames('Sats')

    # VBOX2 e.g. 'VBOX_2(302)_2_VBOX_III'
    #  velocity : 'Velocity_Kmh'
    Device_VBOX_2, =  Source.Parser.getDeviceNames('Velocity_Kmh')

    # VBOX4 e.g. 'VBOX_4(304)_2_VBOX_III'
    #  Lateral_acceleration :   "G"  
    #  Longitudinal_acceleration : "G"  
    Device_VBOX_4, =  Source.Parser.getDeviceNames('Longitudinal_acceleration')
  except:
    print 'Devices missing'
    return None
  
  # show found Devices
  print Device_VBOX_1
  print Device_VBOX_2
  print Device_VBOX_4
  

  t,Sats                         = Source.getSignal(Device_VBOX_1,'Sats')
  Time_since_midnight_hi_byte    = Source.getSignal(Device_VBOX_1,'Time_since_midnight_hi_byte',ScaleTime = t)[1]
  Time_Since_Midnight_lo_bytes   = Source.getSignal(Device_VBOX_1,'Time_Since_Midnight_lo_bytes',ScaleTime = t)[1]
  Velocity_Kmh                   = Source.getSignal(Device_VBOX_2,'Velocity_Kmh',ScaleTime = t)[1]
  Longitudinal_acceleration_raw  = Source.getSignal(Device_VBOX_4,'Longitudinal_acceleration',ScaleTime = t)[1]

  # Filter signal with a zero phase filter
  filter_enabled = 0
  if filter_enabled:
    [b,a]=butter(4,0.2)
    Longitudinal_acceleration=filtfilt(b,a,Longitudinal_acceleration_raw)
  else:
    Longitudinal_acceleration=Longitudinal_acceleration_raw


  # UTC
  Time_Since_Midnight = (Time_since_midnight_hi_byte*(2**16)+Time_Since_Midnight_lo_bytes)


  # collect VBOX signals
  VBOX_sig['t']                             = t
  VBOX_sig['time_since_midnight']           = Time_Since_Midnight
  VBOX_sig['Velocity_Kmh']                  = Velocity_Kmh
  VBOX_sig['Longitudinal_acceleration']     = Longitudinal_acceleration
  VBOX_sig['Longitudinal_acceleration_raw'] = Longitudinal_acceleration_raw

  if enable_plots:
    f=pl.figure(FigNr+1)
    f.suptitle('VBOX %s'%Comment)

    sp=f.add_subplot(411)
    sp.grid()
    sp.plot(t,Time_Since_Midnight-Time_Since_Midnight[0])
    sp.set_title('Time_Since_Midnight Start at %3.2f s'%Time_Since_Midnight[0])

    sp=f.add_subplot(412)
    sp.grid()
    sp.plot(t,Velocity_Kmh)
    sp.set_title('velocity')
    #sp.ylabel('[km/h]')

    sp=f.add_subplot(413)
    sp.grid()
    sp.plot(t,Longitudinal_acceleration_raw*9.81,'b')
    sp.plot(t,Longitudinal_acceleration*9.81,'r')
    sp.set_title('longitudinal acceleration')
    #sp.ylabel('[m/s^2]')

    sp=f.add_subplot(414)
    sp.grid()
    sp.plot(t,Sats)
    sp.set_title('Sats')
    #sp.xlabel('time [s]')

    f.show()

    # Time since midnight
    if 0:
      f=pl.figure(FigNr+2)
      f.suptitle('VBOX')
  
      sp=f.add_subplot(311)
      sp.grid()
      sp.plot(t,Time_since_midnight_hi_byte*100,'d')
      sp.set_title('Time_since_midnight_hi_byte')

      sp=f.add_subplot(312)
      sp.grid()
      sp.plot(t,Time_Since_Midnight_lo_bytes*100,'d')
      sp.set_title('Time_Since_Midnight_lo_bytes')

      sp=f.add_subplot(313)
      sp.grid()
      sp.plot(t,Time_Since_Midnight,'d')
      sp.set_title('Time_Since_Midnight')

      f.show()



  return VBOX_sig

#==========================================================================================
# synchronise signals from two VBOXes
# VBOX_master - master reference
# VBOX_slave  - slave
#
# return : (dictionary)
#
#  under construction
#  it was observed that time since midnight differs about 13 seconds
#  effect will be clarified with Racelogic
def sync_VBOX_signals(VBOX_master,VBOX_slave,FigNr):

  print 'sync_VBOX_signals()'

  if VBOX_master==None or VBOX_slave==None:
    return None

  enable_plots = 1

  # magic !!! -> VBOX Nr.6 from Mr. Ebner has offset + 14 seconds
  VBOX_slave['time_since_midnight'] = VBOX_slave['time_since_midnight']-14

  UTC_start_master = np.mean(VBOX_master['time_since_midnight']-VBOX_master['t'])
  UTC_start_slave  = np.mean(VBOX_slave['time_since_midnight']-VBOX_slave['t'])

  t_offset_slave = UTC_start_slave - UTC_start_master

  print t_offset_slave
  
  VBOX_slave['t'] = VBOX_slave['t'] + t_offset_slave
  
  return VBOX_slave

  
  # --------------------------------------
  # resample slave to master
  VBOX_slave_on_t_master ={}
  VBOX_slave_on_t_master['time_since_midnight'] = np.interp(VBOX_master['t'],
                                                            VBOX_slave['t'],VBOX_slave['time_since_midnight'])

  t_start = np.maximum(VBOX_master['t'][0], VBOX_slave['t'][0])
  t_end   = np.minimum(VBOX_master['t'][-1],VBOX_slave['t'][-1])
  idx = ((VBOX_master['t'] >= t_start) & (VBOX_master['t'] <= t_end)).nonzero()


  # --------------------------------------
  # determine time offset for slave 
  t_offset_slave = np.mean(VBOX_slave_on_t_master['time_since_midnight'] - VBOX_master['time_since_midnight'])
  print "t_offset_slave = %3.2f"%t_offset_slave


  #------------------------------------------------------------------------------------
  #t_offset_slave = -3

  t_start = np.maximum(VBOX_master['t'][0],VBOX_master['t'][0]+t_offset_slave)
  t_end   = np.minimum(VBOX_master['t'][-1],VBOX_master['t'][-1]+t_offset_slave)

  print "t_start = %3.2f"%t_start
  print "t_end   = %3.2f"%t_end

  # --------------------------------------
  # adjust time offset
  VBOX_slave_adjusted  = {}
  for key in VBOX_slave.keys():
    VBOX_slave_adjusted[key] = np.interp(VBOX_master['t']-t_offset_slave,
                                         VBOX_slave['t'],VBOX_slave[key])
  VBOX_slave_adjusted['t'] = VBOX_master['t']
  
  idx = ((VBOX_master['t'] >= t_start) & (VBOX_master['t'] <= t_end)).nonzero()
  for key in VBOX_slave.keys():
    VBOX_slave_adjusted[key] = VBOX_slave_adjusted[key][idx]
 
  VBOX_master_adjusted = {}  
  for key in VBOX_master.keys():
    VBOX_master_adjusted[key] = VBOX_master[key][idx]


  if enable_plots: 
    f=pl.figure(FigNr+1)
    f.suptitle('synchronise signals from two VBOXes')
  
    sp=f.add_subplot(211)
    sp.grid()
    sp.plot(VBOX_master['t'],VBOX_master['time_since_midnight']-VBOX_master['time_since_midnight'][0],'b.')
    sp.plot(VBOX_slave['t'] ,VBOX_slave['time_since_midnight']-VBOX_master['time_since_midnight'][0],'r.')
    sp.plot(VBOX_master['t'],VBOX_slave_on_t_master['time_since_midnight']-VBOX_master['time_since_midnight'][0],'k.')
    #sp.legend('master','slave','slave sampled on master')
    sp.set_title('time_since_midnight Start at %3.2f seconds'%VBOX_master['time_since_midnight'][0])

    sp=f.add_subplot(212)
    sp.grid()
    sp.plot(VBOX_master['t'][idx],VBOX_master['time_since_midnight'][idx]-VBOX_master['time_since_midnight'][0],'b.')
    sp.plot(VBOX_slave_adjusted['t'],VBOX_slave_adjusted['time_since_midnight']-VBOX_master['time_since_midnight'][0],'r.')
    sp.set_title('time_since_midnight Start at %3.2f seconds'%VBOX_master['time_since_midnight'][0])

    f.show()

    f=pl.figure(FigNr+2)
    f.suptitle('VBOX')
  
    sp=f.add_subplot(311)
    sp.grid()
    sp.plot(VBOX_slave_adjusted['t'],VBOX_slave_adjusted['time_since_midnight']-VBOX_master_adjusted['time_since_midnight'],'b.')
    sp.set_title('time_since_midnight')

    sp=f.add_subplot(312)
    sp.grid()
    sp.plot(VBOX_master_adjusted['t'],VBOX_master_adjusted['Velocity_Kmh'],'b.')
    sp.plot(VBOX_slave_adjusted['t'],VBOX_slave_adjusted['Velocity_Kmh'],'r.')
    sp.set_title('Velocity_Kmh')

    sp=f.add_subplot(313)
    sp.grid()
    sp.plot(VBOX_master_adjusted['t'],VBOX_master_adjusted['Longitudinal_acceleration'],'b.')
    sp.plot(VBOX_slave_adjusted['t'],VBOX_slave_adjusted['Longitudinal_acceleration'],'r.')
    sp.set_title('Longitudinal_acceleration')

    f.show()

  return [VBOX_slave_adjusted, VBOX_master_adjusted]

#==========================================================================================
# show VBOX signals from Master and Slave in on plot
# VBOX_master - master reference
# VBOX_slave  - slave
#
# return : (dictionary)
#
#  under construction
#  it was observed that time since midnight differs about 13 seconds
#  effect will be clarified with Racelogic

def cmp_VBOX_signals(VBOX_master,VBOX_slave,FigNr):

  print 'cmp_VBOX_signals()'

  if VBOX_master==None or VBOX_slave==None:
    return

  f=pl.figure(FigNr+1)
  f.suptitle('VBOX')

  sp=f.add_subplot(211)
  sp.grid()
  sp.plot(VBOX_master['t'],VBOX_master['Velocity_Kmh'],'b.')
  sp.plot(VBOX_slave['t'],VBOX_slave['Velocity_Kmh'],'r.')
  sp.set_title('Velocity_Kmh')

  sp=f.add_subplot(212)
  sp.grid()
  sp.plot(VBOX_master['t'],VBOX_master['Longitudinal_acceleration'],'b.')
  sp.plot(VBOX_slave['t'],VBOX_slave['Longitudinal_acceleration'],'r.')
  sp.set_title('Longitudinal_acceleration')

  f.show()

 
#==========================================================================================
# extract LRR3 tracks
#
# arguments: Source   - signal source
#            par      - parameters for selection criterias
#
# return : track_list (dictionary)
#          each track includes the following attributes:
#          't'       - [s]      - time
#          'Handle'  -          - handle (logical number)
#          'dxv'     - [m]      - longitudinal distance
#          'dyv'     - [m]      - lateral distance
#          'angle'   - [degree] - arctan2(dyv,dxv)*180/pi 
#          'vxv'     - [m/s]    - long. velocity
#          'vyv'     - [m/s]    - lateral velocity
#          'axv'     - [m/s^2]  - long. acceleration
#          'ayv'     - [m/s^2]  - lateral acceleration
#          'Stand_b' -          - flag indicating stationary object
#
def extract_LRR3_tracks(Source,par):

  print 'extract_LRR3_tracks()'


  # parmeter
  select_all_b = par['select_all']  # select all tracks
  minimum_required_duration = 1  # only use tracks longer than x second
  select_only_stationary_b = par['only_stationary']
    
  # constants
  N_LRR3_FUS_obj = 33

  # ----------------------------------  
  track_list = [];

  for FUSidx in xrange(N_LRR3_FUS_obj):

    # get LRR3 signals from Source
    t, Handle = Source.getSignalFromECU(('fus.ObjData_TC.FusObj.i%d.Handle'%FUSidx))
    dxv = Source.getSignalFromECU(('fus.ObjData_TC.FusObj.i%d.dxv'%FUSidx),ScaleTime = t)[1]
    dyv = Source.getSignalFromECU(('fus.ObjData_TC.FusObj.i%d.dyv'%FUSidx),ScaleTime = t)[1]
    vxv = Source.getSignalFromECU(('fus.ObjData_TC.FusObj.i%d.vxv'%FUSidx),ScaleTime = t)[1]
    vyv = Source.getSignalFromECU(('fus.ObjData_TC.FusObj.i%d.vyv'%FUSidx),ScaleTime = t)[1]
    axv = Source.getSignalFromECU(('fus.ObjData_TC.FusObj.i%d.axv'%FUSidx),ScaleTime = t)[1]
    ayv = Source.getSignalFromECU(('fus.ObjData_TC.FusObj.i%d.ayv'%FUSidx),ScaleTime = t)[1]
    Stand_b = Source.getSignalFromECU(('fus.ObjData_TC.FusObj.i%d.b.b.Stand_b'%FUSidx),ScaleTime = t)[1]

    # separate handles
    handle_list = scan4handles(Handle)
    #print handle_list

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
                       'Stand_b':Stand_b[idx]
                       }

      # condition1: only use tracks longer than 1 second
      t_start = current_track['t'][0]
      t_stop  = current_track['t'][-1]
      #print t_start, t_stop
      delta_t = t_stop-t_start
      condition1 = delta_t > minimum_required_duration

      # condition2: exclude stationary objects
      condition2 = not current_track['Stand_b'].any()  # all
      #condition2 = 1

      if select_only_stationary_b:
        condition2 =not condition2

      # append current track to track list if conditions are fullfilled
      if select_all_b |(condition1 & condition2):
        # calculate additional signals
        current_track['angle'] = np.arctan2(current_track['dyv'],current_track['dxv'])*(180.0/np.pi)
        
        track_list.append(current_track)


  return track_list
  pass

#==========================================================================================
# plot LRR3 tracks
#
# arguments: track_list  - list of tracks (dictionary)
#            Sync
#            FgNr        - Figure Nummer
#
# return : -
#
def plot_LRR3_tracks(track_list,Sync, FgNr):
  # plot given LRR3 tracks

  print 'plot_LRR3_tracks()'

  if 0==len(track_list):
    return  


  PN = datavis.cPlotNavigator('LRR3', FgNr)

  # Handle
  Signals = []
  for k in xrange(len(track_list)):
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['Handle']])
  PN.addsignal(ylabel = 'Handle',*Signals)

  # dxv
  Signals = []
  for k in xrange(len(track_list)):
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['dxv']])
  PN.addsignal(ylabel = 'dxv [m]',*Signals)

  # dyv
  Signals = []
  for k in xrange(len(track_list)):
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['dyv']])
  PN.addsignal(ylabel = 'dyv [m]',*Signals)

  # angle
  Signals = []
  for k in xrange(len(track_list)):
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['angle']])
  PN.addsignal(ylabel = 'angle [degree]',*Signals)


  # vxv
  Signals = []
  for k in xrange(len(track_list)):
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['vxv']])
  PN.addsignal(ylabel = 'vxv [m/s]',*Signals)

  # vyv
  Signals = []
  for k in xrange(len(track_list)):
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['vyv']])
  PN.addsignal(ylabel = 'vyv [m/s]',xlabel = 'time [s]',*Signals)

  # axv
  Signals = []
  for k in xrange(len(track_list)):
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['axv']])
  PN.addsignal(ylabel = 'axv [m/s^2]',*Signals)

  # ayv
  Signals = []
  for k in xrange(len(track_list)):
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['ayv']])
  PN.addsignal(ylabel = 'ayv [m/s^2]',xlabel = 'time [s]',*Signals)

  Sync.addClient(PN)
  pass

#==========================================================================================
# extract AC100 tracks
#
# arguments: Source   - signal source
#            par      - parameters for selection criterias
#
# return : track_list (dictionary)
#          each track includes the following attributes:
#          't'       - [s]      - time
#          'internal_track_index'  - handle (logical number)
#          'status'  -          - tracking status
#          'range'   - [m]      - longitudinal distance
#          'dyv'     - [m]      - lateral distance
#          'angle'   - [degree] - arctan2(dyv,dxv)*180/pi 
#          'rel_v'   - [m/s]    - relative velocity
#          'accel'   - [m/s^2]  - track acceleration over ground
#          'asso_target_index'  - flag indicating stationary object
#
def extract_AC100_tracks(Source,par):

  print 'extract_AC100_tracks()'

  # parmeter
  select_all_b = 0                 # select all tracks
  minimum_required_duration = 0.1  # only use tracks longer than x second
  select_only_stationary_b = 0     # par['only_stationary']:

  change_angle_sign_b = par['change_angle_sign'];

 
  # ----------------------------------  
  # constants
  N_AC100_TR = 10

  # ----------------------------------  
  # get device name for tracks  Device_Tracks = 'Tracks(663)_2_'
  Source.loadParser()
  Device_Tracks, =   Source.Parser.getDeviceNames('tr1_range')
  print 'Device_Tracks = "%s"' % Device_Tracks

  # ----------------------------------  
  # collect tracks
  track_list = []

  for tr_no in xrange(N_AC100_TR):
    current_track = {}
    t = Source.getSignal(Device_Tracks,('tr%d_range'%tr_no))[0]
    if t.size > 0:
      internal_track_index = Source.getSignal(Device_Tracks,'tr%d_internal_track_index'%tr_no,ScaleTime = t)[1]
      acc_track_info       = Source.getSignal(Device_Tracks,'tr%d_acc_track_info'%tr_no,ScaleTime = t)[1]

      status   = Source.getSignal(Device_Tracks,'tr%d_tracking_status'%tr_no,ScaleTime = t)[1]
      dx_range = Source.getSignal(Device_Tracks,'tr%d_range'%tr_no,ScaleTime = t)[1]
      rel_v    = Source.getSignal(Device_Tracks,'tr%d_relative_velocitiy'%tr_no,ScaleTime = t)[1]
      angle    = Source.getSignal(Device_Tracks,('tr%d_uncorrected_angle'%tr_no),ScaleTime = t)[1]
      corrected_lateral_distance = Source.getSignal(Device_Tracks,('tr%d_corrected_lateral_distance'%tr_no),ScaleTime = t)[1]
      accel    = Source.getSignal(Device_Tracks,('tr%d_acceleration_over_ground'%tr_no),ScaleTime = t)[1]
      asso_target_index = Source.getSignal(Device_Tracks,('tr%d_asso_target_index'%tr_no),ScaleTime = t)[1]
      track_selection_status = Source.getSignal(Device_Tracks,('tr%d_track_selection_status'%tr_no),ScaleTime = t)[1]

      # calculate signal used for selection
      Stand_b = (track_selection_status & (2**4))>0   # Bit4: stationary

      if change_angle_sign_b:
        angle = -angle


      # internal_track_index keeps constant but track is changing
      x = internal_track_index
      x[(status==0).nonzero()] = -1  # status ==0 Track is empty (end of a track)
      handle_list = scan4handles(x,0)



      for k in xrange(len(handle_list)):
        idx = range(handle_list[k][0],handle_list[k][1]+1,1)    # exclude the last point here
        if len(idx) > 0:
          current_track = {'t':t[idx],
                           'internal_track_index':internal_track_index[idx],
                           'acc_track_info':acc_track_info[idx],
                           'status':status[idx],
                           'range':dx_range[idx],
                           'angle':angle[idx],
                           'rel_v':rel_v[idx],
                           'accel':accel[idx],
                           'corrected_lateral_distance':corrected_lateral_distance[idx],
                           'asso_target_index':asso_target_index[idx],
                           'track_selection_status':track_selection_status[idx],
                           'Stand_b':Stand_b[idx],
                           'tr_no':tr_no*np.ones_like(t[idx])
                          }

          # condition1: only use tracks longer than 1 second
          t_start = current_track['t'][0]
          t_stop  = current_track['t'][-1]
          #print t_start, t_stop
          delta_t = t_stop-t_start
          condition1 = delta_t > minimum_required_duration
          #condition1 = 1

          # condition2: exclude stationary objects
          x = current_track['Stand_b']
          condition2 = (1.0*len(x.nonzero()[0])/len(x)) < 0.2
          if select_only_stationary_b:
            condition2 =not condition2

           
          #print current_track['Stand_b']
          
          if select_all_b | (condition1&condition2):
            # calculate additional signals
            current_track['dxv'] = current_track['range']*np.cos(current_track['angle']*(np.pi/180.0))
            current_track['dyv'] = current_track['range']*np.sin(current_track['angle']*(np.pi/180.0))
            # append current track to list   
            track_list.append(current_track)

  return track_list

#==========================================================================================
# clean_up_end_AC100_tracks
#
#   sometimes the last value of a track seems to be already a start of
#   another track
#   goal:   skip last sample if it differs too much from the one before
#          -> need to be carefully tuned
#   workaround: always cut off the last sample
#
# arguments: track_list (dictionary)
#
# return :   track_list (dictionary)

def clean_up_end_AC100_tracks(track_list):

  print 'clean_up_end_AC100_tracks()'

  for k in xrange(len(track_list)):
    #print [track_list[k]['range'][-1],track_list[k]['range'][-2]]
    #print track_list[k]['range']  
    #if np.abs(track_list[k]['range'][-1]-track_list[k]['range'][-2])>10:
    #  print k
    for key in track_list[k].keys():
      track_list[k][key] = track_list[k][key][0:-2]

  return track_list

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

#==========================================================================================
# combine_AC100_tracks
#   combine consecutive tracks having the same internal track index and only a small time gap
#
# arguments: track_list (dictionary)
#
# return :   track_list (dictionary)

def combine_AC100_tracks(track_list):

  print 'combine_AC100_tracks()'

  # maximal permittable time gap
  max_t_gap = 0.3

  if 0==len(track_list):
    return track_list

  
  n = len(track_list)
  new_track_list = [];
  
  # sort list of increasing starting points
  track_list = sorty (track_list,'t')

  # register for used elements in the list (0:unused; 1:used)
  element_used = np.zeros(n)

  for k in xrange(n):
    if not element_used[k]:
      element_used[k] = 1
      new_track = track_list[k]
      for m in xrange(k+1,n):
        if not element_used[m]:
          cond1 = (track_list[m]['internal_track_index'][0] == new_track['internal_track_index'][-1])
          cond2 = ((track_list[m]['t'][0] - new_track['t'][-1])< max_t_gap)
          if  cond1 and cond2:
            element_used[m] = 1  
            for key in new_track.keys():
              new_track[key] = np.hstack((new_track[key], track_list[m][key]))
      
      new_track_list.append(new_track)

  #for k in xrange(len(new_track_list)):
  #  print [k, track_list[k]['t'][0]]

  return new_track_list

#==========================================================================================
# plot_AC100_tracks
#   plot AC100 tracks
#
# arguments: track_list (dictionary)
#
# return :   track_list (dictionary)
  
def plot_AC100_tracks(track_list,Sync, FgNr):

  print 'plot_AC100_tracks()'

  if 0==len(track_list):
    return  

  tracks_to_display = xrange(len(track_list))

  PN = datavis.cPlotNavigator('AC100', FgNr)

  # internal_track_index
  Signals = []
  for k in tracks_to_display:
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['internal_track_index']])
  PN.addsignal(ylabel = 'track_index',*Signals)

  # range
  Signals = []
  for k in tracks_to_display:
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['range']])
  PN.addsignal(ylabel = 'range [m]',*Signals)

  # dyv
  Signals = []
  for k in tracks_to_display:
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['dyv']])
  PN.addsignal(ylabel = 'dyv [m]',*Signals)

  # rel_v
  Signals = []
  for k in tracks_to_display:
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['rel_v']])
  PN.addsignal(ylabel = 'rel_v [m/s]',*Signals)

  # angle
  Signals = []
  for k in tracks_to_display:
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['angle']])
  PN.addsignal(ylabel = 'angle [angle]',*Signals)

  # corrected_lateral_distance
  Signals = []
  for k in tracks_to_display:
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['corrected_lateral_distance']])
  PN.addsignal(ylabel = 'corrected_lateral_distance[m]',*Signals)

  # track acceleration over ground
  Signals = []
  for k in tracks_to_display:
    Signals.append('')
    Signals.append([track_list[k]['t'],track_list[k]['accel']])
  PN.addsignal(ylabel = 'track acceleration over ground[m]',xlabel = 'time [s]',*Signals)

  # for future use
  # status
  #Signals = []
  #for k in tracks_to_display:
  #  Signals.append('')
  #  Signals.append([track_list[k]['t'],track_list[k]['status']])
  #PN.addsignal(ylabel = '[status]',*Signals)


  # asso_target_index
  #Signals = []
  #for k in tracks_to_display:
  #  Signals.append('')
  #  Signals.append([track_list[k]['t'],track_list[k]['asso_target_index']])
  #PN.addsignal(ylabel = '[asso_target_index]',*Signals)


  Sync.addClient(PN)
  pass

#==================================================================================
# visual_compare_AC100_LRR3_tracks
#   
#
# arguments: ACC100_track_list (dictionary)
#            LRR3_track_list   (dictionary)
#
# return :   -

def visual_compare_AC100_LRR3_tracks(AC100_track_list,LRR3_track_list,FgNr):


  PN = datavis.cPlotNavigator('Comparison AC100 LRR3', FgNr)

  # internal_track_index

  # dxv
  Signals = []
  Colors = []
  for k in xrange(len(LRR3_track_list)):
    Signals.append('')
    Signals.append([LRR3_track_list[k]['t'],LRR3_track_list[k]['dxv']])
    Colors.append('b')
  for k in xrange(len(AC100_track_list)):
    Signals.append('')
    Signals.append([AC100_track_list[k]['t'],AC100_track_list[k]['range']])
    Colors.append('r')
  PN.addsignal(ylabel = 'dxv [m]',color=Colors,*Signals)


  # dyv
  Signals = []
  Colors = []
  for k in xrange(len(LRR3_track_list)):
    Signals.append('')
    Signals.append([LRR3_track_list[k]['t'],LRR3_track_list[k]['dyv']])
    Colors.append('b')
  for k in xrange(len(AC100_track_list)):
    Signals.append('')
    Signals.append([AC100_track_list[k]['t'],AC100_track_list[k]['dyv']])
    Colors.append('r')
  PN.addsignal(ylabel = 'dyv [m]',color=Colors,*Signals)

  # vxv
  Signals = []
  Colors = []
  for k in xrange(len(LRR3_track_list)):
    Signals.append('')
    Signals.append([LRR3_track_list[k]['t'],LRR3_track_list[k]['vxv']])
    Colors.append('b')
  for k in xrange(len(AC100_track_list)):
    Signals.append('')
    Signals.append([AC100_track_list[k]['t'],AC100_track_list[k]['rel_v']])
    Colors.append('r')
  PN.addsignal(ylabel = 'vxv [m/s]',color=Colors,*Signals)

  # angle
  Signals = []
  Colors = []
  for k in xrange(len(LRR3_track_list)):
    Signals.append('')
    Signals.append([LRR3_track_list[k]['t'],LRR3_track_list[k]['angle']])
    Colors.append('b')
  for k in xrange(len(AC100_track_list)):
    Signals.append('')
    Signals.append([AC100_track_list[k]['t'],AC100_track_list[k]['angle']])
    Colors.append('r')
  PN.addsignal(ylabel = 'angle [m/s]',color=Colors,*Signals)


  Sync.addClient(PN)

  return
  f=pl.figure(1)
  f.suptitle('Comparison AC100 LRR3')
  
  sp=f.add_subplot(311)
  sp.grid()
  for k in xrange(len(AC100_track_list)):
    sp.plot(AC100_track_list[k]['t'],AC100_track_list[k]['range'],'o')
  for k in xrange(len(LRR3_track_list)):
    sp.plot(LRR3_track_list[k]['t'],LRR3_track_list[k]['dxv'])
  sp.set_title('range')

  sp=f.add_subplot(312)
  sp.grid()
  for k in xrange(len(AC100_track_list)):
    sp.plot(AC100_track_list[k]['t'],AC100_track_list[k]['rel_v'],'o')
  for k in xrange(len(LRR3_track_list)):
    sp.plot(LRR3_track_list[k]['t'],LRR3_track_list[k]['vxv'])
  sp.set_title('relative velocity')
  
  sp=f.add_subplot(313)
  sp.grid()
  for k in xrange(len(AC100_track_list)):
    sp.plot(AC100_track_list[k]['t'],AC100_track_list[k]['angle'],'o')
  for k in xrange(len(LRR3_track_list)):
    sp.plot(LRR3_track_list[k]['t'],LRR3_track_list[k]['angle'])
  sp.set_title('angle')

  if 0:
    sp=f.add_subplot(313)
    sp.grid()
    for k in xrange(len(AC100_track_list)):
      sp.plot(AC100_track_list[k]['t'],AC100_track_list[k]['dyv'],'o')
    for k in xrange(len(LRR3_track_list)):
      sp.plot(LRR3_track_list[k]['t'],LRR3_track_list[k]['dyv'])
    sp.set_title('dyv')
  

  f.show()

  pass


#==================================================================================
# associate tracks from AC100 and LRR3

def associate_AC100_LRR3_tracks(AC100_track_list,LRR3_track_list):
  aso_list = []
  
  for k_LRR3 in xrange(len(LRR3_track_list)):
    for k_AC100 in xrange(len(AC100_track_list)):
      LRR3_t_start = LRR3_track_list[k_LRR3]['t'][0] 
      LRR3_t_end   = LRR3_track_list[k_LRR3]['t'][-1]
      AC100_t_start = AC100_track_list[k_AC100]['t'][0] 
      AC100_t_end   = AC100_track_list[k_AC100]['t'][-1]
      cond1 = (LRR3_t_end >= AC100_t_start) or (AC100_t_end >= LRR3_t_start)
      t_start = np.maximum(LRR3_t_start,AC100_t_start)
      t_end   = np.minimum(LRR3_t_end,AC100_t_end)
      cond2 = (t_end - t_start > 1)
      if cond1 and cond2:
        # LRR3
        t = LRR3_track_list[k_LRR3]['t']
        LRR3_idx = ((t >= t_start) & (t <= t_end)).nonzero()
        LRR3_track  = {}
        for key in LRR3_track_list[k_LRR3].keys():
          LRR3_track[key] = LRR3_track_list[k_LRR3][key][LRR3_idx]

        
        # AC100
        t = AC100_track_list[k_AC100]['t']
        AC100_idx = ((t >= t_start) & (t <= t_end)).nonzero()
        AC100_track  = {}
        for key in AC100_track_list[k_AC100].keys():
           AC100_track[key] = AC100_track_list[k_AC100][key][AC100_idx]

        # resample AC100 to LRR3
        t = LRR3_track['t']
        AC100_track2  = {}
        for key in AC100_track.keys():
           AC100_track2[key] = np.interp(t,AC100_track['t'],AC100_track[key])

        z_1 = LRR3_track['dxv']
        z_2 = AC100_track2['range']

        v = z_1 - z_2
        #print ['v = ',v]
        N = len(v)
        d_sqr = np.inner(v,v)
        d_sqr = 1.0/N * np.sqrt(d_sqr)

        print ([k_LRR3,k_AC100,t_start,t_end,d_sqr])

         
        if d_sqr < 0.1:

          aso_list.append({'LRR3':LRR3_track,'AC100':AC100_track2})
        
  return aso_list
    
  pass

#-------------------------------------------------------------------------------------------
def show_aso_list(aso_list,Sync, FgNr,VBOX_slave):

  if 0==len(aso_list):
    return  

  tracks_to_display = xrange(len(aso_list))

  PN = datavis.cPlotNavigator('aso_list', FgNr)

  # dxv
  Signals = []
  Colors = []
  for k in tracks_to_display:
    Signals.append('AC100')
    Signals.append([aso_list[k]['AC100']['t'],aso_list[k]['AC100']['range']])
    Colors.append('r')
    
    Signals.append('LRR3')
    Signals.append([aso_list[k]['LRR3']['t'],aso_list[k]['LRR3']['dxv']])
    Colors.append('b')  
  PN.addsignal(ylabel = 'dxv [m]',color=Colors,*Signals)

  # vxv
  Signals = []
  Colors = []
  for k in tracks_to_display:
    Signals.append('AC100')
    Signals.append([aso_list[k]['AC100']['t'],aso_list[k]['AC100']['rel_v']])
    Colors.append('r')

    Signals.append('LRR3')
    Signals.append([aso_list[k]['LRR3']['t'],aso_list[k]['LRR3']['vxv']])
    Colors.append('b')

  #Signals.append('VBOX')
  #Signals.append([VBOX_slave['t'],VBOX_slave['Velocity_Kmh']])
  #Colors.append('g')

  PN.addsignal(ylabel = 'vxv [m/s]',color=Colors,*Signals)

  # acceleration 
  Signals = []
  Colors = []

  print 'VBOX_slave'
  print VBOX_slave
  
  if VBOX_slave:
    Signals.append('VBOX')
    Signals.append([VBOX_slave['t'],9.81*VBOX_slave['Longitudinal_acceleration']])
    Colors.append('g')

  for k in tracks_to_display:
    Signals.append('AC100')
    Signals.append([aso_list[k]['AC100']['t'],aso_list[k]['AC100']['accel']])
    Colors.append('r')

    Signals.append('LRR3')
    Signals.append([aso_list[k]['LRR3']['t'],aso_list[k]['LRR3']['axv']])
    Colors.append('b')
    

  PN.addsignal(ylabel = 'acceleration [m/s^2]',xlabel = 'time [s]',color=Colors,*Signals)

  # angle
  Signals = []
  Colors = []
  for k in tracks_to_display:
    Signals.append('AC100')
    Signals.append([aso_list[k]['AC100']['t'],aso_list[k]['AC100']['angle']])
    Colors.append('r')

    Signals.append('LRR3')
    Signals.append([aso_list[k]['LRR3']['t'],aso_list[k]['LRR3']['angle']])
    Colors.append('b')
  PN.addsignal(ylabel = 'angle [degree]',xlabel = 'time [s]',color=Colors,*Signals)


  # dyv
  #Signals = []
  #for k in tracks_to_display:
  #  Signals.append('')
  #  Signals.append([aso_list[k]['AC100']['t'],aso_list[k]['AC100']['dyv']])
  #  Signals.append('')
  #  Signals.append([aso_list[k]['LRR3']['t'],aso_list[k]['LRR3']['dyv']])
  #PN.addsignal(ylabel = 'dyv',xlabel = 'time [s]',*Signals)

  Sync.addClient(PN)

  pass

#==================================================================================

def compare_AC100_LRR3_tracks_2(AC100_track_list,LRR3_track_list):

  f=pl.figure(1)
  f.suptitle('Comparison AC100 LRR3')
  
  sp=f.add_subplot(311)
  sp.grid()
  for k in xrange(len(AC100_track_list)):
    sp.plot(AC100_track_list[k]['t'],AC100_track_list[k]['range'],'o')
  for k in xrange(len(LRR3_track_list)):
    sp.plot(LRR3_track_list[k]['t'],LRR3_track_list[k]['dxv'])
  sp.set_title('range')

  sp=f.add_subplot(312)
  sp.grid()
  for k in xrange(len(AC100_track_list)):
    sp.plot(AC100_track_list[k]['t'],AC100_track_list[k]['rel_v'],'o')
  for k in xrange(len(LRR3_track_list)):
    sp.plot(LRR3_track_list[k]['t'],LRR3_track_list[k]['vxv'])
  sp.set_title('relative velocity')
  
  sp=f.add_subplot(313)
  sp.grid()
  for k in xrange(len(AC100_track_list)):
    sp.plot(AC100_track_list[k]['t'],AC100_track_list[k]['angle'],'o')
  for k in xrange(len(LRR3_track_list)):
    sp.plot(LRR3_track_list[k]['t'],LRR3_track_list[k]['angle'])
  sp.set_title('angle')

  if 0:
    sp=f.add_subplot(313)
    sp.grid()
    for k in xrange(len(AC100_track_list)):
      sp.plot(AC100_track_list[k]['t'],AC100_track_list[k]['dyv'],'o')
    for k in xrange(len(LRR3_track_list)):
      sp.plot(LRR3_track_list[k]['t'],LRR3_track_list[k]['dyv'])
    sp.set_title('dyv')
  

  f.show()

  pass

#==================================================================================
# processing sequence

def cmpAC100_LRR3(Sync, Source, FigureNr,Source2):

  par ={}
  par['change_angle_sign'] = 1
  par['select_all'] = 1
  par['only_stationary'] = 0


  # VBOX
  print 'VBOX'
  VBOX_master = extract_VBOX(Source,10,'Master')
  VBOX_slave  = extract_VBOX(Source2,20,'Slave')

  VBOX_slave = sync_VBOX_signals(VBOX_master,VBOX_slave,30)

  cmp_VBOX_signals(VBOX_master,VBOX_slave,40)

  
  # LRR3
  print 'LRR3'

  LRR3_track_list = extract_LRR3_tracks(Source,par)
  print 'len(LRR3_track_list) %d'%len(LRR3_track_list) 
  plot_LRR3_tracks(LRR3_track_list,Sync,100)
 

  # AC100
  print 'AC100'

  AC100_track_list = extract_AC100_tracks(Source,par)
  print 'len(AC100_track_list) %d (raw)'%len(AC100_track_list) 
  AC100_track_list = clean_up_end_AC100_tracks(AC100_track_list)
  plot_AC100_tracks(AC100_track_list,Sync,201)
  AC100_track_list = combine_AC100_tracks(AC100_track_list)
  print 'len(AC100_track_list) %d (combined)'%len(AC100_track_list) 
  plot_AC100_tracks(AC100_track_list,Sync,200)
  #print AC100_track_list

  # visual comparision AC100 and LRR3
  visual_compare_AC100_LRR3_tracks(AC100_track_list,LRR3_track_list,300)

  # association AC100 and LRR3
  if 1:
    aso_list = associate_AC100_LRR3_tracks(AC100_track_list,LRR3_track_list)
    print 'len(aso_list) %d'%len(aso_list)
    for k in xrange(len(aso_list)):
      print aso_list[k]['LRR3']['t'][-1] - aso_list[k]['LRR3']['t'][0]
    show_aso_list(aso_list,Sync, 400,VBOX_slave)



  pass

#==================================================================================

if __name__ == '__main__':
  import aebs.proc
  import datavis
  import sys
  import os
  
  if len(sys.argv) >= 2:
    AviFile = sys.argv[1].lower().replace('.mdf', '.avi')
    Source  = aebs.proc.cLrr3Source('ECU_0_0', sys.argv[1])
    Sync    = datavis.cSynchronizer()    

    if len(sys.argv) == 3:
      Source2 = aebs.proc.cLrr3Source('ECU_0_0', sys.argv[2])
    else:
      Source2 = None

    cmpAC100_LRR3(Sync, Source, 200, Source2)
   
    if os.path.isfile(AviFile):
      Sync.addClient(datavis.cVideoNavigator(AviFile, {}), Source.getSignal('Multimedia_0_0', 'Multimedia_1'))

 
    Sync.run()    
    raw_input("Press Enter to Exit")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
