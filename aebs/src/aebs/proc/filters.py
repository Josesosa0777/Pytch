import copy

import numpy

import measproc
import aebs

'''
Provides several functions to filter sensor data:

  data: <list>
    list of dict
      list items are tracks
      dict with keys: ["dx"],["dy"],["dvx"]...

  delTypesViaTypeHandle: <func>
    deletes all Objects of given status key (e.g. "stationary")
      
  delStationaryObjects: <func>
    deletes all stationary Objects of given data
  
  delShorttimeObject: <func>
    deletes Objects living less than given number of seconds
  
  delLongrangeObjects: <func>
    deletes all Object with range(["dx"]) higher given maxrange
  
  simulateObject_id_Handle: <func>
    simulates Object_id handle for Objects not leaving track for whole livingtime
    ----> saved in data["id"]
  
  filter_0_object_id_AC100: <func>
    makes differences between object_id=0 and none Objects (id is also 0) depending on object_range
    raises object_id by 1

  getstatus: <func>
    returns attribute status as dict, depending on wich signal is available or not
    
  checkstatus: <func>
    :Params:
      status:
        given status where not all available keys must be defined
    :Returns:
      fully status where keys of other sensors are added as 0
    
'''



def delTypesViaTypeHandle(data, del_status_key="stationary", typehandle={"LRR3_FUS":[0,2],"LRR3_ATS":[16,17],"AC100":[5,6],"ESR":[7,8],"VFP":[11,12,13],"IBEO":[10,9],"Iteris":[14],"MobilEye":[15],"stationary":[2,6,8,12,9],"moving":[15,14,10,11,7,0,5],"Intros":[1]}): #tracks in data must be scaled| data as list of tracks from differnt sensors possible
  '''delets objects via type (key:"type" for each track)'''
  
  """
  :Parameters:
  del_status_key: <string>
    types in status for key are deleted in given data
  """
  bantypes=typehandle[del_status_key]
  for track in range(len(data)):
    if isinstance(data[track]["type"],numpy.ndarray):
        for i in xrange(len(data[track]["type"])):
          if data[track]["type"][i] in bantypes:
            for key in data[track].iterkeys():
              if key in ["dx","dy","dvy","dvx"]:
                data[track][key][i]=0


def delStationaryObjects(data):
   print "delStationaryObjects-->start"
   delTypesViaTypeHandle(data, del_status_key = "stationary")
   print "delStationaryObjects-->stop"
   

def filter_0_object_id_AC100(data):
  '''
  #Problem: AC100 object_id is 0 for objects and 0 for "non object"
  #implemented Solution: if range=0 there is no object
  #----> raise id by 1, so min id=1
  #----> if range=0 <-> id=0
  '''
  #--raise id by one
  for track in range(len(data)):#AC100 got object for id=0, but delShorttimeObject is build for id=0=no object
    for i in range(len(data[track]["id"])):
      data[track]["id"][i]+=1
  #--id with no object=0
  for track in range(len(data)):
    data_track=data[track]
    for i in range(len(data_track["id"])):
      if data_track["dx"][i]==0:
        data_track["id"][i]=0
  
def simulateObject_id_Handle(data):
  '''Simulates object_id_handle (based on : objects dont leave tracks for living time....?!?)'''
  """
  :Parameters:
    length_data: int
      number of tracks
    length_status: int
      number of timesteps
    idcontainer: list
      Container with ids already assigned
    temp_idcontainer:
      ids not used anymore but saved and deleted in idcontainer at the
      start of next timestep, to ensure that lost id isn't used for at least 1 timestep
    found: bool
      new id for raising object is found or not
  """
  
  print "simulateObject_id_Handle-->start"
  length_data=len(data)
  length_status=len(data[0]["dx"])
  idcontainer=[]
  idcontainer.append(0)
  temp_idcontainer=[]
  for track in range(length_data):
    data[track]["id"]=numpy.zeros(length_status)
    data[track]["id"].fill(track+1)
    idcontainer.append(track+1)
  for i in range(1,length_status):
    for k in temp_idcontainer:
      idcontainer=filter (lambda i: i != k, idcontainer)
    del temp_idcontainer[:]
    for track in range(length_data):
      status=data[track]["status"][i]
      status_old=data[track]["status"][i-1]
      #--new object raises
      if status!=status_old and status_old==0:
        found=False
        j=1
        while found==False:
          if not j in idcontainer:
            data[track]["id"][i]=j
            idcontainer.append(j)
            found=True
          j+=1
        #--object lost
      elif status!=status_old and status==0:
        data[track]["id"][i]=0
        temp_idcontainer.append(data[track]["id"][i-1])
      else:
        data[track]["id"][i]=data[track]["id"][i-1]
  print "simulateObject_id_Handle-->stop"


  
def delObjectsForPositions(data, key, float, relation):
    """
    data:
      type: list of dicts
         List of Sensor Objects
    key:
      key to search for relation
    float:
      float value for relation where Objects shall be deleted
    relation:
      relation connecting data[i][key] and value
      (see measproc.relations)
    """
    for i in xrange(len(data)):
      mask = relation(data[i][key], float)
      for tmp_key in data[i].iterkeys():
        if tmp_key in ["dx","dy","dv","id"]:
          data[i][tmp_key][mask]=0

def delLongrangeObjects(data, maxrange=80):
    delObjectsForPositions(data, "dx", maxrange, measproc.greater)

    
