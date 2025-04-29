import copy

import numpy

import viewFUSoverlayLRR3_AC100_ESR
import aebs.proc

def assosiate(reference_sensor_data, sensor_data, sensor_data_name,scaletime,delta_v_half=5,rectangle_width_half=6,rectangle_depth_half=3,start_index=0,stop_index=0):
  '''
  creating new referenced objects from sensor_data objects for assosiation to reference sensor objects
  number of returned referenced objects = number of reference objects
  !!arrays must have same length!!(must be scaled before)
  '''
  
  """
    :Parameters:
      reference_sensor_data: <list>
        list of objects/tracks from reference sensor as dict: {["dx"]:...,["dy"]:... etc}
      sensor_data: <list>
        list of objects/tracks from sensor as dict: {["dx"]:...,["dy"]:... etc}
      sensor_data_name: <string>
        Name used for ["label"] of returned referenced objects
      scaletime: <npy.ndarray>
      rectangle_width_half: <float>
        maximum offset of assosiated IBEO object in positive/negative y-direction to LRR3_ATS0 object [m]
      rectangle_depth_half: <float>
        maximum offset of assosiated IBEO object in positive/negative x-direction to LRR3_ATS0 object [m]
      delta_v_half: <float>
        maximum difference of assosiated IBEO object speed to LRR3_ATS0 object [m/s]
      start_index: <int>
        start index of Interval to reference based on scaletime
      stop_index: <int>
        stop index of Interval to reference based on scaletime
  """
  
  
  
  
  key_v_ref=""
  try:
    reference_sensor_data[0]["dv"]
    key_v_ref="dv"
  except KeyError:
    pass
  try:
    reference_sensor_data[0]["dvx"]
    key_v_ref="dvx"
  except KeyError:
    pass
    
  key_v=""
  try:
    sensor_data[0]["dv"]
    key_v="dv"
  except KeyError:
    pass
  try:
    sensor_data[0]["dvx"]
    key_v="dvx"
  except KeyError:
    pass
  
  banned_keys = ["label", "color", "type"]
  
  #if start and stop index given---->del rest
  if start_index!=0 or stop_index!=0:
    sensor_data=copy.deepcopy(sensor_data)
    reference_sensor_data=copy.deepcopy(reference_sensor_data)
    for track in xrange(len(reference_sensor_data)):
      for key in reference_sensor_data[track].keys():
        if not key in banned_keys:
          reference_sensor_data[track][key]=reference_sensor_data[track][key][start_index:stop_index]
    for track in xrange(len(sensor_data)):
      for key in sensor_data[track].keys():
        if not key in banned_keys:
          sensor_data[track][key]=sensor_data[track][key][start_index:stop_index]
  
  
  print "assosiate--->start"
  
  len_signal=len(reference_sensor_data[0]["dx"])
  len_tracks_ref=len(reference_sensor_data)
  len_tracks=len(sensor_data)
  referenced_data=[]
  
  for track_ref in xrange(len_tracks_ref):
      o={}
      o["dx"]=numpy.zeros(len_signal)
      o["dy"]=numpy.zeros(len_signal)
      o["id"]=numpy.zeros(len_signal)
      o["dv"]=numpy.zeros(len_signal)
      o["id_reference"]=numpy.zeros(len_signal)
      o["hit_ratio"]=numpy.zeros(len_signal)
      o["average_delta_x"]=numpy.zeros(len_signal)
      o["delta_x"]=numpy.zeros(len_signal)
      o["average_delta_y"]=numpy.zeros(len_signal)
      o["delta_y"]=numpy.zeros(len_signal)
      o["delta_v"]=numpy.zeros(len_signal)
      fault_dv=numpy.zeros((len_tracks,len_signal))#(zeile,spalte)
      fault_dx=numpy.zeros((len_tracks,len_signal))
      fault_dy=numpy.zeros((len_tracks,len_signal))
      time_hit=0.
      time_hit_ref=0.
      average_delta_x=0.
      average_delta_y=0.
      
      for track in xrange(len_tracks):
        #print len(fault_dv[track]),len(reference_sensor_data[track_ref]["vrel"]),len(sensor_data[track]["dvx"])
        #print type(fault_dv[track]),type(reference_sensor_data[track_ref]["vrel"]),type(sensor_data[track]["dvx"])
        fault_dv[track]=reference_sensor_data[track_ref][key_v_ref]-sensor_data[track][key_v]
        fault_dx[track]=reference_sensor_data[track_ref]["dx"]-sensor_data[track]["dx"]
        fault_dy[track]=-(reference_sensor_data[track_ref]["dy"]-sensor_data[track]["dy"])
      #pylab.imshow(abs(fault_dx))
      #pylab.show()
      for i in xrange(1,len_signal):
        index=numpy.argmin(abs(fault_dv[:,i]**2+fault_dx[:,i]**2+fault_dy[:,i]**2))
        #print index
        value_dv=abs(fault_dv[index,i])
        value_dx=abs(fault_dx[index,i])
        value_dy=abs(fault_dy[index,i])
        if value_dv<delta_v_half and value_dx<rectangle_depth_half and value_dy<rectangle_width_half:
          o["dx"][i]=sensor_data[index]["dx"][i]
          o["dy"][i]=sensor_data[index]["dy"][i]
          o["id"][i]=sensor_data[index]["id"][i]
          o["id_reference"][i]=reference_sensor_data[track_ref]["id"][i]
          o["dv"][i]=sensor_data[index]["id"][i]
          #o["dv"][i]=reference_sensor_data[track_ref][key_v_ref][i]
          
          time_delta=scaletime[i]+scaletime[i-1]
          time_hit+=time_delta
          time_hit_ref+=time_delta
          
          average_delta_x+=time_delta*fault_dx[index][i]
          average_delta_y+=time_delta*fault_dy[index][i]
          o["delta_x"][i] = fault_dx[index][i]
          o["delta_y"][i] = fault_dy[index][i]
          o["delta_v"][i] = fault_dv[index][i]
          
        else:
          if reference_sensor_data[track_ref][key_v_ref][i]!=0:
            time_delta=scaletime[i]+scaletime[i-1]
            time_hit_ref+=time_delta
        if time_hit_ref>0:
          o["hit_ratio"][i]=float(time_hit/time_hit_ref)
        if time_hit>0:
          o["average_delta_x"][i]=float(average_delta_x/time_hit)
        if time_hit>0:
          o["average_delta_y"][i]=float(average_delta_y/time_hit)
        
      o["type"]=15
      o["color"]=(50,50,50)
      o["label"]="%s_referenced_%d"%(sensor_data_name,track_ref)
      referenced_data.append(o)
      
      #print "\n"+str(o["label"])+"---hitratio_%d:"%track_ref+str(o["hit_ratio"][len(o["hit_ratio"])-1])
      #print str(o["label"])+"---average_delta_x_%d:"%track_ref+str(o["average_delta_x"][len(o["average_delta_x"])-1])
      #print str(o["label"])+"---average_delta_y_%d:"%track_ref+str(o["average_delta_y"][len(o["average_delta_y"])-1])
      
  print "assosiate--->stop"
  return referenced_data, reference_sensor_data
      
    
      
