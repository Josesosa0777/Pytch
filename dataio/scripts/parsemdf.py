#!/usr/bin/env python
"""
python -m parsemf4 [option...] measurementfile

*options*

-f  format:        hdf5
                   if it is not selected no file will be created
                   if no -o option is added the ouput file name is generated
                   based on format
                     hdf5 : .h5

-d  driver:        sec2, stdio, core, family
                   hdf5 file driver

-c  compression:   zlib
                   hdf5 channel compression

-l  comp-level:    0-9
                   compression level 0 (default) means no compression

-o  file-name:     output file name

-s  signalpattern: print the properties of the signal which match to
                   signalpattern regexp

-v  verboselevel:  0,1,2
"""

import sys
import os
import getopt
import re
import copy

import numpy

from measparser.mdf import IDstruct,\
                           HDstruct,\
                           DGstruct,\
                           CGstruct,\
                           CNstruct,\
                           VoidFormats,\
                           Orders,\
                           Formats,\
                           extractCC,\
                           extractCE,\
                           extractTX,\
                           toDTypes,\
                           getValues,\
                           getValue,\
                           convRawPhy,\
                           getTypeSize,\
                           setDefaultByteOrder,\
                           calcReadAttrs,\
                           calcRecord,\
                           patchRecord,\
                           splitDType,\
                           stripZeroChar,\
                           isMdfSorted,\
                           sortMdf

from measparser.Hdf5Parser import init,\
                                  getCompression,\
                                  setHeader,\
                                  addSignal

from measparser.namedump import NameDump

Orders = Orders.copy()


if '-h' in sys.argv:
  print __doc__
  exit(0)

Exts = {None:   '.foo',
        'hdf5': '.h5'}

Opts, Files = getopt.getopt(sys.argv[1:], 'c:l:v:o:f:s:h')
OptDict = dict(Opts)

ShowSignals = [re.compile(v) for k, v in Opts if k == '-s']

ConvFormat  = OptDict.get('-f')
Compression = OptDict.get('-c')
Verbose     = OptDict.get('-v', 0)
CompLevel   = OptDict.get('-l', 0)
CompLevel   = int(CompLevel)

MdfName = Files[0]
if '-o' in OptDict:
  HdfName = OptDict['-o']
else:
  _Name, _Ext = os.path.splitext(MdfName)
  HdfName = _Name + Exts.get(ConvFormat)
  NameDumpName = _Name + '.db'

if not isMdfSorted(MdfName):
  sortMdf(MdfName)

if ConvFormat == 'hdf5':
  H5pyComp = getCompression(Compression, CompLevel)
  Hdf5, Devices, Times = init(HdfName)

Mdf = open(MdfName, 'rb')

CCs = {0: (12, 0, '')}
CEs = {0: ('NULL', 'NULL')}

FileIdentifier,\
FormatIdentifier,\
ProgramIdentifier,\
DefaultByteOrder,\
DefaultFloatingPointFormat,\
VersionNumber = IDstruct.unpack(Mdf.read(IDstruct.size))

DefaultByteOrder = '>' if DefaultByteOrder else '<'
setDefaultByteOrder(Orders, DefaultByteOrder)

UnionType = DefaultByteOrder + 'u1'

Mdf.seek(64)

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
TimerId = HDstruct.unpack(Mdf.read(HDstruct.size))

Comment = extractTX(Mdf, FileComment)

if ConvFormat == 'hdf5':
  setHeader(Hdf5, RecordStartTime_us, Comment)

