import struct
import sys
import os
import subprocess
import numpy
import copy
import logging

import iParser

IDstruct  = struct.Struct('<8s8s8sHHH')
HDstruct  = struct.Struct('<2sH3IH10s8s32s32s32s32sQhH32s')
DGstruct  = struct.Struct('<2sH4IHH')
CGstruct  = struct.Struct('<2sH3I3H2I')
CNstruct  = struct.Struct('<2sH5IH32s128s4H3d2IH')
CCstruct  = struct.Struct('<2s2H2d20s2H')
TXstruct  = struct.Struct('<2sH')
CEstruct  = struct.Struct('<2s2H')
DIMstruct = struct.Struct('<HI80s32s')
CANstruct = struct.Struct('<2I36s36s')

Orders = { 0:'',   1:'',   2:'',   3:'',
           4:'',   5:'',   6:'',
           7:'',   8:'',
           9:'>', 10:'>', 11:'>', 12:'>',
          13:'<', 14:'<', 15:'<', 16:'<'}


def setDefaultByteOrder(Orders, DefaultByteOrder):
  for i in xrange(9):
    Orders[i] = DefaultByteOrder
  return Orders


Formats = { 0:'u',  1:'i',  2:'f',  3:'f',
            4:'f',  5:'f',  6:'f',
            7:'a',  8:'V',
            9:'u', 10:'i', 11:'f', 12:'f',
           13:'u', 14:'i', 15:'f', 16:'f'}


VoidFormats = 'a', 'V', 'f'


ByteSizes = {0:0}
for bit in xrange(1, 65):
  if bit <= 8:
    ByteSizes[bit] = 1
  elif bit <= 16:
    ByteSizes[bit] = 2
  elif bit <= 24:
    ByteSizes[bit] = 3
  elif bit <= 32:
    ByteSizes[bit] = 4
  elif bit <= 40:
    ByteSizes[bit] = 5
  elif bit <= 48:
    ByteSizes[bit] = 6
  elif bit <= 56:
    ByteSizes[bit] = 7
  elif bit <= 64:
    ByteSizes[bit] = 8


DTypeSizes = {0:0}
for byte in xrange(1, 9):
  if byte <= 1:
    DTypeSizes[byte] = 1
  elif byte <= 2:
    DTypeSizes[byte] = 2
  elif byte <= 4:
    DTypeSizes[byte] = 4
  elif byte <= 8:
    DTypeSizes[byte] = 8


class UnknownChannelExtensionError(BaseException):
  pass


class UnknownChannelConversionError(BaseException):
  pass


def getVersion(name):
  if    not os.path.isfile(name)\
     or os.path.getsize(name) < 16:
    return '', ''
  f = open(name)
  Version = f.read(16)
  f.close()
  try:
    File, Version = Version.split()
  except ValueError:
    return '', ''
  else:
    return File, Version

def splitDType(DType):
  return DType[0], DType[1], int(DType[2:])


def getTypeSize(DType):
  return int(DType[2:])


def extractTX(f, link):
  if link == 0:
    return ''
  f.seek(link)
  BlockTypeId,\
  BlockSize = TXstruct.unpack(f.read(TXstruct.size))

  if BlockSize == 0:
    return ''

  Struct = struct.Struct('<' + str(BlockSize - TXstruct.size) + 's')
  Text   = Struct.unpack(f.read(Struct.size))[0]
  i = Text.find('\0')
  if i != -1:
    Text = Text[:i]
  return Text

def extractCE(f, link):
  f.seek(link)

  BlockTypeId  ,\
  BlockSize    ,\
  ExtensionType = CEstruct.unpack(f.read(CEstruct.size))
  if ExtensionType == 2:
    ModuleNr,\
    Address,\
    Description,\
    ECU_ID = DIMstruct.unpack(f.read(DIMstruct.size))
    ECU_ID = ECU_ID.split('\x00')[0]
    DeviceName = ECU_ID
    DeviceExt  = '%X' %Address, '%d' %ModuleNr
  elif ExtensionType == 19:
    CANMessageID,\
    CANChannelIndex,\
    MessageName,\
    SenderName  = CANstruct.unpack(f.read(CANstruct.size))
    MessageName = MessageName.split('\x00')[0]
    SenderName  = SenderName.split('\x00')[0]
    DeviceName  = MessageName
    DeviceExt   = '%X' %CANMessageID, '%d' %CANChannelIndex, SenderName
  else:
    raise UnknownChannelExtensionError(str(ExtensionType))
  DeviceExt = iParser.DEVICE_NAME_SEPARATOR.join(DeviceExt)
  return DeviceName, DeviceExt


