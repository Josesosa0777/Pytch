import numpy as np

import datavis
import viewAC100
import viewESR

def viewLRR3_AC100_ESR_Intro(Source,showLRR3=1,showAC100=1,showESR=1):
  #-----------add Intros into Plot-----------
  #------------------------------------------
  #--loadAC100IntroData
  if showAC100:
    time_AC100,signal_dx_AC100,signal_dy_AC100,signal_rangerate_AC100,signal_angle_AC100=viewAC100.getAC100Introdata(Source)
  if showESR:
    time_ESR,signal_dx_ESR,signal_dy_ESR,signal_rangerate_ESR,signal_angle_ESR=viewESR.getESRIntrodata_FCW(Source)
    signal_dy_ESR=-signal_dy_ESR
  if showLRR3:
    time_LRR3, o_LRR3=viewFUSoverlayLRR3_AC100_ESR.indicateIntro(Source,0)
    time_LRR3, o_LRR3["vx"] = viewFUSoverlayLRR3_AC100_ESR.calcByHandle(Source, 'vxv')
    time_LRR3, o_LRR3["vy"] = viewFUSoverlayLRR3_AC100_ESR.calcByHandle(Source, 'vyv')
    time_LRR3, o_LRR3["angle"] = viewFUSoverlayLRR3_AC100_ESR.calcByHandle(Source, 'alpPiYawAngle')
    o_LRR3["angle"]=180/np.pi*o_LRR3["angle"]
    o_LRR3["angle"]=-o_LRR3["angle"]
    o_LRR3["dy"]=-o_LRR3["dy"]
  
  PN = datavis.cPlotNavigator('LRR3_AC100_ESR IntroDatas(dx,dy)')
  if showAC100==1 and showESR==1 and showLRR3==1:
    PN.addsignal('AC100_Intro_dx [m]',(time_AC100,signal_dx_AC100),'ESR_Intro_dx [m]',(time_ESR,signal_dx_ESR),'LRR3_Intro_dx [m]',(time_LRR3,o_LRR3["dx"]),ylabel='[m]',xlabel='[s]',color=['black','y','pink'])
    PN.addsignal('AC100_Intro_dy [m]',(time_AC100,signal_dy_AC100),'ESR_Intro_dy [m]',(time_ESR,signal_dy_ESR),'LRR3_Intro_dy [m]',(time_LRR3,o_LRR3["dy"]),color=['black','y','pink'])
    Sync.addClient(PN)
    PN = datavis.cPlotNavigator('LRR3_AC100_ESR IntroDatas(range,angle)')
    PN.addsignal('AC100_Intro_rangerate [m/s]',(time_AC100,signal_rangerate_AC100),'ESR_Intro_rangerate [m/s]',(time_ESR,signal_rangerate_ESR),'LRR3_Intro_rangerate [m/s]',(time_LRR3,o_LRR3["vx"]),color=['black','y','pink'])
    PN.addsignal('AC100_Intro_angle [degree]',(time_AC100,signal_angle_AC100),'ESR_Intro_angle [degree]',(time_ESR,signal_angle_ESR),'LRR3_Intro_angle [degree]',(time_LRR3,o_LRR3["angle"]),color=['black','y','pink'])
    Sync.addClient(PN)
  elif showAC100==1 and showESR==1 and showLRR3==0:
    PN.addsignal('AC100_Intro_dx [m]',(time_AC100,signal_dx_AC100),'ESR_Intro_dx [m]',(time_ESR,signal_dx_ESR),ylabel='[m]',xlabel='[s]',color=['black','y'])
    PN.addsignal('AC100_Intro_dy [m]',(time_AC100,signal_dy_AC100),'ESR_Intro_dy [m]',(time_ESR,signal_dy_ESR),color=['black','y'])
    Sync.addClient(PN)
    PN = datavis.cPlotNavigator('LRR3_AC100_ESR IntroDatas(range,angle)')
    PN.addsignal('AC100_Intro_rangerate [m/s]',(time_AC100,signal_rangerate_AC100),'ESR_Intro_rangerate [m/s]',(time_ESR,signal_rangerate_ESR),color=['black','y'])
    PN.addsignal('AC100_Intro_angle [degree]',(time_AC100,signal_angle_AC100),'ESR_Intro_angle [degree]',(time_ESR,signal_angle_ESR),color=['black','y'])
    Sync.addClient(PN)
  elif showLRR3==1 and showESR==1 and showAC100==0:
    PN.addsignal('ESR_Intro_dx [m]',(time_ESR,signal_dx_ESR),ylabel='[m]',xlabel='[s]',color=['y','pink'])
    PN.addsignal('ESR_Intro_dy [m]',(time_ESR,signal_dy_ESR),color=['y','pink'])
    Sync.addClient(PN)
    PN = datavis.cPlotNavigator('LRR3_AC100_ESR IntroDatas(range,angle)')
    PN.addsignal('ESR_Intro_rangerate [m/s]',(time_ESR,signal_rangerate_ESR),color=['y','pink'])
    PN.addsignal('ESR_Intro_angle [degree]',(time_ESR,signal_angle_ESR),color=['y','pink'])
    Sync.addClient(PN)
  elif showLRR3==1 and showAC100==0 and showESR==0:
    PN.addsignal('LRR3_Intro_dx [m]',(time_LRR3,o_LRR3["dx"]),ylabel='[m]',xlabel='[s]',color=['pink'])
    PN.addsignal('LRR3_Intro_dy [m]',(time_LRR3,o_LRR3["dy"]),color=['pink'])
    Sync.addClient(PN)
    PN = datavis.cPlotNavigator('LRR3_AC100_ESR IntroDatas(range,angle)')
    PN.addsignal('LRR3_Intro_rangerate [m/s]',(time_LRR3,o_LRR3["vx"]),color=['pink'])
    PN.addsignal('LRR3_Intro_angle [degree]',(time_LRR3,o_LRR3["angle"]),color=['pink'])
    Sync.addClient(PN)
  else:
    print 'no plot found, watch in def viewLRR3_AC100_ESR_Intro'
  #--------add Intros into Video---------
  #--------------------------------------
  viewFUSoverlayLRR3_AC100_ESR.viewFUSoverlay(Sync, Source, AviFile,showLRR3,showAC100,showESR)
  #------------debug---------
  if 0:
    print object1,object2,object3
  
  
  
  
  pass

  
