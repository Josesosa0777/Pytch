"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis
import numpy as np

#---------ESR-------
def viewESR(Sync, Source, FigureNr, start_track=0, end_track=64):
  #-----------------------------------------------------------
  
  '''
  Prints different signals of ESR-Radar for defined tracks
  '''
  """
  :Parameters:
    Sync : <`datavis.cSynchronizer`>
      Synchronizer instance to connect the `datavis.cPlotNavigators`s.
    Source : <`aebs.proc.cLrr3Source`>
      Signal source to get mdf signals.
    FigureNr: <int>
      not used anymore
    start_track: <int>
      tracks to show between interval (start_track,end_track)
    end_track: <int>
  """
  if end_track>64:
    end_track=64
  start_track=start_track
  #print 'showing data for Track %d till %d'%(start_track,end_track)
  
  #-----------------------------------------------------------
  #show range-time plots of tracks
  Source.loadParser()
  PN = datavis.cPlotNavigator('ESR range [s]')
  #print 'Device and value'
  for Idx in xrange(start_track, end_track):
    hv=Idx+1
    if Idx<9:
        hw='0%d'%hv
    else:
        hw='%d'%hv
    Device_ESR_Track, =   Source.Parser.getDeviceNames('CAN_TX_TRACK_RANGE_'+hw)
    #print Device_ESR_Track+' and CAN_TX_TRACK_RANGE_'+hw
    PN.addsignal(Device_ESR_Track, Source.getSignal(Device_ESR_Track,'CAN_TX_TRACK_RANGE_'+hw))
  
  Sync.addClient(PN)
  
  #-----------------------------------------------------------
  #show rangeaccel-time plots of tracks
  
  Source.loadParser()
  PN = datavis.cPlotNavigator('ESR range accel [rel a]')
  #print 'Device and value'
  for Idx in xrange(start_track, end_track):
    hv=Idx+1
    if Idx<9:
        hw='0%d'%hv
    else:
        hw='%d'%hv
    Device_ESR_Track, =   Source.Parser.getDeviceNames('CAN_TX_TRACK_RANGE_ACCEL_'+hw)
    #print Device_ESR_Track+' and CAN_TX_TRACK_RANGE_ACCEL_'+hw
    PN.addsignal(Device_ESR_Track, Source.getSignal(Device_ESR_Track,'CAN_TX_TRACK_RANGE_ACCEL_'+hw))
  
  Sync.addClient(PN)
  
  #-----------------------------------------------------------
  #show angle-time plots of tracks
  Source.loadParser()
  PN = datavis.cPlotNavigator('ESR angle')
  #print 'Device and value'
  for Idx in xrange(start_track, end_track):
    hv=Idx+1
    if Idx<9:
        hw='0%d'%hv
    else:
        hw='%d'%hv
    Device_ESR_Track, =   Source.Parser.getDeviceNames('CAN_TX_TRACK_ANGLE_'+hw)
    #print Device_ESR_Track+' and CAN_TX_TRACK_ANGLE_'+hw
    PN.addsignal(Device_ESR_Track, Source.getSignal(Device_ESR_Track,'CAN_TX_TRACK_ANGLE_'+hw))
  
  Sync.addClient(PN)
  
  #-----------------------------------------------------------
  #show rangerate-time plots of tracks
  Source.loadParser()
  PN = datavis.cPlotNavigator('ESR rangerate [rel v]')
  #print 'Device and value'
  for Idx in xrange(start_track, end_track):
    hv=Idx+1
    if Idx<9:
        hw='0%d'%hv
    else:
        hw='%d'%hv
    Device_ESR_Track, =   Source.Parser.getDeviceNames('CAN_TX_TRACK_RANGE_RATE_'+hw)
    #print Device_ESR_Track+' and CAN_TX_TRACK_RANGE_RATE_'+hw
    PN.addsignal(Device_ESR_Track, Source.getSignal(Device_ESR_Track,'CAN_TX_TRACK_RANGE_RATE_'+hw))
  #Device_ESR_Track, =   Source.Parser.getDeviceNames('CAN_TX_TRACK_RANGE_RATE_25')
  #print Source.getSignal(Device_ESR_Track,'CAN_TX_TRACK_RANGE_RATE_25')
  Sync.addClient(PN)
  
  #----------------------------------------------------------
  #Show intro of ESR

