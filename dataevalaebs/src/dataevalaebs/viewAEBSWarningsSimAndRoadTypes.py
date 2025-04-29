import datavis
import interface
import aebs
from aebs.par import grouptypes
import numpy

mrr1SignalGroups = [{"vx_ego": ("MRR1plus", "evi.General_TC.vxvRef"),
                     "ax_ego": ("MRR1plus", "evi.General_TC.axvRef"),
                     "YR_ego": ("MRR1plus", "evi.General_TC.psiDtOpt")}]

lrr3repsignalgroups = [{"repprew.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repprew.__b_Rep.__b_RepBase.ExecutionStatus"),
                        "repprew.__b_Rep.__b_RepBase.status": ("ECU", "repprew.__b_Rep.__b_RepBase.status"),
                        "repretg.__b_Rep.__b_RepBase.ExecutionStatus": ("ECU", "repretg.__b_Rep.__b_RepBase.ExecutionStatus"),
                        "repretg.__b_Rep.__b_RepBase.status": ("ECU", "repretg.__b_Rep.__b_RepBase.status")}]

canSignalGroups = [{"tot_veh_dist": ("Veh_Dist_high_Res", "tot_veh_dist"),
                    "BPAct_b":  ("EBC1_2Wab_EBS5Knorr", "EBS_Brake_switch"),
                    "GPPos_uw":  ("EEC2", "AP_position")},
                   {"tot_veh_dist": ("Veh_Dist_high_Res", "tot_veh_dist"),
                    "BPAct_b":  ("EBC1_2Wab_EBS5Knorr", "EBS_Brake_switch"),
                    "GPPos_uw":  ("EEC2-8CF00300", "AP_position")}]

DefParam = interface.NullParam

a_e_threshold = 5.0

