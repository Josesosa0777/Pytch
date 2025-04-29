""" Search and label OHY object indices corresponding to the given position matrix element """
# -*- dataeval: method -*-

import numpy as np

import interface
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from measparser.signalproc import findUniqueValues
from aebs.fill.fillCVR3_OHL import OHL_OBJ_NUM
from search_asso_late import labelMovingState

POS_MTX_ELEM_NUM = 6
INVALID_OHL_INDEX = 255

name2position = {'L1' : 0,
                 'S1' : 1,
                 'R1' : 2,
                 'L2' : 3,
                 'S2' : 4,
                 'R2' : 5}

class cParameter(interface.iParameter):
  def __init__(self, pos):
    self.pos = pos
    self.genKeys()
    self.posname = name2position[self.pos]
    return
# instantiation of module parameters
L1 = cParameter('L1')
S1 = cParameter('S1')
R1 = cParameter('R1')
L2 = cParameter('L2')
S2 = cParameter('S2')
R2 = cParameter('R2')

devnames = 'RadarFC',

radarAttrib2signal = {
  "OhlObj.i%d.stationary_b"      : "ohy.ObjData_TC.OhlObj.i%d.c.c.Stand_b",
  "OhlObj.i%d.stopped_b"         : "ohy.ObjData_TC.OhlObj.i%d.c.c.Stopped_b",
  "OhlObj.i%d.notClassified_b"   : "ohy.ObjData_TC.OhlObj.i%d.c.c.NotClassified_b",
  "OhlObj.i%d.ongoing_b"         : "ohy.ObjData_TC.OhlObj.i%d.c.c.Drive_b",
  "OhlObj.i%d.oncoming_b"        : "ohy.ObjData_TC.OhlObj.i%d.c.c.DriveInvDir_b",
  "OhlObj.i%d.oncomingStopped_b" : "ohy.ObjData_TC.OhlObj.i%d.c.c.StoppedInvDir_b",
}

sgs = []
for devName in devnames:
  sg = {'dummy' : (devName, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i0')}
  for k in xrange(OHL_OBJ_NUM):
    for aliastemplate, signaltemplate in radarAttrib2signal.iteritems():
      sg[aliastemplate %k] = devName, signaltemplate %k
  sgs.append(sg)

def prepareOhyObject(source, group, i):
  obj = {}
  for aliastemplate in radarAttrib2signal:
    signal = source.getSignalFromSignalGroup(group, aliastemplate %i)[1]
    alias = aliastemplate.split('.')[-1]
    if alias.endswith('_b'):
      signal = signal.astype(np.bool)
    obj[alias] = signal
  return obj

class cSearch(interface.iSearch):

  def check(self):
    group = interface.Source.selectSignalGroup(sgs)
    devname = group['dummy'][0]
    return devname, group

  def fill(self, devname, group):
    return devname, group

  def search(self, param, devname, group):
    # find object indices
    pos = name2position[param.posname]
    t, ohyIndices = interface.Source.getOHYindicesAtPosition(devname, pos, InvalidOHYindex=INVALID_OHL_INDEX)
    # create report
    title = 'CVR3 OHY objects at %s position' %param.posname
    votes = interface.Batch.get_labelgroups('OHY object', 'moving state', 'moving direction')
    report = Report(cIntervalList(t), title, votes)
    # label object indices
    for ohyIndex in findUniqueValues(ohyIndices, exclude=INVALID_OHL_INDEX):
      mask = ohyIndex == ohyIndices
      intervals = maskToIntervals(mask)
      for interval in intervals:
        index = report.addInterval(interval)
        report.vote(index, 'OHY object', str(ohyIndex))
        # label moving state
        st,end = interval
        obj = prepareOhyObject(interface.Source, group, ohyIndex)
        labelMovingState(report, index, obj, st, end)
    # sort intervals in report
    report.sort()
    # register report
    result = self.FAILED if report.isEmpty() else self.PASSED
    interface.Batch.add_entry(report, result=result, tags=['CVR3', 'S-Cam', 'SDF', 'association'])
    return
