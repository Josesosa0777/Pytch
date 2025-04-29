# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np
from interface import iCalc
from metatrack import ObjectFromMessage
from primitives.bases import PrimitiveCollection

signalTemplates_roadhypothesisObjectList = (
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aRoadHypotheses_leftBoundaryParts"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aRoadHypotheses_numLeftBoundaryParts"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aRoadHypotheses_numRightBoundaryParts"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aRoadHypotheses_roadSeparation"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aRoadHypotheses_roadType"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aRoadHypotheses_rightBoundaryParts"),
)

signalTemplates_roadhypothesisObjectListh5 = (
		("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aRoadHypotheses_leftBoundaryParts"),
		("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aRoadHypotheses_numLeftBoundaryParts"),
		("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aRoadHypotheses_numRightBoundaryParts"),
		("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aRoadHypotheses_roadSeparation"),
		("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aRoadHypotheses_roadType"),
		("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aRoadHypotheses_rightBoundaryParts"),
)

def createMessageGroups(signalTemplates):
		messageGroups = []
		messageGroup = {}
		signalDict = []
		for signalTemplate in signalTemplates:
				fullName = signalTemplate[1]
				shortName = signalTemplate[1].split('_')[-1]
				messageGroup[shortName] = (signalTemplate[0], fullName)
		signalDict.append(messageGroup)
		messageGroup2= {}
		for signalTemplate in signalTemplates_roadhypothesisObjectListh5:
				fullName = signalTemplate[1]
				shortName = signalTemplate[1].split('_')[-1]
				messageGroup2[shortName] = (signalTemplate[0], fullName)
		signalDict.append(messageGroup2)
		messageGroups.append(signalDict)
		return messageGroups


messageGroups_roadhypothesisObjectList = createMessageGroups(signalTemplates_roadhypothesisObjectList)


class Flc25RoadHypothesisObjects(ObjectFromMessage):
		_attribs = tuple(tmpl[1].split('_')[-1] for tmpl in signalTemplates_roadhypothesisObjectList)

		def __init__(self, id, time, source, group, invalid_mask, scaletime = None):
				self._invalid_mask = invalid_mask
				self._group = group
				super(Flc25RoadHypothesisObjects, self).__init__(id, time, None, None, scaleTime = None)
				return

		def _create(self, signalName):
				value = self._group.get_value(signalName, ScaleTime = self.time)

				mask = ~self._invalid_mask
				out = np.ma.masked_all_like(value)
				out.data[mask] = value[mask]
				out.mask &= ~mask
				return out

		def id(self):
				data = np.repeat(np.uint8(self._id), self.time.size)
				arr = np.ma.masked_array(data, mask = self._invalid_mask)
				return arr

		def leftBoundaryParts(self):
				return self._leftBoundaryParts

		def rightBoundaryParts(self):
				return self._rightBoundaryParts

		def numLeftBoundaryParts(self):
				return self._numLeftBoundaryParts

		def numRightBoundaryParts(self):
				return self._numRightBoundaryParts

		def roadSeparation(self):
				return self._roadSeparation

		def roadType(self):
				return self._roadType


class Calc(iCalc):
		dep = 'calc_common_time-flc25',

		def check(self):
				modules = self.get_modules()
				source = self.get_source()
				commonTime = modules.fill(self.dep[0])
				groups = []
				for sg in messageGroups_roadhypothesisObjectList:
						groups.append(self.source.selectSignalGroup(sg))

				return groups, commonTime

		def fill(self, groups, common_time):
				RoadHypothesisObject = PrimitiveCollection(common_time)
				# Create List of Hypothesis objects

				for _id, group in enumerate(groups):
						invalid_mask = np.zeros(common_time.size, bool)
						RoadHypothesisObject[_id] = Flc25RoadHypothesisObjects(_id, common_time, None, group, invalid_mask,
																																	 scaletime = common_time)

				return RoadHypothesisObject


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"\\pu2w6474\shared-drive\transfer\shubham\measurements\FLC25_CEM_TPF_EM_New\mi5id787__2021-10-28_00-03-59.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		RoadHypothesisObject = manager_modules.calc('fill_flc25_roadhypotheses_objects@aebs.fill', manager)
		print(RoadHypothesisObject)
