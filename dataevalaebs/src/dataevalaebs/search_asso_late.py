""" Investigate latency of fresh object pairs (have not been associated before) below 100m """
# -*- dataeval: method -*-

import numpy as np

import interface
from measproc.report2 import Report
from measproc.IntervalList import maskToIntervals, cIntervalList
from aebs.sdf.asso_cvr3_fus_recalc import AssoCvr3fusRecalc

DefParam = interface.NullParam


DIST_LIMIT = 100 # distance limit [m]
WINDOW_JUMPING_TRACK = 5 # min number of cycles where state jump is investigated

def exclude_interval_object_new(lates, radarHist, videoHist):
  for k, (st,end) in enumerate( list(lates) ):
    # skip single interval as it wouldn't be changed anyway
    if end-st > 1:
      # one (or both) sensor is always new at the beginning of coexistence
      radarNew = ~(radarHist[st+1:end])
      videoNew = ~(videoHist[st+1:end])
      objectsNew = radarNew | videoNew
      if np.any(objectsNew):
        news, = np.where(objectsNew)
        lastNew = int( news[-1] ) # numpy.where creates int32 indices
        lates[k] = (st+1+lastNew,end)
  return

def exclude_interval_object_in_earlier_pair(lates, a, i, j):
  for st,end in list(lates):
    # loop backwards
    for l, pairs in enumerate( a.objectPairs[st:end][::-1] ):
      cond = [True for pair in pairs if i in pair or j in pair]
      if cond:
        n = end-l-1
        if n == end-1:
          lates.remove( (st,end) ) # remove interval as asso was replaced
        elif n == st:
          pass # no earlier asso found, leave interval unchanged
        else:
          lates.remove( (st,end) ) # remove interval as one of the objects was in an earlier pair
        break
  return

def exclude_interval_object_far_away(lates, radarDx, limit=DIST_LIMIT):
  removables = []
  for k, (st,end) in enumerate( list(lates) ):
    farMask = radarDx[st:end] > limit
    if np.any(farMask):
      farIndices, = np.where(farMask)
      lastFarIndex = int( farIndices[-1] )
      n = st + 1 + lastFarIndex
      if n == end:
        removables.append(k) # remove complete interval as radar object dx was above limit the whole time
      else:
        lates[k] = (n,end)
  lates[:] = [elem for i, elem in enumerate(lates) if i not in removables]
  return

def createReport(scaleTime):
  title = 'Late associations'
  votes = interface.Batch.get_labelgroups('OHY object',
                                          'FUS VID object',
                                          'asso problem detailed cause',
                                          'asso problem main cause',
                                          'tracking',
                                          'moving direction',
                                          'moving state')
  return Report(cIntervalList(scaleTime), title, votes)

def labelMovingState(report, index, radarObj, st, end):
  # determine moving direction and moving state on the interval
  # The following state transitions are allowed:
    # any state      -> same state (it is allowed to stay indefinitely in any state)
    # not classified -> standing
    # not classified -> moving
    # not classified -> oncoming
    # standing       -> moving
    # standing       -> oncoming
    # moving         -> "stopped moving"
    # oncoming       -> "stopped oncoming"
    # stopped mov/onc-> oncoming
    # stopped mov/onc-> moving

  unclassified = radarObj['notClassified_b'][st:end]
  ongoing      = radarObj['ongoing_b'][st:end]
  oncoming     = radarObj['oncoming_b'][st:end]
  stationary   = radarObj['stationary_b'][st:end]
  stopped      = radarObj['stopped_b'][st:end]
  oncomingStop = radarObj['oncomingStopped_b'][st:end]

  if np.any(unclassified):
    report.vote(index, 'moving state', 'unclassified')
  if np.any(stationary):
    report.vote(index, 'moving state', 'stationary')
  if np.any(ongoing):
    report.vote(index, 'moving direction', 'ongoing')
    report.vote(index, 'moving state', 'moving')
  if np.any(oncoming):
    report.vote(index, 'moving direction', 'oncoming')
    report.vote(index, 'moving state', 'moving')
  if np.any( stopped ):
    report.vote(index, 'moving direction', 'ongoing')
    report.vote(index, 'moving state', 'stopped')
  if np.any( oncomingStop ):
    report.vote(index, 'moving direction', 'oncoming')
    report.vote(index, 'moving state', 'stopped')
  return

def labelTrackingProblem(report, index, videoObj, st, end, windowSize=WINDOW_JUMPING_TRACK):
  if end-st > windowSize+1:
    # peak detection in 1st order absolute difference, assumimg only one peak
    vidDxAbsDiff = np.abs( np.diff( videoObj['dx'][st:end] ) )
    if hasSinglePeak(vidDxAbsDiff, k=windowSize):
      report.vote(index, 'tracking', 'jumping')
  return

def hasSinglePeak(array, k=5, h=3.):
  """
  :Parameters:
    array : ndarray
      Series of sample points
    k : int, optional
      Window border distance from peak (window size is 2 * `k` + 1)
    h : float, optional
      Constant for peak condition
  :ReturnType: bool
  """
  assert array.size > k
  hasPeak = False
  wsize = 2 * k + 1
  numOfChunks = max(1, array.size - wsize + 1)
  for i in xrange(numOfChunks):
    window = array[i:i+wsize]
    hasPeak = hasSinglePeakInWindow(window, h)
    if hasPeak:
      break
  return hasPeak

