# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from primitives.bases import PrimitiveCollection
import logging

logger = logging.getLogger('fill_flc25_lane_hypothesis')
LANE_HYPO_MESSAGE_NUM = 5

signalTemplates_LaneHypotheses = (
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_lanesI"
     "%dI_centerLine"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_lanesI"
     "%dI_direction"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_lanesI"
     "%dI_directionConfidence"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_lanesI%dI_id"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_lanesI"
     "%dI_leftBoundaryParts"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_lanesI"
     "%dI_leftLane"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_lanesI"
     "%dI_numLeftBoundaryParts"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_lanesI"
     "%dI_numRightBoundaryParts"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_lanesI"
     "%dI_rightBoundaryParts"),
		("CEM_FDP_KB_M_p_RmfOutputIfMeas",
		 "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_lanesI"
     "%dI_rightLane"),
)
header_sgs = [{
		'numLanes'    : ('CEM_FDP_KB_M_p_RmfOutputIfMeas',
										 'MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_numLanes'),
		'egoLaneIndex': ('CEM_FDP_KB_M_p_RmfOutputIfMeas',
										 'MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_aLanesHypotheses_egoLaneIndex'),
}]


def createMessageGroups(MESSAGE_NUM, signalTemplates):
		messageGroups = []
		for m in xrange(MESSAGE_NUM):
				messageGroup = {}
				for signalTemplate in signalTemplates:
						if signalTemplate[1].count('leftBoundaryParts') or signalTemplate[1].count('rightBoundaryParts') == 1:
								for n in xrange(4):
										fullName = signalTemplate[1] % m
										signal = fullName
										signal_name = signal + '[:,' + str(n) + ']'
										shortName = (signal_name.split('[')[0] + 'I' + str(n) + 'I').split('_')[-1]
										messageGroup[shortName] = (signalTemplate[0], signal_name)
						else:
								fullName = signalTemplate[1] % m
								shortName = signalTemplate[1].split('_')[-1]
								messageGroup[shortName] = (signalTemplate[0], fullName)
				messageGroups.append(messageGroup)
		return messageGroups


messageGroups_EmGenObjectList = createMessageGroups(LANE_HYPO_MESSAGE_NUM, signalTemplates_LaneHypotheses)


class Flc25LaneHypothesisObjects(ObjectFromMessage):
		# _attribs = tuple(tmpl[1].split('_')[-1] for tmpl in signalTemplates_LaneHypotheses)
		_attribs = [tmpl[1].split('_')[-1] for tmpl in signalTemplates_LaneHypotheses]
		_attribs.remove("leftBoundaryParts")
		_attribs.remove("rightBoundaryParts")
		second_level_details = ['leftBoundaryPartsI0I', 'leftBoundaryPartsI1I', 'leftBoundaryPartsI2I',
														'leftBoundaryPartsI3I', 'rightBoundaryPartsI0I', 'rightBoundaryPartsI1I',
														'rightBoundaryPartsI2I', 'rightBoundaryPartsI3I']
		_attribs += second_level_details

		_attribs = tuple(_attribs)

		def __init__(self, id, time, source, group, invalid_mask, scaletime = None):
				self._invalid_mask = invalid_mask
				self._group = group
				super(Flc25LaneHypothesisObjects, self).__init__(id, time, None, None, scaleTime = None)
				return

		def _create(self, signalName):
				value = self._group.get_value(signalName, ScaleTime = self.time)

				mask = ~self._invalid_mask
				out = np.ma.masked_all_like(value)
				out.data[mask] = value[mask]
				out.mask &= ~mask
				return out

		def id(self):
				# data = np.repeat(np.uint8(self._id), self.time.size)
				# arr = np.ma.masked_array(data, mask=self.dx.mask)
				return self._id

		def centerLine(self):
				return self._centerLine

		def direction(self):
				return self._direction

		def directionConfidence(self):
				return self._directionConfidence

		def rightLane(self):
				return self._rightLane

		def rightBoundaryPartsI3I(self):
				return self._rightBoundaryPartsI3I

		def rightBoundaryPartsI2I(self):
				return self._rightBoundaryPartsI2I

		def rightBoundaryPartsI1I(self):
				return self._rightBoundaryPartsI1I

		def rightBoundaryPartsI0I(self):
				return self._rightBoundaryPartsI0I

		def numRightBoundaryParts(self):
				return self._numRightBoundaryParts

		def numLeftBoundaryParts(self):
				return self._numLeftBoundaryParts

		def leftLane(self):
				return self._leftLane

		def leftBoundaryPartsI3I(self):
				return self._leftBoundaryPartsI3I

		def leftBoundaryPartsI2I(self):
				return self._leftBoundaryPartsI2I

		def leftBoundaryPartsI1I(self):
				return self._leftBoundaryPartsI1I

		def leftBoundaryPartsI0I(self):
				return self._leftBoundaryPartsI0I


