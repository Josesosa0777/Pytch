import numpy

import measproc
import interface
from measparser import signalproc

INVALID_FUS_HANDLE = 0
INVALID_FUS_INDEX  = 255
INVALID_OHL_INDEX  = 255

class cLrr3Source(measproc.cEventFinder):
  """Signal source for LRR3 purposes."""
  Yticks = {'SIT_Intro'    : {   1 : 'SAM',
                                 2 : 'SXM',
                                 3 : 'SAS',
                                 4 : 'LAM',
                                 5 : 'RAM'},
            'SIT_Relation' : {  16 : 'LAM',     
                                12 : 'LAS',     
                                15 : 'LEM',             
                                11 : 'LES',           
                                14 : 'LLM',          
                                10 : 'LLS',          
                                17 : 'LOM',    
                                36 : 'RAM',          
                                32 : 'RAS',          
                                35 : 'REM',          
                                31 : 'RES',          
                                34 : 'RLM',          
                                30 : 'RLS',          
                                37 : 'ROM',          
                                26 : 'SAM',          
                                22 : 'SAS',          
                                25 : 'SEM',            
                                21 : 'SES',          
                                24 : 'SLM',          
                                20 : 'SLS',          
                                27 : 'SOM',          
                                64 : 'UNCORRELATED',      
                               128 : 'UNKNOWN', 
                               255 : 'INVALID'}} 
  """:type: dict
  Collect the meaning of the signal values."""
  Iterators = {'SIT_IntroFinderObjList' : xrange( 8),
               'SIT_RelGraphObjList'    : xrange(33)}  
  """:type: dict
  Collect one place the number of the signals in the lists."""
  Invalids = {'sit.IntroFinder_TC.Intro.i0.Id'             : 0,
              'sit.IntroFinder_TC.Intro.i0.ObjectList.i%d' : 0}
  """:type: dict
  Collect the invalid values of the signals."""
  HandleName = 'fus.ObjData_TC.FusObj.i%d.%s'
  """:type: str
  Name pattern for handle signal name."""
  HandleSaveName = 'fus.ObjData_TC.FusObj.h%d.%s'
  """:type: str
  Name pattern to save handle signals."""  
  PositionName = 'sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i%d'
  """:type: str
  Name pattern for handle signals of position matrix."""
  AssoMatName = 'fus_asso_mat.LrrObjIdx.i%d'
  """:type: str
  Name pattern for association of OHY and FUS objects."""

  def __init__(self, Measurement, NpyHomeDir, ECU='ECU-0-0'):
    """
    :Parameter:
      ECU : str
        Name of the ECU device on mdf
      Measurement : str
        Path of the selected file.
    """
    measproc.cEventFinder.__init__(self, Measurement, NpyHomeDir)
    self.ECU = ECU
    """:type: str
    Name of the ECU device on mdf"""
    return
  
  def getSignalFromECU(self, SignalName, **kwargs):
    """
    Get the requested signal in time, value numpy array pairs from the default 
    `ECU` device.
    
    :Parameters:
      SignalName : str
        Name of the requested signal.
    """
    return self.getSignal(self.ECU, SignalName, **kwargs)
    
  
  def getSignalByHandle(self, DeviceName, Handle, SignalName, **kwargs):    
    """
    Get the signal via its handle and name.
    
    :Parameters:
      Handle : int
        Handle of the requested signal.
      DeviceName : str
      SignalName : str
        The end of the requested signal name eg dxv.
    :Keywords:
      Keywords are passed to `cSignalSource.getSignal`
    :ReturnType: two element list of `ndarray`
    :Return:
      Requested signal in time, value numpy array pairs.      
    """
    FullSignalName = self.HandleSaveName %(Handle, SignalName)
    if not self.isSignalLoaded(DeviceName, FullSignalName):
      self.__calcSignalByHandle(DeviceName, Handle, SignalName)          
    return self.getSignal(DeviceName, FullSignalName, **kwargs)    
  
  def __calcSignalByHandle(self, DeviceName, Handle, SignalName):
    """
    Calculate the requested signal via `Handle` and store in `cSignalSource`.
    
    :Parameters:
      Handle : int
        Handle of the requested signal.
      SignalName : str
        The end of the requested signal name eg dxv.
    """
    
    Value = self.getSignal(DeviceName, self.HandleName %(0, SignalName))[1]
    Value = numpy.zeros_like(Value) * numpy.NaN
    for FusObjNr in cLrr3Source.Iterators['SIT_RelGraphObjList']:
      Mask = self.getSignal(DeviceName, self.HandleName %(FusObjNr, 'Handle'))[1] == Handle
      Value[Mask] = self.getSignal(DeviceName, self.HandleName %(FusObjNr, SignalName))[1][Mask]
    self.addSignal(DeviceName,
                   self.HandleSaveName %(Handle, SignalName), 
                   self.getTimeKey(DeviceName, self.HandleName %(0, SignalName)),
                   Value)
    return
    
  def getFUSindicesFromHandle(self, DeviceName, Handle, InvalidValue=255, **kwargs):
    """
    Get FUS indices of a given handle for the whole time range.
    
    :Parameters:
      DeviceName : str
      Handle : int
      InvalidValue : int
        Value indicating that no FUS index belongs to the given handle. Should be out of FUS index range.
    :Keywords:
      Keywords are passed to `cSignalSource.getSignal`
    :ReturnType: `ndarray`
    :Return:
      Requested signal in time, value numpy array pairs.
    """
    assert InvalidValue not in cLrr3Source.Iterators['SIT_RelGraphObjList']
    Time, DummyValue = self.getSignal(DeviceName, self.HandleName %(0, 'Handle'), **kwargs)
    Value = numpy.ones_like(DummyValue) * InvalidValue # np.NaN would require float64 dtype
    for FusObjNr in cLrr3Source.Iterators['SIT_RelGraphObjList']:
      FusObjHandles = self.getSignal(DeviceName, self.HandleName %(FusObjNr, 'Handle'), **kwargs)[1]
      Value[FusObjHandles==Handle] = FusObjNr
    return Time, Value
  
  def getFUSindicesAtPosition(self, DeviceName, Position,
                              InvalidFusIndex=INVALID_FUS_INDEX,
                              InvalidFusHandle=INVALID_FUS_HANDLE,
                              **kwargs):
    Time, PosHandles = self.getSignal(DeviceName, self.PositionName %Position, **kwargs)
    UniqueHandles = signalproc.findUniqueValues(PosHandles, exclude=InvalidFusHandle)
    FusIndices = numpy.zeros_like(PosHandles)
    FusIndices += InvalidFusIndex
    if UniqueHandles:
      for Handle in UniqueHandles:
        Mask = Handle == PosHandles
        FusIndex = self.getFUSindicesFromHandle(DeviceName, Handle, InvalidValue=InvalidFusIndex, **kwargs)[1]
        if FusIndex.dtype != FusIndices.dtype:
          FusIndex = FusIndex.astype(FusIndices.dtype)
        FusIndices[Mask] = FusIndex[Mask]
    return Time, FusIndices

  def getOHYindicesAtPosition(self, DeviceName, Position,
                              InvalidOHYindex=INVALID_OHL_INDEX,
                              InvalidFusIndex=INVALID_FUS_INDEX,
                              InvalidFusHandle=INVALID_FUS_HANDLE,
                              **kwargs):
    Time, FusIndices = self.getFUSindicesAtPosition(DeviceName, Position,
                                                    InvalidFusIndex=InvalidFusIndex,
                                                    InvalidFusHandle=InvalidFusHandle,
                                                    **kwargs)
    UniqueFUSindices = signalproc.findUniqueValues(FusIndices, exclude=InvalidFusIndex)
    OhyIndices = numpy.zeros_like(FusIndices)
    OhyIndices += InvalidOHYindex
    if UniqueFUSindices:
      for FUSindex in UniqueFUSindices:
        Mask = FUSindex == FusIndices
        OhyIndex = self.getSignal(DeviceName, self.AssoMatName %FUSindex, **kwargs)[1]
        if OhyIndex.dtype != OhyIndices.dtype:
          OhyIndex = OhyIndex.astype(OhyIndices.dtype)
        OhyIndices[Mask] = OhyIndex[Mask]
    return Time, OhyIndices

  def getFUSIndexMode(self, Handle):
    """
    Get the mode of the FUS index.
    
    :Parameters:
      Handle : int
        Number of ObjectList handle.
    :ReturnType: int    
    """    
    NaN   = 42
    Time, Intro = self.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.ObjectList.i%d' %(Handle,))
    Value = numpy.ones_like(Intro) * NaN
    for i in cLrr3Source.Iterators['SIT_RelGraphObjList']:
      Time, RelGraph = self.getSignalFromECU('sit.RelationGraph_TC.ObjectList.i%d' %i)
      MaskZero = RelGraph != 0
      Mask     = Intro == RelGraph
      Mask = numpy.logical_and(MaskZero, Mask)
      Value[Mask] = i
    return self.mode(Value, NaN)  
      
  def getIntroObjects(self, Time, Pos):
    """
    Get the FUS object handles of the actual SIT intro objects and their 
    realations, too.
    
    :Parameters:
      Time : `ndarray`
        Time of the sit.IntroFinder_TC.Intro.i0.Id signal.
      Pos : int
        `Time` index where the FUS objects are looked for.
    :ReturnType: list
    :Return: 
      List of the FUS handle and relation pairs of the actual SIT intro 
      objects.   
    """
    Objects = []
    for IntroObj in cLrr3Source.Iterators['SIT_IntroFinderObjList']:
      IntroObjHandle = self.getSignalAtPos(self.ECU, 'sit.IntroFinder_TC.Intro.i0.ObjectList.i%d' %(IntroObj,), Time, Pos)
      if IntroObjHandle != cLrr3Source.Invalids['sit.IntroFinder_TC.Intro.i0.ObjectList.i%d']:
        SITObjRel = self.getSignalAtPos(self.ECU, 'sit.IntroFinder_TC.Intro.i0.ObjectRelation.i%d' %(IntroObj,), Time, Pos)
        SITObjRel = cLrr3Source.Yticks['SIT_Relation'][SITObjRel]
        for RelGraphObj in cLrr3Source.Iterators['SIT_RelGraphObjList']:
          RelGraphObjHandle = self.getSignalAtPos(self.ECU, 'sit.RelationGraph_TC.ObjectList.i%d' %(RelGraphObj,), Time, Pos)
          if RelGraphObjHandle == IntroObjHandle:
            Objects.append([RelGraphObj, SITObjRel])
            break
    return time, Objects
  
  def getSITIntroIntervals(self, IntroTime, IntroValue):
    """
    Get the intervals of SIT intro ID where doesn't have invalid value.
    
    :Parameters:
      IntroTime : `ndarray`
        Time of the sit.IntroFinder_TC.Intro.i0.Id signal.
      IntroValue : `ndarray`
        Value of the sit.IntroFinder_TC.Intro.i0.Id signal.
    :ReturnType: `cIntervalList`
    """
    IntroName = 'sit.IntroFinder_TC.Intro.i0.Id'
    Intervals = self.compare(IntroTime, IntroValue, 
                             measproc.not_equal, 
                             cLrr3Source.Invalids[IntroName])     
    Intervals = Intervals.intersect(self.getDomains(IntroTime, IntroValue))
    return Intervals
  
  def getSITIntroObjects(self, IntroTime, IntroValue, Intervals):    
    """
    Merge the `Intervals`, where the same SIT intro objects are.
    
    :Parameters:
      IntroTime : `ndarray`
        Time of the sit.IntroFinder_TC.Intro.i0.Id signal.
      IntroValue : `ndarray`
        Value of the sit.IntroFinder_TC.Intro.i0.Id signal.
      Intervals : `cIntervalList`
        Selected intervals where the objects are looked for.
    :ReturnType: list
    :Return:
      [[LowerBound, UpperBound, IntroID, [[FUS_ObjHandle, SIT_ObjRel],...],...]
    """
    SIT_Intros = []
    Objects    = []
    for Lower, Upper in Intervals:
      Object = [cLrr3Source.Yticks['SIT_Intro'][IntroValue[Lower]],
                self.getIntroObjects(IntroTime, Lower)]
      try:
        Index = Objects.index(Object)
        SIT_Intros[Index][1] = Upper
      except ValueError:
        Objects.append(Object)
        SIT_Intros.append([Lower, Upper])
    
    for i in xrange(len(SIT_Intros)):
      SIT_Intros[i] += Objects[i]
    return SIT_Intros
