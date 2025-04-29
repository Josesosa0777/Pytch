"""
This module shows the 5 different obstacle classification probability signals of the relevant intro, 
plotted against target distance. 
Since all the 5 signals are only present on ohl level, the fus handles of the relevant 
intro (one handle at a specific time) are transformed into ohl object indices as follows:
fus handle -> fus index -> ohl index
The calculations and plots are based on events from a selected report (interface.Report instance), 
and the event intervals are extended with the history of the corresponding ohl object from birth till its end. 
A unique index relationship is assumed, i.e. for an intro fus handle only one ohl object is related if possible.
"""
import os

import numpy as np

import datavis
import measparser
import interface

OBS_CLASSIF_TYPES = ('obstacle', 
                     'underpassable', 
                     'overrunable', 
                     'interference', 
                     'unknown')
INVALID_FUS_HANDLE = 0
INVALID_FUS_INDEX  = 255
INVALID_OHL_INDEX  = 255
INVALID_FUS_2_OHL_ASSOC = 255
FUS_ASSOC_NUM = 32
OHL_OBJ_NUM = 40
UWORD_MAX = float(2**15 - 1)
SPEED_LIM_KMPH = 15.
MPS_2_KMPH = 3.6

# constants to correct wrong reflected power (dbPowerFilt) normalization
N_dBUW_uw   = float(256)
N_dUW_ub    = float(128)
# constants to correct wrong LLR3/CVR3 OHL object variance normalization
N_vSL_ul       = float(2**24) # velocity   [m/s] LRR3/CVR3 norm.h
N_varNormSL_ul = float(2**20) # variance   [m^2]   LRR3/CVR3 norm.h
physUnit2norm = {
  'm/s' : N_vSL_ul,
  'm^2' : N_varNormSL_ul,
  'dB'  : N_dBUW_uw,
  'm'   : N_dUW_ub,
}
Signal2PhysUnit = {
# signal        : correct phys unit
  'dx'                      : 'm',
  'dbPowerFilt'             : 'dB',
  'wInterfProb'             : '-',
  'wConstElem'              : '-',
  'varDy'                   : 'm^2',
  'dLength'                 : 'm',
  'MeasCounter'             : '',
  'DEBUG_probRCSabsFeature' : '',
  'DEBUG_probVariance'      : '',
}
def correctNorming(signal, physUnit, physUnitMeas):
  if physUnitMeas != physUnit:
    normUsedInMeas = physUnit2norm[physUnitMeas]
    normCorrect    = physUnit2norm[physUnit]
    signal = signal * (normUsedInMeas / normCorrect)
  return signal

LRR3shortDeviceName = 'ECU'
CVR3shortDeviceName = 'MRR1plus'
ShortDeviceNames = [LRR3shortDeviceName, CVR3shortDeviceName]
Device2SensorName = { LRR3shortDeviceName : 'LRR3',
                      CVR3shortDeviceName : 'CVR3'}

# common signals (both in LRR3 and CVR3)
SignalGroups = []
for DeviceName in ShortDeviceNames:
  SignalGroup = {'introFUShandle':   (DeviceName, 'sit.IntroFinder_TC.Intro.i0.ObjectList.i0'),
                 'egoSpeed'      :   (DeviceName, 'evi.General_TC.vxvRef'),
                }
  for k in xrange(FUS_ASSOC_NUM):
    SignalGroup['fus.i%d_to_ohl_assoc'%k] = (DeviceName, 'fus_asso_mat.LrrObjIdx.i%d'%k)
  for m in xrange(OHL_OBJ_NUM):
    SignalGroup['dx_%d'                   % m                       ] = (DeviceName, 'ohl.ObjData_TC.OhlObj.i%d.dx'                  %m)
    SignalGroup['OhlObj.i%d.probClass.%s' %(m, OBS_CLASSIF_TYPES[0])] = (DeviceName, 'ohl.ObjData_TC.OhlObj.i%d.probClass.i0'        %m)
    SignalGroup['OhlObj.i%d.probClass.%s' %(m, OBS_CLASSIF_TYPES[1])] = (DeviceName, 'ohl.ObjData_TC.OhlObj.i%d.probClass.i1'        %m)
    SignalGroup['OhlObj.i%d.probClass.%s' %(m, OBS_CLASSIF_TYPES[2])] = (DeviceName, 'ohl.ObjData_TC.OhlObj.i%d.probClass.i2'        %m)
    SignalGroup['OhlObj.i%d.probClass.%s' %(m, OBS_CLASSIF_TYPES[4])] = (DeviceName, 'ohl.ObjData_TC.OhlObj.i%d.probClass.i4'        %m)
    SignalGroup['OhlObj.i%d.probClass.%s' %(m, OBS_CLASSIF_TYPES[3])] = (DeviceName, 'ohl.ObjData_TC.OhlObj.i%d.probClass.i3'        %m)
    SignalGroup['OhlObj.i%d.CntAlive'     % m                       ] = (DeviceName, 'ohl.ObjData_TC.OhlObj.i%d.internal.CntAlive'   %m)
    SignalGroup['OhlObj.i%d.dbPowerFilt'  % m                       ] = (DeviceName, 'ohl.ObjData_TC.OhlObj.i%d.internal.dbPowerFilt'%m)
  SignalGroups.append(SignalGroup)

