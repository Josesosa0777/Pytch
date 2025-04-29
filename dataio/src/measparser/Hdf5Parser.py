import os
import sys
import time
import json
import re
import logging
import subprocess

import h5py
import numpy as np

import iParser

logger = logging.getLogger('Hdf5Parser')

DEVICE_NAME_LIST = ['MFC5xx Device','MFC5xx_Device','ARS4xx','SRR520','ARS620']

class Names(dict):
    def add(self, Path):
        try:
            DeviceName, DeviceExt, SignalName = Path.split("/")
        except ValueError:
            pass
        else:
            Device = DeviceName + iParser.DEVICE_NAME_SEPARATOR + DeviceExt
            Device = self.setdefault(Device, set())
            Device.add(SignalName)
        return


class DeviceName(list):
    def __init__(self, Name):
        list.__init__(self)
        self.Name = Name
        return

    def append(self, Name):
        try:
            Device, Ext, Signal = Name.split("/")
        except ValueError:
            pass
        else:
            if self.Name == Signal:
                if Device == "NULL":
                    Device = ""
                Device = Device + iParser.DEVICE_NAME_SEPARATOR + Ext
                list.append(self, Device)
        return


def splitDeviceName(DeviceName):
    if not DeviceName:
        Device = "NULL"
        Ext = "NULL"
    elif DeviceName[0] == iParser.DEVICE_NAME_SEPARATOR:
        Device = "NULL"
        Ext = DeviceName[1:]
    else:
        try:
            Device, Ext = DeviceName.split(iParser.DEVICE_NAME_SEPARATOR, 1)
        except ValueError:
            Device, Ext = DeviceName, ""
    return Device, Ext


def convName(DeviceName, SignalName):
    DeviceName, DeviceExt = splitDeviceName(DeviceName)
    Name = ["/devices", DeviceName, DeviceExt, SignalName]
    Name = "/".join(Name)
    return Name


def convDeviceName(DeviceName, Ext):
    return DeviceName + "/" + Ext


def checkParser(Name):
    Check = False
    if os.path.isfile(Name) and h5py.is_hdf5(Name):
        exe_path = os.path.dirname(__file__) + r'\build\exe.win-amd64-3.8\hdf5check.exe'
        command = exe_path + ' "{h5_path}"'.format(h5_path=Name)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = process.communicate()
        if result[0] != 'False\r\n':
            Hdf5 = h5py.File(Name)
            Check = True
            Hdf5.close()
    return Check


