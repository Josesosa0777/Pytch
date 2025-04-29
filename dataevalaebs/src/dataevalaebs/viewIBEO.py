"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import copy

import numpy

import datavis
import aebs.proc

#---------IBEO-------
def viewIBEO(Source):
  '''
  views specific IBEO data in PN
  '''
  PN = datavis.cPlotNavigator('IBEO dx [cm]')
  objects = getsorteddata(Source)
  for o in objects:
    o["color"]=(0,0,0)
    o["type"]=3
    o["label"]='ibeo'
    PN.addsignal("IBEO", (o["timestamp"],o["dx"]))
  Sync.addClient(PN)
  
  PN = datavis.cPlotNavigator('IBEO dy [cm]')
  for o in objects:
    PN.addsignal("IBEO", (o["timestamp"],o["dy"]))
  Sync.addClient(PN)

  PN = datavis.cPlotNavigator('IBEO timestamp [ms]')
  for o in objects:
    PN.addsignal("IBEO", (o["timestamp"],o["timestamp"]))
  Sync.addClient(PN)
  
  PN = datavis.cPlotNavigator('IBEO id')
  for o in objects:
    PN.addsignal("IBEO", (o["timestamp"],o["id"]))
  Sync.addClient(PN)

  
  
def viewFUSoverlayIBEO(Source,AviFile):
  '''
  view IBEO data with Videooverlay
  '''
  objects=getsorteddata(Source)
  time=objects[0]["timestamp"]
  vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1',ScaleTime=time)[1]
  j=0
  for o in objects:
    j+=1
    o["color"]=(0,150,255)
    o["type"]=10
    o["label"]='IBEO_%d'%j

  VN = datavis.cVideoNavigator(AviFile, {})
  accel = Source.getSignalFromECU('evi.General_TC.axvRef', ScaleTime=time)[1]
  VN.setobjects(objects, vidtime, accel / 50.)
  Sync.addClient(VN,(time,vidtime))
  #print o["dx"]
  #print o["timestamp"]
  #print vidtime
  #print 'VN added to Sync'
  
  
  
  
def printsorteddata(Source):

  data=makepackets(Source)
  printdata(data)
  print '------------------------------End: makepackets---------------------------'
  data2=maketracks(data)
  printdata2(data2)
  print '------------------------------End: maketracks---------------------------'
  data2=sortdata(data2)
  print '------------------------------End: sortdata---------------------------'
  printdata2(data2)
  
  
  
  
  
def getsorteddata(Source,min_livetime=1,smooth_how_often=1,smooth_dy=True):
  '''
  MAIN METHOD to get IBEO data as list of dicts
  ["dy"] attribute of tracks/objects is smoothed. Results can differ depending on smoothmethod used
  '''

  data=makepackets(Source)
  #printdata(data)
  #print '------------------------------End: makepackets---------------------------'
  data2=maketracks(data,Source)
  #printdata2(data2)
  #print '------------------------------End: maketracks---------------------------'
  ##sortdata(data2)
  #print '------------------------------End: sortdata---------------------------'
  if smooth_dy:
    for i in xrange(smooth_how_often):
     smoothdy(data2,min_livetime)
  for object in data2:
    object["dx"]=object["dx"]/100-4.95#IBEO value in [cm]----> now [m]# 4.95 offset
    object["dy"]=object["dy"]/100
  return data2
  
