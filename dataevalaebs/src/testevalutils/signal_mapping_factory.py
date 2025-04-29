"""
Signal Mapping factory returns group of signal name based on name
"""
import inspect
import os
import subprocess
import logging


class SignalMappingFactory:
	signal_mapping_registry = {}  # {"groupname": groupdetails}

	@staticmethod
	def loadModule(library_path_list):
		""" Imports the libraries and store in registry"""
		for library_path in library_path_list:
			for file_name in os.listdir(os.path.abspath(library_path)):
						module_name, ext = os.path.splitext(file_name)
						if ext == ".ipynb":
							exe_command = 'jupyter nbconvert "{}" --to python'.format(''.join(os.path.join(library_path, file_name)))
							os.system(exe_command)

		for library_path in library_path_list:
			for file_name in os.listdir(os.path.abspath(library_path)):
						module_name, ext = os.path.splitext(file_name)
						if ext == '.py':
							module = SignalMappingFactory.getModule(module_name,
																	 os.path.join(
																			 library_path,
																			 file_name))
							for name, member in inspect.getmembers(module):
								if not (name.startswith('__') and name.endswith('__')):
									SignalMappingFactory.signal_mapping_registry[
										name] = member

	@staticmethod
	def getModule(module_name, full_path):
		import sys
		python_version = sys.version_info
		major = python_version[0]
		minor = python_version[1]
		if (major < 3) and( minor == 7):
			import imp
			return imp.load_source(module_name, full_path)


	@staticmethod
	def getSignalMappingRegistery():
			return SignalMappingFactory.signal_mapping_registry



if __name__=='__main__':

		from measparser import cSignalSource
		from measparser.signalgroup import SignalGroupError
		signal_mapping_factory = SignalMappingFactory()
		library_path_list = []
		library_path = os.path.abspath(
				os.path.join(os.path.dirname(os.path.dirname(__file__)), 'testeval\\suit_4926652\\resources'))
		library_path_list.append(library_path)
		signal_mapping_factory.loadModule(library_path_list)
		signal_mapping = signal_mapping_factory.getSignalMappingRegistery()
		measurement = r"D:\measurements\TSR_evaluation\tssdetected_status\mi5id787__2022-02-08_14-17-40.h5"
		source = cSignalSource(measurement)
		signals = {}
		for groupName , signalInfo in signal_mapping.items() :

				try:
						group = source.selectSignalGroup(signalInfo)
						for alias in group.keys():
								signals[alias] = group.get_signal(alias)
				except SignalGroupError as ex:
						print ("Following signals are not present :\n" + (",".join(signalInfo[0].keys())))
						print("Following signals are configured : \n"+str(signalInfo))
						print("Details of the error: \n" + ex.message)
						print("Please add signal in format: {'alias':'deviceName','signalName'}")

		print(signals)