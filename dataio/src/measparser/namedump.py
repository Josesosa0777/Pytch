# -*- coding: utf-8 -*-

import os

from sqlalchemy import ForeignKey, Column, String, Unicode, Integer, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.expression import bindparam, or_, not_, and_

from SignalSource import findParser
from iParser import iParser, DEVICE_NAME_SEPARATOR

Base = declarative_base()

class Timekeys(Base):
  __tablename__ = 'timekeys'
  timekey = Column(String,  unique=True, primary_key=True)

  def __repr__(self):
    return "<Timekeys(id='%s', timekey='%s')>" % (self.id, self.timekey)

class Devices(Base):
  __tablename__ = 'devices'
  devicename = Column(String, unique=True,  primary_key=True,)

  def __repr__(self):
    return "<Devices(devicename='%s')>" % self.devicename

class Signals(Base):
  __tablename__ = 'signals'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True)
  name = Column(String)
  devicename = Column(String, ForeignKey('devices.devicename'))
  timekey = Column(String, ForeignKey('timekeys.timekey'))
  nr_of_records = Column(Integer)
  unit = Column(Unicode)
  devicealias = Column(String)

  device = relationship('Devices', backref=backref('signals'))
  tk = relationship('Timekeys', backref=backref('signals'))

  UniqueConstraint('name', 'deviceid')

  def __repr__(self):
    return '''<Signals(signal='%s', device='%s', timekey='%s',
                unit='%s', nr_of_record='%s')>''' \
          %(self.name, self.device, self.timekey, self.unit, self.nr_of_records)

