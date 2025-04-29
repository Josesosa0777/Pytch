#!/usr/bin/python

import re
import struct
import os

import numpy

import iParser

class cDatParser(iParser.iParser):
  @staticmethod
  def checkParser(FileName):
    FileName = FileName.lower()
    return FileName.endswith('.dat') and os.path.isfile(FileName)


  def __init__(self, FileName):
    iParser.iParser.__init__(self)
    self.filePath = FileName
    # self.words = {}
    self.lengthCount = {}
    self.channel_count = 0 
    self.datEntries = { '200'  : 'chName',
                        '202'  : 'unit',
                        '210'  : 'channelType',
                        '211'  : 'sourceFile',
                        '213'  : 'dataStruct',
                        '214'  : 'dataType',
                        '220'  : 'size',
                        '221'  : 'channelPos',
                        '222'  : 'binBlock',
                        'null' : 'startPos',
                        '240'  : 'startVal',
                        '241'  : 'stepVal',
                        '250'  : 'minVal',
                        '251'  : 'maxVal'}

    self.binFormat = {'REAL32'  : 4,
                      'REAL48'  : 6,
                      'REAL64'  : 8,
                      'MSREAL32': 4,
                      'INT16'   : 2,
                      'INT32'   : 4,
                      'WORD8'   : 1,
                      'WORD16'  : 2,
                      'WORD32'  : 4,
                      'TWOC12'  : None,
                      'TWOC16'  : 2}
    self.TimeKey = os.path.basename(FileName)
    self.fileRead()
    # print("done")


  def getSignal(self, DeviceName, SignalName):
    Device = self.Devices[DeviceName]
    Signal = Device[SignalName]
    RawValues = self.readRawValue(SignalName, DeviceName)
    TimeKey = Signal['TimeKey']
    # print RawValues, TimeKey
    return RawValues, TimeKey

  def getSignalLength(self, DeviceName, SignalName):
    Device = self.Devices[DeviceName]
    Signal = Device[SignalName]
    Attr   = Signal['TimeKey']
    # print "LENGTH :", DeviceName, SignalName, Attr
    return Attr

  def getTime(self, TimeKey):
    Time  = self.Times[TimeKey]
    Value = self.createTime(Time)
    print "Time", Time
    return Value

  def createTime(self, Time):
    return numpy.linspace(Time['Start'], Time['End'], Time['Size'])
      
  def getTimeKey(self, DeviceName, SignalName):
    Device = self.Devices[DeviceName]
    Signal = Device[SignalName]
    TimeKey = Signal['TimeKey']
    print "Timekey", TimeKey
    return TimeKey

  def procChannel(self, words):
    cName  = words.pop('chName')
    fName  = words.pop('sourceFile')
    dType  = words['dataType']

    Signal = words.copy()
#    Signal['TimeKey']  = cName
    Signal['TimeKey'] = self.TimeKey
    self.lengthCount.setdefault(fName, 0)
    Signal['startPos'] = self.lengthCount[fName]
    self.lengthCount[fName] += self.binFormat[dType]
    Device = self.Devices.setdefault(fName, {})
    Device[cName] = Signal
    pass

  def procTime(self, words):
    Time = {}
    Time['Start'] = float(words['minVal'])
    Time['Step']  = float(words['stepVal'])
    Time['End']   = float(words['maxVal'])
    Time['Size']  = int(  words['size'])
    self.Times[self.TimeKey] = Time
    pass

  def fileRead(self):
    #docName = docName.replace(r"\\","\\")
    words = {}
    f = open(self.filePath)
    line = f.readline()
    while line:
      line.strip()
      if line.startswith('#ENDCHANNELHEADER'):
        if words['chName'] == 'time':
          self.procTime(words)
        else:
          self.procChannel(words)
        words.clear()
      else:
        match = re.search('^(\\d{3}),(.*)',line)
        if match:
          Key, Value = match.groups()
          if Key in self.datEntries:
            Key = self.datEntries[Key]
            words[Key] = Value
      line = f.readline()
    f.close()
    pass

  def readRawValue(self, SignalName, docName):
    values = []
    channelName = SignalName
    ext = re.search('(\.\w{3}$)', docName)
    binFile = self.filePath.replace(".DAT",ext.group(1))
    FH = open(binFile,'rb')
    block = FH.read(self.lengthCount[docName])
    startVal = float(self.Devices[docName][channelName]['startVal'])
    startPos = self.Devices[docName][channelName]['startPos']
    dataType = self.Devices[docName][channelName]['dataType']
    length = int(self.binFormat[dataType])
    while block:
      size = len(block)
      block = block.replace("\a","X")
#      startPos = self.Devices[docName][channelName]['startPos']
#      dataType = self.Devices[docName][channelName]['dataType']
#      length = int(self.binFormat[dataType])
      binVal = block[startPos:startPos + length]
      if length == 8:
        decVal, = struct.unpack('d', binVal)
      elif length == 4:
        decVal, = struct.unpack('f', binVal)
      elif length == 2:
        decVal, = struct.unpack('h', binVal)
      elif length == 1:
        decVal, = struct.unpack('b', binVal)
      else:
        decVal = 0
      decVal -= startVal
      values.append(decVal)          
      block = FH.read(self.lengthCount[docName])
    FH.close()
    values = numpy.array(values,dtype=float)
    return values