def calcSensorPerformance(Source,reference_status_key='IBEO',status_key='LRR3_ATS',minlivetime=1.5,rectangle_width_half=3,delta_v_half=1,rectangle_depth_half=1.5, Rect=None, delstationaryObjects=True):
    '''
    Compares Performance of 2 Sensors. IBEO lidar should be reference.
    '''
    """
    :Parameters:
      Source : <`aebs.proc.cLrr3Source`>
      minlivetime: <float>
        Minimum livetime of sensor object_id in seconds
      rect_width_half: <float>
        maximum offset of referenced object in positive/negative y-direction to LRR3_ATS0 object [m]
      rect_depth_half: <float>
        maximum offset of referenced object in positive/negative x-direction to LRR3_ATS0 object [m]
      delta_v_half: <float>
        maximum difference of referenced object speed to sensor object [m/s]
      maxrange: <float>
        maximum distance of sensor object to ego vehicle [m]
    """
    
    #minlivetime,rect_width_half,delta_v_half,v_ego_min,rect_depth_half,maxrange,kritvalue=checkforxml()
    #print minlivetime,rect_width_half,delta_v_half,v_ego_min,rect_depth_half,maxrange,kritvalue
    
    status = aebs.proc.filters.getstatus(Source)
    data_available=True
    
    if status[status_key]!=1:
      data_available=False
    elif status[reference_status_key]!=1:
      data_available=False
    
    if data_available:
    
        data={}
        for key in status.iterkeys():
          status[key]=0
        status[status_key]=1
        scaletime, data[status_key]=viewFUSoverlayLRR3_AC100_ESR.fillObjects(Source,**status)
        status[status_key]=0
        status[reference_status_key]=1
        scaletime, data[reference_status_key]=viewFUSoverlayLRR3_AC100_ESR.fillObjects(Source,scaletime=scaletime,**status)

        # Device_Tracks,     =  Source.Parser.getDeviceNames('vsp.vxvRefRaw')
        # time_v_ego,v       = Source.getSignal(Device_Tracks,('vsp.vxvRefRaw'))
        # scaletime, v       = measproc.cSignalSource.rescale(time_v_ego,v,scaletime)
        # Device_Tracks,     =  Source.Parser.getDeviceNames('vsp.vxvRef')
        # time_v_ego,v       = Source.getSignal(Device_Tracks,('vsp.vxvRef'))
        # scaletime, v       = measproc.cSignalSource.rescale(time_v_ego,v,scaletime)

        if delstationaryObjects:
          aebs.proc.filters.delStationaryObjects(data[status_key])
          aebs.proc.filters.delStationaryObjects(data[reference_status_key])
        
        if minlivetime>0:
          aebs.proc.filters.delShorttimeObject(scaletime,data[status_key],minlivetime)
          #aebs.proc.filters.delShorttimeObject(scaletime,data[reference_status_key],minlivetime)
        
        if Rect!=None:
          aebs.proc.filters.delOutOfRectObjects(data[status_key],Rect=Rect)
          aebs.proc.filters.delOutOfRectObjects(data[reference_status_key],Rect=Rect)
          
        referenced_data, reference_sensor_data = assosiate(data[reference_status_key], data[status_key], status_key, scaletime, delta_v_half=delta_v_half, rectangle_width_half=rectangle_width_half, rectangle_depth_half=rectangle_depth_half)
    
        return scaletime, referenced_data, data[reference_status_key], data[status_key]
    else:
      return None

      
