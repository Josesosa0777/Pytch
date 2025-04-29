import datavis
import measparser
import interface
import numpy as np

DefParam = interface.NullParam

SignalGroups = [{"front_axle_speed": ("EBC2-98FEBF0B", "front_axle_speed"),
                 "Longitudinal_Acceleration": ("VDC2-98F0093E", "Longitudinal_Acceleration"),
                 "Ext_Acceleration_Demand": ("XBR-8C040B2A", "Ext_Acceleration_Demand"),
                 "XBR_Control_Mode": ("XBR-8C040B2A", "XBR_Control_Mode"),
                 "BrakePedalPosition": ("EBC1", "BrakePedalPosition"),},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      #parameters
      XBR_max_dec_check1 = -3.0
      XBR_max_dec_check2 = -4.5
      XBR_max_speed_reduction = 20.0 / 3.6 
      XBR_t_max_check = 2.0
      print "XBR_max_dec_check1 = %f m/ss" % (XBR_max_dec_check1)
      print "XBR_max_dec_check2 = %f m/ss" % (XBR_max_dec_check2)
      print "XBR_max_speed_reduction = %f km/h" % (XBR_max_speed_reduction * 3.6) 
      print "XBR_t_max_check = %f s" % (XBR_t_max_check)
      #get signals from CAN messages
      tEBC2, vFroAxSpd = interface.Source.getSignalFromSignalGroup(Group, "front_axle_speed")
      tVDC2, vLonAccel = interface.Source.getSignalFromSignalGroup(Group, "Longitudinal_Acceleration")
      tXBR, vExtAccDem = interface.Source.getSignalFromSignalGroup(Group, "Ext_Acceleration_Demand")
      Time, vConMode = interface.Source.getSignalFromSignalGroup(Group, "XBR_Control_Mode")
      tEBC1, vBPPos = interface.Source.getSignalFromSignalGroup(Group, "BrakePedalPosition")
      #initial values
      taskCycle = 0.02        #algorithm cycle time to make it independent from CAN repetition rate
      actDemand = False       #actual demand
      lastDemand = False      #demand from last cycle
      spdRed = 0              #cumulated speed reduction
      initAcc = 0.0           #initial acceleration
      checkRunning = False    #flag for algorithm running or not
      #200ms long ring buffer for longitudinal acceleration
      cbAccLen = int(.2 / taskCycle + .5)  #buffer lenght                    
      cbAcc = np.zeros(cbAccLen)           #buffer 
      icbAcc = 0                           #buffer pointer
      #initialize output signals  
      tTask = np.arange(tVDC2[0], tVDC2[-1], taskCycle)  #task time
      checkTime = np.zeros_like(tTask)                   #timer values
      faultDec = tTask < 0.0                             #decceleration fault
      faultSpdRed = tTask < 0.0                          #speed reduction fault
      #calculation
      for i in range(len(tTask)):
        #fill ringbuffer
        cbAcc[icbAcc] = min(vLonAccel[np.searchsorted(tVDC2, tTask[i]) - 1],0)
        icbAcc += 1
        if icbAcc >= cbAccLen:
          icbAcc = 0
        #get demand values
        idx = np.searchsorted(tXBR, tTask[i])- 1
        actDemand = vConMode[idx] == 1 or vConMode[idx] == 2
        extAccDem = vExtAccDem[idx]      
        #check falling edge of demand to abort checking
        if lastDemand and not actDemand:
          initAcc = 0.0
          checkRunning = False
          checkTime[i] = 0.0
        #fill timer values signal 
        if i > 0 and checkRunning:
         checkTime[i] = checkTime[i - 1] + taskCycle
        #check demand values according to requirements
        if checkRunning:
          if checkTime[i] <= XBR_t_max_check:
            spdRed += max(initAcc - extAccDem, 0.0) * taskCycle
            if extAccDem < XBR_max_dec_check2:
              faultDec[i] = True
            if spdRed > XBR_max_speed_reduction and extAccDem < XBR_max_dec_check1:
              faultSpdRed[i] = True
          else:
            checkRunning = False
            checkTime[i] = 0.0
        #check rising edge of demand to start checking
        if not lastDemand and actDemand:
          initAcc = np.min(cbAcc)
          checkRunning = True
        #set last value for next cycle
        lastDemand = vConMode[idx] == 1 or vConMode[idx] == 2
      #print PASS/FAIL result
      if np.any(faultDec) or np.any(faultSpdRed):
        print "MAN limit check FAILED!"
      else:        
        print "MAN limit check PASSED!"
      #plot values
      Client = datavis.cPlotNavigator(title="PN", figureNr=None)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "front_axle_speed", tEBC2, vFroAxSpd, unit="km/h")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "BrakePedalPosition", tEBC1, vBPPos, unit="%")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "Longitudinal_Acceleration", tVDC2, vLonAccel, unit="m/s^2")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "Ext_Acceleration_Demand", tXBR, vExtAccDem, unit="m/s2/bit")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "XBR_Control_Mode", tXBR, vConMode, unit="")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "XBR_checkTime", tTask, checkTime, unit="s")
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, "EXTERN_DREQ_OUT_OF_RANGE(decceleration)", tTask, faultDec, unit="")
      Client.addSignal2Axis(Axis, "EXTERN_DREQ_OUT_OF_RANGE(speedreduction)", tTask, faultSpdRed, unit="")
      
      
      pass
    pass