DG = 0
while DGlink != 0:
  Mdf.seek(DGlink)

  BlockTypeId,\
  BlockSize,\
  DGlink,\
  CGlink,\
  TRlink,\
  DataBlock,\
  NoCGs,\
  NoRecordIDs = DGstruct.unpack(Mdf.read(DGstruct.size))
  DG += 1
  while CGlink != 0:
    Mdf.seek(CGlink)

    BlockTypeId,\
    BlockSize,\
    CGlink,\
    CNlink,\
    GroupComment,\
    RecordID,\
    NoCNs,\
    SizeOfDataRecord,\
    NoRecords,\
    FirstSampleReductionBlock= CGstruct.unpack(Mdf.read(CGstruct.size))

    if Verbose > 1:
      print >> sys.stderr, 'data group (%d/%d)' %(NoDGs, DG)
      print >> sys.stderr, '  number of channels: %d' %NoCNs
      print >> sys.stderr, '  length of channels: %d' %NoRecords

    if not NoRecords and not ShowSignals:
      if Verbose > 1:
        print >> sys.stderr, "data group %d is skipped, because it's empty" %DG
      continue

    Record = {}
    Reserve = {}
    Signals = {}
    TimeKey = '%05d' %(DG-1)
    while CNlink != 0:
      Mdf.seek(CNlink)

      BlockTypeId,\
      BlockSize,\
      CNlink,\
      CClink,\
      CElink,\
      DependencyBlock,\
      ChannelComment,\
      ChannelType,\
      ShortSignalName,\
      SignalDescription,\
      StartOffsetInBits,\
      NumberOfBits,\
      SignalDataType,\
      ValueRangeValid,\
      MinimumSignalValue,\
      MaximumSignalValue,\
      SamplingRate,\
      LongSignalName,\
      DisplayName,\
      AdditionalByteOffset = CNstruct.unpack(Mdf.read(CNstruct.size))

      if ChannelType:
        Name = TimeKey
      elif LongSignalName:
        Name = extractTX(Mdf, LongSignalName)
      else:
        Name = ShortSignalName.split('\0')[0]

      DType,\
      ByteSize,\
      DByteSize,\
      ByteOffset,\
      UpShift,\
      DownShift = calcReadAttrs(Orders,
                                Formats,
                                SignalDataType,
                                NumberOfBits,
                                StartOffsetInBits,
                                AdditionalByteOffset)

      ByteOffsets = []
      Signal = dict(ByteOffsets=ByteOffsets,
                    CElink=CElink,
                    CClink=CClink,
                    UpShift=UpShift,
                    DownShift=DownShift,
                    DType=DType)
      Signals[Name] = Signal

      calcRecord(Record,
                 Reserve,
                 Signals,
                 ByteOffsets,
                 Name,
                 ByteOffset,
                 ByteSize,
                 DByteSize,
                 DType,
                 UnionType)

      try:
        ConversionType, AdditionalConversionData, PhysicalUnit = CCs[CClink]
      except KeyError:
        CCs[CClink] = extractCC(Mdf, CClink)

      try:
        DeviceName, DeviceExt = CEs[CElink]
      except KeyError:
        DeviceName, DeviceExt = extractCE(Mdf, CElink)
        if not DeviceName:
          DeviceName = 'NULL'
        CEs[CElink] = DeviceName, DeviceExt

    if ConvFormat is not None and NoRecords:
      patchRecord(Record)
      DTypes = toDTypes(Record)
      Values = getValues(Mdf, DTypes, DataBlock, NoRecords)
      for Name, Signal in Signals.iteritems():
        Value = getValue(Values,
                         NoRecords,
                         Signal['ByteOffsets'],
                         Signal['DType'],
                         Signal['UpShift'],
                         Signal['DownShift'])
        ConversionType,\
        AdditionalConversationData,\
        PhysicalUnit = CCs[Signal['CClink']]
        Value = convRawPhy(Value, ConversionType, AdditionalConversationData)

        DeviceName, DeviceExt = CEs[Signal['CElink']]
        if ConvFormat == 'hdf5':
          addSignal(Devices,
                    Times,
                    DeviceName,
                    DeviceExt,
                    Name,
                    TimeKey,
                    Value,
                    H5pyComp,
                    PhysicalUnit,
                    Comment='')

    if ShowSignals:
      for Name, Signal in Signals.iteritems():
        for ShowSignal in ShowSignals:
          if ShowSignal.search(Name):
            Signal = Signals[Name]
            print Name
            print '  data group number:  %d'               %(DG)
            print '  data block:         %d'               %DataBlock
            print '  byte offsets:       %(ByteOffsets)s'  %Signal
            print '  upper garbage bits: %(UpShift)d'      %Signal
            print '  all garbage bits:   %(DownShift)s'    %Signal
            print '  dtype:              %(DType)s'        %Signal
            print '  device name:        %s-%s'        %CEs[Signal['CElink']]
            print '  conversation type:  %d\n'\
                  '               data:  %s\n'\
                  '               unit:  %s\n'         %CCs[Signal['CClink']]


Mdf.close()
if ConvFormat == 'hdf5':
  Hdf5.close()
  namedump = NameDump.fromMeasurement(MdfName, DbName=NameDumpName)
  namedump.close()