class Calc(iCalc):
		dep = 'calc_common_time-flc25',

		def check(self):
				modules = self.get_modules()
				source = self.get_source()
				commonTime = modules.fill(self.dep[0])
				detailed_groups = []
				for sg in messageGroups_EmGenObjectList:
						detailed_groups.append(source.selectSignalGroup([sg]))
				header_group = source.selectSignalGroup(header_sgs)
				return detailed_groups, header_group, commonTime

		def fill(self, groups, header_group, common_time):
				import time
				start = time.time()
				lane_hypos = PrimitiveCollection(common_time)
				numLanes = header_group.get_value("numLanes", ScaleTime= common_time)
				egoLaneIndex = header_group.get_value("egoLaneIndex", ScaleTime= common_time)

				# Create List of Hypothesis objects
				for _id, group in enumerate(groups):
						invalid_mask = np.zeros(len(common_time), dtype = bool)
						if np.all(invalid_mask):
								continue
						lane_hypos[_id] = Flc25LaneHypothesisObjects(_id, common_time, None, group, invalid_mask,
																												 scaletime = common_time)
				# Logic
				LanesHypothesesList = []

				for laneHypoIndex in range(len(common_time)):
						LanesHypotheses = {}
						LanesHypotheses['egoLaneIndex'] = egoLaneIndex[laneHypoIndex]
						lanes = {}
						# Valid lanes [0...4]
						if numLanes[laneHypoIndex] >= 0 and numLanes[laneHypoIndex] < 5:
								for IdxLane in range(numLanes[laneHypoIndex]):
										lane = {}
										lane['id'] = lane_hypos[IdxLane].id  # TODO
										lane['centerLine'] = lane_hypos[IdxLane].centerLine[laneHypoIndex]
										lane['leftLane'] = lane_hypos[IdxLane].leftLane[laneHypoIndex]
										lane['rightLane'] = lane_hypos[IdxLane].rightLane[laneHypoIndex]

										lane['numLeftBoundaryParts'] = lane_hypos[IdxLane].numLeftBoundaryParts[laneHypoIndex]
										lane['numRightBoundaryParts'] = lane_hypos[IdxLane].numRightBoundaryParts[laneHypoIndex]
										leftBoundaryParts = []
										rightBoundaryParts = []
										# Valid boundary parts [0...3]
										if lane['numLeftBoundaryParts'] >= 0 and lane['numLeftBoundaryParts'] < 4:
												for k in range(lane['numLeftBoundaryParts']):
														leftBoundaryParts.append(lane_hypos[IdxLane]["leftBoundaryPartsI%dI" % k][laneHypoIndex])

										if lane['numRightBoundaryParts'] >= 0 and lane['numRightBoundaryParts'] < 4:
												for k in range(lane['numRightBoundaryParts']):
														rightBoundaryParts.append(lane_hypos[IdxLane]["rightBoundaryPartsI%dI" % k][laneHypoIndex])

										lane['leftBoundaryParts'] = np.array(leftBoundaryParts)
										lane['rightBoundaryParts'] = np.array(rightBoundaryParts)
										lanes[IdxLane] = lane
						LanesHypotheses['lanes'] = lanes
						LanesHypothesesList.append(LanesHypotheses)
				done = time.time()
				elapsed = done - start
				logger.info("Lane Hypothesis from road model fusion is completed in " + str(elapsed))
				return LanesHypothesesList


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport\ContiMeasurementsSuport\mfc525_interface\measurements\2020-08-20\NY00__2020-08-20_13-52-08.mat"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		conti = manager_modules.calc('fill_flc25_lane_hypotheses@aebs.fill', manager)
		print(conti)