class cHdf5Parser(iParser.iParser):
    checkParser = staticmethod(checkParser)

    def __init__(self, Name, ParserVersion="", Measurement=None):
        iParser.iParser.__init__(self)
        self.test_02_signal_list = None
        self.Names = []  # Names()
        try:
            self.Hdf5 = h5py.File(Name, "r")
        except IOError:
            sys.stderr.write("Cannot open '%s' to append; it will be replaced\n" % Name)
            DirName = os.path.dirname(Name)
            if not os.path.exists(DirName):
                os.makedirs(DirName)
            self.Hdf5 = h5py.File(Name, "w")
        if ParserVersion:
            if "parser_version" not in self.Hdf5.attrs:
                self.Hdf5.attrs["parser_version"] = ParserVersion
            if self.Hdf5.attrs["parser_version"] != ParserVersion:
                self.Hdf5.close()
                self.Hdf5 = h5py.File(Name, "w")
                self.Hdf5.attrs["parser_version"] = ParserVersion

        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            self.test_02_signal_list = np.array(self.Hdf5['H5DcnvtData/Info/Signal_List'])

        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            self.prepare_device_name()

        if Measurement is not None:
            FileName, Ext = os.path.splitext(Measurement)
            self.Measurement = FileName
        else:
            self.Measurement = Measurement


        return

    def close(self):
        self.Hdf5.close()
        return

    def save(self):
        self.close()
        return

    def setStart(self, start):
        self.Hdf5.attrs["timens"] = start
        return

    def contains(self, DeviceName, SignalName):
        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            if self.Hdf5[u'H5DcnvtData']['Signal_List'][DeviceName].value.size > 0:
                return True
        else:
            if bool(re.findall('_CAN[0-9]+', DeviceName)):
                DeviceName = self.get_original_device_name(DeviceName)
                DeviceRoot = "/devices"
                DevicePath = DeviceRoot + "/" + DeviceName
                SignalPath = DevicePath + "/" + SignalName
                return (
                        DeviceName in self.Hdf5[DeviceRoot]
                        and SignalName in self.Hdf5[DevicePath]
                        and "time" in self.Hdf5[SignalPath]
                        and "value" in self.Hdf5[SignalPath]
                )
            else:
                Ext = list(self.Hdf5["devices"][DeviceName].keys())[0]
                DeviceName = convDeviceName(DeviceName, Ext)
                DeviceRoot = "/devices"
                DevicePath = DeviceRoot + "/" + DeviceName
                SignalPath = DevicePath + "/" + SignalName
                return (
                        DeviceName in self.Hdf5[DeviceRoot]
                        and SignalName in self.Hdf5[DevicePath]
                        and "time" in self.Hdf5[SignalPath]
                        and "value" in self.Hdf5[SignalPath]
                )

    def get_original_device_name(self, DeviceName):
        original_device_name = DeviceName.replace(re.findall('_CAN[0-9]+', DeviceName)[0], '')
        Ext = self.Hdf5["devices"][original_device_name].keys()

        for extended_info in Ext:
            can_channel_number = extended_info.split('-')[1]
            final_device_name = ''.join([original_device_name, '_CAN', can_channel_number])
            if DeviceName == final_device_name:
                DeviceName = convDeviceName(original_device_name, extended_info)
                break
        return DeviceName

    def iterTimeKeys(self):
        return iter(self.Hdf5["/times"])

    def prepare_device_name(self):
        for idx, values in enumerate(self.test_02_signal_list['NameTimeAxis']):
            original_device_name = values
            device_name = values.decode().replace('t_','',1)
            if self.test_02_signal_list[idx][u'NameOrig'] != b't':
                if bool(filter(device_name.startswith, DEVICE_NAME_LIST)):
                    index = [m.start() for m in
                             re.finditer(r'\.', self.test_02_signal_list[idx][u'NameOrig'].decode())]
                    device_name = self.test_02_signal_list[idx][u'NameOrig'].decode()[:index[2]]
                    device_name = re.split('\[\d+]', device_name)[0]
                if device_name not in self.Names:
                    self.Devices[device_name] = original_device_name
                    self.Names.append(device_name)

    def loadNames(self):
        if not self.Names:
            if 'H5DcnvtData' in self.Hdf5.items()[0]:
                self.prepare_device_name()
            else:
                for index, items in enumerate(self.Hdf5['devices'].items()):
                    device_name = items[0]
                    if len(self.Hdf5["devices"].items()[index][1].keys()) > 1:
                        for idx, can_channel in enumerate(self.Hdf5["devices"].items()[index][1].keys()):
                            can_channel_number = can_channel.split('-')[1]
                            final_device_name = ''.join([device_name, '_CAN', can_channel_number])
                            self.Names.append(final_device_name)
                    else:
                        self.Names.append(device_name)
                self.Devices = dict.fromkeys(self.Names, {})
        return

    def iterDeviceNames(self):
        self.loadNames()
        return iter(self.Names)

    def iterSignalNames(self, DeviceName):
        sig_names = []
        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            for index in np.where(self.test_02_signal_list['NameTimeAxis'] == self.Devices[DeviceName])[0]:
                if self.test_02_signal_list['NameOrig'][index] != 't':
                    if 'UserDef01' in self.test_02_signal_list.dtype.names:
                        if bool(self.test_02_signal_list['UserDef01'][index]):
                            shape = int(json.loads(self.test_02_signal_list['UserDef01'][index])[u'Sig_NumCols'])
                            if shape > 1:
                                sig_names.extend([''.join([self.test_02_signal_list['NameOrig'][index],"[:,",str(x), ']']) for x in
                                 range(shape)])
                            else:
                                if bool(filter(str(self.test_02_signal_list['NameOrig'][index]).startswith, DEVICE_NAME_LIST)):
                                    sig_names.append(self.test_02_signal_list['NameOrig'][index])
                                else:
                                    sig_names.append(self.test_02_signal_list['NameOrig'][index])
                    else:
                        # if self.Hdf5[u'H5DcnvtData']['Signal_List'][self.test_02_signal_list[index]['Name']].ndim > 1:
                        shape = self.Hdf5[u'H5DcnvtData']['Signal_List'][self.test_02_signal_list[index]['NameOrig']].ndim
                        if shape > 1:
                            sig_names.extend(
                                [''.join([self.test_02_signal_list['NameOrig'][index], "[:,", str(x), ']']) for x in
                                 range(shape)])
                        else:
                            if bool(filter(str(self.test_02_signal_list['NameOrig'][index]).startswith,
                                           DEVICE_NAME_LIST)):
                                sig_names.append(self.test_02_signal_list['NameOrig'][index])
                            else:
                                sig_names.append(self.test_02_signal_list['NameOrig'][index])
        else:
            try:
                if bool(re.findall('_CAN[0-9]+', DeviceName)):
                    original_device_name = DeviceName.replace(re.findall('_CAN[0-9]+', DeviceName)[0], '')
                    device_name_index = self.Hdf5['devices'].keys().index(original_device_name)
                    if len(self.Hdf5["devices"].items()[device_name_index][1].keys()) > 1:
                        for idx, can_channel in enumerate(self.Hdf5["devices"].items()[device_name_index][1].keys()):
                            can_channel_number = can_channel.split('-')[1]
                            final_device_name = ''.join([original_device_name, '_CAN', can_channel_number])
                            if DeviceName == final_device_name:
                                sig_names = self.Hdf5['devices'][original_device_name][can_channel].keys()
                                self.Devices[DeviceName] = dict.fromkeys(sig_names, {})
                else:
                    extended_info = str(self.Hdf5['devices'][DeviceName].keys()[0])
                    sig_names = self.Hdf5["devices"][DeviceName][extended_info].keys()
                    self.Devices[DeviceName] = dict.fromkeys(sig_names, {})
            except:
                pass
        return iter(sig_names)

    def getSignalShape(self, DeviceName, SignalName):
        if not self.contains(DeviceName, SignalName):
            raise KeyError(DeviceName + "/" + SignalName)
        if bool(re.findall('_CAN[0-9]+', DeviceName)):
            DeviceName = self.get_original_device_name(DeviceName)
            Node = self.Hdf5["/devices/" + DeviceName + "/" + SignalName + "/value"]
        else:
            Ext = list(self.Hdf5["devices"][DeviceName].keys())[0]
            DeviceName = convDeviceName(DeviceName, Ext)
            Node = self.Hdf5["/devices/" + DeviceName + "/" + SignalName + "/value"]
        return list(Node.shape)

    def getExtendedSignalInformation(self, DeviceName, signal_name):
        extended_information = {}
        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            for index in np.where(self.test_02_signal_list['NameTimeAxis'] == self.Devices[DeviceName])[0]:
                if self.test_02_signal_list['NameOrig'][index] != 't' and self.test_02_signal_list['NameOrig'][index] == signal_name:
                    signal_information_fields = list(self.test_02_signal_list.dtype.names)
                    for idx, information_field in enumerate(signal_information_fields):
                        try:
                            data = str(self.test_02_signal_list[information_field][index])
                            extended_information[information_field] = data
                        except:
                            continue
        else:
            for id, device_group in enumerate(self.Hdf5['devices'].keys()):
                for id2, device_id in enumerate(self.Hdf5['devices'][device_group].keys()):
                    for id3, signal_names in enumerate(self.Hdf5['devices'][device_group][device_id].keys()):
                        if signal_name == signal_names:
                            for id4, signal_extended_info in enumerate(
                                    self.Hdf5['devices'][device_group][device_id][signal_names].attrs.keys()):
                                extended_information[signal_extended_info] = \
                                self.Hdf5['devices'][device_group][device_id][signal_names].attrs[signal_extended_info]
                                if 'Message_ID' in extended_information:
                                    extended_information['Message_ID'] = str(extended_information['Message_ID'])
                            for id5, signal_message_info in enumerate(
                                    self.Hdf5['Info'][u'Message_List'][device_group].attrs.keys()):
                                extended_information[signal_message_info] = \
                                self.Hdf5['Info'][u'Message_List'][device_group].attrs[signal_message_info]
            del extended_information['Message_ID_dec']
        return extended_information

    def getSignalLength(self, DeviceName, SignalName):
        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            try:
                length = self.Hdf5[u'H5DcnvtData']['Signal_List'][self.test_02_signal_list['Name'][np.where(self.test_02_signal_list['Name'] == SignalName)[0][0]]].size
            except:
                try:
                    if np.where(self.test_02_signal_list['NameOrig'] == SignalName)[0].size > 1:
                        for index, value in enumerate(np.where(self.test_02_signal_list['NameOrig'] == SignalName)[0]):
                            if ''.join(['t_',DeviceName]) == self.test_02_signal_list['NameTimeAxis'][value]:
                                length = self.Hdf5[u'H5DcnvtData']['Signal_List'][self.test_02_signal_list['Name'][
                                    np.where(self.test_02_signal_list['NameOrig'] == SignalName)[0][index]]].size
                                break
                    else:
                        length = self.Hdf5[u'H5DcnvtData']['Signal_List'][self.test_02_signal_list['Name'][
                            np.where(self.test_02_signal_list['NameOrig'] == SignalName)[0][0]]].size
                except:
                    length = 0
            return length
        else:
            if not self.contains(DeviceName, SignalName):
                raise KeyError(DeviceName + "/" + SignalName)
            if bool(re.findall('_CAN[0-9]+', DeviceName)):
                DeviceName = self.get_original_device_name(DeviceName)
                Node = self.Hdf5["/devices/" + DeviceName + "/" + SignalName + "/value"]
            else:
                Ext = list(self.Hdf5["devices"][DeviceName].keys())[0]
                DeviceName = convDeviceName(DeviceName, Ext)
                Node = self.Hdf5["/devices/" + DeviceName + "/" + SignalName + "/value"]
            return Node.shape[0]

    def isSignalEmpty(self, DeviceName, SignalName):
        return not self.contains(DeviceName, SignalName)

    def getPhysicalUnit(self, DeviceName, SignalName):
        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            try:
                unit = self.test_02_signal_list['Unit'][np.where(self.test_02_signal_list['Name'] == SignalName)[0][0]]
                if len(unit) > 10:
                    unit = ""
            except:
                if np.where(self.test_02_signal_list['NameOrig'] == SignalName)[0].size > 1:
                    for index, value in enumerate(np.where(self.test_02_signal_list['NameOrig'] == SignalName)[0]):
                        if ''.join(['t_', DeviceName]) == self.test_02_signal_list['NameTimeAxis'][value]:
                            unit = self.test_02_signal_list['Unit'][np.where(self.test_02_signal_list['NameOrig'] == SignalName)[0][index]]
                            break
                else:
                    unit = self.test_02_signal_list['Unit'][np.where(self.test_02_signal_list['NameOrig'] == SignalName)[0][0]]

                if len(unit) > 10:
                    unit = ""
        else:
            if not self.contains(DeviceName, SignalName):
                raise KeyError(DeviceName + "/" + SignalName)
            if bool(re.findall('_CAN[0-9]+', DeviceName)):
                DeviceName = self.get_original_device_name(DeviceName)
                try:
                    unit = self.Hdf5["/devices/" + DeviceName + "/" + SignalName + "/value"].attrs["unit"]
                except:
                    unit = ""  # self.Hdf5["/devices/" + Name + "/" + SignalName].attrs["Unit"]
            else:
                Ext = list(self.Hdf5["devices"][DeviceName].keys())[0]
                Name = convDeviceName(DeviceName, Ext)
                try:
                    unit = self.Hdf5["/devices/" + Name + "/" + SignalName + "/value"].attrs["unit"]
                except:
                    unit = ""  # self.Hdf5["/devices/" + Name + "/" + SignalName].attrs["Unit"]
        return unit

    def getDeviceNames(self, SignalName):
        Names = DeviceName(SignalName)
        Group = self.Hdf5["/devices"]
        Group.visit(Names.append)
        return Names

    def getExtendedDeviceNames(self, DeviceName, FavorMatch=False):
        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            if DeviceName not in self.Devices.keys():
                return []
            else:
                Devices = [DeviceName]
        else:
            Device, Search = splitDeviceName(DeviceName)
            if Device not in self.Hdf5["/devices"]:
                return []
            Devices = [
                Device + iParser.DEVICE_NAME_SEPARATOR + Ext
                for Ext in self.Hdf5["/devices/" + Device]
                if Ext.startswith(Search)
            ]
            if FavorMatch and Device + iParser.DEVICE_NAME_SEPARATOR + Search in Devices:
                Devices = [Device + iParser.DEVICE_NAME_SEPARATOR + Search]  # matching only
        return Devices

    def getNames(self, SignalName, Pattern, FavorMatch=False):
        DeviceName, Search = splitDeviceName(Pattern)
        # Names = []
        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            if DeviceName in self.Devices.keys():
                DeviceNames = [DeviceName]
            else:
                return []
        else:
            Devices = self.Hdf5["devices"]
            if bool(re.findall('_CAN[0-9]+', DeviceName)):
                original_device_name = DeviceName.replace(re.findall('_CAN[0-9]+', DeviceName)[0], '')
                if original_device_name not in Devices:
                    return []
                Sep = iParser.DEVICE_NAME_SEPARATOR
                Device = Devices[original_device_name]
                DeviceNames = [
                    DeviceName
                    for Ext in Device
                    if Ext.startswith(Search) and SignalName in Device[Ext] and DeviceName == ''.join(
                        [original_device_name, '_CAN', Ext.split('-')[1]])
                ]
                if FavorMatch and DeviceName + Search in DeviceNames:
                    DeviceNames = [DeviceName + Search]  # return only the matching device

            else:
                if DeviceName not in Devices:
                    return []
                Sep = iParser.DEVICE_NAME_SEPARATOR
                Device = Devices[DeviceName]

                DeviceNames = [
                    DeviceName
                    for Ext in Device
                    if Ext.startswith(Search) and SignalName in Device[Ext]
                ]
                if FavorMatch and DeviceName + Sep + Search in DeviceNames:
                    DeviceNames = [DeviceName + Sep + Search]  # return only the matching device
        return DeviceNames

    def getTimeKey(self, DeviceName, SignalName):
        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            TimeKey = self.Devices[DeviceName]
        else:
            if not self.contains(DeviceName, SignalName):
                raise KeyError(DeviceName + "/" + SignalName)
            if bool(re.findall('_CAN[0-9]+', DeviceName)):
                DeviceName = self.get_original_device_name(DeviceName)
                TimeLink = self.Hdf5.get(
                    "/devices/" + DeviceName + "/" + SignalName + "/time", getlink=True
                )
                TimeKey = TimeLink.path.split("/")[-1]
                if TimeKey == "value":
                    TimeKey = TimeLink.path.split("/")[-2]
            else:
                Ext = list(self.Hdf5["devices"][DeviceName].keys())[0]
                DeviceName = convDeviceName(DeviceName, Ext)
                TimeLink = self.Hdf5.get(
                    "/devices/" + DeviceName + "/" + SignalName + "/time", getlink=True
                )
                TimeKey = TimeLink.path.split("/")[-1]
                if TimeKey == "value":
                    TimeKey = TimeLink.path.split("/")[-2]
        return TimeKey

    def getSignal(self, DeviceName, SignalName):
        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            try:
                Value = self.Hdf5[u'H5DcnvtData']['Signal_List'][self.test_02_signal_list['Name'][np.where(self.test_02_signal_list['Name'] == SignalName)[0][0]]].value
                TimeKey = self.Devices[DeviceName]
            except:
                if np.where(self.test_02_signal_list['NameOrig'] == SignalName)[0].size > 1:
                    for index, value in enumerate(np.where(self.test_02_signal_list['NameOrig'] == SignalName)[0]):
                        if ''.join(['t_', DeviceName]) == self.test_02_signal_list['NameTimeAxis'][value]:
                            Value = self.Hdf5[u'H5DcnvtData']['Signal_List'][
                                self.test_02_signal_list['Name'][
                                    np.where(self.test_02_signal_list['NameOrig'] == SignalName)[0][index]]].value
                            TimeKey = self.Devices[DeviceName]
                            break
                else:
                    Value = self.Hdf5[u'H5DcnvtData']['Signal_List'][
                        self.test_02_signal_list['Name'][np.where(self.test_02_signal_list['NameOrig'] == SignalName)[0][0]]].value
                    TimeKey = self.Devices[DeviceName]

        else:
            if not self.contains(DeviceName, SignalName):
                raise KeyError(DeviceName + "/" + SignalName)

            TimeKey = self.getTimeKey(DeviceName, SignalName)
            if bool(re.findall('_CAN[0-9]+', DeviceName)):
                DeviceName = self.get_original_device_name(DeviceName)
                SignalPath = "/devices/" + DeviceName + "/" + SignalName + "/value"
                Value = self.Hdf5[SignalPath][()]
            else:
                Ext = list(self.Hdf5["devices"][DeviceName].keys())[0]
                DeviceName = convDeviceName(DeviceName, Ext)
                SignalPath = "/devices/" + DeviceName + "/" + SignalName + "/value"
                Value = self.Hdf5[SignalPath][()]

        return Value, TimeKey

    def getTime(self, TimeKey):
        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            Time = self.Hdf5['H5DcnvtData']['Signal_List'][TimeKey].value
        else:
            TimePath = "/times/" + TimeKey
            try:
                Time = self.Hdf5[TimePath][()]
            except:
                Time = self.Hdf5[TimePath + "/value"][()]
        return Time

    def addTime(self, TimeKey, Time, Compression="zlib"):
        self.Hdf5["/times"].create_dataset(TimeKey, data=Time)
        return

    def addSignal(self, DeviceName, SignalName, TimeKey, Value, Compression="zlib"):
        Ext = list(self.Hdf5["devices"][DeviceName].keys())[0]
        DeviceName = convDeviceName(DeviceName, Ext)
        Device = self.Hdf5.require_group("/devices/" + DeviceName)
        Signal = Device.create_group(SignalName)
        Signal.create_dataset("value", data=Value)
        Signal["time"] = h5py.SoftLink("/times/" + TimeKey)
        return

    def rmTime(self, TimeKey):
        """
        :Parameters:
                TimeKey : str
        """
        del self.Hdf5["times"][TimeKey]
        return

    def rmSignal(self, DeviceName, SignalName):
        """
        :Parameters:
                DeviceName : str
                SignalName : str
        """
        Name = convName(DeviceName, SignalName)
        del self.Hdf5[Name]

        if self.Names:
            del self.Names[DeviceName]  # [SignalName]
        return


