# -*- dataeval: method -*-

import sys

import numpy as np

import interface
from measproc.report2 import Report
from measproc.IntervalList import maskToIntervals, cIntervalList
from aebs.sdf.asso_cvr3_fus_result import VID_OBJ_NUM, devnames
from viewIntroObstacleClassif import findUniqueValues

VID_INVALID_IDX = 255
FUS_REGULAR_OBJ_NUM = 32

DefParam = interface.NullParam

sgs = []
for devname in devnames:
  sg = { "egoSpeed" : (devname, "evi.General_TC.vxvRef") }
  for k in xrange(FUS_REGULAR_OBJ_NUM):
    sg['FusObj.i%d.LrrObjIdx' %k] = (devname, 'fus_asso_mat.LrrObjIdx.i%d'  %k)
    sg['FusObj.i%d.VidObjIdx' %k] = (devname, 'fus_s_asso_mat.VidObjIdx.i%d'  %k)
    sg['FusObj.i%d.dxv' %k]       = (devname, 'fus.ObjData_TC.FusObj.i%d.dxv' %k)
    sg['FusObj.i%d.dyv' %k]       = (devname, 'fus.ObjData_TC.FusObj.i%d.dyv' %k)
  for m in xrange(VID_OBJ_NUM):
    sg['VidObj.i%d.dyv' %m] = (devname, 'fus.SVidBasicInput_TC.VidObj.i%d.dyv' %m)
  sgs.append(sg)

# control pars
DDY_LIMIT = .5 # delta dy limit [m]
MERGE_LIMIT = 2. # defect interval merge time limit [s]
DIST_LIMIT = 80 # distance limit of investigation [m]

TITLE = 'Fusion - unstable dy'
INVALID_INTERVAL = 0,0

def shrink_interval_dx_close(st, end, dx, limit):
  """ Cut far away distances from interval beginning and end """
  close = dx[st:end] < limit
  if np.all(close):
    start,stop = st,end
  elif np.any(close):
    closeIdx, = np.where(close)
    start = st + closeIdx[0] # first occurrence of close distance
    stop = st + closeIdx[-1] + 1 # last occurrence of close distance
  else:
    start, stop = INVALID_INTERVAL # no close, all far away
  return start,stop

def createReport(scaleTime):
  emptyIntervals = cIntervalList(scaleTime)
  votes = interface.Batch.get_labelgroups('OHY object',
                                          'FUS VID object')
  names = interface.Batch.get_quanamegroups('ego vehicle', 'target')
  return Report(emptyIntervals, TITLE, votes=votes, names=names)


class cSearch(interface.iSearch):

  def check(self):
    group = interface.Source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    # create report
    scaleTime = interface.Source.getSignalFromSignalGroup(group, 'FusObj.i0.dyv')[0]
    report = createReport(scaleTime)
    egoSpeed = interface.Source.getSignalFromSignalGroup(group, 'egoSpeed')[1]
    egoSpeedKph = egoSpeed * 3.6
    # start investigating unstable dy events
    for l in xrange(FUS_REGULAR_OBJ_NUM):
      videoIdx = interface.Source.getSignalFromSignalGroup(group, 'FusObj.i%d.VidObjIdx' %l)[1]
      vidAssod = videoIdx != VID_INVALID_IDX
      if not np.any(vidAssod):
        continue
      fusDx = interface.Source.getSignalFromSignalGroup(group, 'FusObj.i%d.dxv' %l)[1]
      fusDy = interface.Source.getSignalFromSignalGroup(group, 'FusObj.i%d.dyv' %l)[1]
      for j in findUniqueValues(videoIdx, exclude=VID_INVALID_IDX):
        vidDy = interface.Source.getSignalFromSignalGroup(group, 'VidObj.i%d.dyv' %j)[1]
        vidAssod = videoIdx == j
        assoIntervals = maskToIntervals(vidAssod)
        for st,end in assoIntervals:
          st,end = shrink_interval_dx_close(st, end, fusDx, DIST_LIMIT)
          if (st,end) == INVALID_INTERVAL:
            continue # skip this interval (event far away)
          absError = np.abs( vidDy[st:end] - fusDy[st:end] )
          defectMask = absError > DDY_LIMIT
          if not np.any(defectMask):
            continue
          radarIdx = interface.Source.getSignalFromSignalGroup(group, 'FusObj.i%d.LrrObjIdx' %l)[1]
          try:
            i, = np.unique( radarIdx[st:end] )
          except ValueError:
            sys.stderr.write(
              'Error: multiple radar objects associated to video %d on [%.1f, %.1f]'
              %(j, scaleTime[st], scaleTime[end]) )
            continue
          defectIntervals = cIntervalList.fromMask(scaleTime[st:end], defectMask)
          finalIntervals = defectIntervals.merge(MERGE_LIMIT)
          for start,stop in finalIntervals:
            interval = int(st+start), int(st+stop)
            slicer = slice(*interval)
            # register votes
            index = report.addInterval(interval)
            report.vote(index, 'OHY object',     str(i))
            report.vote(index, 'FUS VID object', str(j))
            # register quantities
            egoSpeedOnEvent = egoSpeedKph[slicer]
            report.set( index, 'ego vehicle', 'speed', np.average(egoSpeedOnEvent) )
            dxOnEvent = fusDx[slicer]
            report.set( index, 'target', 'dx min', np.min(dxOnEvent) )
            report.set( index, 'target', 'dx max', np.max(dxOnEvent) )
            absErrorOnEvent = absError[start:stop]
            report.set( index, 'target', 'dy error max',     np.max(absErrorOnEvent) )
            report.set( index, 'target', 'dy error avg', np.average(absErrorOnEvent) )
    # sort intervals
    report.sort()
    return report

  def search(self, param, report):
    result = self.FAILED if report.isEmpty() else self.PASSED
    tags = ('CVR3', 'S-Cam', 'SDF', 'fusion')
    interface.Batch.add_entry(report,   result=result, tags=tags)
    return