if __name__=='__main__':
  import aebs.proc
  import datavis
  import sys
  import viewAC100
  import viewESR
  import viewFUSoverlayLRR3_AC100_ESR
  import numpy as np
  
  if len(sys.argv) > 1:
    AviFile = sys.argv[1].lower().replace('.mdf', '.avi')
    Source  = aebs.proc.cLrr3Source(sys.argv[1], ECU='ECU_0_0')
    Sync    = datavis.cSynchronizer()
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
    #if os.path.isfile(AviFile):
      #Sync.addClient(datavis.cVideoNavigator(AviFile), Source.getSignal('Multimedia_0_0', 'Multimedia_1'))
  try:
    showLRR3=1
    test = Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.ObjectList.i0')[0]
    print '-----LRR3 exists------'
    if len(sys.argv) > 2:
      showLRR3=int(sys.argv[2])
  except:
    print '------------------------no LRR3 FUS data?????-------------------------'
    showLRR3=0

  try:
    showAC100=1
    Source.loadParser()
    Device_Track,     =  Source.Parser.getDeviceNames('tr0_range')
    test = Source.getSignal(Device_Track,'tr0_range')[0]
    print '-----AC100 exists------'
    if len(sys.argv) > 3:
      showAC100=int(sys.argv[3])
  except:
    print '------------------------no AC100 data?????-------------------------'
    showAC100=0

  try:
    showESR=1
    Source.loadParser()
    Device_ESR_Track,     = Source.Parser.getDeviceNames('CAN_TX_TRACK_RANGE_01')
    test                  = Source.getSignal(Device_ESR_Track,'CAN_TX_TRACK_RANGE_01')[0]
    print '-----ESR exists------'
    if len(sys.argv) > 4:
      showESR=int(sys.argv[4])
  except:
    print '------------------------no ESR data?????-------------------------'
    showESR=0
  
  viewLRR3_AC100_ESR_Intro(Source,showLRR3,showAC100,showESR)



  Sync.run()    
  raw_input("Press Enter to Exit")
  Sync.close()
      
  
###An viewESR.py orientieren!!! Mit sys.argv=intro zum starten der Intros aller Sensoren