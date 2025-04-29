# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

import numpy as np
import numpy.ma as ma
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import TrackingState, LandmarkObjectType
from primitives.bases import PrimitiveCollection
from pyutils.enum import enum

logger = logging.getLogger('fill_flc25_tsr_raw_tracks')
TRACK_MESSAGE_NUM = 50
SECOND_LEVEL_COUNT = 3
OBJ_CLASS_VALS = (
		'UNKNOWN1',
		'UNKNOWN2',
		'TRAFFIC_SIGN',
)
OBJ_CLASS = enum(**dict((name, n) for n, name in enumerate(OBJ_CLASS_VALS)))

signalTemplates_second_level_details = (
		("LmkGenLandmarkList","MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Specifics_TrafficSign_SupplResultsI%dI_eSupplClassId"),
)
signalTemplates_second_level_detailsh5 = (
		("MFC5xx Device.LMK.LmkGenLandmarkList","MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Specifics_TrafficSign_SupplResults%d_eSupplClassId"),
)

signalTemplates_LmkGenLandmarkList = (
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_uId"),
		("LmkGenLandmarkList",
		 "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Specifics_TrafficSign_fMainExistenceProbability"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Specifics_eClassification"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Specifics_uiClassConfidence"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Specifics_TrafficSign_eSignId"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Position_fDistX"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Position_fDistY"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Position_fDistZ"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Geometry_fHeight"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Geometry_fWidth"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Position_fDistXStd"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Position_fDistYStd"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Position_fDistZStd"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Specifics_TrafficSign_etrackCharacteristics"),

)
signalTemplates_LmkGenLandmarkListh5 = (
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_uId"),
		("MFC5xx Device.LMK.LmkGenLandmarkList",
		 "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Specifics_TrafficSign_fMainExistenceProbability"),
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Specifics_eClassification"),
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Specifics_uiClassConfidence"),
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Specifics_TrafficSign_eSignId"),
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Generics_Position_fDistX"),
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Generics_Position_fDistY"),
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Generics_Position_fDistZ"),
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Generics_Geometry_fHeight"),
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Generics_Geometry_fWidth"),
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Generics_Position_fDistXStd"),
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Generics_Position_fDistYStd"),
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Generics_Position_fDistZStd"),
		("MFC5xx Device.LMK.LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark%d_Specifics_TrafficSign_etrackCharacteristics"),
)

def createMessageGroups_second_level_details(TRACK_MESSAGE_NUM, SECOND_LEVEL_COUNT, signalTemplates):
		messageGroups = []  # 0.16
		for n in xrange(TRACK_MESSAGE_NUM):
				# messageGroup = {}
				SubMessageGroups = []
				for m in xrange(SECOND_LEVEL_COUNT):
						messageGroup = {}
						signalDict = []
						for signalTemplate in signalTemplates:
								if signalTemplate[1].count('I%dI') == 1:
										fullName = signalTemplate[1] % n
										shortName = signalTemplate[1].split('_')[-1]
										signal = fullName
										signal_name = signal + '[:,' + str(m) + ']'
										messageGroup[shortName] = (signalTemplate[0], signal_name)
								else:
										fullName = signalTemplate[1] % (n, m)
										shortName = signalTemplate[1].split('_')[-1]
										if 'I%dI' in shortName:
												shortName = shortName.split('I%dI')[0]
										messageGroup[shortName] = (signalTemplate[0], fullName)
						signalDict.append(messageGroup)
						messageGroup1 = {}
						for signalTemplate in signalTemplates_second_level_detailsh5:
								if signalTemplate[1].count('%d') == 1:
										fullName = signalTemplate[1] % n
										shortName = signalTemplate[1].split('_')[-1]
										signal = fullName
										signal_name = signal + '[:,' + str(m) + ']'
										messageGroup1[shortName] = (signalTemplate[0], signal_name)
								else:
										fullName = signalTemplate[1] % (n, m)
										shortName = signalTemplate[1].split('_')[-1]
										if '%d' in shortName:
												shortName = shortName.split('%d')[0]
										messageGroup1[shortName] = (signalTemplate[0], fullName)
						signalDict.append(messageGroup1)
						SubMessageGroups.append(signalDict)
						messageGroups.append(SubMessageGroups)
		return messageGroups

