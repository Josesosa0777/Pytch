import numpy

import interface
import measproc
import aebs

mrr1SignalGroup = {"vx_ego": ("MRR1plus", "evi.General_TC.vxvRef"),
                   "YR_ego": ("MRR1plus", "evi.General_TC.psiDtOpt"),
                   "tot_veh_dist": ("Veh_Dist_high_Res", "tot_veh_dist")}
signalGroups = [mrr1SignalGroup]

DefParam = interface.NullParam

class cSearchRoadTypes(interface.iSearch):
  def check(self):
    source = self.get_source('main')
    signalGroup = source.selectSignalGroup(signalGroups)
    return signalGroup
    
  def fill(self, group):
    return group

  def search(self, param, group):
    batch = self.get_batch()
    source = self.get_source('main')
    classSign = self.getSign()
    parSign   = param.getSign()
    fileName  = source.FileName
    
    time, egoSpeed = source.getSignalFromSignalGroup(group, 'vx_ego')
    egoYr = source.getSignalFromSignalGroup(group, 'YR_ego')[1]
    totdist   = source.getSignalFromSignalGroup(group, 'tot_veh_dist', ScaleTime=time)[1]
    curvature, city, ruralRoad, highway, cityKm, ruralKm, highwayKm = aebs.proc.calcRoadTypes(egoSpeed, egoYr, totdist, time)

    # City
    cityIntervals = source.compare(time, city, measproc.equal, True)
    result = self.PASSED if cityIntervals else self.FAILED
    report = measproc.cIntervalListReport(cityIntervals, "City")
    batch.add_entry(report, result)

    # Rural road
    ruralIntervals = source.compare(time, ruralRoad, measproc.equal, True)
    result = self.PASSED if ruralIntervals else self.FAILED
    report = measproc.cIntervalListReport(ruralIntervals, "Rural road")
    batch.add_entry(report, result)

    # Highway
    highwayIntervals = source.compare(time, highway, measproc.equal, True)
    result = self.PASSED if highwayIntervals else self.FAILED
    report = measproc.cIntervalListReport(highwayIntervals, "Highway")
    batch.add_entry(report, result)
    return
    