# optional signals (needed only in CVR3)
CVR3SignalGroup = {}
OptAlias2SignalNameAndAxisNum = {
  'OhlObj.i%d.wInterfProb'             : ('ohl.ObjData_TC.OhlObj.i%d.wInterfProb'         , 1),
  'OhlObj.i%d.wConstElem'              : ('ohl.ObjData_TC.OhlObj.i%d.wConstElem'          , 1),
  'OhlObj.i%d.varDy'                   : ('ohl.ObjData_TC.OhlObj.i%d.varDy'               , 2),
  'OhlObj.i%d.dLength'                 : ('ohl.ObjData_TC.OhlObj.i%d.dLength'             , 2),
  'OhlObj.i%d.MeasCounter'             : ('ohl.ObjData_TC.OhlObj.i%d.internal.MeasCounter', 3),
  'otcohl.i%d.DEBUG_probRCSabsFeature' : ('otcohl.DEBUG_probRCSabsFeature.i%d'            , 4),
  'otcohl.i%d.DEBUG_probVariance'      : ('otcohl.DEBUG_probRCSabsFeature.i%d'            , 4),
}
for m in xrange(OHL_OBJ_NUM):
  for Alias, (SignalName, _) in OptAlias2SignalNameAndAxisNum.iteritems():
    CVR3SignalGroup[Alias % m] = (CVR3shortDeviceName, SignalName %m)
CVR3SignalGroups = [CVR3SignalGroup, ]

def findUniqueValues(array, exclude=None):
  """
    Finds unique values in an array, optionally excluding a given value.
    
    :Parameters:
      array : ndarray
      exclude : int or float
        The value which should be ignored from unique values.
    :ReturnType: list
    :Return:
      List of unique values.
  """
  uniqueValues = list(np.unique(array))
  if exclude is not None and exclude in uniqueValues:
    uniqueValues.remove(exclude)
  return uniqueValues

def isSorted(array, order, strict):
  """
    Test if the input array is sorted.
    
    :Parameters:
      array : ndarray
      order : str
        Sorting order property of the array. Supported values are 'increasing' and 'decreasing'.
      strict: bool
        Strict or partial order property. True value tests for strict ordering, False for partial ordering.
    :ReturnType: bool
    :Return:
      True if the array is sorted according to the specified conditions, otherwise False.
  """
  assert order in ('increasing', 'decreasing')
  diffarr = np.diff(array)
  if order == 'increasing':
    if strict:
      rel = lambda a,b: a > b
    else:
      rel = lambda a,b: a >= b
  elif order == 'decreasing':
    if strict:
      rel = lambda a,b: a < b
    else:
      rel = lambda a,b: a <= b
  return np.all(rel(diffarr,0))
  
class cParameter(interface.iParameter):
  def __init__(self, DeviceName):
    self.DeviceName = DeviceName
    self.genKeys()
    pass
# instantiation of module parameters
LRR3_Param = cParameter(LRR3shortDeviceName)
CVR3_Param = cParameter(CVR3shortDeviceName)
    