def createVariableMessageGroups(signalTemplates):
		messageGroups = []
		for m in xrange(TRACK_MESSAGE_NUM):
				messageGroup = {}
				SignalDict = []
				for signalTemplate in signalTemplates:
						fullName = signalTemplate[1] % m
						shortName = signalTemplate[1].split('_')[-1]
						messageGroup[shortName] = (signalTemplate[0], fullName)
				SignalDict.append(messageGroup)
				messageGroup2 = {}
				for signalTemplate in signalTemplates_LmkGenLandmarkListh5:
						fullName = signalTemplate[1] % m
						shortName = signalTemplate[1].split('_')[-1]
						messageGroup2[shortName] = (signalTemplate[0], fullName)
				SignalDict.append(messageGroup2)
				messageGroups.append(SignalDict)
		return messageGroups


messageGroup = createVariableMessageGroups(signalTemplates_LmkGenLandmarkList)
messageGroups_second_level_details = createMessageGroups_second_level_details(TRACK_MESSAGE_NUM, SECOND_LEVEL_COUNT,
                                                                              signalTemplates_second_level_details)

class GroundTruthTrack(ObjectFromMessage):
		_attribs = [tmpl[1].split("_")[-1] for tmpl in signalTemplates_LmkGenLandmarkList]
		_attribs += ["eSupplClassId"]
		_attribs += ["etrackBinary"]
		_attribs = tuple(_attribs)

		def __init__(self, id, time, source, group, invalid_mask, scaletime = None):
				self._invalid_mask = invalid_mask
				self._group = group

				super(GroundTruthTrack, self).__init__(id, time, None, None, scaleTime = None)
				return

		def _create(self, signalName):
				value = self._group.get_value(signalName, ScaleTime = self.time)
				if str(signalName).__contains__("etrackCharacteristics"):
					self.etrack = value
				mask = ~self._invalid_mask
				out = np.ma.masked_all_like(value)
				out.data[mask] = value[mask]
				out.mask &= ~mask
				return out

		def id(self):
				data = np.repeat(np.uint8(self._id), self.time.size)
				arr = np.ma.masked_array(data, mask = self._invalid_mask)
				return arr
		def etrackCharacteristics(self):
			return self._etrackCharacteristics

		def etrackBinary(self):
			return np.array([np.binary_repr(value, width=16) for value in self.etrack])

		def dx(self):
				return self._fDistX

		def esupplclassid(self):
				return self._eSupplClassId

		def dy(self):
				return self._fDistY

		def dz(self):
				return self._fDistZ

		def dx_std(self):
				return self._fDistXStd

		def dy_std(self):
				return self._fDistYStd

		def dz_std(self):
				return self._fDistZStd

		def width(self):
				return self._fDistYStd

		def height(self):
				return self._fDistZStd

		def universal_id(self):
				return self._uId

		def traffic_sign_confidence(self):
				return self._uiClassConfidence

		def traffic_sign_id(self):
				return self._eSignId

		def traffic_existence_probability(self):
				return self._fMainExistenceProbability

		def landmark_obj_type(self):
				traffic_sign = self._eClassification == OBJ_CLASS.TRAFFIC_SIGN
				return LandmarkObjectType(traffic_sign = traffic_sign)

		def tr_state(self):
				valid = ma.masked_array(~self._fDistX.mask, self._fDistX.mask)
				meas = np.ones_like(valid)
				hist = np.ones_like(valid)
				for st, end in maskToIntervals(~self._fDistX.mask):
						if st != 0:
								hist[st] = False
				return TrackingState(valid = valid, measured = meas, hist = hist)

		def alive_intervals(self):
				new = self.tr_state.valid & ~self.tr_state.hist
				validIntervals = cIntervalList.fromMask(self.time, self.tr_state.valid)
				newIntervals = cIntervalList.fromMask(self.time, new)
				alive_intervals = validIntervals.split(st for st, _ in newIntervals)
				return alive_intervals


