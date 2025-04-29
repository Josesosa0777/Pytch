#!/usr/bin/env python
"""
python -m parsemat [option...] measurementfile

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

example:
python -m parsemat -f hdf5 -c zlib -l 9 "sample.mat"
"""

import time

start = time.time()
import json
import getopt
import os
import re
import sys

import h5py
import scipy
from measparser.Hdf5Parser import getCompression, init, setHeader
from measparser.iParser import iParser

VERSION = 'backup 0.1.3'

import_time = time.time()

if '-h' in sys.argv:
		print __doc__
		exit(0)

Exts = {
		None  : '.foo',
		'hdf5': '.h5'
}

Opts, Files = getopt.getopt(sys.argv[1:], 'c:l:v:o:f:s:h')
OptDict = dict(Opts)

ShowSignals = [re.compile(v) for k, v in Opts if k == '-s']

ConvFormat = OptDict.get('-f')
Compression = OptDict.get('-c')
Verbose = OptDict.get('-v', 0)
CompLevel = OptDict.get('-l', 0)
CompLevel = int(CompLevel)

MatName = Files[0]
time_axis_as_devicename = True
mat_object = scipy.io.loadmat(MatName, verify_compressed_data_integrity=False)

if '-o' in OptDict:
		HdfName = OptDict['-o']
else:
		_Name, _Ext = os.path.splitext(MatName)
		HdfName = _Name + Exts.get(ConvFormat)
		NameDumpName = _Name + '.db'


def convert_bytes(num):
		"""
		this function will convert bytes to MB.... GB... etc
		"""
		for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
				if num < 1024.0:
						return "%3.1f %s" % (num, x)
				num /= 1024.0


def file_size(file_path):
		"""
		this function will return the file size
		"""
		if os.path.isfile(file_path):
				file_info = os.stat(file_path)
				return convert_bytes(file_info.st_size)

def create_individual_signals_from_multidimensional_array(signal_dictionary, array_dimension, index, signal_name):
		array_count = array_dimension[index]
		if array_count == 0:
				return
		for i in range(array_count):
				array_name = signal_name + str(i) + ','
				final_signal_name = array_name[0:-1] + ']'
				signal_dictionary[final_signal_name] = {}
				create_individual_signals_from_multidimensional_array(signal_dictionary[final_signal_name],
																															array_dimension, index + 1, array_name)
		return


def namesToList(mat, name):
		names = mat[name]
		names = names[0]
		names = names.split(';')
		return names

def get_value(name):
		values = mat_object[name]
		# 1-element array converted to 0-dim array from 1-dim array, due to calling squeeze() #1582
		if values.size == 1:
			values = values.ravel()  # remove single-dimensional  entries (if any)  # TODO: avoid possible copy of ravel()
		else:
			values = values.squeeze()
		return values


view_signal_list = {}
parsing_time = time.time()

is_mat_file_info_present = False
signal_info_mapping = {}
if "Info" in mat_object.keys():
		short_signal_names = mat_object["Info"]["Signal_List"][0][0][0][0].dtype.names
		is_mat_file_info_present = True
		for index, signal_data in enumerate(mat_object["Info"]["Signal_List"][0][0][0][0]):
			short_signal_name = short_signal_names[index]
			original_signal_name = signal_data[0][0][1][0]
			device_name = ""
			if signal_data[0][0][3].size != 0:
				device_name = signal_data[0][0][3][0]
			signal_info_mapping[short_signal_name] = (original_signal_name,	device_name,)

zzzzz_variable_names = namesToList(mat_object, "zzzzz_Vars_IdxString")

if "zzzzz_Units" in mat_object:
	zzzzz_units = namesToList(mat_object, "zzzzz_Units")
	zzzzz_units = [	unit if unit not in ("n/a",) else "" for unit in zzzzz_units]  # replace not informative unit with empty  string
else:
	zzzzz_units = ["" for variable in zzzzz_variable_names]  # backward compatibility with old dcnvt

if "zzzzz_Vars_Parts" in mat_object:
	zzzzz_Vars_Parts = namesToList(mat_object, "zzzzz_Vars_Parts")
else:
	zzzzz_Vars_Parts = zzzzz_variable_names

zzzzz_variable_timeaxis_mapping = mat_object["zzzzz_IdxVariable_IdxTimeaxis"]

if ConvFormat == 'hdf5':
		H5pyComp = getCompression(Compression, CompLevel)
		Hdf5, Hdf5Devices, Hdf5Times = init(HdfName)

Comment = "sample"

if ConvFormat == 'hdf5':
		setHeader(Hdf5, 63456363, Comment)