#---------
def makepackets(Source):

    '''
    making data packets from multiplex message. Packet size depending on total number of Objects for timestep.
    '''
    no_maxObjects=6
    
    Source.loadParser()
    Device_Track, = Source.Parser.getDeviceNames('Ibeo_Start_point_x')
    dx = Source.getSignal(Device_Track,'Ibeo_Start_point_x')[1]
    dy = Source.getSignal(Device_Track,'Ibeo_Start_point_y')[1]
    id = Source.getSignal(Device_Track,'Ibeo_Object_ID_C_h')[1]
    Device_Track,= Source.Parser.getDeviceNames('Ibeo_Number_of_objects')
    number_of_tracks = Source.getSignal(Device_Track,'Ibeo_Number_of_objects')[1]#actual number of objects for timestep
    Device_Track,= Source.Parser.getDeviceNames('Ibeo_Object_classification')
    classification = Source.getSignal(Device_Track,'Ibeo_Object_classification')[1]
    Device_Track,= Source.Parser.getDeviceNames('Ibeo_Velocity_x')
    dv = Source.getSignal(Device_Track,'Ibeo_Velocity_x')[1]
    Device_Track,= Source.Parser.getDeviceNames('Ibeo_NTP_seconds')
    timestamp = Source.getSignal(Device_Track,'Ibeo_NTP_seconds')[0]
    #timestamp=numpy.zeros(len(timestamp_sec),dtype=float)
    #timestamp=timestamp_sec+timestamp_frac/4294967296.
    #print timestamp
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
        packet["timestamp"]=numpy.zeros(no_maxObjects)
        packet["timestamp"].fill(timestamp[actual_packet])
        packet["dx"]=numpy.zeros(no_maxObjects)
        packet["dy"]=numpy.zeros(no_maxObjects)
        packet["id"]=numpy.zeros(no_maxObjects)
        packet["dv"]=numpy.zeros(no_maxObjects)
      data.append(packet)
      values_written += number_of_tracks[actual_packet]
    return data #------type<data>==[packet1{"timestamp","dx","dy","id"},packet2{...},...,packet_n{...}]

      
def printdata(data):
    for track_now in xrange(6):
      for packet_now in xrange(len(data)):
        try:
          print 'packet: %d/%d'%(packet_now/len(data))
          print 'track%d:  '%track_now+'  dx:  '+str(data[packet_now]["dx"][track_now])+'  dy:  '+str(data[packet_now]["dy"][track_now])+'  timestamp:  '+str(data[packet_now]["timestamp"][track_now])+'  id:  '+str(data[packet_now]["id"][track_now])
        except:
          pass
      print '\n'
    print'------------'
    

    

    
    
def printdata2(data2):
  for track_now in xrange(len(data2)):
    for i in xrange(len(data2[track_now]["timestamp"])):
      try:
        print 'track%d'%track_now+'  dx:  '+str(data2[track_now]["dx"][i])+'  dy:  '+str(data2[track_now]["dy"][i])+'  timestamp:  '+str(data2[track_now]["timestamp"][i])+'  id:  '+str(data2[track_now]["id"][i])
      except:
        pass
    print '\n'
  print'-----------'
    
def maketracks(data,Source):
  '''making tracks out of packets. Always 6 objects. If no object detected the track values are 0!
  '''
  
  
  no_maxObjects=6
  
  data2=[]
  for track_now in xrange(no_maxObjects):
    o={}
    o["timestamp"]=numpy.zeros(len(data))
    o["dx"]=numpy.zeros(len(data))
    o["dy"]=numpy.zeros(len(data))
    o["id"]=numpy.zeros(len(data))
    o["dv"]=numpy.zeros(len(data))
    for packet_now in xrange(len(data)):
      #print len(data)
      #print packet_now
      try:
        o["timestamp"][packet_now]=data[packet_now]["timestamp"][track_now]
        o["dx"][packet_now]=data[packet_now]["dx"][track_now]
        o["dy"][packet_now]=data[packet_now]["dy"][track_now]
        o["id"][packet_now]=data[packet_now]["id"][track_now]
        o["dv"][packet_now]=data[packet_now]["dv"][track_now]
        #print 'packet added to track%d'%track_now
      except:#not no_maxObjects available tracks
        o["timestamp"][packet_now]=data[packet_now]["timestamp"][0]
        o["dx"][packet_now]=0
        o["dy"][packet_now]=0
        o["id"][packet_now]=0
        o["dv"][packet_now]=0
        #print ' 0 packet added to track%d'%track_now
    data2.append(o)
  #print 'tracks unsorted ready'
  return data2 #------type<data2>==[track1{"timestamp","dx","dy","id"},track2{...},...,track6{...}]
    
    
