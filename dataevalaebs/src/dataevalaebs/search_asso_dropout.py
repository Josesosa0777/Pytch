# -*- dataeval: method -*-
import numpy as np

import interface
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList
from aebs.sdf.asso_cvr3_fus_result import OHL_OBJ_NUM, VID_OBJ_NUM, AssoCvr3fusResult
from aebs.sdf.asso_cvr3_fus_recalc import defpars
from search_asso_replaced import optsgs

DefParam = interface.NullParam


def afterlifeEnd(valid, hist, n):
  """ determine end of object afterlife """
  invalid = ~(valid[n:])
  new = ~(hist[n:])
  down = invalid | new
  if np.any(down):
    downs, = np.where(down)
    end = n + int( downs[0] ) # numpy.where creates int32 indices
  else:
    end = valid.size
  return end

class cSearch(interface.iSearch):

  def check(self):
    a = AssoCvr3fusResult(interface.Source, useVideoHandle=False)
    a.calc()
    optgroups, _ = interface.Source._filterSignalGroups(optsgs)
    for optgroup in optgroups:
      if len(optgroup) == OHL_OBJ_NUM * VID_OBJ_NUM:
        break
    else:
      # optional signals are NOT present
      optgroup = None
    return a, optgroup

  def fill(self, a, optgroup):
    title = 'Dropouts in associations'
    votes = interface.Batch.get_labelgroups('OHY object',
                                            'FUS VID object',
                                            'sensors involved',
                                            'association weak point',
                                            'association problem cause',
                                            'asso afterlife')
    # create report
    report = Report( cIntervalList(a.scaleTime), title, votes )
    # start investigating dropouts
    last = a.objectPairs[0]
    for n, actual in enumerate(a.objectPairs):
      if actual != last:
        # asso pairs have changed since last cycle
        for (i,j) in last:
          if (i,j) not in actual:
            # pair is deleted or replaced
            for (ii,jj) in actual:
              if i == ii or j == jj:
                # pair is replaced, we are not interested
                break
            else:
              # pair ends but neither of the objects appear in another pair in next cycle
              radarEnd = afterlifeEnd( a.radarValid[i], a.radarHist[i], n )
              videoEnd = afterlifeEnd( a.videoValid[j], a.videoHist[j], n )
              # create basic labels
              labels = {'OHY object' : str(i), 'FUS VID object' : str(j),}
              # determine why association ended
              if radarEnd == n or videoEnd == n:
                labels['association problem cause'] = 'disappearance'
              else:
                if a.radarDx[i][n] > defpars.dExtFusObjMaxDx:
                  labels['association weak point'] = 'too far range'
                if optgroup:
                  # lazy signal query (only when needed)
                  oldPairProb = interface.Source.getSignalFromSignalGroup(optgroup, "ProbAssoMat.i%d.i%d" %(i,j))[1]
                  if oldPairProb[n] < defpars.prob1AsoProbLimit:
                    labels['association problem cause'] = 'gating'
                  else:
                    labels['association problem cause'] = 'unknown'
                else:
                  labels['association problem cause'] = 'n/a'

              if radarEnd == videoEnd == n:
                # both objects disappear (causing the end of association)
                index = report.addInterval( (n,n+1) )
                for labelgroup, label in labels.iteritems():
                  report.vote(index, labelgroup, label)
                report.vote(index, 'sensors involved', 'both')
                report.vote(index, 'asso afterlife', 'no')
              elif radarEnd > n and videoEnd == n:
                # radar object has afterlife, camera disappears (causing the end of association)
                for m, pairs in enumerate( a.objectPairs[n:radarEnd] ):
                  if i in [ii for ii,jj in pairs]:
                    # radar object is reassociated in a new pair
                    labels['asso afterlife'] = 'new pair'
                    break
                else:
                  # radar object is NOT reassociated later
                  labels['asso afterlife'] = 'lonely'
                end = n + m + 1
                index = report.addInterval( (n,end) )
                for labelgroup, label in labels.iteritems():
                  report.vote(index, labelgroup, label)
                report.vote(index, 'sensors involved', 'camera')
              elif videoEnd > n and radarEnd == n:
                # camera object has afterlife, radar disappears (causing the end of association)
                for m, pairs in enumerate( a.objectPairs[n:videoEnd] ):
                  if j in [jj for ii,jj in pairs]:
                    # camera object is reassociated in a new pair
                    labels['asso afterlife'] = 'new pair'
                    break
                else:
                  # camera object is NOT reassociated later
                  labels['asso afterlife'] = 'lonely'
                end = n + m + 1
                index = report.addInterval( (n,end) )
                for labelgroup, label in labels.iteritems():
                  report.vote(index, labelgroup, label)
                report.vote(index, 'sensors involved', 'radar')
              else:
                # both objects are alive when association ends
                laterEnd = max(radarEnd, videoEnd)
                radarReasso = False
                videoReasso = False
                for m, pairs in enumerate( a.objectPairs[n:laterEnd] ):
                  end = n + m + 1
                  radarAlive = end <= radarEnd
                  videoAlive = end <= videoEnd
                  if radarAlive and videoAlive and (i,j) in pairs:
                    # original pair is reassociated
                    radarReasso = True
                    videoReasso = True
                    index = report.addInterval( (n,end) )
                    for labelgroup, label in labels.iteritems():
                        report.vote(index, labelgroup, label)
                    report.vote(index, 'sensors involved', 'both')
                    report.vote(index, 'asso afterlife', 'original pair')
                  else:
                    # original pair is NOT reassociated, objects might be in new pairs
                    if radarAlive and not radarReasso and i in [ii for ii,jj in pairs]:
                      # radar is reassociated
                      radarReasso = True
                      index = report.addInterval( (n,end) )
                      for labelgroup, label in labels.iteritems():
                        report.vote(index, labelgroup, label)
                      report.vote(index, 'sensors involved', 'camera')
                      report.vote(index, 'asso afterlife', 'new pair')
                    if videoAlive and not videoReasso and j in [jj for ii,jj in pairs]:
                      # video is reassociated
                      index = report.addInterval( (n,end) )
                      for labelgroup, label in labels.iteritems():
                        report.vote(index, labelgroup, label)
                      report.vote(index, 'sensors involved', 'radar')
                      report.vote(index, 'asso afterlife', 'new pair')
                  if radarReasso and videoReasso:
                    break
                else:
                  # one (or both) of them is NOT reassociated
                  if not radarReasso:
                    index = report.addInterval( (n,radarEnd) )
                    for labelgroup, label in labels.iteritems():
                        report.vote(index, labelgroup, label)
                    report.vote(index, 'sensors involved', 'radar')
                    report.vote(index, 'asso afterlife', 'lonely')
                  if not videoReasso:
                    index = report.addInterval( (n,videoEnd) )
                    for labelgroup, label in labels.iteritems():
                        report.vote(index, labelgroup, label)
                    report.vote(index, 'sensors involved', 'camera')
                    report.vote(index, 'asso afterlife', 'lonely')
      last = actual
    return report

  def search(self, param, report):
    result = self.FAILED if report.isEmpty() else self.PASSED
    interface.Batch.add_entry(report, result=result, tags=['CVR3', 'S-Cam', 'SDF', 'association', 'dropout'])    
    return
