# -*- dataeval: init -*-

import numpy

import interface
import measparser
from aebs.proc import filters

NO_MAX_OBJECTS = 6

# dummy signal group (not used in the fill method)
SignalGroups = [{'ego_velocity':          ('Ibeo_ego_velocity',   'Ibeo_ego_velocity'),
                 'Start_point_x':         ('Ibeo_Contour_header', 'Ibeo_Start_point_x'),
                 'Start_point_y':         ('Ibeo_Contour_header', 'Ibeo_Start_point_y'),
                 'Object_ID_C_h':         ('Ibeo_Contour_header', 'Ibeo_Object_ID_C_h'),
                 'Number_of_objects':     ('Ibeo_List_header',    'Ibeo_Number_of_objects'),
                 'Object_classification': ('Ibeo_Class_and_box1', 'Ibeo_Object_classification'),
                 'Velocity_x':            ('Ibeo_Tracking1',      'Ibeo_Velocity_x'),
                 'NTP_seconds':           ('Ibeo_Time_stamp',     'Ibeo_NTP_seconds')}]

class cFill(interface.iObjectFill):
  def check(self):
    Group = interface.Source.selectSignalGroup(SignalGroups)
    return Group

  def fill(self, Group):
    Signals = measparser.signalgroup.extract_signals(Group)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    objects_IBEO = getsorteddata(Group)
    
    v_ego = interface.Source.getSignalFromSignalGroup(Group, 'ego_velocity', ScaleTime=scaletime)[1]
      
    Objects=[]
    for i, o in enumerate(objects_IBEO):
      keys = o.keys()
      keys.remove('timestamp')
      time = o['timestamp']
      for key in keys:
        value = o[key]
        o[key] = interface.Source.rescale(time, value, scaletime)[1]
      
      stat_mask=numpy.logical_not(abs(o["dv"]+v_ego)>3)
      o["type"] = numpy.where(stat_mask,
                           self.get_grouptype('IBEO_STAT'),
                           self.get_grouptype('IBEO_MOV') )
      
      o["label"]="IBEO_%d"%i
      o["color"]=(0,150,255)
      Objects.append(o)
    return scaletime, Objects

def makepackets(SignalGroup):
  '''
  making data packets from multiplex message. 
  Packet size depending on total number of Objects for timestep.
  '''
  dx = interface.Source.getSignalFromSignalGroup(SignalGroup, 'Start_point_x')[1]
  dy = interface.Source.getSignalFromSignalGroup(SignalGroup, 'Start_point_y')[1]
  id = interface.Source.getSignalFromSignalGroup(SignalGroup, 'Object_ID_C_h')[1]
  #actual number of objects for timestep
  number_of_tracks = interface.Source.getSignalFromSignalGroup(SignalGroup, 'Number_of_objects')[1]
  classification =   interface.Source.getSignalFromSignalGroup(SignalGroup, 'Object_classification')[1]
  dv =               interface.Source.getSignalFromSignalGroup(SignalGroup, 'Velocity_x')[1]
  timestamp =        interface.Source.getSignalFromSignalGroup(SignalGroup, 'NTP_seconds')[0]
  uniqueid = numpy.unique(id)

  values_written=0
  data=[]
  for actual_packet in xrange(len(number_of_tracks)):
    packet={}
    if number_of_tracks[actual_packet]>0:
      packet["timestamp"]=numpy.zeros(number_of_tracks[actual_packet])
      packet["timestamp"].fill(timestamp[actual_packet])
      packet["dx"]=dx[values_written:values_written+number_of_tracks[actual_packet]]
      packet["dy"]=dy[values_written:values_written+number_of_tracks[actual_packet]]
      packet["id"]=id[values_written:values_written+number_of_tracks[actual_packet]]
      packet["dv"]=dv[values_written:values_written+number_of_tracks[actual_packet]]
    else:
      packet["timestamp"]=numpy.zeros(NO_MAX_OBJECTS)
      packet["timestamp"].fill(timestamp[actual_packet])
      packet["dx"]=numpy.zeros(NO_MAX_OBJECTS)
      packet["dy"]=numpy.zeros(NO_MAX_OBJECTS)
      packet["id"]=numpy.zeros(NO_MAX_OBJECTS)
      packet["dv"]=numpy.zeros(NO_MAX_OBJECTS)
    data.append(packet)
    values_written += number_of_tracks[actual_packet]
  return data #------type<data>==[packet1{"timestamp","dx","dy","id"},packet2{...},...,packet_n{...}]

