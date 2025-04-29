def viewTracksLRR3_AC100_ESR(Sync, Source, FgNr, MeasFile='', **status):
  '''
  Visualize mdf File with Videooverlay and Birdview
  '''
  """
  :Parameters:
    Sync : <`datavis.cSynchronizer`>
    Source : <`aebs.proc.cLrr3Source`>
    FgNr : <int>
      FigureNumber of the Tracknavigator instance
    MeasFile : <str>
      Path of the MDF-File
    status: <dict>
      dictionary of available/requested sensors
      {"LRR3_FUS":0/1,"LRR3_ATS":0/1,"AC100":0/1,"ESR":0/1,"IBEO":0/1,"Iteris":0/1,"VFP":0/1,"MobilEye":0/1}
  """
  
  import os

  import numpy as np

  import datavis
  import viewFUSoverlayLRR3_AC100_ESR
  import measproc
  import aebs.proc

  if MeasFile:
    MainTitle = '%s' %os.path.basename(MeasFile)
  else:
    MainTitle = 'Tracks AC100'
    
  TN = datavis.cTrackNavigator(MainTitle, FgNr)
  TN.setLegend(aebs.proc.DefLegend)

  scaletime, Objects = viewFUSoverlayLRR3_AC100_ESR.fillObjects(Source,**status)
  #----------------------
  #filling objectlist with objects of requested sensors   #scaletime, Objects = viewFUSoverlayLRR3_AC100_ESR.fillObjects(Source,**status)
  print 'TN--->fillObjects completed'

  #----------------------
  #Add IntroObjects / scaletime from "fillObjects"-method
  print 'adding Intro Objects'#
  if status["LRR3_FUS"]:
      Time_LRR3, Intro_LRR3 = viewFUSoverlayLRR3_AC100_ESR.indicateIntro(Source)
      scaletime, Intro_LRR3["dx"] = measparser.cSignalSource.rescale(Time_LRR3,Intro_LRR3["dx"],scaletime)
      scaletime, Intro_LRR3["dy"] = measparser.cSignalSource.rescale(Time_LRR3,Intro_LRR3["dy"],scaletime)
      Objects.append(Intro_LRR3)
      #print Intro
      print 'LRR3 Intro Object added'
  if status["AC100"]:
      Time_AC100, Intro_AC100 = viewFUSoverlayLRR3_AC100_ESR.indicateIntro(Source,1)
      scaletime, Intro_AC100["dx"] = measparser.cSignalSource.rescale(Time_AC100,Intro_AC100["dx"],scaletime)
      scaletime, Intro_AC100["dy"] = measparser.cSignalSource.rescale(Time_AC100,Intro_AC100["dy"],scaletime)
      Objects.append(Intro_AC100)
      print 'AC100 Intro Object added'
  if status["ESR"]:
      Time_ESR,Intro_ESR = viewFUSoverlayLRR3_AC100_ESR.indicateIntro(Source,2)
      scaletime, Intro_ESR["dx"] = measparser.cSignalSource.rescale(Time_ESR,Intro_ESR["dx"],scaletime)
      scaletime, Intro_ESR["dy"] = measparser.cSignalSource.rescale(Time_ESR,Intro_ESR["dy"],scaletime)
      Objects.append(Intro_ESR)
      print 'ESR Intro Object added'

  for Object in xrange(len(Objects)):
    TN.addObject(scaletime, Objects[Object]) #each Object seperatly added to TN
  


  
  # if status["CVR3_FUS"]:
        # Time, ROADRSOEgoLaneLeftPolyA0        = Source.getSignal('MRR1plus_0_0', 'padsit_x_par_a.PCCCROADRSOEgoLaneLeftPolyA0',        ScaleTime=scaletime)
        # Time, ROADRSOEgoLaneRightPolyA0       = Source.getSignal('MRR1plus_0_0', 'padsit_x_par_a.PCCCROADRSOEgoLaneRightPolyA0',       ScaleTime=scaletime)
        # Time, ROADRSORightLaneLeftPolyA0      = Source.getSignal('MRR1plus_0_0', 'padsit_x_par_a.PCCCROADRSORightLaneLeftPolyA0',      ScaleTime=scaletime)
        # Time, ROADRSOLeftLaneRightPolyA0      = Source.getSignal('MRR1plus_0_0', 'padsit_x_par_a.PCCCROADRSOLeftLaneRightPolyA0',      ScaleTime=scaletime)
        # Time, ROADRSOUncorrRightLaneLeftPolyA = Source.getSignal('MRR1plus_0_0', 'padsit_x_par_a.PCCCROADRSOUncorrRightLaneLeftPolyA0', ScaleTime=scaletime)
        # Time, ROADRSOUncorrLeftLaneRightPolyA = Source.getSignal('MRR1plus_0_0', 'padsit_x_par_a.PCCCROADRSOUncorrLeftLaneRightPolyA0', ScaleTime=scaletime)
      
        # Time, kapCurvTraj                     = Source.getSignal('MRR1plus_0_0','evi.MovementData_T20.kapCurvTraj',ScaleTime=scaletime)
        # Time, kapCurvTraj2                     = Source.getSignal('MRR1plus_0_0','dcp.kapCourse',ScaleTime=scaletime)
        
        # kapCurvTraj=-kapCurvTraj
      
        # R2 = 1.0 / kapCurvTraj2
        # R = -1.0 / kapCurvTraj
      
        # TN.addTrack(TN.circle, Time, R2, ROADRSOEgoLaneLeftPolyA0,        color='c')
        # TN.addTrack(TN.circle, Time, R2, ROADRSOEgoLaneRightPolyA0,       color='c')
      
        # TN.addTrack(TN.circle, Time, R, ROADRSOEgoLaneLeftPolyA0,        color='b')
        # TN.addTrack(TN.circle, Time, R, ROADRSOEgoLaneRightPolyA0,       color='b')
        # TN.addTrack(TN.circle, Time, R, ROADRSORightLaneLeftPolyA0,      color='r')
        # TN.addTrack(TN.circle, Time, R, ROADRSOLeftLaneRightPolyA0,      color='r')
        # TN.addTrack(TN.circle, Time, R, ROADRSOUncorrRightLaneLeftPolyA, color='g')
        # TN.addTrack(TN.circle, Time, R, ROADRSOUncorrLeftLaneRightPolyA, color='g')
  
  
  
  # elif status["LRR3_FUS"]:
      # Time, ROADRSOEgoLaneLeftPolyA0        = Source.getSignal('ECU_0_0', 'padsit_par_a.ROADRSOEgoLaneLeftPolyA0',        ScaleTime=scaletime)
      # Time, ROADRSOEgoLaneRightPolyA0       = Source.getSignal('ECU_0_0', 'padsit_par_a.ROADRSOEgoLaneRightPolyA0',       ScaleTime=scaletime)
      # Time, ROADRSORightLaneLeftPolyA0      = Source.getSignal('ECU_0_0', 'padsit_par_a.ROADRSORightLaneLeftPolyA0',      ScaleTime=scaletime)
      # Time, ROADRSOLeftLaneRightPolyA0      = Source.getSignal('ECU_0_0', 'padsit_par_a.ROADRSOLeftLaneRightPolyA0',      ScaleTime=scaletime)
      # Time, ROADRSOUncorrRightLaneLeftPolyA = Source.getSignal('ECU_0_0', 'padsit_par_a.ROADRSOUncorrRightLaneLeftPolyA', ScaleTime=scaletime)
      # Time, ROADRSOUncorrLeftLaneRightPolyA = Source.getSignal('ECU_0_0', 'padsit_par_a.ROADRSOUncorrLeftLaneRightPolyA', ScaleTime=scaletime)
      
      # Time, kapCurvTraj                     = Source.getSignal('ECU_0_0','evi.MovementData_T20.kapCurvTraj',ScaleTime=scaletime)
      # Time, kapCurvTraj2                     = Source.getSignal('ECU_0_0','dcp.kapCourse',ScaleTime=scaletime)
    
      # kapCurvTraj=-kapCurvTraj
      
      # R2 = 1.0 / kapCurvTraj2
      # R = -1.0 / kapCurvTraj
      
      # TN.addTrack(TN.circle, Time, R2, ROADRSOEgoLaneLeftPolyA0,        color='c')
      # TN.addTrack(TN.circle, Time, R2, ROADRSOEgoLaneRightPolyA0,       color='c')
      
      # TN.addTrack(TN.circle, Time, R, ROADRSOEgoLaneLeftPolyA0,        color='b')
      # TN.addTrack(TN.circle, Time, R, ROADRSOEgoLaneRightPolyA0,       color='b')
      # TN.addTrack(TN.circle, Time, R, ROADRSORightLaneLeftPolyA0,      color='r')
      # TN.addTrack(TN.circle, Time, R, ROADRSOLeftLaneRightPolyA0,      color='r')
      # TN.addTrack(TN.circle, Time, R, ROADRSOUncorrRightLaneLeftPolyA, color='g')
      # TN.addTrack(TN.circle, Time, R, ROADRSOUncorrLeftLaneRightPolyA, color='g')
  
  else:
    pass

    
  print 'Tracks added to TN'
  
  # Add field of view
  Y = np.array([0,20,30,100,160,160,100,30,20,0])
  X = np.array([0,12.256,10.8,15.8,17.66,-17.66,-15.8,-10.8,-12.256,0])
  TN.addFOV(X,Y,color=(0,0,0),linestyle='-')
  # Add horizontal lines
  Y = np.array([20,20])
  X = np.array([-50,50])
  TN.addFOV(X,Y,color=(0,0,0),linestyle=':')
  Y = np.array([160,160])
  X = np.array([-50,50])
  TN.addFOV(X,Y,color=(0,0,0),linestyle=':')
  Y = np.array([100,100])
  X = np.array([-50,50])
  TN.addFOV(X,Y,color=(0,0,0),linestyle=':')
  Y = np.array([30,30])
  X = np.array([-50,50])
  TN.addFOV(X,Y,color=(0,0,0),linestyle=':')
  
  
  print 'TN--->Intros added'
  Sync.addClient(TN)
  print 'TN added to Sync'
  return TN, scaletime, Objects# Return for overlay Function, otherwise def fillintro will be executed 2 times
  
  
  

