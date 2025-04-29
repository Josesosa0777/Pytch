# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np
from interface import iCalc
from metatrack import ObjectFromMessage
from primitives.bases import PrimitiveCollection
import logging

logger = logging.getLogger('fill_flc25_linear_objects')
LINEAR_OBJECT_MESSAGE_NUM = 20

signalTemplates_LinearObjectList_header = [{'numLinearObjects':
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		"MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_numLinearObjects"), }]

signalTemplates_LinearObjectList_details = (
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		"MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLinearObjectsI%dI_color"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		"MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLinearObjectsI"
		"%dI_geometry_from"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		"MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLinearObjectsI"
		"%dI_geometry_line"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		"MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLinearObjectsI%dI_geometry_to"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		"MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLinearObjectsI%dI_marking"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		"MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLinearObjectsI%dI_type"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		"MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLinearObjectsI%dI_width"),
)


def createMessageGroups_details(LINEAR_OBJECT_MESSAGE_NUM, signalTemplates):
		messageGroups_details = []
		for m in xrange(LINEAR_OBJECT_MESSAGE_NUM):
				messageGroup_details = {}
				for signalTemplate in signalTemplates:
						fullName = signalTemplate[1] % m
						shortName = signalTemplate[1].split('I_')[-1]
						messageGroup_details[shortName] = (signalTemplate[0], fullName)
				messageGroups_details.append(messageGroup_details)
		return messageGroups_details


messageGroups_LinearObjectList_details = createMessageGroups_details(LINEAR_OBJECT_MESSAGE_NUM,
		signalTemplates_LinearObjectList_details)


class Flc25LinearObjects(ObjectFromMessage):
		_attribs = tuple(tmpl[1].split('I_')[-1] for tmpl in signalTemplates_LinearObjectList_details)

		def __init__(self, id, time, source, group, invalid_mask, scaletime=None):
				self._invalid_mask = invalid_mask
				self._group = group
				super(Flc25LinearObjects, self).__init__(id, time, None, None, scaleTime=None)
				return

		def _create(self, signalName):
				value = self._group.get_value(signalName, ScaleTime=self.time)

				mask = ~self._invalid_mask
				out = np.ma.masked_all_like(value)
				out.data[mask] = value[mask]
				out.mask &= ~mask
				return out

		def id(self):
				data = np.repeat(np.uint8(self._id), self.time.size)
				arr = np.ma.masked_array(data, mask=self._invalid_mask)
				return arr

		def color(self):
				return self._color

		def geometry_from(self):
				return self._geometry_from

		def geometry_line(self):
				return self._geometry_line

		def geometry_to(self):
				return self._geometry_to

		def marking(self):
				return self._marking

		def type(self):
				return self._type

		def width(self):
				return self._width


class Calc(iCalc):
		dep = 'calc_common_time-flc25',

		def check(self):
				modules = self.get_modules()
				source = self.get_source()
				commonTime = modules.fill(self.dep[0])
				detail_group = []
				for sg in messageGroups_LinearObjectList_details:
						detail_group.append(self.source.selectSignalGroup([sg]))
				header_group = source.selectSignalGroup(signalTemplates_LinearObjectList_header)
				return detail_group, header_group, commonTime

		def fill(self, detail_group, header_group, common_time):
				import time
				start = time.time()
				detail_linear_objects = PrimitiveCollection(common_time)
				numLinearObjectsId = header_group.get_value("numLinearObjects", ScaleTime=common_time)
				for _id, group in enumerate(detail_group):
						invalid_mask = np.zeros(common_time.size, bool)
						detail_linear_objects[_id] = Flc25LinearObjects(_id, common_time, None, group, invalid_mask,
								scaletime=common_time)
				# Logic
				LinearObjectList = []
				for linearObjectIndex in range(len(common_time)):
						LinearObjects = {}
						LinearObjects['numLinearObjects'] = numLinearObjectsId[linearObjectIndex]
						if numLinearObjectsId[linearObjectIndex] >= 0 and numLinearObjectsId[linearObjectIndex] < 20:
								for IdxLane in range(numLinearObjectsId[linearObjectIndex]):
										LinearObject = {}
										LinearObject['width'] = detail_linear_objects[IdxLane].width[linearObjectIndex]  # TODO
										LinearObject['marking'] = detail_linear_objects[IdxLane].marking[linearObjectIndex]
										LinearObject['color'] = detail_linear_objects[IdxLane].color[linearObjectIndex]
										LinearObject['type'] = detail_linear_objects[IdxLane].type[linearObjectIndex]
										LinearObject['geometry_line'] = detail_linear_objects[IdxLane].geometry_line[linearObjectIndex]
										LinearObject['geometry_from'] = detail_linear_objects[IdxLane].geometry_from[linearObjectIndex]
										LinearObject['geometry_to'] = detail_linear_objects[IdxLane].geometry_to[linearObjectIndex]
										LinearObjects[IdxLane] = LinearObject
						LinearObjectList.append(LinearObjects)
				done = time.time()
				elapsed = done - start
				logger.info("Liner objects from road model fusion is completed in " + str(elapsed))
				return LinearObjectList


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\__EnduranceRun\MFC525\poc\HMC__2020-04-25_13-34-35_point_clouds.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		linear_objects = manager_modules.calc('fill_flc25_linear_objects@aebs.fill', manager)
# print(linear_objects)
