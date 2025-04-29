"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
__docformat__ = "restructuredtext en"

import iParser

class cMemoryParser(iParser.iParser):
  """Parser for the actuel loaded signal."""
  def getSignal(self, DeviceName, SignalName):
    Device = self.Devices[DeviceName]
    return Device[SignalName]
  
  def getTime(self, TimeKey):
    return self.Times[TimeKey]
  
  def getTimeKey(self, DeviceName, SignalName):
    Device         = self.Devices[DeviceName]
    Value, TimeKey = Device[SignalName]
    return TimeKey
  
  def addSignal(self, DeviceName, SignalName, TimeKey, Signal):
    """
    :Parameters:
      DeviceName : str
      SignalName : str
      TimeKey : str
      Signal : `numpy.ndarray`
    """
    try:
      StoredSignal, StoredTimeKey = self.Devices[DeviceName][SignalName]
    except KeyError:
      pass
    else:
      if Signal is not StoredSignal:
        raise ValueError, ('%(DeviceName)s.%(SignalName)s is a reserved signal name!\n' %locals())
      if TimeKey != StoredTimeKey:
        raise ValueError, ('%(DeviceName)s.%(SignalName)s is connected to %(StoredTimeKey)s time channel that cannot change to %(TimeKey)s!\n' %locals())
      return
    if TimeKey not in self.Times:
      raise ValueError, ('%(TimeKey)s is not a valid time channels!\n' %locals())
    if DeviceName not in self.Devices:
      self.Devices[DeviceName] = {}
    self.Devices[DeviceName][SignalName] = Signal, TimeKey
    pass
  
  def addTime(self, TimeKey, Time):
    """
    :Parameters:
      TimeKey : str
      Time : `numpy.ndarray`
    """
    try:
      StoredTime = self.Times[TimeKey]
    except KeyError:
      pass
    else:
      if Time is not StoredTime:
        raise ValueError, ('%(TimeKey)s is a reserved time channel name!\n' %locals())
      return
    self.Times[TimeKey] = Time
    pass

  def getTimeKeyByTime(self, SearchedTime):
    """
    Get the TimeKey of the selected `SearchedTime`
    
    :Parameters:
      SearchedTime : `ndarray`
    :ReturnType: str
    """
    for TimeKey, Time in self.Times.iteritems():
      if SearchedTime is Time:
        return TimeKey
    else:
      raise ValueError, 'The requested time is not loaded'
