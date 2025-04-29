""" Search for late object detection candidates of CVR3 and S-Cam sensors """
# -*- dataeval: method -*-

import numpy as np

import interface
from measproc.report2 import Report
from measproc.IntervalList import maskToIntervals, cIntervalList
from aebs.sdf.asso_cvr3_fus_result import AssoCvr3fusResult

DefParam = interface.NullParam

def createReport(scaleTime):
  title = 'Late radar and camera object detection candidates'
  votes = interface.Batch.get_labelgroups('OHY object',
                                          'FUS VID object',
                                          'sensor type',
                                         )
  return Report(cIntervalList(scaleTime), title, votes)

def registerIntervals(report, sensorLates, sensorName):
  for (i,j), lates in sensorLates.iteritems():
    for interval in lates:
      index = report.addInterval(interval)
      report.vote(index, 'OHY object',     str(i))
      report.vote(index, 'FUS VID object', str(j))
      report.vote(index, 'sensor type',    sensorName)
  return

def calcLatency(bothObjAlive, objHist, lateDetections, i, j):
  for k in bothObjAlive:
    new = ~(objHist[:k])
    if np.any(new):
      news, = np.where(new)
      lastNew = int( news[-1] ) # numpy.where creates int32 indices
      lates = lateDetections.setdefault((i,j), [])
      lates.append( [lastNew, k] )
  return

def getRadarCameraLateDetection(a):
  radarLates = {}
  videoLates = {}
  """ { (i,j) : lates<list> } """
  for (i,j), indices in a.assoData.iteritems():
    assoMask = np.zeros(a.N, dtype=np.bool)
    assoMask[indices] = True
    validMask = a.masks[i,j]
    defectMask = validMask & (~assoMask)
    if np.any(defectMask):
      # search for intervals where asso seems to be late
      defects = maskToIntervals(defectMask)
      assos = maskToIntervals(assoMask)
      assoLates = [ (st,end) for st,end in defects for start,_ in assos if end == start ]
      if assoLates:
        bothObjAliveRadarEarlier = []
        bothObjAliveVideoEarlier = []
        for st,end in assoLates:
          # loop backwards to see if pair was associated earlier
          for l, pairs in enumerate( a.objectPairs[st:end][::-1] ):
            n = end-l-1
            if n == 0:
              # both objects co-existed from beginning of measurement (not interesting)
              break
            radarNewNow = ~(a.radarHist[i][n])
            videoNewNow = ~(a.videoHist[j][n])
            earlierFound = [True for pair in pairs if i in pair or j in pair]
            if   not earlierFound and not videoNewNow and not radarNewNow:
              # 000: nothing happened, take next step backwards
              continue
            elif not earlierFound and not videoNewNow and     radarNewNow:
              # 001: camera started tracking earlier
              bothObjAliveVideoEarlier.append(n)
              break
            elif not earlierFound and     videoNewNow and not radarNewNow:
              # 010: radar started tracking earlier
              bothObjAliveRadarEarlier.append(n)
              break
            elif not earlierFound and     videoNewNow and     radarNewNow:
              # 011: both started tracking at same time (not interesting)
              break
            elif     earlierFound and not videoNewNow and not radarNewNow:
              # 100: no object changed but one of them was associated with another object earlier (asso replaced/dropout)
              break
            else:
              # situation is suspicious, take no action
              break
          else:
            # association dropout
            pass
        # calculate latency of object detections
        calcLatency(bothObjAliveRadarEarlier, a.radarHist[i], videoLates, i, j)
        calcLatency(bothObjAliveVideoEarlier, a.videoHist[j], radarLates, i, j)
  return radarLates, videoLates


class cSearch(interface.iSearch):

  def check(self):
    a = AssoCvr3fusResult(interface.Source)
    a.calc()
    return a

  def fill(self, a):
    # create report
    report = createReport(a.scaleTime)
    # search for late detections
    radarLates, videoLates = getRadarCameraLateDetection(a)
    # register results in report
    registerIntervals(report, radarLates, 'radar')
    registerIntervals(report, videoLates, 'camera')
    # sort intervals in report
    report.sort()
    return report

  def search(self, param, report):
    result = self.FAILED if report.isEmpty() else self.PASSED
    interface.Batch.add_entry(report, result=result, tags=['CVR3', 'S-Cam', 'SDF', 'association', 'late'])
    return