class cViewAebsWarningSimAndRoadTypes(interface.iView):
  dep = ('fillAC100_POS@aebs.fill', 'fillCVR3_POS@aebs.fill',
         'fillLRR3_POS@aebs.fill')
  def check(self):
    mrr1Group = interface.Source.selectSignalGroup(mrr1SignalGroups)
    lrr3Group = interface.Source.selectSignalGroup(lrr3repsignalgroups)
    canGroup = interface.Source.selectSignalGroup(canSignalGroups)
    return mrr1Group, lrr3Group, canGroup

  def fill(self, mrr1Group, lrr3Group, canGroup):
    time, posObjectsAC100 = interface.Objects.fill("fillAC100_POS@aebs.fill")
    time, posObjectsCVR3  = interface.Objects.fill("fillCVR3_POS@aebs.fill")
    time, posObjectsLRR3  = interface.Objects.fill("fillLRR3_POS@aebs.fill")
    return mrr1Group, lrr3Group, canGroup, posObjectsAC100, posObjectsCVR3, posObjectsLRR3

  def view(self, param, mrr1Group, lrr3Group, canGroup, posObjectsAC100, posObjectsCVR3, posObjectsLRR3):
    time = interface.Objects.ScaleTime
    egoSpeed = interface.Source.getSignalFromSignalGroup(mrr1Group, 'vx_ego', ScaleTime=time)[1]
    egoAccel = interface.Source.getSignalFromSignalGroup(mrr1Group, 'ax_ego', ScaleTime=time)[1]
    egoYr = interface.Source.getSignalFromSignalGroup(mrr1Group, 'YR_ego', ScaleTime=time)[1]
    BPAct = interface.Source.getSignalFromSignalGroup(canGroup, 'BPAct_b', ScaleTime=time)[1]
    GPPos = interface.Source.getSignalFromSignalGroup(canGroup, 'GPPos_uw', ScaleTime=time)[1]

    TestsToRun = {'Mitigation20': 20.0 / 3.6, 'Mitigation10': 10.0 / 3.6, 'KBAEBS': 0.0, 'Avoidance': None, 'KBASFAvoidance': None}
    sensorsToEvaluate = {
      'CVR3': {
        'obj': posObjectsCVR3,
        'label': 'SameLane_near',
        'statType': grouptypes.CVR3_POS_STAT},
      'AC100': {
        'obj': posObjectsAC100,
        'label': 'ACC',
        'statType': grouptypes.AC100_STAT},
      'LRR3': {
        'obj': posObjectsLRR3,
        'label': 'LRR3_SameLane_near',
        'statType': grouptypes.LRR3_POS_STAT}}

    for sensor, prop in sensorsToEvaluate.iteritems():
      client = datavis.cPlotNavigator(title="%s warnings" % sensor, figureNr=None)
      interface.Sync.addClient(client)
      for obj in prop['obj']:
        if obj["label"] == prop['label']:
          stat = numpy.where(obj["type"] == prop['statType'], True, False)
          axis = client.addAxis()
          client.addSignal2Axis(axis, "%s dx" % obj["label"], time, obj["dx"],  unit="m")
          axis = client.addAxis()
          client.addSignal2Axis(axis, "%s vx" % obj["label"], time, obj["vx"],  unit="m/s")
          axis = client.addAxis()
          client.addSignal2Axis(axis, "%s ax" % obj["label"], time, obj["ax"],  unit="m/s2")
          axis1 = client.addAxis()
          axis2 = client.addAxis()
          axis3 = client.addAxis()
          client.addSignal2Axis(axis3, "%s stationary" % obj["label"], time, stat,  unit="-")
          for testname, vel_reduc in TestsToRun.iteritems():
            # a_e = numpy.zeros_like(time)
            if testname != 'KBASFAvoidance':
              a_e, regu_viol,TTC_em = aebs.proc.calcAEBSDeceleration(obj["dx"], obj["vx"], stat, egoSpeed, v_red=vel_reduc)
              activity = aebs.proc.calcAEBSActivity(a_e, a_e_threshold)
            else:
              # AEBS ASF
              ego ={}
              ego['vx']   = egoSpeed
              ego['ax']   = egoAccel
              ego['BPact']  = BPAct
              ego['GPPos']  = GPPos
              obs = {}
              obs['dx']   =  obj["dx"]
              obs['vRel'] =  obj["vx"]
              obs['aRel'] =  obj["ax"]
              obs['dy']   =  obj["dy"]
              obs['vy']   =  obj["vy"]
              obs['MotionClassification'] = numpy.where(stat, 3, 1)
              par = {}
              par['tWarn']                =   0.6
              par['tPrediction']          =   0.8
              par['P_aStdPartialBraking'] =  -3.0
              par['P_aEmergencyBrake']    =  -5.0
              par['P_aGradientBrake']     = -10.0
              par['dxSecure']             =   1.0
              par['dyminComfortSwingOutMO'] = 3.0
              par['dyminComfortSwingOutSO'] = 3.0
              par['P_aComfortSwingOut']     = 1.0
              a_e, situ, coltilpred = aebs.proc.calcASFaAvoid(ego, obs, par)
              a_e = -a_e
              activity = aebs.proc.calcASFActivity(ego, obs, par)
            client.addSignal2Axis(axis1, "Req decel for %s" % testname, time, a_e,  unit="m/s2")
            client.addSignal2Axis(axis2, "AEBS activity for %s" % testname, time, activity,  unit="m/s2")
            # client.addSignal2Axis(axis5, "Regulation violated", time, regu_viol,      unit="-")
            # client.addSignal2Axis(axis5, "TTC_em", time, TTC_em,      unit="s")

    client = datavis.cPlotNavigator(title="Reaction pattern of LRR3", figureNr=None)
    interface.Sync.addClient(client)
    axis1 = client.addAxis()
    axis2 = client.addAxis()
    time, value = interface.Source.getSignalFromSignalGroup(lrr3Group, "repprew.__b_Rep.__b_RepBase.status")
    client.addSignal2Axis(axis1, "Warning active", time, value == 6, unit="-")
    #client.addSignal2Axis(axis1, "repprew.Status", time, value, unit="-")
    time, value = interface.Source.getSignalFromSignalGroup(lrr3Group, "repretg.__b_Rep.__b_RepBase.status")
    client.addSignal2Axis(axis1, "Braking active", time, value == 6, unit="-")
    #client.addSignal2Axis(axis1, "repretg.Status", time, value, unit="-")
    time, value = interface.Source.getSignalFromSignalGroup(lrr3Group, "repprew.__b_Rep.__b_RepBase.ExecutionStatus")
    client.addSignal2Axis(axis2, "repprew.Execution", time, value, unit="-")
    time, value = interface.Source.getSignalFromSignalGroup(lrr3Group, "repretg.__b_Rep.__b_RepBase.ExecutionStatus")
    client.addSignal2Axis(axis2, "repretg.Execution", time, value, unit="-")

    # Road types
    timeCVR3, egoSpeedCVR3 = interface.Source.getSignalFromSignalGroup(mrr1Group, 'vx_ego')
    egoYrCVR3 = interface.Source.getSignalFromSignalGroup(mrr1Group, 'YR_ego')[1]
    totdist   = interface.Source.getSignalFromSignalGroup(canGroup, 'tot_veh_dist', ScaleTime=timeCVR3)[1]
    curvature, city, ruralRoad, highway, cityKm, ruralKm, highwayKm = aebs.proc.calcRoadTypes(egoSpeedCVR3, egoYrCVR3, totdist, timeCVR3)
    client = datavis.cPlotNavigator(title="Road type", figureNr=None)
    interface.Sync.addClient(client)
    axis1 = client.addAxis()
    client.addSignal2Axis(axis1, "City",       timeCVR3, city,      unit="-")
    client.addSignal2Axis(axis1, "Rural road", timeCVR3, ruralRoad, unit="-")
    client.addSignal2Axis(axis1, "Highway",    timeCVR3, highway,   unit="-")
    axis2 = client.addAxis()
    client.addSignal2Axis(axis2, "Ego speed",  timeCVR3, egoSpeedCVR3 * 3.6,  unit="km/h")
    axis3 = client.addAxis()
    client.addSignal2Axis(axis3, "Curvature",  timeCVR3, curvature,  unit="1/km")
    ListNav = datavis.cListNavigator(title="Road length")
    interface.Sync.addClient(ListNav)
    ListNav.addsignal("City KM", (numpy.array([time.min()]), numpy.array([cityKm])))
    ListNav.addsignal("Rural KM", (numpy.array([time.min()]), numpy.array([ruralKm])))
    ListNav.addsignal("Highway KM", (numpy.array([time.min()]), numpy.array([highwayKm])))

    return