def splitAssosiatedObjects(scaletime, referenced_data, reference_data, sensor_data):
    
    
    ####################
    ## reference_data ##
    ####################
    referenced_data_id_key="id_reference"
    
    maxgap = 3
    
    len_scaletime = len(scaletime)
    len_referenced_data = len(referenced_data)
    len_reference_data = len(reference_data)
    
    ids = numpy.zeros((len_scaletime, len_referenced_data))
    for track in xrange(len_referenced_data):
      ids[:,track] = referenced_data[track][referenced_data_id_key]
    ids_unique = numpy.unique(ids)
    len_ids_unique = len(ids_unique)
    # ids_hit_reference: matrix to represent if object for id in timestep is already calculated or not.
    ids_hit_reference = numpy.zeros((len_scaletime, len_ids_unique))
    
    # Create new_data_reference for standalone new objects
    new_data_reference=[]
    for x in xrange(len_reference_data):
      o={}
      o["dx"] = numpy.zeros(len_scaletime)
      o["dy"] = numpy.zeros(len_scaletime)
      o["dv"] = numpy.zeros(len_scaletime)
      o["id"] = numpy.zeros(len_scaletime)
      o["id_reference"] = numpy.zeros(len_scaletime)
      new_data_reference.append(o)
    
    
    id_index=-1
    for id in ids_unique:
      if id!=0:
        id_index+=1
        for referenced_track in referenced_data:
          for x in xrange(len_scaletime):
            actual_id = referenced_track[referenced_data_id_key][x]
            if id == actual_id:
              other_id = referenced_track["id"][x]
              if ids_hit_reference[x, id_index]==0:
                  start_index = x
                  #found same id
                  #now search id in reference_data, forward
                  actual_track = 0
                  stepsgap = 0
                  for i in xrange(x, len_scaletime):
                    found = False
                    if reference_data[actual_track]["id"][i] == id:
                      stepsgap = 0
                      found = True
                    else:
                      for track in xrange(len_reference_data):
                        if reference_data[track]["id"][i] == id:
                          actual_track = track
                          stepsgap = 0
                          found = True
                          break
                    if not found:
                      stepsgap +=1
                      if stepsgap >= maxgap:
                        break
                    #save the results
                    new_data_reference[actual_track]["id_reference"][i] = id
                    new_data_reference[actual_track]["id"][i] = other_id
                    new_data_reference[actual_track]["dx"][i] = reference_data[actual_track]["dx"][i]
                    new_data_reference[actual_track]["dy"][i] = reference_data[actual_track]["dy"][i]
                    new_data_reference[actual_track]["dv"][i] = reference_data[actual_track]["dv"][i]
                    ids_hit_reference[i, id_index] = 1
                    
                  #backward
                  stepsgap = 0
                  actual_track=0
                  i = x
                  while i!=0:
                    i-=1
                    found = False
                    if reference_data[actual_track]["id"][i] == id:
                      stepsgap = 0
                      found = True
                    else:
                      for track in xrange(len_reference_data):
                        if reference_data[track]["id"][i] == id:
                          actual_track = track
                          stepsgap = 0
                          found = True
                          break
                    if not found:
                      stepsgap +=1
                      if stepsgap >= maxgap:
                        break
                    #save the results
                    new_data_reference[actual_track]["id_reference"][i] = id
                    new_data_reference[actual_track]["id"][i] = other_id
                    new_data_reference[actual_track]["dx"][i] = reference_data[actual_track]["dx"][i]
                    new_data_reference[actual_track]["dy"][i] = reference_data[actual_track]["dy"][i]
                    new_data_reference[actual_track]["dv"][i] = reference_data[actual_track]["dv"][i]
                    ids_hit_reference[i, id_index] = 1
                    
    for object in new_data_reference:
      object["type"]=16
      object["color"]=(0,0,255)
      object["label"]="Asso_IBEO"


    ####################
    ##   sensor_data  ##
    ####################
    referenced_data_id_key="id"
    
    maxgap = 3
    
    len_scaletime = len(scaletime)
    len_referenced_data = len(referenced_data)
    len_sensor_data = len(sensor_data)
    
    ids = numpy.zeros((len_scaletime, len_referenced_data))
    for track in xrange(len_referenced_data):
      ids[:,track] = referenced_data[track][referenced_data_id_key]
    ids_unique = numpy.unique(ids)
    len_ids_unique = len(ids_unique)
    # ids_hit: matrix to represent if object for id in timestep is already calculated or not.
    ids_hit = numpy.zeros((len_scaletime, len_ids_unique))
    
    # Create new_data for standalone new objects
    new_data=[]
    for x in xrange(len_sensor_data):
      o={}
      o["dx"] = numpy.zeros(len_scaletime)
      o["dy"] = numpy.zeros(len_scaletime)
      o["dv"] = numpy.zeros(len_scaletime)
      o["id"] = numpy.zeros(len_scaletime)
      new_data.append(o)
    
    
    id_index=-1
    for id in ids_unique:
      if id!=0:
        id_index+=1
        for referenced_track in referenced_data:
          for x in xrange(len_scaletime):
            actual_id = referenced_track[referenced_data_id_key][x]
            if id == actual_id:
              if ids_hit[x, id_index]==0:
                  start_index = x
                  #found same id
                  #now search id in sensor_data, forward
                  actual_track = 0
                  stepsgap = 0
                  for i in xrange(x, len_scaletime):
                    found = False
                    if sensor_data[actual_track]["id"][i] == id:
                      stepsgap = 0
                      found = True
                    else:
                      for track in xrange(len_sensor_data):
                        if sensor_data[track]["id"][i] == id:
                          actual_track = track
                          stepsgap = 0
                          found = True
                          break
                    if not found:
                      stepsgap +=1
                      if stepsgap >= maxgap:
                        break
                    #save the results
                    new_data[actual_track]["id"][i] = id
                    new_data[actual_track]["dx"][i] = sensor_data[actual_track]["dx"][i]
                    new_data[actual_track]["dy"][i] = sensor_data[actual_track]["dy"][i]
                    new_data[actual_track]["dv"][i] = sensor_data[actual_track]["dv"][i]
                    ids_hit[i, id_index] = 1
                    
                  #backward
                  stepsgap = 0
                  actual_track=0
                  i = x
                  while i!=0:
                    i-=1
                    found = False
                    if sensor_data[actual_track]["id"][i] == id:
                      stepsgap = 0
                      found = True
                    else:
                      for track in xrange(len_sensor_data):
                        if sensor_data[track]["id"][i] == id:
                          actual_track = track
                          stepsgap = 0
                          found = True
                          break
                    if not found:
                      stepsgap +=1
                      if stepsgap >= maxgap:
                        break
                    #save the results
                    new_data[actual_track]["id"][i] = id
                    new_data[actual_track]["dx"][i] = sensor_data[actual_track]["dx"][i]
                    new_data[actual_track]["dy"][i] = sensor_data[actual_track]["dy"][i]
                    new_data[actual_track]["dv"][i] = sensor_data[actual_track]["dv"][i]
                    ids_hit[i, id_index] = 1
                    
    for object in new_data:
      object["type"]=16
      object["color"]=(255,0,0)
      object["label"]="Asso_CVR3_FUS"
    
    return new_data, new_data_reference
                  
                        
                        
                        
                    
      
        


