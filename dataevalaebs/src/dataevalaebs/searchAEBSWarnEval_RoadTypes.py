import sys
from collections import OrderedDict

import numpy

import interface
from aebs.proc.RoadTypeClassification import calcRoadTypes
from measproc.report2 import Report
from measproc.relations import equal
from measproc.Statistic import cDinStatistic
from measproc.IntervalList import cIntervalList
from measparser.signalgroup import SignalGroup

DefParam = interface.NullParam

sensorSignalGroups = OrderedDict([
  ('ecu', {
    "vx_ego": ("ECU", "evi.General_TC.vxvRef"),
    "YR_ego": ("ECU", "evi.General_TC.psiDtOpt"),
  },),
  ('radar', {
    "vx_ego": ("General_radar_status", "actual_vehicle_speed"),
    "YR_ego": ("General_radar_status", "cvd_yawrate"),
  },),
  ('trw', {
    'vx_ego': ('General_radar_status', 'actual_vehicle_speed'),
    'YR_ego': ('General_radar_status', 'cvd_yawrate'),
  },),
])
for device in 'MRR1plus', 'RadarFC':
  sensorSignalGroups[device] = {
    "vx_ego": (device, "evi.General_TC.vxvRef"),
    "YR_ego": (device, "evi.General_TC.psiDtOpt")
  }

canSignalGroups = OrderedDict([
  (0, {
    "tot_veh_dist": ("Veh_Dist_high_Res",   "tot_veh_dist"),
  },),
  (1, {
    "tot_veh_dist": ("Veh_Dist_high_Res",   "tot_veh_dist"),
  },),
  (2, {
    "tot_veh_dist": ("VDHR-DTCOorMTCOTachograph", "HghRslutionTotalVehicleDistance"),
  },),
  (3, {
    "tot_veh_dist": ("VD_00", "VD_TotVehDist_00"),
  },),
  (4, {
    "tot_veh_dist": ("VDHR_EE", "VDHR_HRTotVehDist_EE"),
  },),
  (5, {
    "tot_veh_dist": ("VDHR_EE-Tachograph_EE-Message-Tachograph_EE-J1939_DAS_Ford", "VDHR_HRTotVehDist_EE"),
  },),
])

class cSearch(interface.iSearch):
  def check(self):
    Source = self.get_source('main')
    sensorGroup = SignalGroup.from_named_signalgroups(sensorSignalGroups, Source)
    canGroup = SignalGroup.from_named_signalgroups(canSignalGroups, Source)
    return sensorGroup, canGroup
  
  def fill(self, sensorGroup, canGroup):
    Source = self.get_source('main')
    time, egoSpeed = sensorGroup.get_signal('vx_ego')   # m/s
    egoYR = sensorGroup.get_value('YR_ego', ScaleTime=time)
    
    # The yaw rate in AC100 General_radar_status is in deg/sec, should be
    # converted to rad/sec!
    if sensorGroup.winner in ('radar', 'trw'):
      print >> sys.stderr,\
      "YR_ego in message General_radar_status converted to rad/sec"
      sys.stderr.flush()
      egoYR = numpy.deg2rad(egoYR)

    totdist = canGroup.get_value('tot_veh_dist', ScaleTime=time)
    # The tot_veh_dist in some dbc is in m instead of km! 
    # It seems that VDHR-DTCOorMTCOTachograph device name indicates this.
    if canGroup.winner == 2:
      print >> sys.stderr,\
      "tot_veh_dist in message VDHR-DTCOorMTCOTachograph is converted to km"
      sys.stderr.flush()
      totdist = totdist / 1000.0

    curvature, city, ruralRoad, highway, cityKm, ruralKm, highwayKm = \
    calcRoadTypes(egoSpeed, egoYR, totdist, time)

    roadtypeLength = {
      'city':    cityKm,
      'rural':   ruralKm,
      'highway': highwayKm,
    }

    batch = self.get_batch()
    intervals = cIntervalList(time)
    road_votes = 'road type'
    votes = batch.get_labelgroups(road_votes)
    ego_quas = 'ego vehicle'
    names = batch.get_quanamegroups(ego_quas)
    report = Report(intervals, "AEBS-RoadType-Intervals", names=names,
                    votes=votes)
    for road_type, road_intervals in [
      ("city",     cIntervalList.fromMask(time, city)),
      ("rural",    cIntervalList.fromMask(time, ruralRoad)),
      ("highway",  cIntervalList.fromMask(time, highway)),
      
      ]:
      for interval in road_intervals:
        idx = report.addInterval(interval)
        report.vote(idx, road_votes, road_type)
        start, end = interval
        dist = totdist[end-1] - totdist[start]
        report.set(idx, ego_quas, 'driven distance', dist)
    return roadtypeLength, report
  
  def search(self, param, roadtypeLength, report):
    batch = self.get_batch()

    roadtypes = cDinStatistic('AEBS_RoadType_Milages',
                              [['RoadTypes', ['rural', 'city', 'highway']]])
    roadtypes.set([['RoadTypes','city']], roadtypeLength['city'])
    roadtypes.set([['RoadTypes','rural']], roadtypeLength['rural'])
    roadtypes.set([['RoadTypes','highway']], roadtypeLength['highway'])
    batch.add_entry(roadtypes, self.NONE)

    batch.add_entry(report)
    return

