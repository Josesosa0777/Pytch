import numpy
import datavis
import interface
import aebs
import kbtools_user   # required for cCalcAEBS
from aebs.par import grouptypes
import numpy

mrr1SignalGroup = {"vx_ego": ("ECU", "evi.General_TC.vxvRef"),
                   "ax_ego": ("ECU", "evi.General_TC.axvRef"),
                   "AcousticalWarning": ("PGNFFB2", "AcousticalWarning"),
                   "Ext_Acceleration_Demand": ("XBR-8C040B2A", "Ext_Acceleration_Demand")}
signalGroups = [mrr1SignalGroup]

DefParam = interface.NullParam

class cViewAebsWarningSimAndRoadTypes(interface.iView):
  dep = 'fillLRR3_POS@aebs.fill',
  def check(self):
    signalGroup = interface.Source.selectSignalGroup(signalGroups)
    return signalGroup

  def fill(self, signalGroup):
    time, LRR3PosObjects  = interface.Objects.fill("fillLRR3_POS@aebs.fill")
    return signalGroup, time, LRR3PosObjects

  def view(self, param, signalGroup, time, LRR3PosObjects):
    egoSpeed = interface.Source.getSignalFromSignalGroup(signalGroup, 'vx_ego', ScaleTime=time)[1]
    egoAccel = interface.Source.getSignalFromSignalGroup(signalGroup, 'ax_ego', ScaleTime=time)[1]

    # LRR3
    client = datavis.cPlotNavigator(title="LRR3", figureNr=None)
    interface.Sync.addClient(client)
    axis1 = client.addAxis()
    axis2 = client.addAxis()
    axis3 = client.addAxis()
    axis4 = client.addAxis()
    axis5 = client.addAxis()
    axis6 = client.addAxis()
    for obj in LRR3PosObjects:
      if obj["label"] == 'LRR3_SameLane_near':
        stat = numpy.where(obj["type"] == grouptypes.LRR3_POS_STAT, True, False)
        client.addSignal2Axis(axis1, "%s dx" % obj["label"], time, obj["dx"], unit="m")
        client.addSignal2Axis(axis2, "%s vx" % obj["label"], time, obj["vx"], unit="m/s")
        # AEBS simple
        a_e, regu_viol,TTC_em = aebs.proc.calcAEBSDeceleration(obj["dx"], obj["vx"], stat, egoSpeed, t_w=1.2, t_p=1.2, a_p=3.0, a_max=10.0, d_e=2.5)
        a_e = numpy.where((obj["dx"] == 0.0) & (obj["vx"] == 0.0), 0.0, a_e)
        # activity = aebs.proc.calcAEBSActivity(a_e, 5.5)
        client.addSignal2Axis(axis5, "aAvoid Simple", time, a_e,      unit="m/s^2")
        # client.addSignal2Axis(axis6, "AEBS activity",         time, activity, unit="-")
        # AEBS ASF
        ego ={}
        ego['vx']   = egoSpeed
        ego['ax']   = egoAccel
        obs = {}
        obs['dx']   =  obj["dx"]
        obs['vRel'] =  obj["vx"]
        obs['aRel'] =  obj["ax"]
        dxSecure = 2.5
        myCalcAEBS = kbtools_user.cCalcAEBS()
        # aAvoidance,Situation,UndefinedaAvoidDueToWrongdxSecure = myCalcAEBS.cpr_CalcaAvoidance(ego, obs, dxSecure)
        par = {}
        par['tWarn']                =   0.6
        par['tPrediction']          =   0.8
        par['P_aStdPartialBraking'] =  -3.0
        par['P_aEmergencyBrake']    =  -5.0
        par['P_aGradientBrake']     = -10.0
        aAvoidancePredicted,Situation,CollisionOccuredTillTPredict = myCalcAEBS.cpr_CalcaAvoidancePredictedModelbased(ego, obs, dxSecure, par)
        aAvoidancePredicted = numpy.where((obj["dx"] == 0.0) & (obj["vx"] == 0.0), 0.0, aAvoidancePredicted)
        client.addSignal2Axis(axis6, "aAvoid ASF", time, -1 * aAvoidancePredicted,      unit="m/s^2")

    # client.addSignal2Axis(axis2, "Ego speed",  time, egoSpeed * 3.6,  unit="km/h")

    Time, Value = interface.Source.getSignalFromSignalGroup(signalGroup, "AcousticalWarning")
    client.addSignal2Axis(axis3, "AcousticalWarning", Time, Value, unit="")
    Time, Value = interface.Source.getSignalFromSignalGroup(signalGroup, "Ext_Acceleration_Demand")
    client.addSignal2Axis(axis4, "Ext_Acceleration_Demand", Time, Value, unit="m/s2/bit")

    return
