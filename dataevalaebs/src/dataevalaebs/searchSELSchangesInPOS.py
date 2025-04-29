import sys

import measparser
import measproc
import interface

POS_MTX_ELEM_NUM = 6

deviceName = "MRR1plus"
titlePattern = 'SELS changes in POSition matrix - %s'
handleAliasTemplate = 'ObjectList.i%d'
warningTemplate = 'Warning: search ended without result (reason: %s)'

class cParameter(interface.iParameter):
  def __init__(self, name):
    self.name = name
    self.genKeys()
    pass
# instantiation of module parameters
par000 = cParameter('par000')
par001 = cParameter('par001')
par002 = cParameter('par002')
par003 = cParameter('par003')
par004 = cParameter('par004')
par005 = cParameter('par005')
par006 = cParameter('par006')
par007 = cParameter('par007')
par008 = cParameter('par008')
par009 = cParameter('par009')
par010 = cParameter('par010')
par011 = cParameter('par011')
par012 = cParameter('par012')
par013 = cParameter('par013')
par014 = cParameter('par014')
par015 = cParameter('par015')
par016 = cParameter('par016')
par017 = cParameter('par017')
par018 = cParameter('par018')
par019 = cParameter('par019')
par020 = cParameter('par020')
par021 = cParameter('par021')
par022 = cParameter('par022')
par023 = cParameter('par023')
par024 = cParameter('par024')
par025 = cParameter('par025')
par026 = cParameter('par026')
par027 = cParameter('par027')
par028 = cParameter('par028')
par029 = cParameter('par029')
par030 = cParameter('par030')

signalGroup = {}
for i in xrange(POS_MTX_ELEM_NUM):
  signalGroup[handleAliasTemplate %i] = (deviceName, "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i%d" %i)
signalGroups = [signalGroup,]

class cSearch(interface.iSearch):
  
  def check(self):
    source = self.get_source('main')
    group = source.selectSignalGroup(signalGroups)
    return group
    
  def fill(self, group):
    return group
  
  def search(self, param, group):
    batch = self.get_batch()
    source = self.get_source('main')
    # get sels device names from backup
    selsDeviceNames = source.BackupParser.getDeviceNames('SelsValidity')
    try:
      selsDeviceName, = [elem for elem in selsDeviceNames if param.name in elem]
      selsSignalGroup = {'validity' : (selsDeviceName, 'SelsValidity')}
      for index in xrange(POS_MTX_ELEM_NUM):
        selsSignalGroup[handleAliasTemplate %index] = (selsDeviceName, 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i%d' %index)
      selsSignalGroups = [selsSignalGroup,]
      selsGroup = source.selectSignalGroup(selsSignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      # necessary sels signals are not present
      print >> sys.stderr, warningTemplate %error.message
    except ValueError, error:
      # missing / ambigous backup for sels parameter
      print >> sys.stderr, warningTemplate %error.message
    else:
      # query the available signals from the original meas
      tcTime = source.getSignalFromSignalGroup(group, handleAliasTemplate %0)[0] # dummy time query
      posHandlesMeas = {} # { posIndex<int> : handle<ndarray> }
      for index in xrange(POS_MTX_ELEM_NUM):
        signal = source.getSignalFromSignalGroup(group, handleAliasTemplate %index)[1]
        posHandlesMeas[index] = signal
      # store intervals where handle of SELS position matrix element has changed
      intervalsHandleChangedUnion = measproc.cIntervalList(tcTime)
      # loop through sels POS elements
      for index in xrange(POS_MTX_ELEM_NUM):
        handleSels = source.getSignalFromSignalGroup(selsGroup, handleAliasTemplate %index)[1]
        handleMeas = posHandlesMeas[index]
        intervalsHandleChanged = source.compare(tcTime, handleMeas, measproc.not_equal, handleSels)
        intervalsHandleChangedUnion = intervalsHandleChangedUnion.union(intervalsHandleChanged)
      # get valid intervals of the SELS run
      validity = source.getSignalFromSignalGroup(selsGroup, 'validity')[1]
      intervalsValid = source.compare(tcTime, validity, measproc.equal, True)
      # intersect the two above intervals
      intervals = intervalsHandleChangedUnion.intersect(intervalsValid)
      if intervals:
        result = self.PASSED
      else:
        result = self.FAILED
      title = titlePattern %param.name
      # register report
      report = measproc.cIntervalListReport(intervals, title)
      batch.add_entry(report, result)
    return
