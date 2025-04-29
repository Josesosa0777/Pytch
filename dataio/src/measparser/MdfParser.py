"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""
__docformat__ = "restructuredtext en"

import sys
import os
import shutil
import mmap
import datetime

import numpy

import iParser
import mdf


def calcReadAttrs(Orders, Formats, SignalDataType, NumberOfBits, StartOffsetInBits, AdditionalByteOffset, SizeOfDataRecord, **drop):
  DType,\
  ByteSize,\
  DByteSize,\
  ByteOffset,\
  UpShift,\
  DownShift = mdf.calcReadAttrs(Orders, Formats, SignalDataType, NumberOfBits, StartOffsetInBits, AdditionalByteOffset)

  if ByteSize != DByteSize:
    ByteOffsets = [str(i) for i in xrange(ByteSize)]
    DTypes = [(o, '<u1') for o in ByteOffsets]
  else:
    DTypes = [('value', DType)]

  if ByteOffset:
    DTypes.insert(0, ('pre',  '|V%d' %(ByteOffset)))
  Post = SizeOfDataRecord - ByteSize - ByteOffset
  if Post:
    DTypes.append(   ('post', '|V%d' %(Post)))

  return DTypes, DType, UpShift, DownShift


def checkParser(FileName):
  File, Version = mdf.getVersion(FileName)
  return     File == 'MDF'\
         and Version <= '3.30'


def calcSplits(DTypes):
  """
  :Parameters:
    DTypes : list
      [(Name<srt>, DType<str>)]

  :ReturnType: int, int
    offset for reading data
    number of dtypes which are named by their byte offset in the datagroup
  """
  DTypesDict = dict(DTypes)
  if 'pre' in DTypesDict:
    DataBlockExtra = mdf.getTypeSize(DTypesDict['pre'])
  else:
    DataBlockExtra = 0
  Splits = len([n for n, f in DTypes if n.isdigit()])
  return Splits, DataBlockExtra


class UnsortedMdf(BaseException):
  pass