def viewESRIntro(Source):
    time,dx,dy,rangerate,angle=getESRIntrodata(Source)
    PN = datavis.cPlotNavigator('ESR IntroData')
    PN.addsignal('ESR_Intro_dx [m]',(time,dx))
    PN.addsignal('ESR_Intro_dy [m]',(time,dy))
    PN.addsignal('ESR_Intro_rangerate [m/s]',(time,rangerate))
    PN.addsignal('ESR_Intro_angle [degree]',(time,angle))
    Sync.addClient(PN)
  
  
  #---------------------------------------------------------- 

def getESRIntrodata_FCW(Source):
    '''
    returns Forward collision warning Object signals
    '''
    Source.loadParser()
    Device_ESR_Track1, = Source.Parser.getDeviceNames('CAN_TX_PATH_ID_FCW_MOVE')
    time, handle = Source.getSignal(Device_ESR_Track1, 'CAN_TX_PATH_ID_FCW_MOVE')
    n=len(handle)
    signal_dx = np.zeros(n)
    signal_dy = np.zeros(n)
    signal_rangerate = np.zeros(n)
    signal_angle = np.zeros(n)
    
    o={}
    
    for track in xrange(64):
      track+=1
      if track<10:
        hw='0%d'%track
      else:
        hw='%d'%track
      Device_ESR_Track,     = Source.Parser.getDeviceNames('CAN_TX_TRACK_RANGE_'+hw)
      dxi                   = Source.getSignal(Device_ESR_Track,'CAN_TX_TRACK_RANGE_'+hw,ScaleTime=time)[1]
      vxi                   = Source.getSignal(Device_ESR_Track,'CAN_TX_TRACK_RANGE_RATE_'+hw,ScaleTime=time)[1]

      anglei                = Source.getSignal(Device_ESR_Track,'CAN_TX_TRACK_ANGLE_'+hw,ScaleTime=time)[1]
      dxi                   = dxi*np.cos(anglei*(np.pi/180.0))
      dyi                   = -dxi*np.sin(anglei*(np.pi/180.0))
      for i in xrange(n):
          if handle[i]==track and handle[i]!=0:
           signal_rangerate[i]   = vxi[i]
           signal_dx[i]          = dxi[i]
           signal_dy[i]          = dyi[i]
           signal_angle[i]       = anglei[i]
    return time,signal_dx,signal_dy,signal_rangerate,signal_angle
    
  
  #----------------------------------------------------------
  
  
  
if __name__ == '__main__':
  import aebs.proc
  import datavis
  import sys
  import os
  
  if len(sys.argv) > 2:
    if sys.argv[2]=='intro' or 'Intro' or 'i' or 'I':
      showIntro=1
    else:
      start_track=int(sys.argv[2])
      showIntro='no input'
      if len(sys.argv) > 3:
        end_track=int(sys.argv[3])
      else:
        end_track=start_track+5
  else:
    start_track=0
    showIntro='no input'
  
      
  
  if len(sys.argv) > 1:
    AviFile = sys.argv[1].lower().replace('.mdf', '.avi')
    Source  = aebs.proc.cLrr3Source('ECU_0_0', sys.argv[1])
    Sync    = datavis.cSynchronizer()    

    if showIntro:
      viewESRIntro(Source)
    else:
      viewESR(Sync, Source, 200, start_track, end_track)
    
    if os.path.isfile(AviFile):
      Sync.addClient(datavis.cVideoNavigator(AviFile, {}), Source.getSignal('Multimedia_0_0', 'Multimedia_1'))
    
    Sync.run()    
    raw_input("Press Enter to Exit")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