class NameDump(iParser):
  DB_Path = r'sqlite:///'
  def __init__(self, DbName):
    self.DbName = DbName

    Path = self.DB_Path + DbName


    self.Engine = create_engine(Path, echo=False)
    session = sessionmaker(bind=self.Engine)
    self.Session = session()
    Base.metadata.create_all(self.Engine)
    return

  @classmethod
  def fromParser(cls, Parser, DbName):
    NameDump = cls(DbName)

    for TimeKey in Parser.iterTimeKeys():
      Tk = Timekeys()
      Tk.timekey = TimeKey
      NameDump.Session.add(Tk)

    for DeviceName in Parser.iterDeviceNames():
      Device = Devices(devicename=DeviceName)
      NameDump.Session.add(Device)
      for SignalName in Parser.iterSignalNames(DeviceName):
        Unit = Parser.getPhysicalUnit(DeviceName, SignalName)
        try:
          Unit = unicode(Unit, errors='ignore')
        except TypeError:
          pass
        try:
          NrOfRecord = Parser.getMeasSignalLength(DeviceName, SignalName)
        except KeyError:
          NrOfRecord = 0
        TimeKeyName = Parser.getTimeKey(DeviceName, SignalName)
        Alias, Sig = Parser.getAlias(DeviceName, SignalName)
        Signal = Signals(name=SignalName, devicename=DeviceName,
                        timekey=TimeKeyName, nr_of_records=NrOfRecord,
                        unit=Unit, devicealias=Alias)
        NameDump.Session.add(Signal)
    NameDump.Session.commit()
    NameDump.save()
    return NameDump

  @classmethod
  def fromMeasurement(cls, Measurement, DbName="namedump.db"):
    cParser = findParser(Measurement)
    Parser = cParser(Measurement)
    return NameDump.fromParser(Parser, DbName=DbName)

  def save(self):
    self.Session.close()
    return

  def close(self):
    self.save()
    self.Engine.dispose()
    return

  def iterDeviceNames(self):
    """
    Iterator over the available device names.

    :ReturnType: str
    """
    Devs = self.Session.query(Devices.devicename).all()
    for Dev in Devs:
      Dev,  =  Dev
      yield Dev

  def iterTimeKeys(self):
    """
    Iterator over the available device names.

    :ReturnType: str
    """
    TimeKeys = self.Session.query(Timekeys.timekey).all()
    for Tk in TimeKeys:
      Tk,  =  Tk
      yield Tk

  def contains(self, DeviceName, SignalName):
    """
    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: bool
    """
    Query = self.Session.query(Signals).\
                    filter(Signals.name == SignalName).\
                    filter(Signals.devicename == DeviceName)
    Signal = Query.first()
    return Signal != None

  def getPhysicalUnit(self, DeviceName, SignalName):
    """
    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: str
    """
    Query = self.Session.query(Signals.unit).\
                    filter(Signals.name == SignalName).\
                    filter(Signals.devicename == DeviceName)
    Unit = Query.first()
    if Unit:
      Unit, = Unit
    else:
      Unit = ''
    return Unit

  def iterSignalNames(self, DeviceName):
    """
    Iterator over the available signal names of the `DeviceName` in the
    measurement file.

    :Parameters:
      DeviceName : str
    :ReturnType: dictionary-keyiterator
    """
    Query = self.Session.query(Devices).filter(Devices.devicename == DeviceName)
    Devs = Query.first()
    for Sig in Devs.signals:
      yield Sig.name

  def getDeviceNames(self, SignalName):
    """
    Get the device name swhich contains the `SignalName`.

    :Parameters:
      SignalName : str
        Name of the selected signal.
    :ReturnType: list
    """
    Query = self.Session.query(Signals).filter(Signals.name == SignalName)
    Sigs = Query.all()
    return [Sig.device.devicename for Sig in Sigs]

  def getExtendedDeviceNames(self, DeviceName, FavorMatch=False):
    """
    'AMB'     -> ['AMB-23-78', 'AMB-98-9']
    'AMB-23'  -> ['AMB-23-78',]
    'AMB-*-9' -> ['AMB-98-9',]

    :Parameters:
      DeviceName : str
    :ReturnType: list
    """
    Query = self.Session.query(Devices.devicename)
    Devs = Query.filter(Devices.devicename.startswith(DeviceName)).all()
    DeviceNames = [Name for Name, in Devs]
    if FavorMatch and DeviceName in DeviceNames:
      DeviceNames = [DeviceName]  # return only the matching device
    return DeviceNames

  def getNames(self, SignalName, Pattern, FavorMatch=False):
    """
    Get the DeviceNames which contain `SignalName` and start with `Pattern`.
    
    If `FavorMatch` is True, and `Pattern` is an existing device name, return
    only the matching device name, regardless of possible other devices that
    start with `Pattern`. Default is False - returning all device names that
    start with `Pattern`.
    
    :Parameters:
      SignalName : str
        Name of the selected signal.
      Pattern : str
        Beginning of the name of device which contains the selected signal.
      FavorMatch : bool, optional
        See method description.
    :ReturnType: list
    :Return: [DeviceName<str>]
    """
    Query = self.Session.query(Signals.devicename)

    Devices = Query.filter(Signals.devicealias.startswith(Pattern)).\
                    filter(Signals.name == SignalName).all()
    DeviceNames = [Dev for Dev, in Devices]
    if FavorMatch and Pattern in DeviceNames:
      DeviceNames = [Pattern]  # return only the matching device
    return DeviceNames

  def getTimeKey(self, DeviceName, SignalName):
    """
    Get the time key of the selected signal

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the selected signal.
    :ReturnType: str
    :Exceptions:
      KeyError : if the `DeviceName` or `SignalName` is incorrect.
    """
    Query = self.Session.query(Signals.timekey).\
                         filter(Signals.name == SignalName).\
                         filter(Signals.devicename == DeviceName)
    Tk = Query.first()
    if Tk is None:
      raise KeyError, ('%s.%s' %(DeviceName, SignalName))
    else:
      Tk, = Tk
      return Tk

  def getSignalLength(self, DeviceName, SignalName):
    """
    Get the length of the selected signal.

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: int
    :Exceptions:
      KeyError : if the `DeviceName` or `SignalName` is incorrect.
    """
    Query = self.Session.query(Signals.nr_of_records).\
                         filter(Signals.name == SignalName).\
                         filter(Signals.devicename == DeviceName)
    NrOfRecord = Query.first()
    if NrOfRecord is None:
      raise KeyError, ('%s.%s' %(DeviceName, SignalName))
    else:
      NrOfRecord, = NrOfRecord
      return NrOfRecord

  def isMissingSignal(self, DeviceName, SignalName):
    return not self.contains(DeviceName, SignalName)

  def isMissingDevice(self, DeviceName):
    Query = self.Session.query(Devices).filter(Devices.devicename == DeviceName)
    Device = Query.first()
    return Device == None

  def isMissingTime(self, TimeKey):
    Query = self.Session.query(Timekeys).filter(Timekeys.timekey == TimeKey)
    Tk = Query.first()
    return Tk == None

  def querySignalNames(self,
                       PosDevTags,
                       NegDevTags,
                       PosSigTags,
                       NegSigTags,
                       MatchCase,
                       DisableEmpty):
    """
    Get the aliases, that contain the input strings.

    :Parameters:
      PosDevTags : list
        Tags that have to be in the device name
      NegDevTags : list
        Tags that doas not have to be in the device name
      PosSigTags : list
        Tags that have to be in the signal name
      NegSigTags : list
        Tags that doas not have to be in the signal name
    :KeyWords:
      MatchCase : bool
      DisableEmpty : bool
        Do not search in signal names which are empty.
    :ReturnType: list
    :Return:     [[ShortDeviceName<str>, Signalame<str>],]
    """
    FuncName = 'like' if MatchCase else 'ilike'


    Query = self.Session.query(Signals.name, Signals.devicealias,
                               Signals.nr_of_records)
    if PosDevTags:
      Tags = self._createTags(PosDevTags, FuncName, Signals.devicealias)
      Query = Query.filter(and_(*Tags))
    if NegDevTags and not MatchCase:
      Tags = self._createTags(NegDevTags, FuncName, Signals.devicealias,
                               Negative=True)
      Query = Query.filter(and_(*Tags))
    if PosSigTags:
      Tags = self._createTags(PosSigTags, FuncName, Signals.name)
      Query = Query.filter(and_(*Tags))
    if NegSigTags and not MatchCase:
      Tags = self._createTags(NegSigTags, FuncName, Signals.name,
                               Negative=True)
      Query = Query.filter(and_(*Tags))

    Matched = Query.all()
    Names = []
    for SigName, DevAlias, Len in Matched:
      if DisableEmpty and Len == 0: continue

      if MatchCase:
        for PosDevTag in PosDevTags:
          if PosDevTag in DevAlias:
            self._checkNames(DevAlias, SigName, Names)
        for PosSigTag in PosSigTags:
          if PosSigTag in SigName:
            self._checkNames(DevAlias, SigName, Names)
        #order is important, first we add signals, then we remove
        for NegDevTag in NegDevTags:
          if NegDevTag in DevAlias:
            self._checkNames(DevAlias, SigName, Names, Negative=True)
        for NegSigTag in NegSigTags:
          if NegSigTag in SigName:
            self._checkNames(DevAlias, SigName, Names, Negative=True)
      else:
        self._checkNames(DevAlias, SigName, Names)
    Names.sort()
    return Names

  def _createTags(self, Tags, Func, Column, Negative=False):
    Columnfunc = getattr(Column, Func)
    if not Negative:
      return [Columnfunc('%' + Tag + '%') for Tag in Tags]
    else:
      return [not_(Columnfunc('%' + Tag + '%'))for Tag in Tags]

  def _checkNames(self, DevAlias, SigName, Names, Negative=False):
    if Negative:
      if (DevAlias, SigName) in Names:
        Names.remove((DevAlias, SigName))
    else:
      if (DevAlias, SigName) not in Names:
        Names.append((DevAlias, SigName))
    return