class cIntroObstacleClassif(interface.iView):
  @classmethod
  def view(cls, Param):
    try:
      # select signal group based on parameter value
      Index = ShortDeviceNames.index(Param.DeviceName)
      ActSignalGroup = SignalGroups[Index]
      Group = interface.Source.selectSignalGroup([ActSignalGroup,])
      OptGroup = None
      if Param.DeviceName == CVR3shortDeviceName:
        try:
          OptGroup = interface.Source.selectSignalGroup(CVR3SignalGroups)
        except measparser.signalgroup.SignalGroupError, error:
          print error.message
      # event intervals and scaletime
      IntervalList = interface.Report.IntervalList
      scaletime    = IntervalList.Time
      # check preconditions
      assert len(IntervalList) > 0
      SensorName  = Device2SensorName[Param.DeviceName]
      ReportTitle = interface.Report.getTitle()
      if not SensorName in ReportTitle:
        print 'Warning: sensor name parameter (%s) does not agree with report title: %s!' \
              %(SensorName, ReportTitle)
    except measparser.signalgroup.SignalGroupError, error:
      print error.message
    except AttributeError:
      print 'No specific report is selected!'
    except AssertionError, error:
      print error.message
    else:
      # query fus handle of relevant intro object (different fus handles over the timerange)
      kwargs = dict(ScaleTime=scaletime)
      Time, introHandles = interface.Source.getSignalFromSignalGroup(Group, 'introFUShandle', **kwargs)
      Time, speed   = interface.Source.getSignalFromSignalGroup(Group, 'egoSpeed',         **kwargs)
      speedUnit     = interface.Source.getPhysicalUnitFromSignalGroup(Group, 'egoSpeed')
      if speedUnit == 'm/s' or speedUnit == 'mps':
        speedLimit = SPEED_LIM_KMPH / MPS_2_KMPH
      else:
        speedLimit = SPEED_LIM_KMPH
      
      # loop through the interval of each event
      events = {}
      """:type: dict
      {event<int> : [(handle<int>, mask<ndarray>), ]}"""
      for eventnum, (Lower, Upper) in enumerate(IntervalList):
        eventmask = np.zeros(shape=scaletime.shape, dtype=np.bool)
        eventmask[Lower:Upper] = True
        noteventmask = ~eventmask
        # skip event if ego vehicle is too slow
        if np.all(speed[eventmask] < speedLimit):
          print 'Warning: event %2d skipped, ego speed is below %.1f km/h on whole interval [%.2f, %.2f]!'\
                %(eventnum, SPEED_LIM_KMPH, scaletime[Lower], scaletime[Upper-1])
          continue
        introHandlesOnEvent = introHandles[eventmask]
        uniqueHandle = findUniqueValues(introHandlesOnEvent, exclude=INVALID_FUS_HANDLE)
        try: 
          handle, = uniqueHandle
        except ValueError:
          handlesAndMasks = []
          # check if unique handle masks are continous
          for handle in uniqueHandle:
            handlemask = handle==introHandles
            handlemask[noteventmask] = False
            diffmask = np.diff(handlemask)
            trueIndices, = np.nonzero(diffmask)
            if trueIndices.size > 2:
              print 'Warning: event %2d skipped, different handles %s on interval [%.2f, %.2f], and the occurrence of handle %d is not continous!'\
                %(eventnum, uniqueHandle, scaletime[Lower], scaletime[Upper-1], handle)
              break
            else:
              handlesAndMasks.append((handle, handlemask))
          else:
            events[eventnum] = handlesAndMasks
        else:
          events[eventnum] = [(handle, eventmask), ]
      
      # get fus indices belonging to the events
      event2fus = {}
      """:type: dict
      {event<int> : [(handle<int>, fusIndex<int>, mask<ndarray>), ]}"""
      ExtendedDeviceName, = interface.Source.getExtendedDeviceNames(Param.DeviceName)
      for eventnum, handlesAndMasks in events.iteritems():
        eventFusList = []
        event2fus[eventnum] = eventFusList
        for handle, mask in handlesAndMasks:
          Time, fusIndexValue = interface.Source.getFUSindicesFromHandle(ExtendedDeviceName, handle,
                                                                      InvalidValue=INVALID_FUS_INDEX, **kwargs)
          uniqueIndices = findUniqueValues(fusIndexValue[mask], exclude=INVALID_FUS_INDEX)
          try:
            fusIndex, = uniqueIndices
          except ValueError:
            handleTime = scaletime[mask]
            print 'Warning: handle %2d on event %2d skipped, different FUS indices %s on interval [%.2f, %.2f]!'\
                  %(handle, eventnum, uniqueIndices, handleTime[0], handleTime[-1])
            eventFusList.append((handle, None,     mask))
          else:
            eventFusList.append((handle, fusIndex, mask))
      
      # get ohl indices belonging to the events
      event2ohl = {}
      """:type: dict
      {event<int> : [(handle<int>, fusIndex<int>, ohlIndex<int>, mask<ndarray>), ]}"""
      for eventnum, eventFusList in event2fus.iteritems():
        eventOhlList = []
        event2ohl[eventnum] = eventOhlList
        for handle, fusIndex, mask in eventFusList:
          if fusIndex is None:
            eventOhlList.append((handle, None, None, mask))
            continue
          Time, ohlIndexValue = interface.Source.getSignalFromSignalGroup(Group, 'fus.i%d_to_ohl_assoc'%fusIndex, **kwargs)
          uniqueIndices = findUniqueValues(ohlIndexValue[mask], exclude=INVALID_OHL_INDEX)
          try: 
            ohlIndex, = uniqueIndices
          except ValueError:
            handleTime = scaletime[mask]
            print 'Warning: handle %2d on event %2d skipped, different OHL indices %s on interval [%.2f, %.2f]!'\
                  %(handle, eventnum, uniqueIndices, handleTime[0], handleTime[-1])
            eventOhlList.append((handle, fusIndex, None,     mask))
          else:
            eventOhlList.append((handle, fusIndex, ohlIndex, mask))
      
      # get ohl object signals for each event
      ohlObjects = {}
      """:type: dict
      {ohlIndex<int> : ohlObject<dict>}"""
      event2ohlExt = {}
      """:type: dict
      {event<int> : [(handle<int>, fusIndex<int>, ohlIndex<int>, mask<ndarray>, extendedmask<ndarray>), ]}"""
      for eventnum, eventOhlList in event2ohl.iteritems():
        eventOhlExtList = []
        event2ohlExt[eventnum] = eventOhlExtList
        for handle, fusIndex, ohlIndex, mask in eventOhlList:
          if ohlIndex is None:
            eventOhlExtList.append((handle, fusIndex, None, mask, None))
            continue
          dx = interface.Source.getSignalFromSignalGroup(Group, 'dx_%d' %ohlIndex, **kwargs)[1]
          Lower, Upper = IntervalList[eventnum]
          # trace back ohl object's history till birth
          ohlAlive = interface.Source.getSignalFromSignalGroup(Group, 'OhlObj.i%d.CntAlive' %ohlIndex, **kwargs)[1]
          ohlAliveStart = ohlAlive[0:Upper]
          ohlBirthIndices, = np.where(ohlAliveStart == 0)
          ohlBirthIndex = ohlBirthIndices[-1]
          # trace forward ohl object's history till its end
          ohlAliveEnd = ohlAlive[Upper:]
          ohlEndIndices, = np.where(ohlAliveEnd == 0)
          ohlEndIndex = ohlEndIndices[0]
          ohlEndIndex += Upper
          # extend event mask with object's birth and end period
          extmask  = np.zeros_like(mask)
          extmask[ohlBirthIndex:ohlEndIndex] = True
          dxOnExtEvent = dx[extmask]
          # domain's strict ordering check (needed for plotting and sychronization reasons)
          if not isSorted(dxOnExtEvent, order='decreasing', strict=True):
            extTime = scaletime[extmask]
            print 'Warning: handle %2d on event %2d skipped, distance of ohl object %d is not strictly decreasing on extended interval [%.2f, %.2f]!'\
                  %(handle, eventnum, ohlIndex, extTime[0], extTime[-1])
            eventOhlExtList.append((handle, fusIndex, ohlIndex, mask, None))
            continue
          eventOhlExtList.append((handle, fusIndex, ohlIndex, mask, extmask))
          # store ohl object signals
          ohlObjects[ohlIndex] = {}
          """:type: dict
          { signalID<str> : (signal<ndarray>, physUnitMeas<str>, axisNum<int>) }"""
          # get common signals (both LRR3 and CVR3)
          dbPowerFilt = interface.Source.getSignalFromSignalGroup(Group, 'OhlObj.i%d.dbPowerFilt' %ohlIndex, **kwargs)[1]
          dxUnit      = interface.Source.getPhysicalUnitFromSignalGroup(Group, 'dx_%d'                  %ohlIndex)
          dbPowUnit   = interface.Source.getPhysicalUnitFromSignalGroup(Group, 'OhlObj.i%d.dbPowerFilt' %ohlIndex)
          ohlObjects[ohlIndex]['dx'         ] = dx         , dxUnit   , None
          ohlObjects[ohlIndex]['dbPowerFilt'] = dbPowerFilt, dbPowUnit, 0
          # get optional signals
          if OptGroup:
            for Alias, (_, axisNum) in OptAlias2SignalNameAndAxisNum.iteritems():
              signal = interface.Source.getSignalFromSignalGroup(OptGroup, Alias %ohlIndex, **kwargs)[1]
              unit   = interface.Source.getPhysicalUnitFromSignalGroup(OptGroup, Alias %ohlIndex)
              signalID = Alias.split('.')[-1]
              ohlObjects[ohlIndex][signalID] = signal, unit, axisNum
          # get classification probability signals
          classifProbUnit = '-'
          for classifType in OBS_CLASSIF_TYPES:
            signal = interface.Source.getSignalFromSignalGroup(Group, 'OhlObj.i%d.probClass.%s' %(ohlIndex,classifType), **kwargs)[1]
            # normalize signal if needed
            if np.any(signal > 1.0):
              signal = signal.astype(np.float)
              signal /= UWORD_MAX
            ohlObjects[ohlIndex][classifType] = signal, classifProbUnit, None
      
      # correct wrong normalizations
      for ohlObject in ohlObjects.itervalues():
        for signalID, (signal, physUnitMeas, _) in ohlObject.iteritems():
          if signalID not in OBS_CLASSIF_TYPES:
            physUnit = Signal2PhysUnit[signalID]
            signal = correctNorming(signal, physUnit, physUnitMeas)
            ohlObject[signalID] = signal, physUnit, _
      
      # mark unused variables
      del events, event2fus, event2ohl
      
      # plotting
      for eventnum, eventOhlExtList in event2ohlExt.iteritems():
        # create figure
        PN = datavis.cPlotNavigator(figureNr=eventnum)
        # prepare figure title and axes
        fusIndices, ohlIndices, handles, extmasks = [], [], [], []
        axes = {}
        for handle, fusIndex, ohlIndex, _, extmask in eventOhlExtList:
          if extmask is None:
            continue
          ohlIndices.append(ohlIndex)
          fusIndices.append(fusIndex)
          handles.append(handle)
          extmasks.append(extmask)
          # prepare axes for object attributes
          object = ohlObjects[ohlIndex]
          for _, __, axisNum in object.itervalues():
            if axisNum is None:
              continue
            elif axisNum not in axes:
              ax = PN.addAxis()
              axes[axisNum] = ax
        # skip plotting if necessary data is not available
        if extmasks.count(None) == len(extmasks):
          continue
        # set figure title
        PN.fig.suptitle('%s SIT intro, event #%d, FUS handle %s, FUS object %s, OHL object %s'\
                        %(SensorName, eventnum, handles, fusIndices, ohlIndices) )
        for handle, fusIndex, ohlIndex, _, extmask in eventOhlExtList:
          if extmask is None:
            continue
          object = ohlObjects[ohlIndex]
          # flip domain (increasing order for plotting)
          dx = object['dx'][0]
          domain = -dx[extmask]
          # obstacle classification signals
          Axis = PN.addAxis(xlabel='target distance [%s]' %dxUnit, ylabel='h%d' %handle)
          for classifType in OBS_CLASSIF_TYPES:
            signal, physUnit, _ = object[classifType]
            PN.addSignal2Axis(Axis, '%s [%s]' %(classifType, physUnit), domain, signal[extmask])
          # other object attributes
          for signalName, (signal, physUnit, axisNum) in object.iteritems():
            if axisNum is not None:
              ax = axes[axisNum]
              PN.addSignal2Axis(ax, 'h%d %s [%s]' %(handle, signalName, physUnit), domain, signal[extmask])
        # add client to synchronizer
        interface.Sync.addClient(PN, timesyncfunc=(scaletime[extmask], domain))
      print '%s intro obstacle classifier finished.' %SensorName
    pass
