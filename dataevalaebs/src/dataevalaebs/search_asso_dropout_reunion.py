# -*- dataeval: method -*-

""" Search for association dropouts that are later followed by reunion """

import numpy as np

import interface
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList
from aebs.sdf.asso_cvr3_fus_result import AssoCvr3fusResult, OHL_OBJ_NUM, devnames
from search_asso_dropout_reunion_flr20 import SearchFlr20AssoReunion

DefParam = interface.NullParam

sgs = []
for devname in devnames:
  sg = { "egoSpeed" : (devname, "evi.General_TC.vxvRef") }
  for k in xrange(OHL_OBJ_NUM):
    sg['ohy.i%d.dx' %k] = (devname, "ohy.ObjData_TC.OhlObj.i%d.dx" %k)
  sgs.append(sg)

def createReport(scaleTime):
  title = 'Association dropout - reunion'
  emptyIntervals = cIntervalList(scaleTime)
  votes = interface.Batch.get_labelgroups('OHY object',
                                          'FUS VID object')
  names = interface.Batch.get_quanamegroups('ego vehicle', 'target')
  return Report(emptyIntervals, title, votes=votes, names=names)

def registerIntervals(report, reunions, source, group):
  egoSpeed = source.getSignalFromSignalGroup(group, 'egoSpeed')[1]
  egoSpeedKph = egoSpeed * 3.6
  for (i,j), reunion in reunions.iteritems():
    dx = source.getSignalFromSignalGroup(group, 'ohy.i%d.dx' %i)[1]
    for interval in reunion:
      index = report.addInterval(interval)
      # labels
      report.vote(index, 'OHY object',     str(i))
      report.vote(index, 'FUS VID object', str(j))
      # quantities
      st,end = interval
      dxOnEvent = dx[st:end]
      egoSpeedOnEvent = egoSpeedKph[st:end]
      report.set( index, 'target', 'dx min', np.min(dxOnEvent) )
      report.set( index, 'target', 'dx max', np.max(dxOnEvent) )
      report.set( index, 'ego vehicle', 'speed', np.average(egoSpeedOnEvent) )
  return

def getReunions(a):
  reunions = {}
  for i,j in a.assoData.iterkeys():
    reunion = SearchFlr20AssoReunion.findReunion(
                a, i, j, a.masks[i,j], a.radarHist[i], a.videoHist[j])
    if reunion:
      reunions[i,j] = reunion
  return reunions


class cSearch(interface.iSearch):

  def check(self):
    a = AssoCvr3fusResult(interface.Source)
    a.calc()
    group = interface.Source.selectSignalGroup(sgs)
    return a, group

  def fill(self, a, group):
    # create report
    report = createReport(a.scaleTime)
    # search for reunions
    reunions = getReunions(a)
    # register results in report
    registerIntervals(report, reunions, interface.Source, group)
    # sort intervals in report
    report.sort()
    return report

  def search(self, param, report):
    result = self.FAILED if report.isEmpty() else self.PASSED
    tags = ('CVR3', 'S-Cam', 'SDF', 'association', 'dropout')
    interface.Batch.add_entry(report, result=result, tags=tags)
    return