VERSION = ["backup 0.1.3", "customer-0.1.1"]

BYTE_ORDERS = {"<": "little", ">": "big", "|": None, "=": None}

COMPRESSIONS = {"zlib": "gzip"}


def init(Name):
    """
    :Parameters:
            Name : str
    :ReturnType:
            h5py._hl.files.File
            h5py._hl.group.Group
            h5py._hl.group.Group
            list
    :Return:
            hdf5 file object
            hdf5 group for devices
            hdf5 group for times
            [[DeviceName<str>, SignalName<str>]]
    """
    Parser = cHdf5Parser(Name)
    return Parser.Hdf5, Parser.Hdf5["devices"], Parser.Hdf5["times"]


def setHeader(Hdf5, Start, Comment):
    """
    :Parameters:
            Hdf5 : h5py._hl.files.File
            Start : int
            Comment : str
    """
    Hdf5.attrs["comment"] = Comment
    Hdf5.attrs["timens"] = Start
    Hdf5.attrs["version"] = VERSION[0]
    return


def getCompression(Compression, CompLevel=1):
    """
    :Parameters:
            Compression : str
                    zlib
            Complevel : int
    :ReturnType:
            str | int
            tables.filters.Filters
    :Return:
            compression flag for h5py, it can be integer (CompLevel) in case of zlib
            compression flag for tables
    """
    H5pyComp = COMPRESSIONS[Compression]
    if H5pyComp == "gzip":
        H5pyComp = CompLevel
    return H5pyComp