def maketracks(data):
    '''making tracks out of packets. Always NO_MAX_OBJECTS objects. 
    If no object detected the track values are 0!
    '''
    data2=[]
    for track_now in xrange(NO_MAX_OBJECTS):
      o={}
      o["timestamp"]=numpy.zeros(len(data))
      o["dx"]=numpy.zeros(len(data))
      o["dy"]=numpy.zeros(len(data))
      o["id"]=numpy.zeros(len(data))
      o["dv"]=numpy.zeros(len(data))
      for packet_now in xrange(len(data)):
        try:
          o["timestamp"][packet_now]=data[packet_now]["timestamp"][track_now]
          o["dx"][packet_now]=data[packet_now]["dx"][track_now]
          o["dy"][packet_now]=data[packet_now]["dy"][track_now]
          o["id"][packet_now]=data[packet_now]["id"][track_now]
          o["dv"][packet_now]=data[packet_now]["dv"][track_now]
        except:#not NO_MAX_OBJECTS available tracks
          o["timestamp"][packet_now]=data[packet_now]["timestamp"][0]
          o["dx"][packet_now]=0
          o["dy"][packet_now]=0
          o["id"][packet_now]=0
          o["dv"][packet_now]=0
      data2.append(o)
    return data2 #------type<data2>==[track1{"timestamp","dx","dy","id"},track2{...},...,track6{...}]


def smoothdy(data2,min_livetime=1, use_pt1=True):
  '''smoothes dy value of object living for more than minlivetime seconds via object_id_handle'''
  """
  :Parameters:
    #######################################
    min_livetime: float
      minimal seconds object_id must exist
    min_timesteps: int
      number of timesteps for average value
    #######################################
    length_id: int
      number of timesteps
    length_data: int
      number of tracks
    handle_ges: ndarray
      2d array with object_id_handle of each track as rows
    mask_tracks: mask
      mask for spectific object_id. Each row represents each track. 
      True: object_id on track, False: object_id not on track
    mask_all: mask
      projection through all mask_tracks rows
    time_new: float
      actual time of timestep
    time_old: float
      time of timestep when object_id raised
    timestep_old: int
      timestep to time_old
    (i: int
      timestep to time_new)
  """
  min_timesteps=10
  length_id=len(data2[0]["id"])
  length_data=len(data2)
  handle_ges=numpy.zeros(length_data*length_id)
  for track in xrange(length_data):
    handle_ges[track*length_id:(track+1)*length_id]=data2[track]["id"]
  handle_ges=numpy.unique(handle_ges)# unique handles over all tracks
  for object_id in handle_ges:
    # object_id 0 is defined as None object. Can occour on several track for 1 timestep
    if object_id!=0:
      mask_tracks=numpy.zeros((length_data,length_id))
      mask_tracks.fill(False)
      mask_all=numpy.zeros(length_id)
      mask_all.fill(False)
      for track in xrange(length_data):
        mask_tracks[track]=numpy.logical_not(data2[track]["id"]!=object_id)
        mask_all=numpy.logical_or(mask_tracks[track],mask_all)#sum of all mask_tracks rows
      time_old=data2[0]["timestamp"][0]
      timestep_old=0
      for i in xrange(1,length_id):
        time_new=data2[0]["timestamp"][i]
        #--new object found--
        if mask_all[i]==True and mask_all[i-1]==False:
          time_old=time_new
          timestep_old=i
        time_delta=time_new-time_old
        #--object lost--
        if mask_all[i]==False and mask_all[i-1]==True and time_delta>min_livetime and i-timestep_old>min_timesteps:
          values=[]
          #get data for average filtering
          for j in xrange(timestep_old,i):
            for track in xrange(length_data):
              if mask_tracks[track][j]==True:
                #Values in correct timeorder for specific object_id
                values.append(data2[track]["dy"][j])
                break
          #make average values over x timesteps
          if not use_pt1:
              values_copy=values[:]
              for v in xrange(min_timesteps,len(values_copy)):
                values[v]=sum(values_copy[v-min_timesteps:v])/min_timesteps
          else:
              values = filters.pt1overSteps(values, frac=5)
          #write new values
          for j in xrange(timestep_old,i):
            for track in xrange(length_data):
              if mask_tracks[track][j]==True:
                data2[track]["dy"][j]=values[j-timestep_old]
                break
          time_old=time_new
          timestep_old=i

def getsorteddata(SignalGroup, min_livetime=1,smooth_how_often=1,smooth_dy=True):
  '''
  MAIN METHOD to get IBEO data as list of dicts
  ["dy"] attribute of tracks/objects is smoothed. Results can differ depending on smoothmethod used
  '''

  data=makepackets(SignalGroup)
  data2=maketracks(data)
  if smooth_dy:
    for i in xrange(smooth_how_often):
      smoothdy(data2,min_livetime)
  for object in data2:
    object["dx"]=object["dx"]/100-4.95#IBEO value in [cm]----> now [m]# 4.95 offset
    object["dy"]=object["dy"]/100
  return data2