TIME_PREFIX = 't_'
time_prefix_len = len(TIME_PREFIX)
time_key_to_device_name = {}
multiple_can_channels=[]
MatDevices = {}
MatTimes = {}
for variable_index, time_index, Dummy in zzzzz_variable_timeaxis_mapping:
	variable_index = int(variable_index)
	time_index = int(time_index)
	if time_index < 0:
		pass
	elif variable_index == time_index:
		time_key = zzzzz_variable_names[variable_index]

		result = re.search(r'CAN\d+', time_key)
		if result is None:
			if not is_mat_file_info_present:
				# print("[DEBUG] Name retrieved from zzzzz_Vars_Parts")
				device_name = zzzzz_Vars_Parts[variable_index]
			else:
				# print("[DEBUG] Name retrieved from info variable Original name : " + time_key + ", Info name : " + signal_info_mapping[time_key][0])
				device_name = signal_info_mapping[time_key][0]
				device_name = device_name.split(".")[-1]
		else:
			device_name = time_key
			multiple_can_channels.append(time_key)

		if device_name.startswith("t_") or device_name.startswith("t-"):
			device_name = device_name[time_prefix_len:]
		device_name = device_name.replace(" ", "_")
		device_name = device_name.replace(".", "_")

		time_key_to_device_name[time_key] = device_name
		MatDevices[device_name] = {}
		view_signal_list[device_name] = {}
		time_value = get_value(time_key)
		MatTimes[time_key] = time_value
		Hdf5Times.create_dataset(time_key, data = time_value, compression = H5pyComp)
	else:
		signal_name = zzzzz_variable_names[variable_index]
		time_key = zzzzz_variable_names[time_index]
		device_name = time_key_to_device_name[time_key]
		signal_unit = zzzzz_units[variable_index]

		data = get_value(signal_name)
		if not is_mat_file_info_present:
			if signal_name.endswith(device_name) and len(device_name) > 0:
				signal_name = signal_name[: -len(device_name)]
				signal_name = signal_name.strip("_")
		else:
			signal_name = signal_info_mapping[signal_name][0]
			if time_axis_as_devicename is False:

				device_name = signal_info_mapping[signal_name][1]
				time_key_to_device_name[time_key] = device_name
				if device_name in MatDevices.keys():
					MatDevices[device_name] = {}
				if device_name in view_signal_list.keys():
					view_signal_list[device_name] = {}

		signal_name = signal_name.replace(" ", "_")
		signal_name = signal_name.replace(".", "_")
		signal_name = signal_name.replace('[', 'I')
		signal_name = signal_name.replace(']', 'I')
		if ConvFormat == 'hdf5':
			H5DeviceGroup = Hdf5Devices.require_group(device_name)
			H5Device = H5DeviceGroup.require_group('Controller')
			# print("[DEBUG]\t" + device_name + "   " + signal_name)
			H5ValueGroup = H5Device.create_group(signal_name)
			H5Data = H5ValueGroup.create_dataset('value', data = data, compression = H5pyComp)
			H5Data.attrs['unit'] = signal_unit
			H5Data.attrs['comment'] = Comment

			H5TimeLink = Hdf5Times.name + '/' + time_key
			H5ValueGroup['time'] = h5py.SoftLink(H5TimeLink)
		MatDevices[device_name][signal_name] = data, time_key, signal_unit
		view_signal_list[device_name][signal_name] = {}
		array_dimension = tuple(list(data.shape[1:]) + [0])
		create_individual_signals_from_multidimensional_array(view_signal_list[device_name][signal_name],	array_dimension,0,signal_name + "[:,",)
for can_channel in multiple_can_channels:
	device_name_in_devices_dict = can_channel
	if can_channel.startswith("t_") or can_channel.startswith("t-"):
		device_name_in_devices_dict = can_channel[time_prefix_len:]
	device_name_in_devices_dict = device_name_in_devices_dict.replace(" ", "_")
	device_name_in_devices_dict = device_name_in_devices_dict.replace(".", "_")

	new_device_name = signal_info_mapping[can_channel][0]
	if new_device_name.startswith("t_") or new_device_name.startswith("t-"):
		new_device_name = new_device_name[time_prefix_len:]
	new_device_name = new_device_name.replace(" ", "_")
	new_device_name = new_device_name.replace(".", "_")
	can_device = MatDevices[device_name_in_devices_dict]
	can_signals = view_signal_list[device_name_in_devices_dict]
	if new_device_name not in MatDevices.keys():
		MatDevices[new_device_name] = can_device
		view_signal_list[new_device_name] = can_signals

	if new_device_name not in Hdf5Devices.keys():
		hdf5_can_device = Hdf5Devices[device_name_in_devices_dict]
		Hdf5Devices[new_device_name] = hdf5_can_device
total_devices = len(Hdf5Devices.keys())
total_signals = 0
for device in Hdf5Devices.keys():
	for signal_name in Hdf5["devices"][device]["Controller"].keys():
		total_signals = total_signals + 1
json_view_signal_list = json.dumps(view_signal_list)
Hdf5.attrs['namedump'] = json_view_signal_list
Hdf5.attrs['version']  = VERSION
Hdf5.attrs['timens']   = str(iParser.getStartDate(MatName))
Hdf5.attrs['parser_version'] = ''

creation_time = time.time()
if ConvFormat == 'hdf5':
		Hdf5.close()

end = time.time()


print MatName

print 'original file size:     ' + file_size(MatName)
print 'converted file size:    ' + file_size(HdfName)

print 'total devices:         %d' % (total_devices)
print 'total signals:         %d' % (total_signals)
print 'total time:            %f' % (end - start)
print 'import time:           %f' % (import_time - start)
print 'mat parsing time:      %f' % (parsing_time - import_time)
print 'conversion time:       %f' % (end - parsing_time)