# def splitAssosiatedObjects(scaletime, referenced_data, sensor_data, referenced_data_id_key="id"):
    
    # len_scaletime = len(scaletime)
    # len_referenced_data = len(referenced_data)
    # ids = numpy.zeros((len_scaletime, len_referenced_data))
    # for track in xrange(len_referenced_data):
      # ids[:,track] = referenced_data[track][referenced_data_id_key]
    # ids_unique = numpy.unique(ids)
    # len_ids_unique = len(ids_unique)
    # # ids_hit: matrix to represent if object for id in timestep is already calculated or not.
    # ids_hit = numpy.zeros((len_scaletime, len_ids_unique))
    
    # # create copy of referenced_data to save result_objectlist as standalone data.
    # new_data = copy.deepcopy(referenced_data)
    
    # id_index=-1
    # for id in ids_unique:
      # id_index+=1
      # print id_index, id
      # for referenced_track in referenced_data:
        # for x in xrange(len_scaletime):
          # if ids_hit[x, id_index]==0:
            # if referenced_track[referenced_data_id_key][x]==id:
              # # id gefunden: Jetzt Suche vorwearts!
              # ids_hit[x, id_index] == 1
              # for i in xrange(x+1, len_scaletime):
                # found = False
                # ids_hit[i, id_index] == 1
                # start_index = -1
                
                # # 1: Suche in referenced_data:
                # for track in referenced_data:
                  # if track[referenced_data_id_key][i]==id:
                  
                    # if start_index==-1:
                      # start_index = i
                      
                    # found = True
                    
                # if not found:
                  # # 2: Suche in sensor_data
                  # for track in sensor_data:
                    # if track["id"][i] == id:
                    
                      # if start_index==-1:
                        # start_index = i
                        
                      # found = True
                      # end_index = i
                      # for track_new_data in new_data:
                        # if track_new_data["dx"][i]==0:
                          # for key in track.iterkeys():
                            # if key in ["dx","dy","dv","id"]:
                              # # new_data beschreiben
                              # track_new_data[key][i] = track[key][i]
                # if not found:
                  # break
    # return new_data
                  
              
    
    
      
      
      

      
    
            
          