#old one, not up to date or used....
def sortdata(data2):
  '''
  sorting algorithm depending on idea, that object_id is as long as possible on one track if its not lost in between
  
  '''
  potential_IDs_masked1=numpy.zeros(0)
  found_actual_id=0
  potential_ID_track=0
  potential_IDs=numpy.zeros(len(data2))
  for track_now in xrange(len(data2)):
    #print 'sorting track%d'%track_now
    for i in xrange(1,len(data2[track_now]["timestamp"])):# searching through time
      #print'     %d'%i
      actual_id=data2[track_now]["id"][i-1]
      #print actual_id
      found_actual_id=0
      for id_search in xrange(len(data2)):
        #print '              search for id in track%d'%id_search
        if data2[id_search]["id"][i]==actual_id: # id found, so swap or go to next packet
          found_actual_id=1
          #print '---ID still exists---'
          if id_search==track_now: #already sorted, all fine
            #print '<<same track'
            pass
          else:#switch all values
            #print '>>other track------->switching'
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
        #print '---ID does not exist, searching new one---'
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
        #print 'already_taken_IDs:   '+str(already_taken_IDs)
        #print 'potential_Ids:   '+str(potential_Ids)
        mask=numpy.logical_and(potential_IDs_masked>-5,potential_IDs_masked>-5)
        #print mask
        potential_IDs_masked=potential_IDs_masked[mask] # delete all -5 ids from potential_IDs_masked
        
        #print 'potential_IDs_masked:    '+str(potential_IDs_masked)
        if len(potential_IDs_masked)>0: # find id found to go on with
          for j in xrange(len(data2)):
            #print j
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
    
def tripelsortdata(data2):#experimental
  sortdata(data2)
  sortdata(data2)
  sortdata(data2)

def endlessort(data2):#experimental
  #run till data=new data
  i=0
  old=0
  while old==0:
    i+=1
    print "IBEO sort: %d"%i
    old_data=data2[:]
    sortdata(data2)
    if old_data is data2:
      old=1
  
  
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
  print "IBEO-smoothdy via object_id_handle--->start"
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
              values = aebs.proc.filters.pt1overSteps(values, frac=5)
          #write new values
          for j in xrange(timestep_old,i):
            for track in xrange(length_data):
              if mask_tracks[track][j]==True:
                data2[track]["dy"][j]=values[j-timestep_old]
                break
          time_old=time_new
          timestep_old=i
  print "IBEO-smoothdy via object_id_handle--->stop"
  
  
  
def smoothdy2(data2,midfrom_x_timesteps=10):#simple average filter
  #filter over x timesteps-->midfrom_x_timesteps
  '''making average value over x timesteps if id is constant for track
  not searching for object_id over several tracks if lost
  '''
  """
  :Parameters:
    midfrom_x_timesteps: int
      number of timesteps to smooth over
    test_id: int
      test_id==0: id not constant for last x timesteps
      test_id==1: id id constant for last x timesteps
    sum: float
      sum over the last x values
  """
  data3=copy.deepcopy(data2)
  if midfrom_x_timesteps<3:
     midfrom_x_timesteps=3
  for o in xrange(len(data3)):
    for i in xrange(midfrom_x_timesteps,len(data3[o]["timestamp"])):
      test_id = 1
      for j in xrange(midfrom_x_timesteps-1):
        if data3[o]["id"][i-j]!=data3[o]["id"][i-j-1]:
          test_id = 0
      if test_id!=0 and ((data3[o]["dx"][i]-data3[o]["dx"][i-1])-(data3[o]["dx"][i-1]-data3[o]["dx"][i-2])>100 or (data3[o]["dx"][i]-data3[o]["dx"][i-1])-(data3[o]["dx"][i-1]-data3[o]["dx"][i-2])<200):#distance in cm...
        sum=0
        for j in xrange(midfrom_x_timesteps):
          sum += data3[o]["dy"][i-j]
        data2[o]["dy"][i]=sum/midfrom_x_timesteps
  
  
if __name__ == '__main__':
  import aebs.proc
  import datavis
  import sys
  
  if len(sys.argv) > 1:
    AviFile = sys.argv[1].lower().replace('.mdf', '.avi')
    Source  = aebs.proc.cLrr3Source(sys.argv[1], ECU='ECU_0_0')
    Sync    = datavis.cSynchronizer()  
    show_only_print=0
    if len(sys.argv)>2:
      if str(sys.argv[2])=='p':
        show_only_print=1
    
    if show_only_print==0:
      viewFUSoverlayIBEO(Source,AviFile)
      viewIBEO(Source)
    else:
      printsorteddata(Source)
      
    Sync.run()    
    raw_input("Press Enter to Exit")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