def extractCC(f, link):
  f.seek(link)

  BlockTypeId,\
  BlockSize,\
  PhysicalValueRangeValid,\
  MinimumPhysicalSignalValue,\
  MaximumPhysicalSignalValue,\
  PhysicalUnit,\
  ConversionType,\
  SizeInformation = CCstruct.unpack(f.read(CCstruct.size))

  PhysicalUnit = PhysicalUnit.split('\0')[0]

  AdditionalConversionData = []
  if ConversionType in (0, 6, 7, 8, 9):
    Struct = struct.Struct('<' + SizeInformation * 'd')
    AdditionalConversionData = Struct.unpack(f.read(Struct.size))
    if AdditionalConversionData == (0, 1):
      AdditionalConversionData = []
  # 1 = tabular with interpolation
  # 2 = tabular
  elif ConversionType in (1, 2):
    Struct = struct.Struct('<' + SizeInformation * 'dd')
    temp = Struct.unpack(sf.read(Struct.size))
    for coeff in zip(temp[:-1:2], temp[1::2]):
      AdditionalConversionData.append(coeff)
  # ASAM-MCD2 Text Table, (COMPU_VTAB)
  elif ConversionType == 11:
    Struct = struct.Struct('<' + SizeInformation * 'd32s')
    temp = Struct.unpack(f.read(Struct.size))
    for coeff in zip(temp[:-1:2], temp[1::2]):
      AdditionalConversionData.append(coeff)
  # ASAM-MCD2 Text Range Table (COMPU_VTAB_RANGE)
  elif ConversionType == 12:
    Struct = struct.Struct('<' + SizeInformation * 'ddI')
    temp = Struct.unpack(f.read(Struct.size))
    for coeff in zip(temp[:-2:3], temp[1:-1:3], temp[2::3]):
      AdditionalConversionData.append(coeff)
  # ASAM-MCD2 Text formula
  elif ConversionType == 10:
    Struct = struct.Struct('<' + SizeInformation * 's')
    AdditionalConversionData = Struct.unpack(f.read(Struct.size))
  return ConversionType, AdditionalConversionData, PhysicalUnit


def isMdfSorted(FileName):
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
  TimerId = HDstruct.unpack(f.read(HDstruct.size))

  Sorted = False
  while DGlink:
    f.seek(DGlink)

    BlockTypeId,\
    BlockSize,\
    DGlink,\
    CGlink,\
    TRlink,\
    DataBlock,\
    NoCGs,\
    NoRecordIDs = DGstruct.unpack(f.read(DGstruct.size))
    if NoRecordIDs != 0:
      break
  else:
    Sorted = True
  f.close()
  return Sorted


def sortMdf(FileName):
  call = '%s\\%s -S "%s"' %(os.path.dirname(__file__), 'mdfsort.exe', FileName)
  print >> sys.stderr, call
  o = subprocess.call(call)
  if o != 0:
    print >> sys.stderr, 'mdf sorting was unsuccessful'
    exit(o)
  return

def readRaw(f, DataBlock, BlockSize, NoRecords, DType, UpShift, DownShift,
            Splits=None):
  Value = readSortedData(f, DataBlock, BlockSize, NoRecords, DType, Splits)
  Value = shift(Value, UpShift, DownShift, DType)
  return Value

def readData(f, DataBlock, VoidOffset, RecSizes, RecIdSize, RecId, NoRecords,
             DType, UpShift, DownShift, Splits=None):
  if RecIdSize:
    Data = readUnsortedData(f, DataBlock, RecSizes, RecIdSize, RecId,
                            NoRecords, DType, VoidOffset, Splits)
  else:
    Data = readSortedData(f, DataBlock+VoidOffset, RecSizes[RecId], NoRecords,
                          DType, Splits)
  Data = shift(Data, UpShift, DownShift, DType)
  return Data

def readSortedData(f, DataBlock, BlockSize, NoRecords, DType, Splits):
  if Splits:
    Value = SplitData(f, NoRecords, DType, Splits)
  else:
    Value = Data(f, NoRecords, DType, Splits)

  for i, s in enumerate(xrange(DataBlock, DataBlock+NoRecords*BlockSize, BlockSize)):
    f.seek(s)
    try:
      Value.fill(i)
    except ValueError:
      sys.stderr.write(
        'Warning: EOF is reached signal length is cut from %d to %d\n'
        %(NoRecords, i))
      sys.stderr.flush()
      Value.chunk(i)
      break

  Value.shift()
  return Value.Value

class Data:
  def __init__(self, f, NoRecords, DType, Splits):
    self.Value = numpy.zeros(NoRecords, dtype=DType)
    self.f = f
    return

  def fill(self, i):
    self.Value[i], = numpy.fromfile(self.f, dtype=self.Value.dtype, count=1)
    return

  def chunk(self, i):
    self.Value = self.Value[:i]
    return

  def shift(self):
    return

