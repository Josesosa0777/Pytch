""" Investigate reasons of associated pair breakup """
# -*- dataeval: method -*-

import numpy as np

import interface
from measproc.report2 import Report
from measproc.IntervalList import maskToIntervals, cIntervalList
from search_asso_late import labelMovingState, labelAssociationProblem

DefParam = interface.NullParam

def createReport(scaleTime):
  title = 'Association breakups'
  votes = interface.Batch.get_labelgroups('OHY object',
                                          'FUS VID object',
                                          'asso problem detailed cause',
                                          'asso problem main cause',
                                          'moving direction',
                                          'moving state')
  return Report(cIntervalList(scaleTime), title, votes)

class cSearch(interface.iSearch):

  dep = ('search_asso_late', )

  def check(self):
    a = interface.Objects.check('search_asso_late')
    return a

  def fill(self, a):
    # create report
    report = createReport(a.scaleTime)
    # start investigating late associations
    for (i,j), indices in a.assoData.iteritems():
      radarObj = a.radarTracks[i]
      videoObj = a.videoTracks[j]
      assoMask = np.zeros(a.N, dtype=np.bool)
      assoMask[indices] = True
      assoIntervals = maskToIntervals(assoMask)
      for interval in assoIntervals:
        index = report.addInterval(interval)
        report.vote(index, 'OHY object',     str(i))
        report.vote(index, 'FUS VID object', str(j))
        st,end = interval
        if end == a.N:
          # end of measurement
          pass
        else:
          # label moving state during association
          labelMovingState(report, index, radarObj, st, end)
          # label association problem at breakup
          if (not a.masks[end,i,j] or not radarObj['historical_b'][end] or
              not radarObj['historical_b'][end]):
            report.vote(index, 'asso problem main cause', 'disappearance')
          else:
            labelAssociationProblem(report, index, end, end+1, a, i, j, radarObj['dx'])
    # sort intervals in report
    report.sort()
    return report

  def search(self, param, report):
    result = self.FAILED if report.isEmpty() else self.PASSED
    interface.Batch.add_entry(report, result=result, tags=['CVR3', 'S-Cam', 'SDF', 'association'])
    return