def hasSinglePeakInWindow(window, h):
  detected = False
  peakIndex = np.argmax(window)
  peakNeighbours = np.concatenate( [window[:peakIndex], window[peakIndex+1:]] )
  mean = np.mean(peakNeighbours)
  std = np.std(peakNeighbours)
  peak = window[peakIndex]
  # peak condition (see Chebyshev's inequality)
  if np.abs(peak - mean) >= h * std:
    detected = True
  return detected

def labelAssociationProblem(report, index, st, end, a, i, j, dx):
  # if gate was passed, only the solver could block the way
  filteredAssoProb = a.filteredAssoProb[st:end,i,j]
  if np.any( filteredAssoProb > a.params.prob1AsoProbLimit ):
    report.vote(index, 'asso problem main cause', 'solver')
  # check if pair failed to pass the gate
  if np.any(filteredAssoProb < a.params.prob1AsoProbLimit):
    report.vote(index, 'asso problem main cause', 'gate')
  currentAssoProb = a.currentAssoProb[st:end,i,j]
  # check if actual asso prob was always above filtered value where gate was not passed
  currentProbBlameMask = (currentAssoProb <= filteredAssoProb) & (filteredAssoProb < 1)
  if np.any(currentProbBlameMask):
    filteredAssoProbOk = filteredAssoProb[currentProbBlameMask]
    angleAssoProb   = a.measures.angle    [st:end,i,j][currentProbBlameMask]
    dxAssoProb      = a.measures.dx       [st:end,i,j][currentProbBlameMask]
    counterAssoProb = a.measures.counter  [st:end,i,j][currentProbBlameMask]
    invTtcAssoProb  = a.measures.invttc   [st:end,i,j][currentProbBlameMask]
    occluded        = a.measures.occlusion[st:end,i,j][currentProbBlameMask]

    if np.any(angleAssoProb <= filteredAssoProbOk):
      report.vote(index, 'asso problem detailed cause', 'angle')
    dxAssoProbBlameMask = dxAssoProb <= filteredAssoProbOk
    if np.any(dxAssoProbBlameMask):
      radarDx = dx[st:end][currentProbBlameMask]
      if np.any(radarDx[dxAssoProbBlameMask] > a.params.dExtFusObjMaxDx):
        report.vote(index, 'asso problem detailed cause', 'dx far range')
      else:
        report.vote(index, 'asso problem detailed cause', 'dx')
    if np.any(counterAssoProb <= filteredAssoProbOk):
      report.vote(index, 'asso problem detailed cause', 'counter')
    if np.any(invTtcAssoProb <= filteredAssoProbOk):
      report.vote(index, 'asso problem detailed cause', 'invttc')
    if np.any(occluded):
      report.vote(index, 'asso problem detailed cause', 'occlusion')
  else:
    report.vote(index, 'asso problem main cause', 'filter')
  return

def findLates(a, i, j, bothValid, radarHist, videoHist, radarDx):
  indices = a.assoData[i,j]
  assoMask = np.zeros(a.N, dtype=np.bool)
  assoMask[indices] = True
  defectMask = bothValid & (~assoMask)
  if np.any(defectMask):
    # search for intervals where asso seems to be late
    defects = maskToIntervals(defectMask)
    assos = maskToIntervals(assoMask)
    lates = [ (st,end) for st,end in defects for start,_ in assos if end == start ]
    if lates:
      # exclude intervals where one of the objects became new
      exclude_interval_object_new(lates, radarHist, videoHist)
      # exclude intervals where one of the objects was involved in another pair earlier
      exclude_interval_object_in_earlier_pair(lates, a, i, j)
      # exclude part of intervals where OHY obj dx was above distance limit
      exclude_interval_object_far_away(lates, radarDx)
  else:
    lates = []
  return lates

class cSearch(interface.iSearch):

  def check(self):
    a = AssoCvr3fusRecalc(interface.Source)
    a.calc()
    return a

  def fill(self, a):
    # create report
    report = createReport(a.scaleTime)
    # start investigating late associations
    for (i,j) in a.assoData:
      radarObj = a.radarTracks[i]
      videoObj = a.videoTracks[j]
      validMask = a.masks[:,i,j]
      lates = findLates(a, i, j, validMask,
                        radarObj['historical_b'],
                        videoObj['historical_b'],
                        radarObj['dx'])
      # register late asso intervals (if any)
      for interval in lates:
        st,end = interval
        index = report.addInterval(interval)
        report.vote(index, 'OHY object',     str(i))
        report.vote(index, 'FUS VID object', str(j))
        # set moving state labels
        labelMovingState(report, index, radarObj, st, end)
        # look for state jump in camera tracking
        labelTrackingProblem(report, index, videoObj, st, end)
        # determine association problems by back propagating errors
        labelAssociationProblem(report, index, st, end, a, i, j, radarObj['dx'])
    # sort intervals in report
    report.sort()
    return report

  def search(self, param, report):
    result = self.FAILED if report.isEmpty() else self.PASSED
    interface.Batch.add_entry(report, result=result, tags=['CVR3', 'S-Cam', 'SDF', 'association', 'late'])
    return