class cMdfParser(iParser.iParser):
  """Mdf parser. close method has to be called before the python session is
  terminated."""
  checkParser = staticmethod(checkParser)

  @classmethod
  def readStartDate(cls, FileName):
    """
    Get the start of the measurement from the RecordStartDate_ns and GMTTimeZone
    attributes of the header block

    :Parameters:
      FileName : str

    :Exceptions:
      AssertionError

    :ReturnType: `datetime.datetime`
    """
    assert os.path.isfile(FileName), '%s does not exists' % FileName
    f = open(FileName, 'rb')
    f.seek(64)

    BlockTypeId,\
    BlockSize,\
    DGlink,\
    FileComment,\
    ProgramBlock,\
    NoDGs,\
    RecordStartDate,\
    RecordStartTime,\
    AuthorName,\
    Organization,\
    ProjectNames,\
    Subject,\
    RecordStartTime_us,\
    GMTTimeZone,\
    TimeQualityClass,\
    TimerId = mdf.HDstruct.unpack(f.read(mdf.HDstruct.size))

    f.close()

    Date =  datetime.datetime.fromtimestamp(RecordStartTime_us * 1e-9)\
          + datetime.timedelta(hours=GMTTimeZone)
    return Date

  def __init__(self, FileName):
    """
    :Parameters:
      FileName : str
        Path of the mdf file to pars.
    """
    iParser.iParser.__init__(self)

    self.__fin = None
    """:type: file
    The input mdf file"""
    self.__fout = None
    """:type: file
    The output mdf file"""
    self.ReSorted = False
    """:type: bool
    Flag to show the mdf file was resorted during the parsing or not."""
    self.CNs = {0:dict(PrevCNlink = 0L,
                       NextCNlink = 0L,
                       CGlink     = 0L)}
    """:type: dict
    Container of the channel blocks."""
    self.OutCNs = {}
    """:type: dict
    Container of the channel blocks for output file."""
    self.CEs = {}
    """:type: dict
    {DeviceName<str>:CEBlockPtr<long>}"""

    self.Orders = mdf.Orders.copy()

    self.EmptyCNstruct = mdf.CNstruct.pack(*(['CN', mdf.CNstruct.size] + [0]*6 + ['\0'*32] + ['\0'*128] + [0]*10))
    """:type: str
    Empty channel block for deleting."""
    self.EmptyDIMstruct = mdf.DIMstruct.pack(0, 0, '\0'*80, '\0'*32)
    """:type: str
    Empty DIM block supplement"""
    self.EmptyCANstruct = mdf.CANstruct.pack(0, 0, '\0'*36, '\0'*36)
    """:type: str
    Empty CAN block supplement"""

    self.__open_fin(FileName)
    pass

  def getTimeKey(self, DeviceName, SignalName):
    """"
    :Parameters:
      DeviceName : str
        Name of device which contain the selected signal.
      SignalName : str
        Name of the selected signal.
    :ReturnType: str
    """
    Device = self.Devices[DeviceName]
    Signal = Device[SignalName]
    Attr   = Signal['TimeKey']
    return Attr

  def getSignalLength(self, DeviceName, SignalName):
    """"
    :Parameters:
      DeviceName : str
        Name of device which contain the selected signal.
      SignalName : str
        Name of the selected signal.
    :ReturnType: int
    """
    TimeKey = self.getTimeKey(DeviceName, SignalName)
    Time = self.getTime(TimeKey)
    return Time.size

  def getMeasSignalLength(self, DeviceName, SignalName):
    """"
    Get the registered signal length, that can differ from the read signal in
    case of corrupt measurement

    :Parameters:
      DeviceName : str
        Name of device which contain the selected signal.
      SignalName : str
        Name of the selected signal.
    :ReturnType: int
    """
    Device = self.Devices[DeviceName]
    Signal = Device[SignalName]
    Attr   = Signal['NoRecords']
    return Attr

  def isSignalEmpty(self, DeviceName, SignalName):
    return self.getMeasSignalLength(DeviceName, SignalName) == 0

  def getPhysicalUnit(self, DeviceName, SignalName):
    """"
    :Parameters:
      DeviceName : str
        Name of device which contain the selected signal.
      SignalName : str
        Name of the selected signal.
    :ReturnType: str
    """
    Device = self.Devices[DeviceName]
    Signal = Device[SignalName]
    Attr   = Signal['PhysicalUnit']
    return Attr

  def close(self):
    """Close the mdf files. This has to be called before the python session is
    terminated."""
    if self.__fin:
      self.__fin.close()
    if self.__fout:
      self.__fout.close()
    pass

  def getSignalShape(self, DeviceName, SignalName):
    #FIXME As of now we do not work with mf3 files which have signals with more than one dimension
    #so we simply return the NoRecords, which represents the size of the first dimension
    Device = self.Devices[DeviceName]
    Signal = Device[SignalName]
    if Signal['NoRecords'] == 0:
      return [0]
    else:
      NoRecords = Signal['NoRecords']
      DataBlock = Signal['DataBlock']
      BlockSize = Signal['SizeOfDataRecord']
      return[NoRecords]
      #TODO correctly determine the shape

  def getSignal(self, DeviceName, SignalName, dtype=None, factor=None,
                offset=None):
    """
    Get a signal from the mdf file.

    :Parameters:
      DeviceName : str
        Name of device which contain the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: `ndarray`, str
    :Return:     Values of the requested signal.
                 Timekey of the requested signal.
    :Exceptions:
      KeyError : if the `DeviceName` or `SignalName` is incorrect.
      ValueError : if the data type of the requested signal is not implemented
    """
    Device   = self.Devices[DeviceName]
    Signal   = Device[SignalName]
    if Signal['NoRecords'] == 0:
      PhysValues = numpy.empty(0)
    else:
      RawValues  = self.__read_raw_value(Signal, DType=dtype)
      PhysValues = self.__convert_RAW_PHY(Signal, RawValues, Factor=factor,
                                          Offset=offset)
    return PhysValues, Signal['TimeKey']

  def getTime(self, TimeKey):
    """
    Get a time channel from the mdf file.

    :Parameters:
      TimeKey : str
        Key of the time channel.
    :ReturnType: `ndarray`
    :Exceptions:
      KeyError : if the `TimeKey` is incorrect.
    """
    Time = self.Times[TimeKey]
    if Time['NoRecords'] == 0:
      PhysValues = numpy.empty(0)
    else:
      RawValues  = self.__read_raw_value(Time)
      PhysValues = self.__convert_RAW_PHY(Time, RawValues)
    return PhysValues

  def setSignal(self, DeviceName, SignalName, SignalValues):
    """
    Set a signal in the output mdf file.

    :Parameters:
      DeviceName : str
        Name of device which contain the selected signal.
      SignalName : str
        Name of signal to set.
      SignalValues : `ndarray`
        Values of the signal to set.
      FileName : str, default None
        The path of the output mdf file. If the default value is used, then the
        the old output file will be used.
    :Exceptions:
      KeyError : if the `DeviceName` or `SignalName` is incorrect.
      ValueError : if the length of `SignalValues` and NoRecords of the
                   requested signal are not equal.
    """
    Device = self.Devices[DeviceName]
    Signal = Device[SignalName]
    if SignalValues.size != Signal['NoRecords']:
      raise ValueError ('Lenghts of SigalValues and %s are not equal' %SignalName)
    RawValues = self.__convert_PHY_RAW(Signal, SignalValues)
    self.__write_raw_value(Signal, RawValues)
    pass

  def rmDevice(self, DeviceName):
    """
    Remove the device and the signals under it.

    :Parameters:
      DeviceName : str
    """
    CGlinks = set()
    Device   = self.Devices[DeviceName]
    for SignalName in self.Devices[DeviceName]:
      Signal  = Device[SignalName]
      CNlink = Signal['CNlink']
      Blocks  = self.OutCNs[CNlink]
      CGlink = Blocks['CGlink']
      CGlinks.add(CGlink)
      self.rmSignal(DeviceName, SignalName)
    self.__del_CEBlock(DeviceName)
    for CGlink in CGlinks:
      self.__clear_CGBLOCKComment(CGlink)
    pass

  def rmSignal(self, DeviceName, SignalName):
    """
    :Parameters:
      DeviceName : str
      SignalName : str
    """
    Device = self.Devices[DeviceName]
    Signal = Device[SignalName]
    self.__del_CNBLOCK(Signal)
    pass

  def openOutputFile(self, FileName):
    """
    Create the `__fout` and open it.

    :Parameters:
      FileName : str
        Path of the output mdf file
    """
    if self.__fout:
      self.__fout.close()
      sys.stderr('The output file is changed from <%s> to <%s>!\n' %(self.__fout.name, FileName))
    shutil.copy2(self.FileName, FileName)
    self.__fout = open(FileName, 'r+b')
    self.OutCNs = self.CNs.copy()
    pass

  def closeOutputFile(self):
    """Close the output mdf file"""
    if self.__fout:
      self.__fout.close()
      self.__fout = None
    pass

  def __open_fin(self, FileName):
    """
    Open the `__fin` and fill up the `__Mdf`.

    :Parameters:
      FileName : str
        Path of the input df file
    :Exceptions:
      ValueError : If the file extension is not match or the `FileName` not
                   valid.
    """
    if not checkParser(FileName):
      raise ValueError('%s is not an mdf file!\n' %(FileName))
    self.FileName = FileName
    fin = open(FileName, 'rb')
    try:
      self.__fin = mmap.mmap(fin.fileno(), 0, access=mmap.ACCESS_COPY)
    except WindowsError:
      self.__fin = fin
      try:
        self.__extract_Mdf()
      except UnsortedMdf:
        fin.close()
        mdf.sortMdf(FileName)
        self.ReSorted = True
        self.__open_fin(FileName)
    else:
      try:
        self.__extract_Mdf()
      except UnsortedMdf:
        fin.close()
        self.__fin.close()
        mdf.sortMdf(FileName)
        self.ReSorted = True
        self.__open_fin(FileName)
      else:
        self.__fin.close()
        self.__fin = fin
    return

  def __extract_Mdf(self):
    """Fill up the `__Mdf`"""
    self.Devices.clear()
    self.Times.clear()

    self.Signal  = {}
    self.ActCGlink  = 0L
    self.NoDGs      = 0L
    self.NoCGs      = 0L
    self.NoCNs      = 0L
    self.DGlink     = 0L
    self.CGlink     = 0L
    self.CNlink     = 0L
    self.CClink     = 0L
    self.PrevCNlink = 0L
    self.CElink     = 0L

    self.CCs = {0:(12, None, '')}
    self.CEs = {0:'NULL'}

    self.__extract_IDBLOCK()
    self.__extract_HDBLOCK()
    for i in xrange(self.NoDGs):
      self.Signal['DGnr'] = i
      self.__extract_DGBLOCK()
      for ii in xrange(self.NoCGs):
        self.Signal['CGnr'] = ii
        self.__extract_CGBLOCK()
        for iii in xrange(self.NoCNs):
          self.__extract_CNBLOCK()
    self.CEs = dict([(DeviceName, CEBlockPtr) for CEBlockPtr, DeviceName in self.CEs.iteritems()])
    del self.Signal
    del self.ActCGlink
    del self.NoDGs
    del self.NoCGs
    del self.NoCNs
    del self.DGlink
    del self.CGlink
    del self.CNlink
    del self.CClink
    del self.PrevCNlink
    del self.CElink
    del self.CCs
    return

  def __del_TXBlock(self, TXLink):
    """
    :Parameters:
      TXLink : long
    :Exceptions:
      ValueError
        If the read block identifier ois wrong.
    """
    if TXLink == 0:
      return
    self.__fout.seek(TXLink)
    BlockTypeId,\
    BlockSize = mdf.TXstruct.unpack(self.__fout.read(mdf.TXstruct.size))
    if BlockTypeId != 'TX':
      raise ValueError
    self.__fout.write('\x00'*(BlockSize-4))
    self.__fout.flush()
    pass

  def __extract_IDBLOCK(self):
    """Extract the Identification Block of the mdf file"""
    self.__fin.seek(0)

    self.FileIdentifier,\
    self.FormatIdentifier,\
    self.ProgramIdentifier,\
    self.DefaultByteOrder,\
    self.DefaultFloatingPointFormat,\
    self.VersionNumber = mdf.IDstruct.unpack(self.__fin.read(mdf.IDstruct.size))

    DefaultByteOrder = '>' if self.DefaultByteOrder else '<'
    mdf.setDefaultByteOrder(self.Orders, DefaultByteOrder)

    for AttrName in ['FileIdentifier', 'ProgramIdentifier', 'FormatIdentifier']:
      Attr = getattr(self, AttrName)
      Attr = Attr.split('\0')[0]
      setattr(self, AttrName, Attr)
    pass


  def __extract_HDBLOCK(self):
    """Extract the Header Block of the mdf file"""
    self.__fin.seek(64)

    BlockTypeId,\
    BlockSize,\
    self.DGlink,\
    FileComment,\
    ProgramBlock,\
    self.NoDGs,\
    self.RecordStartDate,\
    self.RecordStartTime,\
    self.AuthorName,\
    self.Organization,\
    self.ProjectNames,\
    self.Subject,\
    self.RecordStartTime_us,\
    self.GMTTimeZone,\
    self.TimeQualityClass,\
    self.TimerId = mdf.HDstruct.unpack(self.__fin.read(mdf.HDstruct.size))

    self.FileComment = mdf.extractTX(self.__fin, FileComment)

    for AttrName in ['AuthorName', 'Organization', 'ProjectNames', 'Subject']:
      Attr = getattr(self, AttrName)
      Attr = Attr.split('\0x00')[0]
      setattr(self, AttrName, Attr)
    pass

  def __extract_DGBLOCK(self):
    """Extract a Data Group Block from the `DataGroupBlock` file position."""
    # NIL allowed
    if self.DGlink == 0:
      return
    self.__fin.seek(self.DGlink)

    BlockTypeId,\
    BlockSize,\
    self.DGlink,\
    self.CGlink,\
    TRlink,\
    self.Signal['DataBlock'],\
    self.NoCGs,\
    NoRecordIDs = mdf.DGstruct.unpack(self.__fin.read(mdf.DGstruct.size))
    if NoRecordIDs != 0:
      raise UnsortedMdf()
    return

  def __extract_CGBLOCK(self):
    """Extract a Channel Group Block from the `ChannelGroupBlock` file position."""
    # NIL allowed
    if self.CGlink == 0:
      return
    self.__fin.seek(self.CGlink)

    self.ActCGlink = self.CGlink
    self.PrevCNlink = 0

    BlockTypeId,\
    BlockSize,\
    self.CGlink,\
    self.CNlink,\
    GroupComment,\
    RecordID,\
    self.NoCNs,\
    self.Signal['SizeOfDataRecord'],\
    self.Signal['NoRecords'],\
    FirstSampleReductionBlock= mdf.CGstruct.unpack(self.__fin.read(mdf.CGstruct.size))
    pass

  def __clear_CGBLOCKComment(self, CGlink):
    """
    Clear the comment of the channel group block if the block contains only the
    time signal.

    :Parameters:
      CGlink : long
    :Exceptions:
      ValueError
        If the read block identifier ois wrong.
    """
    if CGlink == 0:
      return
    self.__fout.seek(CGlink)
    Block = mdf.CGstruct.unpack(self.__fout.read(mdf.CGstruct.size))
    if Block[0] != 'CG':
      raise ValueError
    if Block[6] > 1:
      return

    Block = list(Block)
    self.__del_TXBlock(Block[4])
    Block[4] = 0

    Block = mdf.CGstruct.pack(*Block)
    self.__fout.seek(CGlink)
    self.__fout.write(Block)
    self.__fout.flush()
    pass

  def __extract_CNBLOCK(self):
    """Extract a Channel Block from the `ChannelBlock` file position."""
    # NIL allowed
    if self.CNlink == 0:
      return
    self.__fin.seek(self.CNlink)

    ActCNlink = self.CNlink

    BlockTypeId,\
    BlockSize,\
    self.CNlink,\
    self.CClink,\
    self.CElink,\
    DependencyBlock,\
    ChannelComment,\
    ChannelType,\
    ShortSignalName,\
    SignalDescription,\
    self.Signal['StartOffsetInBits'],\
    self.Signal['NumberOfBits'],\
    self.Signal['SignalDataType'],\
    ValueRangeValid,\
    MinimumSignalValue,\
    MaximumSignalValue,\
    SamplingRate,\
    LongSignalName,\
    DisplayName,\
    self.Signal['AdditionalByteOffset'] = mdf.CNstruct.unpack(self.__fin.read(mdf.CNstruct.size))

    self.__extract_CCBlock()

    TimeKey = '%(DGnr)05d' %self.Signal

    self.CNs[ActCNlink] = dict(PrevCNlink  = self.PrevCNlink,
                               NextCNlink  = self.CNlink,
                               CGlink      = self.ActCGlink)

    self.Signal['CNlink'] = ActCNlink
    self.PrevCNlink       = ActCNlink

    # time channel
    if ChannelType:
      self.Times[TimeKey] = self.Signal.copy()
    # data channel
    else:
      self.Signal['TimeKey'] = TimeKey
      DeviceName = self.__extract_CEBlock()
      if LongSignalName != 0:
        SignalName = mdf.extractTX(self.__fin, LongSignalName)
      else:
        SignalName = ShortSignalName.split('\x00')[0]
      if DeviceName in self.Devices:
        self.Devices[DeviceName][SignalName] = self.Signal.copy()
      else:
        self.Devices[DeviceName] = {SignalName : self.Signal.copy()}
    pass

  def __del_CNBLOCK(self, Signal):
    """
    :Parameters:
      Signal : dict
        {'CNlink':<long>, ...}
    :Exceptions:
      ValueError
        If the read block identifier ois wrong.
    """
    CNlink     = Signal['CNlink']
    Blocks     = self.OutCNs[CNlink]
    NextCNlink = Blocks['NextCNlink']
    PrevCNlink = Blocks['PrevCNlink']
    CGlink     = Blocks['CGlink']

    # delete the channel block of the signal
    self.__fout.seek(CNlink)
    Block = mdf.CNstruct.unpack(self.__fout.read(mdf.CNstruct.size))
    if Block[0] != 'CN':
      raise ValueError
    self.__del_TXBlock(Block[6])
    self.__del_TXBlock(Block[17])
    self.__del_TXBlock(Block[18])
    self.__fout.seek(CNlink)
    self.__fout.write(self.EmptyCNstruct)

    # decrease the number of the channels at the channel group of the signal
    self.__fout.seek(CGlink)
    Block = mdf.CGstruct.unpack(self.__fout.read(mdf.CGstruct.size))
    if Block[0] != 'CG':
      raise ValueError
    Block     = list(Block)
    Block[6] -= 1
    if PrevCNlink == 0:
      Block[3] = NextCNlink
    Block = mdf.CGstruct.pack(*Block)
    self.__fout.seek(CGlink)
    self.__fout.write(Block)

    # set the next channel block pointer of the previous channel block to the
    # next channel block pointer of the channel block of the signal
    if PrevCNlink != 0:
      self.__fout.seek(PrevCNlink)
      Block    = mdf.CNstruct.unpack(self.__fout.read(mdf.CNstruct.size))
      if Block[0] != 'CN':
        raise ValueError
      Block    = list(Block)
      Block[2] = NextCNlink
      Block    = mdf.CNstruct.pack(*Block)
      self.__fout.seek(PrevCNlink)
      self.__fout.write(Block)

    self.__fout.flush()
    self.OutCNs[PrevCNlink]['NextCNlink'] = NextCNlink
    self.OutCNs[NextCNlink]['PrevCNlink'] = PrevCNlink
    del self.OutCNs[CNlink]
    pass

  def __extract_CCBlock(self):
    """Extract a Channel Conversation Block from the `ConversationFormula` file
    position."""
    # NIL allowed self.CCs is initialized with {0:(0, [0, 1])}
    try:
      ConversionType, AdditionalConversionData, PhysicalUnit = self.CCs[self.CClink]
    except KeyError:
      ConversionType, AdditionalConversionData, PhysicalUnit = mdf.extractCC(self.__fin, self.CClink)
      self.CCs[self.CClink] = ConversionType, AdditionalConversionData, PhysicalUnit
    self.Signal['ConversionType']           = ConversionType
    self.Signal['AdditionalConversionData'] = AdditionalConversionData
    self.Signal['PhysicalUnit']             = PhysicalUnit
    pass

  def __extract_CEBlock(self):
    try:
      DeviceName = self.CEs[self.CElink]
    except KeyError:
      DeviceTags = mdf.extractCE(self.__fin, self.CElink)
      DeviceName = iParser.DEVICE_NAME_SEPARATOR.join(DeviceTags)
      self.CEs[self.CElink] = DeviceName
    return DeviceName

  def __del_CEBlock(self, DeviceName):
    """
    :Parameters:
      DeviceName : str
    :Exceptions:
      ValueError
        If the read block identifier ois wrong.
    """
    CEBlock = self.CEs[DeviceName]
    self.__fout.seek(CEBlock)
    BlockTypeId,\
    BlockSize,\
    ExtensionType = mdf.CEstruct.unpack(self.__fout.read(mdf.CEstruct.size))
    if BlockTypeId != 'CE':
      raise ValueError, BlockTypeId
    if ExtensionType == 2:
      self.__fout.write(self.EmptyDIMstruct)
    elif ExtensionType == 19:
      self.__fout.write(self.EmptyCANstruct)
    self.__fout.flush()
    pass

  def __read_raw_value(self, Signal, DType=None):
    """
    Read the raw values of the selected signal.

    :Parameters:
      Signal : dict
        The parameter cointaner of the selected signal.
    :ReturnType: `ndarray`
    :Return:      The read raw values.
    """
    NoRecords = Signal['NoRecords']
    DataBlock = Signal['DataBlock']
    BlockSize = Signal['SizeOfDataRecord']

    DTypes, DType_, UpShift, DownShift = calcReadAttrs(self.Orders, mdf.Formats, **Signal)
    DType = DType_ if DType is None else DType

    Splits, DataBlockExtra = calcSplits(DTypes)
    DataBlock += DataBlockExtra

    return mdf.readRaw(self.__fin, DataBlock, BlockSize, NoRecords, DType, UpShift, DownShift, Splits)

  def __write_raw_value(self, Signal, Value):
    """
    Change the values of the `Signal` in the `__fout` to `RawValues`.

    :Parameters:
      Signal : dict
        The parameter cointaner of the selected signal.
      Value : `ndarray`
        The new value os the selected signal.
    """
    if not self.__fout:
      sys.stderr.write('The output file is not loaded!\n')
      sys.exit()

    DTypes, DType, UpShift, DownShift = calcReadAttrs(self.Orders, mdf.Formats, **Signal)
    self.__fin.seek(Signal['DataBlock'])
    Values = numpy.fromfile(self.__fin, dtype=DTypes, count=Signal['NoRecords'])

    Order, Format, Size = mdf.splitDType(DType)


    BitOffset = Signal['StartOffsetInBits'] % 8
    BitUpset = Size * 8 - Signal['NumberOfBits'] - BitOffset
    Mask = ((1 << Signal['NumberOfBits']) - 1) << BitOffset
    Unmask = ~Mask

    if 'value' in dict(DTypes):
      if BitOffset or BitUpset:
        RawType = DType.replace(Format, 'u')
        Value = Value.copy()
        Value.dtype = RawType
        Values['value'].dtype = RawType
        Values['value'] = (Value << BitOffset & Mask) | (Values['value'] & Unmask)
      else:
        Values['value'] = Value
    else:
      for i, ByteOffset in enumerate(ByteOffsets):
        Part = Value >> i * 8 & 255
        if BitOffset or BitUpset:
          PartMask = Mask >> i*8 & 255
          PartUnmask = Unmask >> i*8 & 255
          PartOffset = BitOffset >> i*8 & 255
          Part.dtype = '<u1'
          Values[ByteOffset].dtype = '<u1'
          Values[ByteOffset] = (Part << PartOffset & PartMask) | (Values[ByteOffset] & PartUnmask)
        else:
          Values[ByteOffset] = Part
    self.__fout.seek(Signal['DataBlock'])
    Values.tofile(self.__fout)
    self.__fout.flush()
    return

  def __convert_RAW_PHY(self, Signal, Value, Factor=None, Offset=None):
    """
    Convert the raw value into physical value of the selected `Signal`.

    :Parameters:
      Signal : dict
        The parameter cointaner of the selected signal.
      Value : `ndarray`
        The raw values.
    :ReturnType: `ndarray`
    :Return: The converted physical value.
    """
    ConversionType           = Signal['ConversionType']
    AdditionalConversionData = Signal['AdditionalConversionData']
    return mdf.convRawPhy(Value, ConversionType, AdditionalConversionData,
                          Factor=Factor, Offset=Offset)

  def __convert_PHY_RAW(self, Signal, Phys):
    """
    Convert the physical value into raw value of the selected `Signal`.

    :Parameters:
      Signal : dict
        The parameter cointaner of the selected signal.
      Phys : `ndarray`
        The physical values.
    :ReturnType: `ndarray`
    :Return: The converted raw value.
    """
    ConversionType           = Signal['ConversionType']
    AdditionalConversionData = Signal['AdditionalConversionData']

    if ConversionType == 0:
      AddConLen = len(AdditionalConversionData)
      if AddConLen == 2:
        return (Phys - AdditionalConversionData[0]) / AdditionalConversionData[1]
      elif AddConLen == 0:
        return Phys
      else:
        print >> sys.stderr, 'AdditionalConversionData is invalid in __convert_PHY_RAW!'
        sys.exit(1)
    elif ConversionType == 12:
      return Phys
    else:
      sys.stderr.write('New ConversionType must be implemented in __convert_PHY_RAW: %d!\n' %ConversionType)
      sys.exit(1)
    pass
  pass