class SplitData:
  def __init__(self, f, NoRecords, DType, Splits):
    self.Value = numpy.zeros((NoRecords, Splits), dtype='<u1')
    self.Splits = Splits
    self.DType = DType
    self.f = f
    return

  def fill(self, i):
    self.Value[i,:] = numpy.fromfile(self.f, dtype='<u1', count=self.Splits)
    return

  def chunk(self, i):
    self.Value = self.Value[:i,:]
    return

  def shift(self):
    Order, Format, Size = splitDType(self.DType)
    if Order == '<':
      Shift = numpy.arange(0, self.Splits*8, 8)
    else:
      Shift = numpy.arange(self.Splits*8, 0, -8)
    self.Value = (self.Value << Shift).sum(axis=1)
    return

RecorIdTypes = {
  0: None,
  1: struct.Struct('<B'),
  2: struct.Struct('<H'),
  4: struct.Struct('<I'),
  8: struct.Struct('<Q'),
}

def readUnsortedData(f, DataBlock, RecSizes, RecIdSize, RecId, NoRecords,
                     DType, VoidOffset, Splits):
  if Splits:
    Value = SplitData(f, NoRecords, DType, Splits)
  else:
    Value = Data(f, NoRecords, DType, Splits)

  RecorIdType = RecorIdTypes[RecIdSize]
  RecordNr = 0
  f.seek(DataBlock)
  _RecId, = RecorIdType.unpack(f.read(RecIdSize))

  while RecordNr != NoRecords and _RecId in RecSizes:
    RecSize = RecSizes[_RecId]
    if _RecId == RecId:
      f.seek(VoidOffset, 1)
      Value.fill(RecordNr)
      RecordNr += 1
    else:
      f.seek(RecSize, 1)
    _RecId, = RecorIdType.unpack(f.read(RecIdSize))

  if RecordNr != NoRecords:
    sys.stderr.write(
      'Warning: invalid record id is reached signal length is cut from %d to %d\n'
      %(NoRecords, RecordNr))
    sys.stderr.flush()
    Value.chunk(RecordNr)

  Value.shift()
  return Value.Value

def shift(Value, UpShift, DownShift, DType):
  Order, Format, Size = splitDType(DType)

  if UpShift:
    Value <<= UpShift
  if Value.dtype != DType:
    Value.dtype = DType
  if DownShift:
    Value >>= DownShift

  if Format == 'a':
    Value = stripZeroChar(Value)
  return Value

def convRawPhy(Value, Type, Data, Factor=None, Offset=None):
  if Type == 0:
    if Factor and Offset:
      Value = Value * Factor + Offset
    elif Data:
      Offset_, Factor_ = Data
      Factor = Factor_ if Factor is None else Factor
      Offset = Offset_ if Offset is None else Offset
      Value = Value * Factor + Offset
  elif Type in (10, 11, 12):  # text data
    pass
  elif Type == 65535:  # 1:1 mapping
    pass
  else:
    raise UnknownChannelConversionError()
  return Value

def stripZeroChar(Value):
  for i, E in enumerate(Value):
    p = E.find('\0')
    if p == -1:
      continue
    Value[i] = E[:p]
  return Value

def calcReadAttrs(Orders,
                  Formats,
                  SignalDataType,
                  NumberOfBits,
                  StartOffsetInBits,
                  AdditionalByteOffset):
  """
  :Parameters:
    Orders : dict
      {SignalType<int>: '<|>'}
    Formats : dict
      {SignalType<int>: 'u|i|f|a'}
    NumberOfBits : int
    StartOffsetInBits : int
    AdditionalByteOffset : int
  :ReturnType: str, int, int, int, int, int
  :Return:
    String representation of the required numpy dtype.
    Required number of byte to read a channel element.
    Byte size of the required numpy dtype.
    Byte offset insdie the channel group.
    Number of bits to mask above the channel element in numpy dtype.
    Number of bits to mask below the channel element in numpy dtype.
  """
  ByteOffset = AdditionalByteOffset + StartOffsetInBits / 8
  BitOffset  = StartOffsetInBits % 8
  BitNeeded  = BitOffset + NumberOfBits
  Format     = Formats[SignalDataType]

  if Format in VoidFormats and not (BitOffset or NumberOfBits % 8):
    ByteSize  = NumberOfBits / 8
    DByteSize = ByteSize
    DownShift = 0
    UpShift   = 0
  else:
    ByteSize  = ByteSizes[BitNeeded]
    DByteSize = DTypeSizes[ByteSize]
    DownShift = DByteSize * 8 - NumberOfBits
    UpShift   = DownShift - BitOffset

  Order = Orders[SignalDataType]
  DType = '%s%s%d' %(Order, Format, DByteSize)

  return DType, ByteSize, DByteSize, ByteOffset, UpShift, DownShift