def delOutOfRectObjects(data, Rect):
    """
    data:
      type: list of objects
    Rect:
      Tuple/List with 2 Points (edges of Rectangle)
      Points: (x,y)  (distance, longitudinal offset)
      eg. ((80,10),(0,-10))
    """
    delObjectsForPositions(data, "dx", max(Rect[0][0],Rect[1][0]), measproc.greater)
    delObjectsForPositions(data, "dx", min(Rect[0][0],Rect[1][0]), measproc.less)
    delObjectsForPositions(data, "dy", max(Rect[0][1],Rect[1][1]), measproc.greater)
    delObjectsForPositions(data, "dy", min(Rect[0][1],Rect[1][1]), measproc.less)

  
  
  
def delShorttimeObject(scaletime,data,minlivetime=2):# scaletime in seconds....
  '''deletes Objects existing less than minlivetime via handle (key:"id" for each track)'''

  """
  :Parameters:
    ##################
    scaletime: <npy.ndarray>
    data: <list>
      list of dicts
    minlivetime: float
      number of seconds object with same object_id must exist on any track
    ##################
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
  print "delShorttimeObject-->start"
  length_id=len(data[0]["id"])
  length_data=len(data)
  handle_ges=numpy.zeros(length_data*length_id)
  for track in xrange(length_data):
    handle_ges[track*length_id:(track+1)*length_id]=data[track]["id"]
  handle_ges=numpy.unique(handle_ges)
  for object_id in handle_ges:
    if object_id!=0:
      mask_tracks=numpy.zeros((length_data,length_id))
      mask_tracks.fill(False)
      mask_all=numpy.zeros(length_id)
      mask_all.fill(False)
      for i in range(length_data):
        mask_tracks[i]=numpy.logical_not(data[i]["id"]!=object_id)
        mask_all=numpy.logical_or(mask_tracks[i],mask_all)
      time_old=scaletime[0]
      timestep_old=0
      for i in range(1,length_id):
        time_new=scaletime[i]
        if mask_all[i]==True and mask_all[i-1]==False:#new object found
          time_old=time_new
          timestep_old=i
        time_delta=time_new-time_old
        if mask_all[i]==False and mask_all[i-1]==True and time_delta<minlivetime:#object lost
          for track in range(length_data):
            for j in range(i-timestep_old):
              if mask_tracks[track][j+timestep_old]==True:
                for key in data[track].iterkeys():
                  if key in ["dx","dy","dvy","dvx","id"]:
                    data[track][key][j+timestep_old]=0
          time_old=time_new
          timestep_old=i
  print "delShorttimeObject-->stop"
        
        
        
def pt1overSteps(value, frac=20): #frac20---> half distance for T20
    """
    :Parameters:
      value: ndarray (or list)
        input array
      frac: fraq of difference added to last timestep
    """
    value_pt1=copy.deepcopy(value)
    for x in xrange(1,len(value)):
      value_pt1[x] = value_pt1[x-1]+(value_pt1[x]-value_pt1[x-1])/frac
    return value_pt1
    
def checklength(ndarray):
   if len(ndarray)<1:
     raise KeyError
  
def getstatus(Source):
  '''checks is data is available and return status as dict'''
  """
  :Parameters:
    status: dict
      status of all Sensors (1: available; 0: not available)
  """
  
  if not aebs.proc.status:
  
      status = aebs.proc.DefStatus
      
      statusSignalsCrossTable = aebs.proc.statusSignalsCrossTable
      
      print '\n###################################################################'
      print '#   Checking available Signals: (\ aebs.proc\ filters.getstatus())\n#'
      for key in statusSignalsCrossTable.iterkeys():
        try:
          checklength(Source.getSignal(*statusSignalsCrossTable[key]))
          print "#    >%s<"%key
        except KeyError:
          status[key] = 0
          print "#    -%s not found (%s,%s)-"%(key,statusSignalsCrossTable[key][0],statusSignalsCrossTable[key][1])
      print '#####################################################################\n'
      aebs.proc.status = status
  
  return aebs.proc.status

def checkstatus(Source, status):
    """
    checks if status contains object requested or not
    
    :Return: status
    """

    status_raw = getstatus(Source)
    for key, value in status_raw.iteritems():
      try:
        status[key]
        if status_raw[key]!=1 and status[key]==1:
          status[key]=0
      except KeyError:
        status[key] = 0

    return status

    
def getStatusByKeyWords(Source, KeyWords=[]):
    status = {}
    status_raw = aebs.proc.DefStatus
    for key in status_raw.iterkeys():
      for KeyWord in KeyWords:
        if KeyWord in key:
          status[key]=status_raw[key]
    status = checkstatus(Source, status)
    return status
    
def getGroups(Source, status):
    """
    returns a default Group setup for given status
    """
    status = checkstatus(Source, status)
    Groups_raw = aebs.proc.DefGroups
    Groups = []
    for key in status.iterkeys():
        if status[key]==1:
          Groups.append(Groups_raw[key])
    for value in aebs.proc.StandartGroups.itervalues():
      Groups.append(value)
    
    return Groups
    
def getTypeAngles(Source, status):
    """
    returns default TypeAngles for given status
    """
    status = checkstatus(Source, status)
    typeangles_raw = copy.deepcopy(aebs.proc.DefTypeAngles)
    for key in status.iterkeys():
        if status[key]!=1:
          del typeangles_raw[key]
    return typeangles_raw
        

