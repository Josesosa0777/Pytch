import logging
import os
import re
import time
import numpy

import iParser
import scipy.io
from PostmarkerJSONParser import PostmarkerJSONParser
from pyutils.cache_manager import get_meas_cache, is_meas_cache_available, \
    store_meas_cache

logger = logging.getLogger('MatParser')

DEVICE_NAME_LIST = ['MFC5xx Device','MFC5xx_Device','ARS4xx','SRR520','ARS620']


class cMatParser(iParser.iParser):
    @staticmethod
    def checkParser(FileName):
        FileName = FileName.lower()
        return FileName.endswith('.mat') and os.path.isfile(FileName)

    TIME_PREFIX = 't_'

    def __init__(self, FileName, time_axis_as_devicename=True):
        """
        :param FileName: Matlab binary file full path
        :param time_axis_as_devicename:
                True: Use legacy time axis suffix was used as devicename,
                False : Use actual device name from DBC/Info structure
        """
        iParser.iParser.__init__(self)
        if is_meas_cache_available(FileName):
            self.Devices, self.Times = get_meas_cache(FileName)
            return

        start = time.time()
        try:
            # TODO fix workaround verify_compressed_data_integrity=True: https://stackoverflow.com/questions/42607271/unable-to-read-mat-file-with-scipy
            # logger.info("Loading mat file : " + FileName)
            self.mat_object = scipy.io.loadmat(FileName, verify_compressed_data_integrity=False)
        except Exception as e:
            self.Devices = {}
            self.Times = {}
            logger.critical(str(e))
            return

        done = time.time()
        elapsed = done - start
        logger.info("[Scipy] Mat file is loaded in {:.2f} seconds".format(elapsed))

        self.view_signal_list = {}
        mat_file_info_start = time.time()
        self.is_mat_file_info_present = False
        self.signal_info_mapping = {}
        is_message_list_present = bool
        try:
            is_message_list_present = bool('Message_List' in self.mat_object['Info'].dtype.names)
        except:
            self.create_view_signal_list(FileName, time_axis_as_devicename)

        # if "Info" in self.mat_object.keys():
        if is_message_list_present and (
                'NameOrig' not in self.mat_object['Info']['Signal_List'][0][0][0][0][0].dtype.names):
            if "Info" in self.mat_object.keys():
                short_signal_names = self.mat_object["Info"]["Signal_List"][0][0][0][0].dtype.names
                self.is_mat_file_info_present = True
                for index, signal_data in enumerate(self.mat_object["Info"]["Signal_List"][0][0][0][0]):
                    short_signal_name = short_signal_names[index]
                    # signal_data[0][0][1]   indicates for NameFromDBC
                    try:
                        if len(signal_data[0][0][1]) != 0:
                            original_signal_name = signal_data[0][0][1][0]
                        else:
                            original_signal_name = signal_data[0][0][2][0]
                    except:
                        original_signal_name = short_signal_name
                    device_name = ""
                    if signal_data[0][0][3].size != 0:
                        device_name = signal_data[0][0][3][0]
                    self.signal_info_mapping[short_signal_name] = (
                        original_signal_name,
                        device_name,
                    )
            self.create_view_signal_list(FileName, time_axis_as_devicename)
            done = time.time()
            elapsed = done - start
            total_devices = len(self.Devices.keys())
            total_signals = 0
            for device in self.Devices.keys():
                total_signals = total_signals + len(self.Devices[device].keys())
            logger.info(
                "Mat file loaded in {:.2f} seconds, Total Devices: {}, Total Signals: {}".format(elapsed,
                                                                                                 total_devices,
                                                                                                 total_signals))
        else:
            start = time.time()
            if 'Info' in self.mat_object.keys():
                short_signal_names = self.mat_object["Info"]["Signal_List"][0][0][0][0].dtype.names
                self.Devices = {}
                self.signal_info_mapping = {}
                self.is_mat_file_info_present = True
                for index, signal_data in enumerate(self.mat_object["Info"]["Signal_List"][0][0][0][0]):
                    if not (signal_data[0][0]['NameOrig'][0] == 't'):
                        try:
                            if bool(filter(signal_data[0][0]['Device_Name'][0].startswith, DEVICE_NAME_LIST)):
                                idx = [m.start() for m in
                                       re.finditer(r'\.', signal_data[0][0]['NameOrig'][0].decode())]
                                device_name = signal_data[0][0]['NameOrig'][0].decode()[:idx[2]]
                                device_name = re.split('\[\d+]', device_name)[0]
                                signal_name = signal_data[0][0]['NameOrig'][0].decode()
                                time_axis = signal_data[0][0]['NameTimeAxis'][0].decode()
                                self.Times[time_axis] = self.get_value(time_axis)
                            else:
                                device_name = signal_data[0][0]['NameTimeAxis'][0].decode().replace('t_', '')
                                signal_name = signal_data[0][0]['NameOrig'][0].decode()
                                time_axis = signal_data[0][0]['NameTimeAxis'][0].decode()
                                self.Times[time_axis] = self.get_value(time_axis)
                            try:
                                unit = signal_data[0][0]['Unit'][0].decode()
                            except:
                                unit = ''
                            if device_name not in self.Devices.keys():
                                self.view_signal_list[device_name] = {}
                                self.Devices[device_name] = {}

                            # signal_name = signal_name.replace(" ", "_")
                            # signal_name = signal_name.replace(".", "_")
                            signal_name = signal_name.replace('[', '')
                            signal_name = signal_name.replace(']', '')
                            self.view_signal_list[device_name][signal_name] = {}
                            self.view_signal_list[device_name][signal_name]['TimeAxis'] = time_axis
                            if bool(unit):
                                self.view_signal_list[device_name][signal_name]['Unit'] = unit

                            data = self.get_value(short_signal_names[index])
                            self.Devices[device_name][
                                signal_name] = data, time_axis, unit
                            array_dimension = tuple(list(data.shape[1:]) + [0])
                            self.create_individual_signals_from_multidimensional_array(
                                self.view_signal_list[device_name][signal_name],
                                array_dimension,
                                0,
                                signal_name + "[:,",
                            )
                        except:
                            device_name = signal_data[0][0]['NameTimeAxis'][0].decode().replace('t_', '')
                            signal_name = signal_data[0][0]['NameOrig'][0].decode()
                            time_axis = signal_data[0][0]['NameTimeAxis'][0].decode()
                            self.Times[time_axis] = self.get_value(time_axis)
                            try:
                                unit = signal_data[0][0]['Unit'][0].decode()
                            except:
                                unit = ''
                            if device_name not in self.Devices.keys():
                                self.view_signal_list[device_name] = {}
                                self.Devices[device_name] = {}

                            signal_name = signal_name.replace(" ", "_")
                            signal_name = signal_name.replace(".", "_")
                            signal_name = signal_name.replace('[', '')
                            signal_name = signal_name.replace(']', '')
                            self.view_signal_list[device_name][signal_name] = {}
                            self.view_signal_list[device_name][signal_name]['TimeAxis'] = time_axis
                            if bool(unit):
                                self.view_signal_list[device_name][signal_name]['Unit'] = unit

                            data = self.get_value(short_signal_names[index])
                            self.Devices[device_name][
                                signal_name] = data, time_axis, unit
                            array_dimension = tuple(list(data.shape[1:]) + [0])
                            self.create_individual_signals_from_multidimensional_array(
                                self.view_signal_list[device_name][signal_name],
                                array_dimension,
                                0,
                                signal_name + "[:,",
                            )

            done = time.time()
            elapsed = done - start
            total_devices = len(self.Devices.keys())
            total_signals = 0
            for device in self.Devices.keys():
                total_signals = total_signals + len(self.Devices[device].keys())
            logger.info(
                "Mat file loaded in {:.2f} seconds, Total Devices: {}, Total Signals: {}".format(elapsed,
                                                                                                 total_devices,
                                                                                                 total_signals))
            store_meas_cache(FileName, (self.Devices, self.Times))

    def get_value(self, name):
        values = self.mat_object[name]
        # 1-element array converted to 0-dim array from 1-dim array, due to calling squeeze() #1582
        if values.size == 1:
            values = values.ravel()  # remove single-dimensional  entries (if any)  # TODO: avoid possible copy of ravel()
        else:
            values = values.squeeze()
        return values

    def create_view_signal_list(self, file_name, time_axis_as_devicename):
        zzzzz_start = time.time()
        zzzzz_variable_names = self.namesToList(
            self.mat_object, "zzzzz_Vars_IdxString"
        )

        if "zzzzz_Units" in self.mat_object:
            zzzzz_units = self.namesToList(self.mat_object, "zzzzz_Units")
            zzzzz_units = [
                unit if unit not in ("n/a",) else "" for unit in zzzzz_units
            ]  # replace not informative unit with empty  string
        else:
            zzzzz_units = [
                "" for variable in zzzzz_variable_names
            ]  # backward compatibility with old dcnvt

        if "zzzzz_Vars_Parts" in self.mat_object:
            zzzzz_Vars_Parts = self.namesToList(self.mat_object,
                                                "zzzzz_Vars_Parts")
        else:
            zzzzz_Vars_Parts = zzzzz_variable_names

        zzzzz_variable_timeaxis_mapping = self.mat_object[
            "zzzzz_IdxVariable_IdxTimeaxis"
        ]

        done = time.time()
        elapsed = done - zzzzz_start
        # logger.info("zzzzz variables are loaded in {:.2f} seconds".format(elapsed))
        time_prefix_len = len(self.TIME_PREFIX)
        device_start = time.time()
        time_key_to_device_name = {}
        multiple_can_channels = []
        for variable_index, time_index, Dummy in zzzzz_variable_timeaxis_mapping:
            variable_index = int(variable_index)
            time_index = int(time_index)
            if time_index < 0:
                pass
            elif variable_index == time_index:
                time_key = zzzzz_variable_names[variable_index]

                result = re.search(r'CAN\d+', time_key)
                if result is None:
                    if not self.is_mat_file_info_present:
                        # print("[DEBUG] Name retrieved from zzzzz_Vars_Parts")
                        device_name = zzzzz_Vars_Parts[variable_index]
                    else:
                        # print("[DEBUG] Name retrieved from info variable
                        # Original name : " + time_key + ", Info name : " +
                        # signal_info_mapping[time_key][0])
                        device_name = self.signal_info_mapping[time_key][0]
                        device_name = device_name.split(".")[-1]
                else:
                    device_name = time_key
                    multiple_can_channels.append(time_key)

                if device_name.startswith("t_") or device_name.startswith("t-"):
                    device_name = device_name[time_prefix_len:]
                device_name = device_name.replace(" ", "_")
                device_name = device_name.replace(".", "_")

                time_key_to_device_name[time_key] = device_name
                self.Devices[device_name] = {}
                self.view_signal_list[device_name] = {}
                self.Times[time_key] = self.get_value(time_key)
            else:
                signal_name = zzzzz_variable_names[variable_index]
                time_key = zzzzz_variable_names[time_index]
                device_name = time_key_to_device_name[time_key]
                signal_unit = zzzzz_units[variable_index]

                data = self.get_value(signal_name)
                if not self.is_mat_file_info_present:
                    if signal_name.endswith(device_name) and len(device_name) > 0:
                        signal_name = signal_name[: -len(device_name)]
                        signal_name = signal_name.strip("_")
                else:
                    signal_name = self.signal_info_mapping[signal_name][0]
                    if time_axis_as_devicename is False:
                        device_name = self.signal_info_mapping[signal_name][1]
                        time_key_to_device_name[time_key] = device_name
                        if device_name in self.Devices.keys():
                            self.Devices[device_name] = {}
                        if device_name in self.view_signal_list.keys():
                            self.view_signal_list[device_name] = {}

                signal_name = signal_name.replace(" ", "_")
                signal_name = signal_name.replace(".", "_")
                signal_name = signal_name.replace('[', 'I')
                signal_name = signal_name.replace(']', 'I')
                # print("[DEBUG]\t" + device_name + "   " + signal_name)
                self.Devices[device_name][
                    signal_name] = data, time_key, signal_unit
                self.view_signal_list[device_name][signal_name] = {}
                array_dimension = tuple(list(data.shape[1:]) + [0])
                self.create_individual_signals_from_multidimensional_array(
                    self.view_signal_list[device_name][signal_name],
                    array_dimension,
                    0,
                    signal_name + "[:,",
                )
        for can_channel in multiple_can_channels:
            device_name_in_devices_dict = can_channel
            if can_channel.startswith("t_") or can_channel.startswith("t-"):
                device_name_in_devices_dict = can_channel[time_prefix_len:]
            device_name_in_devices_dict = device_name_in_devices_dict.replace(
                " ",
                "_")
            device_name_in_devices_dict = device_name_in_devices_dict.replace(
                ".",
                "_")

            new_device_name = self.signal_info_mapping[can_channel][0]
            if new_device_name.startswith("t_") or new_device_name.startswith(
                    "t-"):
                new_device_name = new_device_name[time_prefix_len:]
            new_device_name = new_device_name.replace(" ", "_")
            new_device_name = new_device_name.replace(".", "_")

            can_device = self.Devices[device_name_in_devices_dict]
            can_signals = self.view_signal_list[device_name_in_devices_dict]
            if new_device_name not in self.Devices.keys():
                self.Devices[new_device_name] = can_device
                self.view_signal_list[new_device_name] = can_signals
        done = time.time()
        elapsed = done - device_start
        # logger.info("Devices are loaded in {:.2f} seconds".format(elapsed))

        json_file_name = file_name.split(".mat")[0] + ".json"
        postmarker_raw_data = PostmarkerJSONParser.is_postmarker_json(json_file_name)
        common_time = None
        if postmarker_raw_data is not None:
            logger.info("Loading postmarker JSON data")
            time_keys = self.Times.keys()
            common_time = self.Times[time_keys[0]]
            self.Times["t_Postmarker_time"] = common_time
            postmarker_obj = PostmarkerJSONParser(postmarker_raw_data, common_time)

            traffic_sign_reports = postmarker_obj.get_traffic_info()
            meta_info_reports = postmarker_obj.get_meta_info()

            _, meta_signal_dict = postmarker_obj.get_meta_info_signals(meta_info_reports)
            _, traffic_signal_dict = postmarker_obj.get_traffic_sign_signals(traffic_sign_reports)
            traffic_signal_dict.update(meta_signal_dict)
            # Insert this dict into mat Devices, Times
            self.view_signal_list["Postmarker"] = {}
            for signal in traffic_signal_dict.keys():
                self.view_signal_list["Postmarker"][signal] = {}
            self.Devices["Postmarker"] = traffic_signal_dict

        store_meas_cache(file_name, (self.Devices, self.Times))

    def getExtendedSignalInformation(self, device_name, signal_name):
        # start = time.time()
        extended_information = {}
        if 'Message_List' in self.mat_object['Info'].dtype.names:
            for id, signal_data in enumerate(self.mat_object["Info"]["Signal_List"][0][0][0][0]):
                signal_information_fields = signal_data.dtype.names
                if len(signal_data[0][0][1]) != 0:
                    complexName = signal_data[0][0][1][0]
                else:
                    complexName = signal_data[0][0][2][0]
                if signal_name == complexName.replace('.', '_').replace(' ', '_').replace('[', 'I').replace(']', 'I'):
                    for index, information_field in enumerate(signal_information_fields):
                        try:
                            data = str(signal_data[0][0][index][0]).replace('[', "").replace(']', '')
                            extended_information[information_field] = data
                        except:
                            continue

                    message_node = signal_data[0][0][7][0]

                    if type(message_node) == numpy.unicode_:
                        message_node = signal_data[0][0][9][0]

                    for index, signal_info in enumerate(self.mat_object["Info"]["Message_List"][0][0][0][0]):
                        message_information_fields = signal_info.dtype.names
                        if message_node == signal_info[0][0][1][0]:
                            for id, information_field in enumerate(message_information_fields):
                                try:
                                    values = str(signal_info[0][0][id][0]).replace('[', "").replace(']', '')
                                    extended_information[information_field] = values
                                except:
                                    continue
            return extended_information
        else:
            for index, signal_data in enumerate(self.mat_object["Info"]["Signal_List"][0][0][0][0]):
                signal_information_fields = signal_data.dtype.names
                if not (signal_data[0][0]['NameOrig'][0] == 't'):
                    for index, information_field in enumerate(signal_information_fields):
                        sig_name = signal_data[0][0]['NameOrig'][0].decode()
                        sig_name = sig_name.replace(" ", "_")
                        sig_name = sig_name.replace(".", "_")
                        sig_name = sig_name.replace('[', '')
                        sig_name = sig_name.replace(']', '')
                        if signal_name == sig_name:
                            extended_information[information_field] = str(
                                signal_data[0][0][information_field][0]).replace('[', '').replace(']', '')

            return extended_information

    def create_individual_signals_from_multidimensional_array(self, signal_dictionary, array_dimension, index,
                                                              signal_name):
        array_count = array_dimension[index]
        if array_count == 0:
            return
        for i in range(array_count):
            array_name = signal_name + str(i) + ','
            final_signal_name = array_name[0:-1] + ']'
            signal_dictionary[final_signal_name] = {}
            self.create_individual_signals_from_multidimensional_array(signal_dictionary[final_signal_name],
                                                                       array_dimension, index + 1, array_name)
        return

    @staticmethod
    def namesToList(mat, name):
        names = mat[name]
        names = names[0]
        names = names.split(';')
        return names

    def getSignal(self, DeviceName, SignalName):
        Device = self.Devices[DeviceName]
        Signal, TimeKey, Unit = Device[SignalName]
        return Signal, TimeKey

    def getSignalShape(self, DeviceName, SignalName):
        Device = self.Devices[DeviceName]
        Signal, TimeKey, Unit = Device[SignalName]
        return list(Signal.shape)

    def getTime(self, TimeKey):
        return self.Times[TimeKey]

    def getTimeKey(self, DeviceName, SignalName):
        Device = self.Devices[DeviceName]
        Signal, TimeKey, Unit = Device[SignalName]
        return TimeKey

    def getSignalLength(self, DeviceName, SignalName):
        Device = self.Devices[DeviceName]
        Signal, TimeKey, Unit = Device[SignalName]
        return Signal.size

    def getPhysicalUnit(self, DeviceName, SignalName):
        Device = self.Devices[DeviceName]
        Signal, TimeKey, Unit = Device[SignalName]
        return Unit

    def getOriginalNamesFromInfoStruct(self, mat_obj):
        """
        class my_signal
        {
        "IDX_Value":("Long_signal_name", "DeviceName")
        }
        :return:
        """
        InfoStructInternalSignals = None
        try:
            # fetching short name of signals which is in IDX format
            InfoStructSignalShortName = mat_obj["Info"]["Signal_List"][0][0][0][0].dtype.names
            # fetching signal_list
            InfoStructSignalData = mat_obj["Info"]["Signal_List"][0][0][0][0]
        except Exception as e:
            raise KeyError(str(e))
        # mat_obj["Info"]["Signal_List"][0][0][0][0][2][0][0].dtype = list of
        # tuples          =>      Get index of NameFromDBC
        InfoStructSignalDataValues = []
        # fetching signals with full name as per DBC from signal_list
        for Signal in InfoStructSignalData:
            SignalName = Signal[0][0][1][0]
            if Signal[0][0][3].size == 0:
                DeviceName = ""
            else:
                DeviceName = Signal[0][0][3][0]
            InfoStructSignalDataValues.append((SignalName, DeviceName,))
        # creating signal dictory which mapps shornames and full names
        InfoStructInternalSignals = {InfoStructSignalShortName[i]: InfoStructSignalDataValues[i]
                                     for i in range(len(InfoStructSignalShortName))}
        return InfoStructInternalSignals
