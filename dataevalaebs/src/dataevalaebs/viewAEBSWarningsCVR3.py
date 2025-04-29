import numpy
import datavis
import interface
import aebs
# import kbtools_user   # required for cDataCVR3 and cDataAC100
from aebs.par import grouptypes
import numpy


mrr1SignalGroup = {"vx_ego": ("MRR1plus", "evi.General_TC.vxvRef"),
                   "ax_ego": ("MRR1plus", "evi.General_TC.axvRef"),
                   "BPAct_b":  ("EBC1_2Wab_EBS5Knorr", "EBS_Brake_switch"),
                   "GPPos_uw":  ("EEC2", "AP_position")}
signalGroups = [mrr1SignalGroup]

DefParam = interface.NullParam

class cViewAebsWarningSimAndRoadTypes(interface.iView):
  dep = 'fillCVR3_POS@aebs.fill',
  def check(self):
    signalGroup = interface.Source.selectSignalGroup(signalGroups)
    return signalGroup

  def fill(self, signalGroup):
    time, CVR3PosObjects  = interface.Objects.fill("fillCVR3_POS@aebs.fill")
    return signalGroup, time, CVR3PosObjects

  def view(self, param, signalGroup, time, CVR3PosObjects):
    egoSpeed = interface.Source.getSignalFromSignalGroup(signalGroup, 'vx_ego', ScaleTime=time)[1]
    egoAccel = interface.Source.getSignalFromSignalGroup(signalGroup, 'ax_ego', ScaleTime=time)[1]
    BPAct    = interface.Source.getSignalFromSignalGroup(signalGroup, 'BPAct_b', ScaleTime=time)[1]
    GPPos    = interface.Source.getSignalFromSignalGroup(signalGroup, 'GPPos_uw', ScaleTime=time)[1]

    # CVR3
    client = datavis.cPlotNavigator(title="CVR3 movement", figureNr=None)
    client2 = datavis.cPlotNavigator(title="CVR3 AEBS", figureNr=None)
    interface.Sync.addClient(client)
    interface.Sync.addClient(client2)
    axis1 = client.addAxis()
    axis2 = client.addAxis()
    axis3 = client.addAxis()
    axis4 = client.addAxis()
    axis5 = client2.addAxis()
    axis6 = client2.addAxis()
    axis7 = client2.addAxis()
    axis8 = client2.addAxis()
    for obj in CVR3PosObjects:
      if obj["label"] == 'SameLane_near':
        stat = numpy.where(obj["type"] == grouptypes.CVR3_POS_STAT, True, False)
        client.addSignal2Axis(axis1, "%s dx" % obj["label"], time, obj["dx"], unit="m")
        client.addSignal2Axis(axis2, "%s vx" % obj["label"], time, obj["vx"], unit="m/s")
        client.addSignal2Axis(axis3, "ego vx" , time, egoSpeed, unit="m/s")
        client.addSignal2Axis(axis4, "ego ax" , time, egoAccel, unit="m/ss")
        client.addSignal2Axis(axis4, "%s ax" % obj["label"] , time, obj["ax"], unit="m/ss")
        # AEBS simple
        a_e, regu_viol,TTC_em = aebs.proc.calcAEBSDeceleration(obj["dx"], obj["vx"], stat, egoSpeed)
        a_e = numpy.where((obj["dx"] == 0.0) & (obj["vx"] == 0.0), 0.0, a_e)
        activity = aebs.proc.calcAEBSActivity(a_e, 5.0)
        client.addSignal2Axis(axis5, "aAvoid Simple", time, a_e,      unit="m/s^2")
        client.addSignal2Axis(axis8, "simple AEBS activity",         time, activity, unit="-")

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
        obs['MotionClassification'] = numpy.where(obj["type"] == grouptypes.CVR3_POS_STAT, 3, 1)

        par = {}
        par['tWarn']                =   0.6
        par['tPrediction']          =   0.8
        par['P_aStdPartialBraking'] =  -3.0
        par['P_aEmergencyBrake']    =  -5.0
        par['P_aGradientBrake']     = -10.0
        par['dxSecure']             =   2.5
        par['dyminComfortSwingOutMO'] = 3.0
        par['dyminComfortSwingOutSO'] = 3.0
        par['P_aComfortSwingOut']     = 1.0

        aAvoidancePredicted,Situation,CollisionOccuredTillTPredict = aebs.proc.calcASFaAvoid(ego, obs, par)
        client.addSignal2Axis(axis6, "aAvoid ASF", time, -1 * aAvoidancePredicted,      unit="m/s^2")

        out_ayAvoid= aebs.proc.calcASF_aYAvoid(ego, obs, par)

        aySwingOutRight = out_ayAvoid['l_DSOayReqComfortSwingOutRight_f']
        aySwingOutLeft  = out_ayAvoid['l_DSOayReqComfortSwingOutLeft_f']

        client.addSignal2Axis(axis7, "aySwingOutRight", time, aySwingOutRight,      unit="m/s^2")
        client.addSignal2Axis(axis7, "aySwingOutLeft", time, aySwingOutLeft,        unit="m/s^2")

        ASFactivity = aebs.proc.calcASFActivity(ego, obs, par)
        client.addSignal2Axis(axis8, "ASF AEBS activity",         time, ASFactivity, unit="-")

    return