def info(object, spacing=10, collapse=1):
    """Print methods and doc strings.
    Takes module, class, list, dictionary, or string."""
    
    methodList = [method for method in dir(object) if callable(getattr(object, method))]
    processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
    print "\n".join(["%s %s" %
                      (method.ljust(spacing),
                       processFunc(str(getattr(object, method).__doc__)))
                     for method in methodList])
  

  
  
if __name__ == '__main__':
  import sys
  import os
  import time
  import xml.dom.minidom

  import datavis
  import aebs.proc
  import viewFUSoverlayLRR3_AC100_ESR
  import measproc
  import measparser
  
  starting_time=time.time()

  # status  = {"LRR3_FUS":1,"LRR3_ATS":1,"AC100":1,"ESR":1,"IBEO":1,"Iteris":1,"VFP":1,"MobilEye":1}
  """
  type: dict
    dict representing if Sensor data is available or not: 0 or 1
  """
  
  # ConfigFile=os.path.join(os.curdir,"view_config.xml")
  # if os.path.exists(ConfigFile):
        # Config = xml.dom.minidom.parse(ConfigFile)
        # Directories, = Config.getElementsByTagName('Params')
        # for key in status.iterkeys():
          # try:
            # status[key]=int(Directories.getAttribute('%s_%s'%("viewTracksLRR3_AC100_ESR.py", key)))
          # except ValueError:
            # pass

  
  if len(sys.argv) > 1:
    MdfFile = sys.argv[1]
  else:
    MdfFile = r'D:\Measuremets\mdf\sensor_benchmark_H05.2604_2010-07-15_11-26_05.MDF'
    sys.stderr.write('Default mesurement file is used: %s\n' %MdfFile)
  
  
  
  AviFile = MdfFile.lower().replace('.mdf', '.avi')
  Sync    = datavis.cSynchronizer()
  Source  = aebs.proc.cLrr3Source(MdfFile, ECU='ECU_0_0')
  
  
  #---------------------------------------
  #check for available Sensor data
  #---------------------------------------
  status={"CVR3_ATS":1,"CVR3_FUS":1,"IBEO":1,"CVR3_LOC":1,"CVR3_POS":1,"CVR3_OHL":1}
  status = aebs.proc.filters.checkstatus(Source, status)
  #status = aebs.proc.filters.getstatus(Source)
  Groups = aebs.proc.filters.getGroups(Source, status)
  typeangles = aebs.proc.filters.getTypeAngles(Source, status)
  
  
  

  TN, scaletime, Objects=viewTracksLRR3_AC100_ESR(Sync, Source, 100, MdfFile, **status)
  for key in typeangles.iterkeys():
    if status[key]==1:
      TN.setViewAngle(-typeangles[key][0],typeangles[key][0],facecolor = typeangles[key][1],alpha = typeangles[key][2],GroupName = key)
  TN.addGroups(Groups)
  TN.fig.canvas.manager.window.geometry('400x800-10+0')
  TN.fig.axes[0].set_axis_bgcolor((0.92,0.92,0.92))
  print 'viewTracksLRR3_AC100_ESR method done'


  if os.path.exists(AviFile):
    try:
      VN = viewFUSoverlayLRR3_AC100_ESR.viewFUSoverlay(Sync, Source, AviFile,scaletime,Objects,**status)
      VN.addGroups(Groups)
    except NameError:
      VN = viewFUSoverlayLRR3_AC100_ESR.viewFUSoverlay(Sync, Source, AviFile,**status)
  try:
    Sync.connect('selectGroup', VN, TN)
  except NameError:
    print"not possible to connect ""select Group""-method of VN and TN"
  
  if 0:
      #-------------------
      #---marks debugging
      status2={"CVR3_FUS":1}
      status2 = aebs.proc.filters.checkstatus(Source, status2)
      scaletime, location_objects = viewFUSoverlayLRR3_AC100_ESR.fillObjects(Source, scaletime=scaletime, **status2)
      keys=["dx","dy","dv","axv","ayv","DriveInvDir_b","Drive_b","NotClassified_b","Stand_b","StoppedInvDir_b","Stopped_b","wObstacle","wGroundReflex","wExistProbBase"]
      index = [5,17,24,6,13,23,28]
      
      
      
      for x in index:
        LN = datavis.cListNavigator("LRR3_FUS_%d"%x)
        for key in keys:
          LN.addsignal("%s_%d"%(key, x),(scaletime, location_objects[x][key]))
        Sync.addClient(LN)
      
      
      PN = datavis.cPlotNavigator("Plot",333)
      signals_dx=[]
      for x in xrange(len(location_objects)):
        signals_dx.append("LRR3_FUS_%d"%x)
        signals_dx.append((scaletime, location_objects[x]["dx"]))
      color2=[]
      for x in xrange(len(location_objects)):
        color2.append('.')
      PN.addsignal(color = color2, *signals_dx)
      Sync.addClient(PN)
      
      PN = datavis.cPlotNavigator("Plot",334)
      location=[]
      for x in xrange(len(location_objects)):
        location.append("LRR3_FUS_%d"%x)
        location.append((location_objects[x]["dy"][location_objects[x]["type"]==0], location_objects[x]["dx"][location_objects[x]["type"]==0]))
      color2=[]
      for x in xrange(len(location_objects)):
        color2.append('.')
      PN.addsignal(color = color2, *location)
      Sync.addClient(PN)
      
        
        
      #ego motion
      #------------
      LN = datavis.cListNavigator("ego motion")
      LN.addsignal("vxvRef",Source.getSignal("MRR1plus_0_0","evi.General_T20.vxvRef"))
      LN.addsignal("axvRef",Source.getSignal("MRR1plus_0_0","evi.General_T20.axvRef"))
      Sync.addClient(LN)
      #------------
      #-------------------
    
    
  
  Sync.run()
  ending_time=time.time()
  print "***LOADING TIME: %d seconds***"%(ending_time-starting_time)
  raw_input("Press Enter to Exit\n")
  Sync.close()