def addCArray(Hdf5, Device, Name, Value, Compression):
    """
    :Parameters:
            Hdf5 : tables.file.File
            Device : tables.group.Group
            Name : str
            Value : numpy.ndarray
            Compression : tables.filters.Filters
    :ReturnType: tables.carray.CArray
    """
    Atom = tables.Atom.from_dtype(Value.dtype)
    ByteOrder = BYTE_ORDERS[Value.dtype.byteorder]
    Array = Hdf5.createCArray(
        Device, Name, Atom, Value.shape, byteorder=ByteOrder, filters=Compression
    )
    Array[:] = Value
    return Array


def addSignal(
        Devices,
        Times,
        DeviceName,
        DeviceExt,
        Name,
        TimeKey,
        Value,
        Compression,
        PhysicalUnit,
        Comment="",
):
    """
    :Parameters:
            Devices : h5py._hl.group.Group
            Times : h5py._hl.group.Group
            Names : list
                    [[DeviceName<str>, SignalName<str>]]
            DeviceName : str
            DeviceExt : str
            Name : str
            TimeKey : str
            Value : numpy.ndarray
            Compression : str | int
                    Name of the compression lib, it can be integer to provoke gzip and show
                    the compression level
            PhysicalUnit : str
            Comment : str
    """
    if Name == TimeKey:
        Times.create_dataset(TimeKey, data=Value, compression=Compression)
    else:
        DeviceGroup = Devices.require_group(DeviceName)
        Device = DeviceGroup.require_group(DeviceExt)

        ValueGroup = Device.create_group(Name)
        Data = ValueGroup.create_dataset("value", data=Value, compression=Compression)
        Data.attrs["unit"] = PhysicalUnit
        Data.attrs["comment"] = Comment

        TimeLink = Times.name + "/" + TimeKey
        ValueGroup["time"] = h5py.SoftLink(TimeLink)

        DeviceId = DeviceName + iParser.DEVICE_NAME_SEPARATOR + DeviceExt
    return
