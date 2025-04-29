# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from primitives.bases import PrimitiveCollection

NUM_ABDLANEDATA = 10

signalTemplates_ABDLaneObjectList = (
		("ABDLaneData", "MFC5xx_Device_LD_ABDLaneData_asLaneBoundaryI%dI_sGeometry_sParameters_fDistanceMeter"),
		("ABDLaneData", "MFC5xx_Device_LD_ABDLaneData_asLaneBoundaryI%dI_sGeometry_sParameters_fYawAngleRad"),
		("ABDLaneData", "MFC5xx_Device_LD_ABDLaneData_asLaneBoundaryI%dI_sGeometry_sParameters_sClothoidNear_fCurvature"),
		("ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundaryI%dI_sGeometry_sParameters_sClothoidNear_fCurvatureRate"),
		("ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundaryI%dI_sGeometry_sParameters_sClothoidNear_fValidLengthMeter"),
		("ABDLaneData", "MFC5xx_Device_LD_ABDLaneData_asLaneBoundaryI%dI_sGeometry_sParameters_sClothoidFar_fCurvature"),
		("ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundaryI%dI_sGeometry_sParameters_sClothoidFar_fCurvatureRate"),
		("ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundaryI%dI_sGeometry_sParameters_sClothoidFar_fValidLengthMeter"),
		("ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundaryI%dI_sGeometry_sParameters_sClothoidVertical_fCurvature"),
		("ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundaryI%dI_sGeometry_sParameters_sClothoidVertical_fCurvatureRate"),
		("ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundaryI%dI_sGeometry_sParameters_sClothoidVertical_fValidLengthMeter"),
		("ABDLaneData", "MFC5xx_Device_LD_ABDLaneData_asLaneBoundaryI%dI_sStatus_bAvailable"),
)

signalTemplates_ABDLaneObjectListh5 = (
		("MFC5xx Device.LD.ABDLaneData", "MFC5xx_Device_LD_ABDLaneData_asLaneBoundary%d_sGeometry_sParameters_fDistanceMeter"),
		("MFC5xx Device.LD.ABDLaneData", "MFC5xx_Device_LD_ABDLaneData_asLaneBoundary%d_sGeometry_sParameters_fYawAngleRad"),
		("MFC5xx Device.LD.ABDLaneData", "MFC5xx_Device_LD_ABDLaneData_asLaneBoundary%d_sGeometry_sParameters_sClothoidNear_fCurvature"),
		("MFC5xx Device.LD.ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundary%d_sGeometry_sParameters_sClothoidNear_fCurvatureRate"),
		("MFC5xx Device.LD.ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundary%d_sGeometry_sParameters_sClothoidNear_fValidLengthMeter"),
		("MFC5xx Device.LD.ABDLaneData", "MFC5xx_Device_LD_ABDLaneData_asLaneBoundary%d_sGeometry_sParameters_sClothoidFar_fCurvature"),
		("MFC5xx Device.LD.ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundary%d_sGeometry_sParameters_sClothoidFar_fCurvatureRate"),
		("MFC5xx Device.LD.ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundary%d_sGeometry_sParameters_sClothoidFar_fValidLengthMeter"),
		("MFC5xx Device.LD.ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundary%d_sGeometry_sParameters_sClothoidVertical_fCurvature"),
		("MFC5xx Device.LD.ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundary%d_sGeometry_sParameters_sClothoidVertical_fCurvatureRate"),
		("MFC5xx Device.LD.ABDLaneData",
		 "MFC5xx_Device_LD_ABDLaneData_asLaneBoundary%d_sGeometry_sParameters_sClothoidVertical_fValidLengthMeter"),
		("MFC5xx Device.LD.ABDLaneData", "MFC5xx_Device_LD_ABDLaneData_asLaneBoundary%d_sStatus_bAvailable"),
)

def createMessageGroups(MESSAGE_NUM, signalTemplates):
		messageGroups = []
		for m in xrange(MESSAGE_NUM):
				messageGroup = {}
				signalDict = []
				for signalTemplate in signalTemplates:
						fullName = signalTemplate[1] % m
						shortName = signalTemplate[1].split('_s')[-1]
						messageGroup[shortName] = (signalTemplate[0], fullName)
				signalDict.append(messageGroup)
				messageGroup2 = {}
				for signalTemplate_h5 in signalTemplates_ABDLaneObjectListh5:
						fullName = signalTemplate_h5[1] % m
						shortName = signalTemplate_h5[1].split('_s')[-1]
						messageGroup2[shortName] = (signalTemplate_h5[0], fullName)
				signalDict.append(messageGroup2)
				messageGroups.append(signalDict)
		return messageGroups


messageGroups_ABDLaneObjectList = createMessageGroups(NUM_ABDLANEDATA, signalTemplates_ABDLaneObjectList)


class FLC25ABDLanes(ObjectFromMessage):
		_attribs = tuple(tmpl[1].split('_s')[-1] for tmpl in signalTemplates_ABDLaneObjectList)

		def __init__(self, id, time, source, group, invalid_mask, scaletime = None):
				self._invalid_mask = invalid_mask
				self._group = group
				super(FLC25ABDLanes, self).__init__(id, time, None, None, scaleTime = None)
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

		def Parameters_fDistanceMeter(self):
				return self._Parameters_fDistanceMeter

		def Parameters_fYawAngleRad(self):
				return self._Parameters_fYawAngleRad

		def ClothoidNear_fCurvature(self):
				return self._ClothoidNear_fCurvature

		def ClothoidNear_fCurvatureRate(self):
				return self._ClothoidNear_fCurvatureRate

		def ClothoidNear_fValidLengthMeter(self):
				return self._ClothoidNear_fValidLengthMeter

		def ClothoidFar_fCurvature(self):
				return self._ClothoidFar_fCurvature

		def ClothoidFar_fCurvatureRate(self):
				return self._ClothoidFar_fCurvatureRate

		def ClothoidFar_fValidLengthMeter(self):
				return self._ClothoidFar_fValidLengthMeter

		def ClothoidVertical_fCurvature(self):
				return self._ClothoidVertical_fCurvature

		def ClothoidVertical_fCurvatureRate(self):
				return self._ClothoidVertical_fCurvatureRate

		def ClothoidVertical_fValidLengthMeter(self):
				return self._ClothoidVertical_fValidLengthMeter

		def Status_bAvailable(self):
				return self._Status_bAvailable


class Calc(iCalc):
		dep = 'calc_common_time-flc25',

		def check(self):
				modules = self.get_modules()
				source = self.get_source()
				commonTime = modules.fill(self.dep[0])
				groups = []
				for sg in messageGroups_ABDLaneObjectList:
						groups.append(self.source.selectSignalGroup(sg))
				return groups, commonTime

		def fill(self, groups, common_time):

				lanes = PrimitiveCollection(common_time)
				for _id, group in enumerate(groups):
						invalid_mask = np.zeros(common_time.size, bool)
						lanes[_id] = FLC25ABDLanes(_id, common_time, None, group, invalid_mask, scaletime = common_time)
				return lanes


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\mfc525_interface" \
								r"\measurements\HMC__2020-04-25_13-34-35_ABDLaneData.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti = manager_modules.calc('fill_lanes_flc25_abd@aebs.fill', manager)
		print(conti)
