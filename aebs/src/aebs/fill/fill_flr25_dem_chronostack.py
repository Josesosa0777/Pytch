# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np
import numpy.ma as ma
from interface import iCalc
from metatrack import ObjectFromMessage
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from primitives.bases import PrimitiveCollection


DEM_CHRONOSTACK_OBJ_NUM = 30
sgn_group = [
	("DEM_CHRONOSTACK","ARS4xx_Device_SW_Every10ms_DEM_CHRONOSTACK[%d]_Dem_Event_Dem_EventId"),
	("DEM_CHRONOSTACK","ARS4xx_Device_SW_Every10ms_DEM_CHRONOSTACK[%d]_Dem_Event_Dem_EventStatusEx"),
]
sgn_grouph5 = [
	("ARS4xx Device.SW_Every10ms.DEM_CHRONOSTACK","ARS4xx_Device_SW_Every10ms_DEM_CHRONOSTACK%d_Dem_Event_Dem_EventId"),
	("ARS4xx Device.SW_Every10ms.DEM_CHRONOSTACK","ARS4xx_Device_SW_Every10ms_DEM_CHRONOSTACK%d_Dem_Event_Dem_EventStatusEx"),
]

def createMessageGroups(MESSAGE_NUM, signalTemplates):
		messageGroups = []
		for m in xrange(MESSAGE_NUM):
				messageGroup = {}
				SignalDict = []
				for signalTemplate in signalTemplates:
						fullName = signalTemplate[1] % m
						shortName = signalTemplate[1].split('_')[-1]
						messageGroup[shortName] = (signalTemplate[0], fullName)
				SignalDict.append(messageGroup)
				messageGroup2 = {}
				for signalTemplate in sgn_grouph5:
						fullName = signalTemplate[1] % m
						shortName = signalTemplate[1].split('_')[-1]
						messageGroup2[shortName] = (signalTemplate[0], fullName)
				SignalDict.append(messageGroup2)
				messageGroups.append(SignalDict)
		return messageGroups


dem_messageGroup = createMessageGroups(DEM_CHRONOSTACK_OBJ_NUM, sgn_group)


class DEMChronostack(ObjectFromMessage):
	#attribs = [k for d,s in signalTemplates_DTClist2 for k in key_tmpl if k in s]

	_attribs = tuple(tmpl[1].split('_')[-1] for tmpl in sgn_group)
	_reserved_names = ObjectFromMessage._reserved_names + ('get_selection_timestamp',)

	def __init__(self, id, time, source, group, invalid_mask, scaletime = None):
		self._invalid_mask = invalid_mask
		self._group = group
		super(DEMChronostack, self).__init__(id, time, None, None, scaleTime = None)
		return

	def _create(self, signalName):
		value = self._group.get_value(signalName, ScaleTime = self.time)
		mask = ~self._invalid_mask
		out = np.ma.masked_all_like(value)
		out.data[mask] = value[mask]
		out.mask &= ~mask
		return out

	def EventId(self):
		return self._EventId

	def EventStatusEx(self):
		return self._EventStatusEx


class Calc(iCalc):
	dep = 'calc_common_time-flr25',

	def check(self):
		modules = self.get_modules()
		source = self.get_source()
		commonTime = modules.fill(self.dep[0])
		groups = []
		for sg in dem_messageGroup:
			groups.append(self.source.selectSignalGroup(sg))
		return groups, commonTime

	def fill(self, groups, common_time):
		dem_event_data = PrimitiveCollection(common_time)
		for _id, group in enumerate(groups):
			event_id = group.get_value("EventId", ScaleTime = common_time)
			invalid_mask = np.isnan(event_id)
			dem_event_data[_id] = DEMChronostack(_id, common_time, None, group, invalid_mask, scaletime = common_time)
		return dem_event_data


if __name__ == '__main__':
	from config.Config import init_dataeval

	meas_path = r"\\pu2w6474\shared-drive\transfer\shubham\measurements\ARS4xx_new_dcnvt_h5_format\New folder\mi5id787__2021-06-09_06-40-32.h5"
	# meas_path = r"X:\eval_team\meas\conti\fcw\2020-08-17\FCW__2020-08-17_11-11-01.mat"
	config, manager, manager_modules = init_dataeval(['-m', meas_path])
	conti = manager_modules.calc('fill_flr25_dem_chronostack@aebs.fill', manager)
	print(conti)