class Calc(iCalc):
		dep = 'calc_common_time-tsrresim',

		def check(self):
				modules = self.get_modules()
				source = self.get_source()
				commonTime = modules.fill(self.dep[0])
				second_level_detail_group = []

				for _sg in messageGroups_second_level_details:
						second_level_detail_subGroup = []
						for signal in _sg:
								second_level_detail_subGroup.append(self.source.selectSignalGroup(signal))
						second_level_detail_group.append(second_level_detail_subGroup)

				groups = []
				for sg in messageGroup:
						groups.append(source.selectSignalGroup(sg))
				return second_level_detail_group, groups, commonTime

		def fill(self, second_level_detail_group, groups, common_time):
				lmk_tracks = PrimitiveCollection(common_time)
				VALID_FLAG = False
				supplementary_sign_details = {} #PrimitiveCollection(common_time)
				for _id, group in enumerate(groups):
						uid = group.get_value("uId", ScaleTime = common_time)
						invalid_mask = (uid == 255) | (uid == 0) | (np.isnan(uid))
						invalid_mask = invalid_mask
						# if np.all(invalid_mask):
						# 		continue
						VALID_FLAG = True
						lmk_tracks[_id] = GroundTruthTrack(_id, common_time, None, group, invalid_mask,
																							 scaletime = common_time)

						second_level_group = second_level_detail_group[_id]
						second_level = PrimitiveCollection(common_time)
						for id, detail in enumerate(second_level_group):
								second_level[id] = GroundTruthTrack(id, common_time, None, detail, invalid_mask,
								                                       scaletime = common_time)
						supplementary_sign_details[_id] = second_level
				# Filter out supplementary_sign_details
				# for id, details in supplementary_sign_details.items():
				# 		suppl_sign_id = details
				# 		invalid_mask = (uid == 255) | (np.iscalc_common_timenan(uid))
				# 		if np.all(invalid_mask):
				# 				continue
				suppl_signs = {}
				# suppl_track[0]["esupplclassid"][suppl_track[0]["esupplclassid"].mask] = 0

				# Add supplementary track if it has sign detected
				for id, suppl_tracks in supplementary_sign_details.iteritems():

						# Clean other values where sign is not detected
						suppl_sign_dict = {}
						for _id, suppl_track in suppl_tracks.items():
								suppl_track["esupplclassid"][suppl_track["esupplclassid"].mask] = 0
								invalid_mask = (suppl_track["esupplclassid"].data == 0.0)
								# if np.all(invalid_mask):
								# 		continue
								suppl_sign_dict[_id] = {
										"esupplclassid": np.ma.array(suppl_track["esupplclassid"].data, mask = invalid_mask)
								}
						# if suppl_sign_dict != {}:
						suppl_signs[id] = suppl_sign_dict
				if not VALID_FLAG:
						logging.warning("Error: {} :Measurement does not contain TSR object data".format(self.source.FileName))
				return lmk_tracks, suppl_signs


if __name__ == '__main__':
		from config.Config import init_dataeval

		# meas_path = r"\\pu2w6474\shared-drive\measurements\new_meas_09_11_21\mi5id787__2021-10-28_00-03-59.h5"
		meas_path = r"C:\KBData\TSR\test\2021-11-16\mi5id5321__2021-11-16_10-55-20_tsrresim.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		object = manager_modules.calc('fill_flc25_tsr_raw_tracks@aebs.fill', manager)
		print(object)
