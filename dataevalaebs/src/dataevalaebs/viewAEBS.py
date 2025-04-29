"""
:Organization: Knorr-Bremse SfN GmbH T/CES3.2 (BU2) Budapest Schwieberdingen T/CES3.2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis
import interface

DefParam = interface.NullParam

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    
    ############################
    #acceleration-, IMU-signals#
    ############################
    Client = datavis.cPlotNavigator(title="acceleration", figureNr=101)
    interface.Sync.addClient(Client)
    Client.addsignal('aAvoid [m/ss]', interface.Source.getSignal('ECU_0_0', 'repretg.aAvoid_DEBUG'),
                     #'aEmergency [m/ss]', interface.Source.getSignal('ECU_0_0', 'padasf_x_par_a.REPaEmergencyBrake'),
                     'CurrActThresh [m/ss]', interface.Source.getSignal("PGNFFB2(98FFB2FE)_1_", "CurrentAEBSActivationThreshold"),
                     'ReqActThresh [m/ss]', interface.Source.getSignal("PGNFFBA(98FFBAFE)_1_", "ReqAEBSActivationThreshold"),
                     'ExtAccDem [m/ss]', interface.Source.getSignal("XBR(8C040B2A)_1_", "Ext_Acceleration_Demand"))
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignal("IMU_XAccel_and_YawRate(306)_2_", "X_Accel")
    Client.addSignal2Axis(Axis, "X_Accel", Time, Value, unit="g")
    Time, Value = interface.Source.getSignal("IMU_YAccel_and_Temp(307)_2_", "Y_Accel")
    Client.addSignal2Axis(Axis, "Y_Accel", Time, Value, unit="g")
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignal("IMU_XAccel_and_YawRate(306)_2_", "Yaw_Rate")
    Client.addSignal2Axis(Axis, "Yaw_Rate", Time, Value, unit="/s")

    ###################
    #CAN input signals#
    ###################
    Client = datavis.cPlotNavigator(title="CAN_input", figureNr=102)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignal("ECU_0_0", "csi.VehicleData_TC.nMot")
    Client.addSignal2Axis(Axis, "nMot", Time, Value, unit="1/min")
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignal("ECU_0_0", "evi.General_TC.vxvRef")
    Client.addSignal2Axis(Axis, "vRef", Time, Value, unit="m/s")   
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignal("ECU_0_0", "csi.VehicleData_TC.psiDt")
    Client.addSignal2Axis(Axis, "psiDt", Time, Value, unit="1/s")  
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignal("ECU_0_0", "csi.VelocityData_TC.vDis")
    Client.addSignal2Axis(Axis, "vDis", Time, Value, unit="m/s")     
    Time, Value = interface.Source.getSignal("ECU_0_0", "csi.VelocityData_TC.vxwflRaw")
    Client.addSignal2Axis(Axis, "vfl", Time, Value, unit="m/s")     
    Time, Value = interface.Source.getSignal("ECU_0_0", "csi.VelocityData_TC.vxwfrRaw")
    Client.addSignal2Axis(Axis, "vfr", Time, Value, unit="m/s")     
    Time, Value = interface.Source.getSignal("ECU_0_0", "csi.VelocityData_TC.vxwrlRaw")
    Client.addSignal2Axis(Axis, "vrl", Time, Value, unit="m/s")     
    Time, Value = interface.Source.getSignal("ECU_0_0", "csi.VelocityData_TC.vxwrrRaw")
    Client.addSignal2Axis(Axis, "vrr", Time, Value, unit="m/s")      

    ################################################
    #SystemAvailabilityMonitoring (SAM) LED analyze#
    ################################################
    Client = datavis.cPlotNavigator(title="SAM_LED_analyze", figureNr=103) 
    interface.Sync.addClient(Client) 
    Client.addsignal('LED_1 []', interface.Source.getSignal("PGNFFB2(98FFB2FE)_1_", "SAMLED1"),
             'LED_2[]', interface.Source.getSignal("PGNFFB2(98FFB2FE)_1_", "SAMLED2"),
             'LED_3[]', interface.Source.getSignal("PGNFFB2(98FFB2FE)_1_", "SAMLED3"),
             'BITBE[]', interface.Source.getSignal("ECU_0_0", "asf.HmiReq_TC.SystemAvailMon.w.BITBE_b2"))
    
    #################
    #Driver override#
    #################
    Client = datavis.cPlotNavigator(title="driver_override", figureNr=104)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignal("ECU_0_0", "csi.DriverActions_TC.Driveractions.Driveractions.DriverOverride_b")
    Client.addSignal2Axis(Axis, "DrvOverride", Time, Value, unit="bool")
    Time, Value = interface.Source.getSignal("ECU_0_0", "Dam_x._.InitialDriverOverride_b")
    Client.addSignal2Axis(Axis, "InitialDrvOverride", Time, Value, unit="bool")
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignal("ECU_0_0", "csi.DriverActions_TC.fak1uGPPos")
    Client.addSignal2Axis(Axis, "GPPos", Time, Value, unit="%")
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignal("EBC1(98F001FE)_1_", "BrakePedalPosition")
    Client.addSignal2Axis(Axis, "BrakePedalPosition", Time, Value, unit="%")
    Time, Value = interface.Source.getSignal("EBC1(98F001FE)_1_", "EBSBrakeSwitch")
    Client.addSignal2Axis(Axis, "EBSBrakeSwitch", Time, Value, unit="")
    Time, Value = interface.Source.getSignal("CCVS(98FEF1FE)_1_", "ParkingBrakeSwitch")
    Client.addSignal2Axis(Axis, "ParkingBrakeSwitch", Time, Value, unit="")
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignal("VDC2(98F009FE)_1_", "SteeringWheelAngle")
    Client.addSignal2Axis(Axis, "SteeringWheelAngle", Time, Value, unit="rad")
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignal("ECU_0_0", "lca.TimeIndicatorLeft")
    Client.addSignal2Axis(Axis, "indic_left", Time, Value, unit="")    
    Time, Value = interface.Source.getSignal("ECU_0_0", "lca.TimeIndicatorRight")
    Client.addSignal2Axis(Axis, "indic_right", Time, Value, unit="")    

    #################################################
    #SIT- acceptance filter - adpat for known object#
    #################################################
    Index=24 #object ID to change for known object
    Client = datavis.cPlotNavigator(title="SIT- acceptance filter", figureNr=201) 
    interface.Sync.addClient(Client)
    Client.addsignal('wExistProb_i%d []'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.wExistProb'%Index),
             'wObstacle_i%d []'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.wObstacle'%Index),
             'dVarYv_i%d []'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.dVarYv'%Index),
             'wGroundReflex_i%d []'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.wGroundReflex'%Index),
             'TruckCabIndicator_b_i%d []'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.b.b.TruckCabIndicator_b'%Index),
             'NotClassified_b_i%d []'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.b.b.NotClassified_b'%Index))
    
    ########################################
    #Position Matrix - Object list/relation#
    ########################################
    Index=25 #object ID to change for known object
    Client = datavis.cPlotNavigator(title="Position Matrix - Object list/relation", figureNr=202) 
    interface.Sync.addClient(Client)    
    Client.addsignal('FUS_dxv_i%d []'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.dxv'%Index))
    Client.addsignal('SIT_Intro_Id []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.Intro.i0.Id'))
    Client.addsignal('i0_FiltObjList []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i0'),
             'i1_FiltObjList []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i1'),
             'i2_FiltObjList []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i2'))
    Client.addsignal('i0_IntroObjList []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.Intro.i0.ObjectList.i0'),
             'i1_IntroObjList []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.Intro.i0.ObjectList.i1'),
             'i2_IntroObjList []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.Intro.i0.ObjectList.i2'))
    Client.addsignal('i3_IntroObjList []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.Intro.i0.ObjectList.i3'),
             'i4_IntroObjList []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.Intro.i0.ObjectList.i4'),
             'i5_IntroObjList []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.Intro.i0.ObjectList.i5'))
    Client.addsignal('i0_FiltObjRel []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectRelation.i0'),
             'i1_FiltObjRel []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectRelation.i1'),
             'i2_FiltObjRel []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectRelation.i2')) 
    Client.addsignal('i0_ObjRel []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.Intro.i0.ObjectRelation.i0'),
             'i1_ObjRel []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.Intro.i0.ObjectRelation.i1'),
             'i2_ObjRel []', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.Intro.i0.ObjectRelation.i2')) 

    ########################
    #Mrf object information#
    ########################
    Client = datavis.cPlotNavigator(title="Mrf_object_info", figureNr=203)
    interface.Sync.addClient(Client)
    Client.addsignal('TC.vDis [km/h]', interface.Source.getSignal('ECU_0_0', 'csi.VelocityData_TC.vDis'),
            factor=[3.6])
    Client.addsignal('Mrf_dxv [m]', interface.Source.getSignal('ECU_0_0', 'Mrf._.PssObjectDebugInfo.dxv'),
                     'Mrf_dyv [m]', interface.Source.getSignal('ECU_0_0', 'Mrf._.PssObjectDebugInfo.dyv'))
    Client.addsignal('Mrf_vxv [m/s]', interface.Source.getSignal('ECU_0_0', 'Mrf._.PssObjectDebugInfo.vxv'))
    Client.addsignal('Mrf_wExistProb', interface.Source.getSignal('ECU_0_0', 'Mrf._.PssObjectDebugInfo.wExistProb'),
                     'Mrf_wObstacle', interface.Source.getSignal('ECU_0_0', 'Mrf._.PssObjectDebugInfo.wObstacle'),
                     'TC.Intro.i0.Id', interface.Source.getSignal('ECU_0_0', 'sit.IntroFinder_TC.Intro.i0.Id'))
    Client.addsignal('ObjectIndex', interface.Source.getSignal('ECU_0_0', 'Mrf._.PssObjectDebugInfo.Index')) 
             
    ##########################
    #RETG w/ in_crash analyze#
    ##########################
    Client = datavis.cPlotNavigator(title="retg", figureNr=204) 
    interface.Sync.addClient(Client)
    y_limits = [-1,11]
    Client.addsignal('shot_dep_retg []', interface.Source.getSignal('ECU_0_0', 'pressam.ShotTheDeputy_RETG'),
                     'shot_sher_retg []', interface.Source.getSignal('ECU_0_0', 'repretg.ShotTheSheriff'),ylim=y_limits)
    Client.addsignal('rep_status_retg []', interface.Source.getSignal('ECU_0_0', 'repretg.__b_Rep.__b_RepBase.status'),
                     'rep_exec_status_deretg []', interface.Source.getSignal('ECU_0_0', 'repretg.__b_Rep.__b_RepBase.ExecutionStatus'),	
                     'mast_sam_act_phase[]', interface.Source.getSignal('ECU_0_0', 'mastsam.__b_Mst.activePhase'),
                     'enable_rep_retg[]', interface.Source.getSignal('ECU_0_0', 'repretg.EnableREPRETG_b'),ylim=y_limits)
    Client.addsignal('a_avoid_debug [m/ss]', interface.Source.getSignal('ECU_0_0', 'repretg.aAvoid_DEBUG'),
                    #'a_Ref_sync_T20 [m/ss]', interface.Source.getSignal('ECU_0_0', 'fus.General_T20.aRefSync'),
                     'a_Ref_sync_TC [m/ss]', interface.Source.getSignal('ECU_0_0', 'fus.General_TC.aRefSync'),
                     'a_Partial_brake [m/ss]', interface.Source.getSignal('ECU_0_0', 'repretg.aPartialBraking'))
    Client.addsignal('t_act_retg []', interface.Source.getSignal('ECU_0_0', 'repretg.tActivationTimer'),
                     't_act_aco_retg []', interface.Source.getSignal('ECU_0_0', 'repretg.tAcoActivationTimer'),
                     't_block_retg[]', interface.Source.getSignal('ECU_0_0', 'repretg.tBlockingTimer'))
    Client.addsignal('in_Crash_act [bool]', interface.Source.getSignal('ECU_0_0', 'asf.pubFlagsASF.b.InCrashBrakingActive_B'),
                     'aEmergency [m/ss]', interface.Source.getSignal('ECU_0_0', 'padasf_x_par_a.REPaEmergencyBrake'))
    #Client.addsignal('ExtAccelDemand[]', interface.Source.getSignal('XBR(8C04FEFE)_1_', 'XBRControlMode'))

    ##############
    #DeSu analyze#
    ##############
    Client = datavis.cPlotNavigator(title="Deceleration_support", figureNr=205) 
    interface.Sync.addClient(Client) 
    Client.addsignal('shot_dep_desu []', interface.Source.getSignal('ECU_0_0', 'pressam.ShotTheDeputy_DESU'),
             'shot_sher_desu []', interface.Source.getSignal('ECU_0_0', 'repdesu.ShotTheSheriff'))
    Client.addsignal('rep_status_desu []', interface.Source.getSignal('ECU_0_0', 'repdesu.__b_Rep.__b_RepBase.status'),
             'rep_exec_status_desu []', interface.Source.getSignal('ECU_0_0', 'repdesu.__b_Rep.__b_RepBase.ExecutionStatus'),	
             'mast_sam_act_phase[]', interface.Source.getSignal('ECU_0_0', 'mastsam.__b_Mst.activePhase'),
             'enable_rep_desu[]', interface.Source.getSignal('ECU_0_0', 'repdesu.EnableREPDESU_b'))
    Client.addsignal('a_avoid_desu [m/ss]', interface.Source.getSignal('ECU_0_0', 'repdesu.aAvoid'),
             'a_avoid_stop_desu [m/ss]', interface.Source.getSignal('ECU_0_0', 'repdesu.aAvoidThresholdStop'),
             'a_avoid_start_desu[m/ss]', interface.Source.getSignal('ECU_0_0', 'repdesu.aAvoidThresholdStart'))
    Client.addsignal('t_act_desu []', interface.Source.getSignal('ECU_0_0', 'repdesu.tActivationTimer'),
             't_act_aco_desu []', interface.Source.getSignal('ECU_0_0', 'repdesu.tAcoActivationTimer'),
             't_block_desu[]', interface.Source.getSignal('ECU_0_0', 'repdesu.tBlockingTimer'))
    Client.addsignal('pBrake[bar]', interface.Source.getSignal('ECU_0_0', 'namespaceSIT._.Egve._.pBrake_uw'))
    Client.addsignal('ExtAccelDemand[]', interface.Source.getSignal('XBR(8C04FEFE)_1_', 'XBRControlMode'))       
    
    #######################################
    #Action coordinator / Reaction pattern#
    #######################################
    Client = datavis.cPlotNavigator(title="Action coordinator", figureNr=206)
    interface.Sync.addClient(Client)
    Client.addsignal('acoacoi', interface.Source.getSignal('ECU_0_0', 'acoacoi.__b_AcoNoFb.__b_Aco.status'),
                     # 'acobelj', interface.Source.getSignal('ECU_0_0', 'acobelj.__b_AcoNoFb.__b_Aco.status'),
                     # 'acobelt', interface.Source.getSignal('ECU_0_0', 'acobelt.__b_AcoNoFb.__b_Aco.status'),
                     'acobraj', interface.Source.getSignal('ECU_0_0', 'acobraj.__b_AcoCoFb.__b_Aco.status'),
                     # 'acobrap', interface.Source.getSignal('ECU_0_0', 'acobrap.__b_AcoNoFb.__b_Aco.status'),
                     # 'acochas', interface.Source.getSignal('ECU_0_0', 'acochas.__b_AcoNoFb.__b_Aco.status'),
                     # 'acohbat', interface.Source.getSignal('ECU_0_0', 'acohbat.__b_AcoNoFb.__b_Aco.status'),
                     # 'acoopti', interface.Source.getSignal('ECU_0_0', 'acoopti.__b_AcoNoFb.__b_Aco.status'),
                     'acopebe', interface.Source.getSignal('ECU_0_0', 'acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.status'),
                     'acopebm', interface.Source.getSignal('ECU_0_0', 'acopebm.__b_AcoDece.__b_AcoCoFb.__b_Aco.status'),
                     'acopebp', interface.Source.getSignal('ECU_0_0', 'acopebp.__b_AcoDece.__b_AcoCoFb.__b_Aco.status'),
                     # 'acowarb', interface.Source.getSignal('ECU_0_0', 'acowarb.__b_AcoNoFb.__b_Aco.status'),
                     'acoxbad', interface.Source.getSignal('ECU_0_0', 'acoxbad.__b_AcoDece.__b_AcoCoFb.__b_Aco.status'),
                     'InCrashBrakingActive', interface.Source.getSignal('ECU_0_0', 'asf.pubFlagsASF.b.InCrashBrakingActive_B'))
    
    ##################
    #Reaction pattern#
    ##################
    # Client = datavis.cPlotNavigator(title="Reaction pattern", figureNr=207)
    # interface.Sync.addClient(Client)
    Client.addsignal('repacuw', interface.Source.getSignal('ECU_0_0', 'repacuw.__b_Rep.__b_RepBase.status'),
                     'repaubr', interface.Source.getSignal('ECU_0_0', 'repaubr.__b_Rep.__b_RepBase.status'),
                     # 'repbrph', interface.Source.getSignal('ECU_0_0', 'repbrph.__b_Rep.__b_RepBase.status'),
                     # 'repbrpp', interface.Source.getSignal('ECU_0_0', 'repbrpp.__b_Rep.__b_RepBase.status'),
                     'repdesu', interface.Source.getSignal('ECU_0_0', 'repdesu.__b_Rep.__b_RepBase.status'),
                     # 'repinfo', interface.Source.getSignal('ECU_0_0', 'repinfo.__b_Rep.__b_RepBase.status'),
                     # 'repladi', interface.Source.getSignal('ECU_0_0', 'repladi.__b_Rep.__b_RepBase.status'),
                     # 'repprew', interface.Source.getSignal('ECU_0_0', 'repprew.__b_Rep.__b_RepBase.status'),
                     'repretg', interface.Source.getSignal('ECU_0_0', 'repretg.__b_Rep.__b_RepBase.status'))
    Client.addsignal('repacuw.Execution', interface.Source.getSignal('ECU_0_0', 'repacuw.__b_Rep.__b_RepBase.ExecutionStatus'),
                     'repaubr.Execution', interface.Source.getSignal('ECU_0_0', 'repaubr.__b_Rep.__b_RepBase.ExecutionStatus'),
                     # 'repbrph.Execution', interface.Source.getSignal('ECU_0_0', 'repbrph.__b_Rep.__b_RepBase.ExecutionStatus'),
                     # 'repbrpp.Execution', interface.Source.getSignal('ECU_0_0', 'repbrpp.__b_Rep.__b_RepBase.ExecutionStatus'),
                     'repdesu.Execution', interface.Source.getSignal('ECU_0_0', 'repdesu.__b_Rep.__b_RepBase.ExecutionStatus'),
                     # 'repinfo.Execution', interface.Source.getSignal('ECU_0_0', 'repinfo.__b_Rep.__b_RepBase.ExecutionStatus'),
                     # 'repladi.Execution', interface.Source.getSignal('ECU_0_0', 'repladi.__b_Rep.__b_RepBase.ExecutionStatus'),
                     # 'repprew.Execution', interface.Source.getSignal('ECU_0_0', 'repprew.__b_Rep.__b_RepBase.ExecutionStatus'),
                     'repretg.Execution', interface.Source.getSignal('ECU_0_0', 'repretg.__b_Rep.__b_RepBase.ExecutionStatus'))
                     
    ##################
    #FUS objects - dx#
    ##################
    Client = datavis.cPlotNavigator(title="FUS_objects_dx", figureNr=301)
    interface.Sync.addClient(Client)
    signals=[] #Erstellen einer leeren Liste
    for i in xrange(0,33,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
      signals.append("FUS_dx_%d"%i) #Name der Signalbezeichnung
      signals.append(interface.Source.getSignal('ECU_0_0','fus.ObjData_TC.FusObj.i%d.dxv'%i)) # Angabe des Geraetes und des Signalnamens
    Client.addsignal(*signals) #entpacken der liste
    
    ##################
    #FUS objects - dy#
    ##################
    Client = datavis.cPlotNavigator(title="FUS_objects_dy", figureNr=302)
    interface.Sync.addClient(Client)
    signals=[] #Erstellen einer leeren Liste
    for i in xrange(0,33,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
      signals.append("FUS_dy_%d"%i) #Name der Signalbezeichnung
      signals.append(interface.Source.getSignal('ECU_0_0','fus.ObjData_TC.FusObj.i%d.dyv'%i)) # Angabe des Geraetes und des Signalnamens
    Client.addsignal(*signals) #entpacken der liste 

    ###################
    #FUS objects - vxv#
    ###################
    Client = datavis.cPlotNavigator(title="FUS_objects_vxv", figureNr=303)
    interface.Sync.addClient(Client)
    signals=[] #Erstellen einer leeren Liste
    for i in xrange(0,33,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
      signals.append("FUS_vxv_%d"%i) #Name der Signalbezeichnung
      signals.append(interface.Source.getSignal('ECU_0_0','fus.ObjData_TC.FusObj.i%d.vxv'%i)) # Angabe des Geraetes und des Signalnamens
    Client.addsignal(*signals) #entpacken der liste

    #############################
    #FUS objects - standing flag#
    ############################# 
    Client = datavis.cPlotNavigator(title="FUS_objects_standing_flag", figureNr=304)
    interface.Sync.addClient(Client)    
    signals=[] #Erstellen einer leeren Liste
    for i in xrange(0,33,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
      signals.append("FUS_flag stand_%d"%i) #Name der Signalbezeichnung
      signals.append(interface.Source.getSignal('ECU_0_0','fus.ObjData_TC.FusObj.i%d.b.b.Stand_b'%i)) # Angabe des Geraetes und des Signalnamens
    Client.addsignal(*signals) #entpacken der liste 

    ##########################
    #FUS Objects - drive flag#
    ##########################
    Client = datavis.cPlotNavigator(title="FUS_objects_drive_flag", figureNr=305)
    interface.Sync.addClient(Client) 
    signals=[] #Erstellen einer leeren Liste
    for i in xrange(0,33,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
      signals.append("FUS_flag_drive_%d"%i) #Name der Signalbezeichnung
      signals.append(interface.Source.getSignal('ECU_0_0','fus.ObjData_TC.FusObj.i%d.b.b.Drive_b'%i)) # Angabe des Geraetes und des Signalnamens
    Client.addsignal(*signals) #entpacken der liste

    ############################ 
    #FUS Objects - stopped flag#
    ############################
    Client = datavis.cPlotNavigator(title="FUS_objects_stopped_flag", figureNr=306)
    interface.Sync.addClient(Client)
    signals=[] #Erstellen einer leeren Liste
    for i in xrange(0,33,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
      signals.append("FUS_flag stopped%d"%i) #Name der Signalbezeichnung
      signals.append(interface.Source.getSignal('ECU_0_0','fus.ObjData_TC.FusObj.i%d.b.b.Stopped_b'%i)) # Angabe des Geraetes und des Signalnamens
    Client.addsignal(*signals) #entpacken der liste
   
    ######################################################
    #FUS object information - if relevant object is known#
    ######################################################
    if True:
      Index=24 #object ID to change for known object
      Client = datavis.cPlotNavigator(title="known_FUS_object_info", figureNr=307)
      interface.Sync.addClient(Client)
      Client.addsignal('TC.FusObj.i%d.dxv [m]'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.dxv'%Index))
      Client.addsignal('TC.FusObj.i%d.dyv [m]'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.dyv'%Index))
      Client.addsignal('TC.FusObj.i%d.vxv [m/s]'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.vxv'%Index))
      Client.addsignal('TC.FusObj.i%d.wExistProb'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.wExistProb'%Index),
                       'TC.FusObj.i%d.wObstacle'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.wObstacle'%Index),
                       'TC.FusObj.i%d.wGroundReflex'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.wGroundReflex'%Index))
      Client.addsignal('TC.FusObj.i%d.DriveInvDir_b'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.b.b.DriveInvDir_b'%Index),
                       'TC.FusObj.i%d.Drive_b'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.b.b.Drive_b'%Index),
                       'TC.FusObj.i%d.Hist_b'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.b.b.Hist_b'%Index),
                       'TC.FusObj.i%d.Measurable_b'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.b.b.Measurable_b'%Index),
                       'TC.FusObj.i%d.Measured_b'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.b.b.Measured_b'%Index),
                       'TC.FusObj.i%d.NotClassified_b'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.b.b.NotClassified_b'%Index),
                       'TC.FusObj.i%d.Stand_b'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.b.b.Stand_b'%Index),
                       'TC.FusObj.i%d.StoppedInvDir'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.b.b.StoppedInvDir_b'%Index),
                       'TC.FusObj.i%d.Stopped_b'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.b.b.Stopped_b'%Index),
                       'TC.FusObj.i%d.TruckCabIndicator_b'%Index, interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.b.b.TruckCabIndicator_b'%Index),
                       factor=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                       offset=[0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9],
                       color=['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       linewidth=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                       displayscaled=[False, False, False, False, False, False, False, False, False, False],
               ylim=(-1.0,11.0))
      Client.addsignal('probClass.i0', interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.probClass.i0'%Index),
                       'probClass.i1', interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.probClass.i1'%Index),
                       'probClass.i2', interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.probClass.i2'%Index),
                       'probClass.i3', interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.probClass.i3'%Index),
                       'probClass.i4', interface.Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i%d.probClass.i4'%Index)) 
    
    # ###########################          
    # #DSP radar locations dMeas# 
    # ###########################
    # Client = datavis.cPlotNavigator(title="DSP radar locations_dMeas", figureNr=401)
    # interface.Sync.addClient(Client)
    # signals=[] #Erstellen einer leeren Liste
    # for i in xrange(0,48,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
      # signals.append("d_Meas%d"%i) #Name der Signalbezeichnung
      # signals.append(interface.Source.getSignal('ECU_0_0','dsp.LocationData_TC.Location.i%d.dMeas'%i)) # Angabe des Geraetes und des Signalnamens
    # Client.addsignal(*signals) #entpacken der liste 

    # ###########################          
    # #DSP radar locations vMeas# 
    # ###########################
    # Client = datavis.cPlotNavigator(title="DSP radar locations_vMeas", figureNr=402)
    # interface.Sync.addClient(Client)
    # signals=[] #Erstellen einer leeren Liste
    # for i in xrange(0,48,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
      # signals.append("v_Meas%d"%i) #Name der Signalbezeichnung
      # signals.append(interface.Source.getSignal('ECU_0_0','dsp.LocationData_TC.Location.i%d.vMeas'%i)) # Angabe des Geraetes und des Signalnamens
    # Client.addsignal(*signals) #entpacken der liste

    ###########################          
    #RMP radar locations dMeas# 
    ###########################
    Client = datavis.cPlotNavigator(title="RMP radar locations_dMeas", figureNr=410)
    interface.Sync.addClient(Client)
    signals=[] #Erstellen einer leeren Liste
    for i in xrange(0,48,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
      signals.append("d_Meas%d"%i) #Name der Signalbezeichnung
      signals.append(interface.Source.getSignal('ECU_0_0','rmp.D2lLocationData_TC.Location.i%d.dMeas'%i)) # Angabe des Geraetes und des Signalnamens
    Client.addsignal(*signals) #entpacken der liste     

    ###########################          
    #RMP radar locations vMeas# 
    ###########################
    Client = datavis.cPlotNavigator(title="RMP radar locations_vMeas", figureNr=411)
    interface.Sync.addClient(Client)
    signals=[] #Erstellen einer leeren Liste
    for i in xrange(0,48,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
      signals.append("v_Meas%d"%i) #Name der Signalbezeichnung
      signals.append(interface.Source.getSignal('ECU_0_0','rmp.D2lLocationData_TC.Location.i%d.vMeas'%i)) # Angabe des Geraetes und des Signalnamens
    Client.addsignal(*signals) #entpacken der liste         

    ###################################
    #dbPower - for radom investigation#
    ###################################
    Client = datavis.cPlotNavigator(title="dbPower", figureNr=501)
    interface.Sync.addClient(Client)
    signals=[] #Erstellen einer leeren Liste
    for i in xrange(0,40,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
      signals.append("dbPowerFilt_i%d"%i) #Name der Signalbezeichnung
      signals.append(interface.Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i%d.internal.maxDbPowerFilt'%i)) 
    Client.addsignal(*signals)  

    #####################
    #ATS objects - dx,dy#
    #####################
    Client = datavis.cPlotNavigator(title="ATS objects - dx,dy", figureNr=601)
    interface.Sync.addClient(Client)
    signals=[] #Erstellen einer leeren Liste
    for i in xrange(0,5,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
      signals.append("ats_dx_i%d"%i) #Name der Signalbezeichnung
      signals.append(interface.Source.getSignal('ECU_0_0','ats.Po_TC.PO.i%d.dxvFilt'%i)) # Angabe des Geraetes und des Signalnamens
    Client.addsignal(*signals)  
    signals=[] #Erstellen einer leeren Liste
    for i in xrange(0,5,1):
      signals.append("ats_dy_i%d"%i) #Name der Signalbezeichnung
      signals.append(interface.Source.getSignal('ECU_0_0','ats.Po_TC.PO.i%d.dyv'%i))
    Client.addsignal(*signals) #entpacken der liste

                  

  
    return []

