import h5py
import json
import re
import numpy as np


class CreateViewSignalList:

    def __init__(self, measurement_file):
        self.Hdf5 = None
        self.measurement_name = measurement_file
        self.view_signal_list = {}
        self.deviceName = []

    def generate_signal_list(self):
        self.Hdf5 = h5py.File(self.measurement_name, "a")
        if 'H5DcnvtData' in self.Hdf5.items()[0]:
            test_02_signal_list = np.array(self.Hdf5['H5DcnvtData/Info/Signal_List'])
            for id, device_group in enumerate(self.Hdf5[u'H5DcnvtData']['Signal_List'].keys()):
                if not (device_group.startswith('t_') or device_group.startswith('zzzzz_')):
                    if device_group.startswith('MFC5xx'):
                        index = [m.start() for m in re.finditer(r'\.', test_02_signal_list[id][u'NameOrig'].decode())]
                        device_name = test_02_signal_list[id][u'NameOrig'].decode()[:index[2]]
                        device_name = re.split('\[\d+]', device_name)[0]
                        signal_name = test_02_signal_list[id][u'Name'].decode()
                        time_axis = test_02_signal_list[id][u'NameTimeAxis'].decode()
                        unit = test_02_signal_list[id][u'Unit'].decode()
                    elif device_group.startswith('ARS4xx'):
                        index = [m.start() for m in re.finditer(r'\.', test_02_signal_list[id][u'NameOrig'].decode())]
                        device_name = test_02_signal_list[id][u'NameOrig'].decode()[:index[2]]
                        signal_name = test_02_signal_list[id][u'Name'].decode()
                        time_axis = test_02_signal_list[id][u'NameTimeAxis'].decode()
                    elif device_group.startswith('SRR520'):
                        index = [m.start() for m in re.finditer(r'\.', test_02_signal_list[id][u'NameOrig'].decode())]
                        device_name = test_02_signal_list[id][u'NameOrig'].decode()[:index[2]]
                        signal_name = test_02_signal_list[id][u'Name'].decode()
                        time_axis = test_02_signal_list[id][u'NameTimeAxis'].decode()
                        unit = test_02_signal_list[id][u'Unit'].decode()
                    else:
                        device_name = test_02_signal_list[id][u'NameTimeAxis'].decode().replace('t_','')
                        if device_name.startswith('idx'):
                            device_name = test_02_signal_list[id]['Device_Name'].replace(' ','_') + '_' + test_02_signal_list[id][
                                'Message_ID_Symbolic']
                        signal_name = test_02_signal_list[id][u'NameOrig'].decode()
                        time_axis = test_02_signal_list[id][u'NameTimeAxis'].decode()
                        unit = test_02_signal_list[id][u'Unit'].decode()
                    if device_name not in self.deviceName:
                        self.view_signal_list[device_name] = {}
                        self.deviceName.append(device_name)
                    self.view_signal_list[device_name][signal_name] = {}
                    self.view_signal_list[device_name][signal_name]['TimeAxis'] = time_axis
                    if bool(unit):
                        self.view_signal_list[device_name][signal_name]['Unit'] = unit
                    data_shape = self.Hdf5[u'H5DcnvtData']['Signal_List'][device_group].shape
                    array_dimension = tuple(list(data_shape[1:]) + [0])
                    self.create_individual_signals_from_multidimensional_array(
                        self.view_signal_list[device_name][signal_name],
                        array_dimension, 0, signal_name + "[:,", )
                    pass
            json_string = json.dumps(self.view_signal_list)
            self.Hdf5.attrs["namedump"] = json_string
        else:
            for id, device_group in enumerate(self.Hdf5['devices'].keys()):
                for id2, device_id in enumerate(self.Hdf5['devices'][device_group].keys()):
                    if device_group not in self.view_signal_list.keys():
                        self.view_signal_list[device_group] = {}
                    for id3, signal_name in enumerate(self.Hdf5['devices'][device_group][device_id].keys()):
                        self.view_signal_list[device_group][signal_name] = {}
                        data_shape = self.Hdf5['devices'][device_group][device_id][signal_name]["value"].shape
                        array_dimension = tuple(list(data_shape[1:]) + [0])
                        self.create_individual_signals_from_multidimensional_array(
                            self.view_signal_list[device_group][signal_name],
                            array_dimension, 0, signal_name + "[:,", )
                        pass
            json_string = json.dumps(self.view_signal_list)
            self.Hdf5.attrs["namedump"] = json_string
        return

    def create_individual_signals_from_multidimensional_array(self, signal_dictionary, array_dimension, index,
                                                              signal_name):
        try:
            array_count = array_dimension[index]
        except:
            pass
        if array_count == 0:
            return
        for i in range(array_count):
            array_name = signal_name + str(i) + ','
            final_signal_name = array_name[0:-1] + ']'
            signal_dictionary[final_signal_name] = {}
            self.create_individual_signals_from_multidimensional_array(signal_dictionary[final_signal_name],
                                                                       array_dimension, index + 1, array_name)
        return

    # TODO self.Hdf5["/devices/" + Name + "/" + SignalName + "/value"].shape


if __name__ == '__main__':
    obj = CreateViewSignalList(r"C:\KBData\Python_Toolchain_2\Evaluation_data\SRR\latest_generated_file\2023-06-01\mi5id5506__2023-06-01_09-00-40.h5")
    obj.generate_signal_list()
