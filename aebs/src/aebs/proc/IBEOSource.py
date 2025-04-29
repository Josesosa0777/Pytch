import numpy

import measparser
import filters

class cIBEOSource(measparser.cSignalSource):
  def  __init__(self, Measurement):
    self.no_maxObjects=6
    measparser.cSignalSource.__init__(self, Measurement)
  def makepackets(self):

    '''
    making data packets from multiplex message. Packet size depending on total number of Objects for timestep.
    '''
    
    dx = self.getSignal('Ibeo_Contour_header(506)_3_Ibeo','Ibeo_Start_point_x')[1]
    dy = self.getSignal('Ibeo_Contour_header(506)_3_Ibeo','Ibeo_Start_point_y')[1]
    id = self.getSignal('Ibeo_Contour_header(506)_3_Ibeo','Ibeo_Object_ID_C_h')[1]
    number_of_tracks = self.getSignal('Ibeo_List_header(500)_3_Ibeo','Ibeo_Number_of_objects')[1]#actual number of objects for timestep
    classification = self.getSignal('Ibeo_Class_and_box1(504)_3_Ibeo','Ibeo_Object_classification')[1]
    dv = self.getSignal('Ibeo_Tracking1(502)_3_Ibeo','Ibeo_Velocity_x')[1]
    timestamp = self.getSignal('Ibeo_Time_stamp(501)_3_Ibeo','Ibeo_NTP_seconds')[0]
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
        packet["timestamp"]=numpy.zeros(self.no_maxObjects)
        packet["timestamp"].fill(timestamp[actual_packet])
        packet["dx"]=numpy.zeros(self.no_maxObjects)
        packet["dy"]=numpy.zeros(self.no_maxObjects)
        packet["id"]=numpy.zeros(self.no_maxObjects)
        packet["dv"]=numpy.zeros(self.no_maxObjects)
      data.append(packet)
      values_written += number_of_tracks[actual_packet]
    return data #------type<data>==[packet1{"timestamp","dx","dy","id"},packet2{...},...,packet_n{...}]
  
  def maketracks(self, data):
      '''making tracks out of packets. Always self.no_maxObjects objects. If no object detected the track values are 0!
      '''
      
      
      
      data2=[]
      for track_now in xrange(self.no_maxObjects):
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
          except:#not self.no_maxObjects available tracks
            o["timestamp"][packet_now]=data[packet_now]["timestamp"][0]
            o["dx"][packet_now]=0
            o["dy"][packet_now]=0
            o["id"][packet_now]=0
            o["dv"][packet_now]=0
        data2.append(o)
      return data2 #------type<data2>==[track1{"timestamp","dx","dy","id"},track2{...},...,track6{...}]
        
    
  #old one, not up to date or used....
  def sortdata(self, data2):
      '''
      sorting algorithm depending on idea, that object_id is as long as possible on one track if its not lost in between
      
      '''
      potential_IDs_masked1=numpy.zeros(0)
      found_actual_id=0
      potential_ID_track=0
      potential_IDs=numpy.zeros(len(data2))
      for track_now in xrange(len(data2)):
        for i in xrange(1,len(data2[track_now]["timestamp"])):# searching through time
          actual_id=data2[track_now]["id"][i-1]
          found_actual_id=0
          for id_search in xrange(len(data2)):
            if data2[id_search]["id"][i]==actual_id: # id found, so swap or go to next packet
              found_actual_id=1
              if id_search==track_now: #already sorted, all fine
                pass
              else:#switch all values
                tmp_id=data2[track_now]["id"][i]
                tmp_dx=data2[track_now]["dx"][i]
                tmp_dy=data2[track_now]["dy"][i]
                data2[track_now]["id"][i]=data2[id_search]["id"][i]
                data2[track_now]["dx"][i]=data2[id_search]["dx"][i]
                data2[track_now]["dy"][i]=data2[id_search]["dy"][i]
                data2[id_search]["id"][i]=tmp_id
                data2[id_search]["dx"][i]=tmp_dx
                data2[id_search]["dy"][i]=tmp_dy
          if found_actual_id==0:#id not found, so look for other ids not used by other tracks
            for t in xrange(track_now,len(data2)):
              potential_IDs[t]=data2[t]["id"][i]
            already_taken_IDs=[]
            for k in xrange(len(data2)):
              already_taken_IDs.append(data2[k]["id"][i-1])
            for l in xrange(len(already_taken_IDs)):
              for m in xrange(len(potential_IDs)):
                if already_taken_IDs[l]==potential_IDs[m]:
                  potential_IDs[m]=-5
            potential_IDs_masked=potential_IDs[:]
            mask=numpy.logical_and(potential_IDs_masked>-5,potential_IDs_masked>-5)
            potential_IDs_masked=potential_IDs_masked[mask] # delete all -5 ids from potential_IDs_masked
            
            if len(potential_IDs_masked)>0: # find id found to go on with
              for j in xrange(len(data2)):
                if already_taken_IDs[j]==potential_IDs_masked[0]:
                  potential_ID_track=j
                tmp_id=data2[track_now]["id"][i]
                tmp_dx=data2[track_now]["dx"][i]
                tmp_dy=data2[track_now]["dy"][i]
                data2[track_now]["id"][i]=potential_IDs_masked[0]
                data2[track_now]["dx"][i]=data2[potential_ID_track]["dx"][i]
                data2[track_now]["dy"][i]=data2[potential_ID_track]["dy"][i]
                data2[potential_ID_track]["id"][i]=tmp_id
                data2[potential_ID_track]["dx"][i]=tmp_dx
                data2[potential_ID_track]["dy"][i]=tmp_dy
            else: # no new or old id
              pass # perhaps id = -1 so no value.......lets keep it this way
      return data2#------type<data2> look above ("def maketracks")
  
  def smoothdy(self,data2,min_livetime=1, use_pt1=True):
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
          mask for spectific object_id. Each row represents each track. True: object_id on track, False: object_id not on track
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
        if object_id!=0:# object_id 0 is defined as None object. Can occour on several track for 1 timestep
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
                    values.append(data2[track]["dy"][j])#Values in correct timeorder for specific object_id
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
  
  def getsorteddata(self,min_livetime=1,smooth_how_often=1,smooth_dy=True):
      '''
      MAIN METHOD to get IBEO data as list of dicts
      ["dy"] attribute of tracks/objects is smoothed. Results can differ depending on smoothmethod used
      '''

      data=self.makepackets()
      data2=self.maketracks(data)
      if smooth_dy:
        for i in xrange(smooth_how_often):
         self.smoothdy(data2,min_livetime)
      for object in data2:
        object["dx"]=object["dx"]/100-4.95#IBEO value in [cm]----> now [m]# 4.95 offset
        object["dy"]=object["dy"]/100
      return data2
    
    