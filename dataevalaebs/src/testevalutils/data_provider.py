import logging
import os

from measparser.signalgroup import SignalGroupError
from measparser import cSignalSource
from testevalutils.signal_mapping_factory import SignalMappingFactory

logger = logging.getLogger("DataProvider")

class SignalDict(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [SignalDict(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, SignalDict(b) if isinstance(b, dict) else b)

class DataProvider:
		def __init__(self,measurement,testsuit_resources_path):
				self.signals = {}

				self.valid_signal = None

				self.source = cSignalSource(measurement)

				signal_mapping_factory = SignalMappingFactory()
				self.library_path_list = []

				library_path= testsuit_resources_path
				self.library_path_list.append(library_path)
				signal_mapping_factory.loadModule(self.library_path_list)
				self.signal_mapping = signal_mapping_factory.getSignalMappingRegistery()

				commonTimeGroup = self.source.selectSignalGroup(self.signal_mapping['commonTimeGroupList'])
				self.commonTime, _ = commonTimeGroup.get_signal('commonTime')
				# subgroup = {}
				# subgroup["commonTime"] = self.commonTime, _
				# self.signals["commonTimeGroupList"]=subgroup

				self.signals["commonTime"] = self.commonTime, _
				for groupName, signalInfo in self.signal_mapping.items():
						try:
								if groupName != "commonTimeGroupList":
										group = self.source.selectSignalGroup(signalInfo)
										subsignals = {}
										for alias in group.keys():
											subsignals[alias] = group.get_signal(alias, ScaleTime=self.commonTime)
										self.signals[groupName.replace("List", '')] = subsignals
											# self.signals[alias] = group.get_signal(alias, ScaleTime = self.commonTime)
						except SignalGroupError as ex:
								logger.info("Following signals are not present :\n" + (",".join(signalInfo[0].keys())))
								logger.info("Following signals are configured : \n" + str(signalInfo))
								logger.info("Details of the error: \n" + ex.message)
								logger.info("Please add signal in format: {'alias':'deviceName','signalName'}")

				self.createSignalClassObject()

		def createSignalClassObject(self):
			self.valid_signal = SignalDict(self.signals)

		def printSignalgroupList(self,signalGroupName,signalGroupList):
				print("{} :".format(signalGroupName.replace("List","")))
				for signalGroup in signalGroupList :
						for alias, details in signalGroup.items():
								# logger.info("{} : {}".format(alias, details))
								print("\t{} : {}".format(alias, details))



		def addSignal(self,DeviceName,SignalName, Alias=None):
				if self.commonTime is not None:
						customSignal = {}
						if Alias is None :
							customSignal[SignalName] = self.source.getSignal(DeviceName,SignalName,ScaleTime=self.commonTime)
							self.signals["customGroup"] = customSignal
						else:
							customSignal[Alias] = self.source.getSignal(DeviceName, SignalName, ScaleTime=self.commonTime)
							self.signals["customGroup"] = customSignal

		def showPreDefinedSignals(self):
				if self.signal_mapping is not None:
						for groupName, groupDetails in self.signal_mapping.items():
										self.printSignalgroupList(groupName,groupDetails)


		def showAllValidSignals(self):
				for groupName,groupDetails in self.signals.items():
						if type(groupDetails) == dict:
							for signalAlias, signalInfo in groupDetails.items():
								print("{} : {}".format(groupName, signalAlias))
						else:
							print("{} ".format(groupName))



if __name__ == '__main__':
		provider = DataProvider(r"D:\measurements\TSR_evaluation\tssdetected_status\mi5id787__2022-02-08_14-17-40.h5",r"C:\KBApps\PythonToolchain_git\dataevalaebs\src\testeval\suit_4926652\resources")
		provider.addSignal("VDC2_0B_s0B","VDC2_LongAccel_0B")
		# provider.showPreDefinedSignals()
		provider.showAllValidSignals()