if __name__ == '__main__':
  import copy
  import optparse

  import pylab

  parser = optparse.OptionParser()
  parser.add_option('-m', '--measurement',
                    help='measurement file, default is %default',
                    default='d:/measurement/dataeval-test/CVR3_B1_2011-02-10_16-53_020.mdf')
  parser.add_option('-o', '--measout',
                    help='modified measurement file, default is %default',
                    default='d:/measurement/dataeval-test/CVR3_B1_2011-02-10_16-53_020.mod.mdf')
  parser.add_option('-p', '--plot',
                    help='Plot the signals, default is %default',
                    default=False,
                    action='store_true')
  Opts, Args = parser.parse_args()

  DeviceName1  = 'MRR1plus-0-0'
  SignalName11 = 'csi.VehicleData_T20.nMot'
  SignalName12 = 'sit.IntroFinder_TC.Intro.i0.Id'
  DeviceName2  = 'EBC2-98FEBF0B-1-EBS'
  SignalName21 = 'speed_rear1_left'
  DeviceName3  = 'ASC2_A-8CD22F21-1-ZBR'

  myMdfParser = cMdfParser(Opts.measurement)

  SignalValues10, TimeKey10 = myMdfParser.getSignal(DeviceName1, SignalName11)
  TimeStamps10              = myMdfParser.getTime(TimeKey10)

  SignalValues20, TimeKey20 = myMdfParser.getSignal(DeviceName1, SignalName12)
  TimeStamps20              = myMdfParser.getTime(TimeKey20)

  # change the signal to 1 from start to 10.0 [s]
  SignalValues11 = copy.deepcopy(SignalValues10)
  SignalValues11[:TimeStamps10.searchsorted(180.0)] = 1

  SignalValues21 = numpy.zeros_like(SignalValues20)
  SignalValues21[TimeStamps20.searchsorted(180.0):] = 1

  myMdfParser.openOutputFile(Opts.measout)
  myMdfParser.setSignal(DeviceName1, SignalName11, SignalValues11)
  myMdfParser.setSignal(DeviceName1, SignalName12, SignalValues21)
  myMdfParser.rmSignal( DeviceName2, SignalName21)
  myMdfParser.rmDevice( DeviceName3)
  myMdfParser.closeOutputFile()

  myMdfParser2 = cMdfParser(Opts.measout)
  SignalValues12, TimeKey12 = myMdfParser2.getSignal(DeviceName1, SignalName11)
  SignalValues22, TimeKey22 = myMdfParser2.getSignal(DeviceName1, SignalName12)

  print '\n'.join(myMdfParser.Devices[DeviceName2].keys())
  assert SignalName21 in myMdfParser.Devices[ DeviceName2],\
         'original measurement is not complete'
  print '='*80
  print '\n'.join(myMdfParser2.Devices[DeviceName2].keys())
  assert SignalName21 not in myMdfParser2.Devices[DeviceName2],\
         'purged measurement still contains the purged signal'
  print '='*80
  print DeviceName3 in myMdfParser2.Devices
  assert DeviceName3 not in myMdfParser2.Devices,\
         'purged measurement still contains the purges device'
  print myMdfParser.getTimeKey(DeviceName1, SignalName11)
  assert myMdfParser.getTimeKey(DeviceName1, SignalName11) == '00002',\
         'wrong timekey for %s %s' %(DeviceName1, SignalName11)
  print myMdfParser.getSignalLength(DeviceName2, SignalName21)
  assert myMdfParser.getSignalLength(DeviceName2, SignalName21) == 1498,\
         'wrong signal length for %s %s' %(DeviceName2, SignalName21)

  if Opts.plot:
    pylab.figure(1)
    pylab.plot(TimeStamps10, SignalValues10, TimeStamps10, SignalValues12)
    pylab.figure(2)
    pylab.plot(TimeStamps20, SignalValues20, TimeStamps20, SignalValues22)
    pylab.show()
  myMdfParser.close()
  myMdfParser2.close()