def calcRecord(Record,
               Reserve,
               Signals,
               ByteOffsets,
               Name,
               ByteOffset,
               ByteSize,
               DByteSize,
               DType,
               UnionType):
  """
  Calcuates record to read a whole channel group together.

  :Parameters:
    Record : dict
      {ByteOffset<int>: DType<str>, [Name<str>]}
    Reserve : dict
      {ByteOffset<int>: NoByte<int>}
    Signals : dict
      {Name<str>: {'ByteOffsets': [ByteOffset<int>], ...}}
    ByteOffsets : list
      [ByteOffset<int>]
    Name : str
      Name of the channel.
    ByteOffset : int
      Byte offset of the channel inside the channel group.
    ByteSize : int
      Byte size of the channel.
    DByteSize : int
      ByteSize of the channel to read into a numpy type.
    DType : str
      String representation of the numpy dtype.
    UnionType : str
      String representation of the unsigned 1 byte integer numpy dtype.
  """
  if ByteSize != DByteSize:
    ByteOffsets.extend(xrange(ByteOffset, ByteOffset+ByteSize))
    DType = UnionType
    ByteSize = 1
  else:
    ByteOffsets.append(ByteOffset)

  for ByteOffset in copy.copy(ByteOffsets):
    if ByteOffset in Record and Record[ByteOffset][0] == DType:
      Record[ByteOffset][1].append(Name)
    else:
      if DType[1] in VoidFormats:
        Record[ByteOffset] = DType, [Name]
        continue
      Size = ByteSize
      ROffset = ByteOffset
      ROffsets = []
      while Size > 0:
        try:
          NoByte = Reserve[ROffset]
        except KeyError:
          Jump = 1
        else:
          RStart = ROffset - NoByte
          ROffsets.append(RStart)
          Jump = getTypeSize(Record[RStart][0]) - NoByte
        finally:
          ROffset += Jump
          Size -= Jump
      if ROffsets:
        ByteOffsets.extend(xrange(ByteOffset+1, ByteOffset+ByteSize))
        for Offset in set(ByteOffsets).difference(ROffsets):
          Reserve[Offset] = 0
          Record[Offset] = UnionType, [Name]
        for Offset in ROffsets:
          RDType, RNames = Record[Offset]
          RByteOffsets = range(Offset, Offset+getTypeSize(RDType))
          if RDType != UnionType:
            for RName in RNames:
              Signals[RName]['ByteOffsets'] = RByteOffsets
          RNames.append(Name)
          for ROffset in RByteOffsets:
            Reserve[ROffset] = 0
            Record[ROffset] = UnionType, RNames
      else:
        Record[ByteOffset] = DType, [Name]
        for NoByte, Offset in enumerate(xrange(ByteOffset, ByteOffset+ByteSize)):
          Reserve[Offset] = NoByte
  return


def patchRecord(Record):
  """
  :Parameters:
    Record : dict
      {ByteOffset<int>: DType<str>, [Name<str>]}
  """
  Pos = 0
  Size = 0
  for ByteOffset in sorted(Record):
    Gap = ByteOffset - Pos
    if Gap:
      Record[ByteOffset-Size] = '|a%d' %Gap, []
      Pos += Gap
    DType, Names = Record[ByteOffset]
    Size = getTypeSize(DType)
    Pos += Size
  return


def toDTypes(Record):
  DTypes = [(str(ByteOffset), Record[ByteOffset][0])
             for ByteOffset in sorted(Record)]
  return numpy.dtype(DTypes)

def getValues(Mdf, DTypes, DataBlock, NoRecords):
  Mdf.seek(DataBlock)
  return numpy.fromfile(Mdf, dtype=DTypes, count=NoRecords)


def getValue(Values, NoRecords, ByteOffsets, DType, UpShift, DownShift):
  Order, Format, Size = splitDType(DType)

  ByteOffsets = [str(ByteOffset) for ByteOffset in ByteOffsets]

  try:
    ByteOffset, = ByteOffsets
  except ValueError:
    RawType = Order+'u'+str(Size)
    Value = numpy.zeros(NoRecords, dtype=RawType)
    if Order == '>':
      ByteOffsets.reverse()
    for i, ByteOffset in enumerate(ByteOffsets):
      Raw = Values[ByteOffset].astype(RawType)
      Raw <<= 8 * i
      Value += Raw
  else:
    Value = Values[ByteOffset]
    if DownShift or UpShift or Value.dtype != DType:
      Value = Value.copy()

  if UpShift:
    Value <<= UpShift

  if Value.dtype != DType:
    Value.dtype = DType

  if DownShift:
    Value >>= DownShift

  if Format == 'a':
    Value = stripZeroChar(Value)
  return Value

