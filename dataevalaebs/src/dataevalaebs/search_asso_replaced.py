# -*- dataeval: method -*-
import interface
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList
from aebs.sdf.asso_cvr3_fus_result import OHL_OBJ_NUM, VID_OBJ_NUM, devnames, AssoCvr3fusResult
from aebs.sdf.asso_cvr3_fus_recalc import defpars

DefParam = interface.NullParam

# optional signals (might not be recorded)
optsgs = []
for devname in devnames:
  optsg = {}
  for k in xrange(OHL_OBJ_NUM):
    for l in xrange(VID_OBJ_NUM):
      optsg["ProbAssoMat.i%d.i%d" %(k,l)] = devname, "fus_s_asso_mat.ProbAssoMat.probability.i%d.i%d" %(k,l)
  optsgs.append(optsg)

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
    title = 'Replaced associations'
    votes = interface.Batch.get_labelgroups('OHY object', 'FUS VID object', 'sensor type', 'asso problem main cause')
    # create report
    report = Report( cIntervalList(a.scaleTime), title, votes )
    # start investigating replaced pairs
    last = a.objectPairs[0]
    for n, actual in enumerate(a.objectPairs):
      if actual != last:
        # asso pairs have changed since last cycle
        for (i,j) in last:
          if (i,j) not in actual:
            # pair is deleted or replaced
            for (ii,jj) in actual:
              if i == ii or j == jj:
                index = report.addInterval( (n,n+1) )
                report.vote(index, 'OHY object',     str(i))
                report.vote(index, 'FUS VID object', str(j))
                # check which sensor's object was replaced
                if i == ii:
                  newpair = i,jj
                  report.vote(index, 'sensor type', 'camera')
                else:
                  newpair = ii,j
                  report.vote(index, 'sensor type', 'radar')
                # determine possible causes
                if not a.masks[i,j][n]:
                  report.vote(index, 'asso problem main cause', 'disappearance')
                elif optgroup:
                  # lazy signal query (only when needed)
                  oldPairProb = interface.Source.getSignalFromSignalGroup(optgroup, "ProbAssoMat.i%d.i%d" %(i,j)  )[1]
                  newPairProb = interface.Source.getSignalFromSignalGroup(optgroup, "ProbAssoMat.i%d.i%d" %newpair)[1]
                  if oldPairProb[n] < defpars.prob1AsoProbLimit:
                    report.vote(index, 'asso problem main cause', 'gate')
                  elif oldPairProb[n] < newPairProb[n]:
                    report.vote(index, 'asso problem main cause', 'solver')
                  else:
                    report.vote(index, 'asso problem main cause', 'unknown')
                else:
                  # problem cause can not be determined w/o optional signals
                  pass
      last = actual
    return report

  def search(self, param, report):
    result = self.FAILED if report.isEmpty() else self.PASSED
    interface.Batch.add_entry(report, result=result, tags=['CVR3', 'S-Cam', 'SDF', 'association', 'replaced'])    
    return
