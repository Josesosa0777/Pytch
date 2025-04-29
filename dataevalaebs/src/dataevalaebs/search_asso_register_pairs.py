""" Registers association pairs as report intervals """
# -*- dataeval: method -*-

import numpy as np

import interface
from measproc.report2 import Report
from measproc.IntervalList import maskToIntervals, cIntervalList
from aebs.sdf.asso_cvr3_fus_result import AssoCvr3fusResult

DefParam = interface.NullParam

def createReport(scaleTime):
  title = 'Association pairs'
  votes = interface.Batch.get_labelgroups('OHY object', 'FUS VID object')
  return Report(cIntervalList(scaleTime), title, votes)

class cSearch(interface.iSearch):

  def check(self):
    a = AssoCvr3fusResult(interface.Source)
    a.calc()
    return a

  def fill(self, a):
    # create report
    report = createReport(a.scaleTime)
    # start investigating late associations
    for (i,j), indices in a.assoData.iteritems():
      assoMask = np.zeros(a.N, dtype=np.bool)
      assoMask[indices] = True
      assoIntervals = maskToIntervals(assoMask)
      for interval in assoIntervals:
        index = report.addInterval(interval)
        report.vote(index, 'OHY object',     str(i))
        report.vote(index, 'FUS VID object', str(j))
    # sort intervals in report
    report.sort()
    return report

  def search(self, param, report):
    result = self.FAILED if report.isEmpty() else self.PASSED
    interface.Batch.add_entry(report, result=result, tags=['CVR3', 'S-Cam', 'SDF', 'association'])
    return