if __name__=="__main__":
  
  import time
  import sys
  import os
  import aebs.proc
  import datavis
  
  starting_time=time.time()
  if len(sys.argv) > 1:
    MeasFile   = sys.argv[1]
    Head, Tail = os.path.splitext(sys.argv[1])
    AviFile  = Head + '.avi'
    # Data source
    Source = aebs.proc.cLrr3Source(MeasFile, ECU='ECU_0_0')
    # Synchronizer for visualization  
    Sync = datavis.cSynchronizer()
  
  
    Groups=[]
    '''type: list
    '''
    Groups.append(['stationary', [2,6,8,12,9,17], '0', False])
    Groups.append(['moving', [15,14,10,11,7,0,5], '9', True])
    Groups.append(['Intros', [1], 'I', False])
    Groups.append(['LRR3_FUS', [0,2], '1', False])
    Groups.append(['AC100', [5,6], '2', False])
    Groups.append(['ESR', [7,8], '3', False])
    Groups.append(['IBEO', [10,9], '4', False])
    Groups.append(['VFP', [11,12,13], '5', False])
    Groups.append(['Iteris', [14], '6', False])
    Groups.append(['MobilEye', [15], '7', False])
    Groups.append(['LRR3_ATS', [16,17], '8', False])
  
  
  
    scaletime, data=aebs.proc.filters.getdata(Source)
    aebs.proc.filters.simulateObject_id_Handle(data["ESR"])
    aebs.proc.filters.delStationaryObjects(data["LRR3_FUS"])
    aebs.proc.filters.delStationaryObjects(data["AC100"])
    #aebs.proc.filters.delStationaryObjects(data["ESR"])
    #aebs.proc.filters.delStationaryObjects(data["IBEO"])
    aebs.proc.filters.filter_0_object_id_AC100(data["AC100"])
    aebs.proc.filters.delShorttimeObject(scaletime,data["LRR3_FUS"])
    aebs.proc.filters.delShorttimeObject(scaletime,data["AC100"])
    #aebs.proc.filters.delShorttimeObject(scaletime,data["ESR"])
    #aebs.proc.filters.delShorttimeObject(scaletime,data["IBEO"])
    data_of_referenced_sensor, data_of_reference_sensor=assosiate(data["LRR3_ATS"],data["AC100"],"AC100",scaletime)
  
    objects=[]
    
    signals_x=[]
    signals_y=[]
    for o in data_of_reference_sensor:
      objects.append(o)
      signals_x.append("%s_dx_reference"%o["label"])
      signals_x.append((scaletime,o["dx"]))
      signals_y.append("%s_dy_reference"%o["label"])
      signals_y.append((scaletime,o["dy"]))
    
    PN=datavis.cPlotNavigator("reference_sensor")
    PN.addsignal(*signals_x)
    PN.addsignal(*signals_y)
    Sync.addClient(PN)
    
    
    signals_x=[]
    signals_y=[]
    PN=datavis.cPlotNavigator("referenced_sensor_ratio_average")
    for o in data_of_referenced_sensor:
      objects.append(o)
      signals_x.append("%s_dx_referenced"%o["label"])
      signals_x.append((scaletime,o["dx"]))
      signals_y.append("%s_dy_referenced"%o["label"])
      signals_y.append((scaletime,o["dy"]))
      signal_ratio=[]
      signal_ratio.append("%s_hit_ratio"%o["label"])
      signal_ratio.append((scaletime,o["hit_ratio"]))
      signal_ratio.append("%s_average_delta_x"%o["label"])
      signal_ratio.append((scaletime,o["average_delta_x"]))
      signal_ratio.append("%s_average_delta_y"%o["label"])
      signal_ratio.append((scaletime,o["average_delta_y"]))
      PN.addsignal(*signal_ratio)
    Sync.addClient(PN)
    
    PN=datavis.cPlotNavigator("referenced_sensor")
    PN.addsignal(*signals_x)
    PN.addsignal(*signals_y)
    Sync.addClient(PN)
    
    
    
    
    #signals_x=[]
    #signals_y=[]
    
    #for o in data["LRR3_FUS"]:
    #  signals_x.append("dx")
    #  signals_x.append((scaletime,o["dx"]))
    #  signals_y.append("dy")
    #  signals_y.append((scaletime,o["dy"]))
    #  
    #PN=datavis.cPlotNavigator("before")
    #PN.addsignal(*signals_x)
    #PN.addsignal(*signals_y)
    #Sync.addClient(PN)
      
      
  
    VN = datavis.cVideoNavigator(AviFile, {})
    #VN.addGroups(Groups)
    vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1', ScaleTime=scaletime)[1]
    accel = Source.getSignalFromECU('evi.General_TC.axvRef', ScaleTime=scaletime)[1]
    VN.setobjects(objects, vidtime, accel / 50.)
    Sync.addClient(VN,(scaletime,vidtime))
  
  
    
    Sync.run()
    ending_time=time.time()
    print "***LOADING TIME: %d seconds***"%(ending_time-starting_time)
    raw_input("Press Enter to Exit\r\n")
    Sync.close()
  
  
  
  
