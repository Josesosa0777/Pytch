# -*- dataeval: init -*-
# -*- coding: utf-8 -*-


import numpy as np
from interface import iCalc
from metatrack import ObjectFromMessage
from primitives.bases import PrimitiveCollection
import logging

logger = logging.getLogger('fill_flc25_line_attributes')
# TODO numLines is missing
FIRST_LEVEL_COUNT = 17
SECOND_LEVEL_COUNT = 150

# signalTemplates_LineAttributes = (  # 17
#     ("CEM_FDP_KB_M_p_RmfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_lineAttributesI%dI_line"),
# )
signalTemplates_LineAttributes = (  # 17
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas.sGeometries.lineAttributes[%d].line"),
)

# signalTemplates_LaneHypotheses_details = (  # 150
#     ("CEM_FDP_KB_M_p_RmfOutputIfMeas",
#      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_lineAttributesI%dI_headingYaw")
# )

signalTemplates_LaneHypotheses_details = (  # 150
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas.sGeometries.lineAttributes[%d].headingYaw"),
)

header_sgs = [{
    'numLineAttributes': ('CEM_FDP_KB_M_p_RmfOutputIfMeas',
                          'MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_numLineAttributes'),
},
    {
        "numLineAttributes": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
                              "MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas.sGeometries.numLineAttributes"),
    }]


def createMessageGroups_second_level_details(FIRST_LEVEL_COUNT, SECOND_LEVEL_COUNT, signalTemplates):
    messageGroups = []  # 0.16
    for n in xrange(FIRST_LEVEL_COUNT):
        # messageGroup = {}
        SubMessageGroups = []
        for m in xrange(SECOND_LEVEL_COUNT):
            messageGroup = {}
            for signalTemplate in signalTemplates:
                if signalTemplate[1].count('[%d]') == 1:
                    fullName = signalTemplate[1] % n
                    shortName = signalTemplate[1].split('.')[-1]
                    signal = fullName
                    # signal_name = signal + '[:,' + str(m) + ']'
                    signal_name = signal
                    messageGroup[shortName] = (signalTemplate[0], signal_name)
            SubMessageGroups.append(messageGroup)
        # SubMessageGroup.append()
        messageGroups.append(SubMessageGroups)
    return messageGroups


def createMessageGroups__first_level_details(FIRST_LEVEL_COUNT, signalTemplates):
    messageGroups_header = []
    for m in xrange(FIRST_LEVEL_COUNT):
        messageGroup = {}
        for signalTemplate in signalTemplates:
            fullName = signalTemplate[1] % m
            shortName = signalTemplate[1].split('.')[-1]
            messageGroup[shortName] = (signalTemplate[0], fullName)
        messageGroups_header.append(messageGroup)
    return messageGroups_header


messageGroups_second_level_details = createMessageGroups_second_level_details(FIRST_LEVEL_COUNT, SECOND_LEVEL_COUNT,
                                                                              signalTemplates_LaneHypotheses_details)
messageGroups_first_level_details = createMessageGroups__first_level_details(FIRST_LEVEL_COUNT,
                                                                             signalTemplates_LineAttributes)


class FLC25GeometriesLine(ObjectFromMessage):
    _attribs = [tmpl[1].split('.')[-1] for tmpl in signalTemplates_LineAttributes]
    second_level_details = ['headingYaw']
    _attribs += second_level_details

    _attribs = tuple(_attribs)

    def __init__(self, id, time, source, group, invalid_mask, scaletime=None):
        self._invalid_mask = invalid_mask
        self._group = group
        super(FLC25GeometriesLine, self).__init__(id, time, None, None, scaleTime=None)
        return

    def _create(self, signalName):
        value = self._group.get_value(signalName, ScaleTime=self.time)
        mask = ~self._invalid_mask
        out = np.ma.masked_all_like(value)
        out.data[mask] = value[mask]
        out.mask &= ~mask
        return out

    # def id(self):
    #     data = np.repeat(np.uint8(self._id), self.time.size)
    #     arr = np.ma.masked_array(data, mask=self._invalid_mask)
    #     return arr

    def line(self):
        return self._line

    def headingYaw(self):
        return self._headingYaw


class Calc(iCalc):
    dep = 'calc_common_time-flc25',

    def check(self):
        modules = self.get_modules()
        source = self.get_source()
        commonTime = modules.fill(self.dep[0])
        second_level_detail_group = []

        for sg in messageGroups_second_level_details:
            second_level_detail_subGroup = []
            for signal in sg:
                second_level_detail_subGroup.append(self.source.selectSignalGroup([signal]))
            second_level_detail_group.append(second_level_detail_subGroup)

        first_level_detail_group = []
        for sg in messageGroups_first_level_details:
            first_level_detail_group.append(self.source.selectSignalGroup([sg]))
        header_group = source.selectSignalGroup(header_sgs)
        return second_level_detail_group, first_level_detail_group, header_group, commonTime

    def fill(self, second_level_detail_group, first_level_detail_group, header_group, common_time):
        import time
        start = time.time()
        numLineAttributes = header_group.get_value("numLineAttributes", ScaleTime=common_time)
        first_level_detail = PrimitiveCollection(common_time)
        second_level_details = PrimitiveCollection(common_time)

        for _id, group in enumerate(first_level_detail_group):
            invalid_mask = np.zeros(common_time.size, bool)
            first_level_detail[_id] = FLC25GeometriesLine(_id, common_time, None, group, invalid_mask,
                                                          scaletime=common_time)
            second_level_group = second_level_detail_group[_id]
            second_level = PrimitiveCollection(common_time)
            for id, detail in enumerate(second_level_group):
                second_level[id] = FLC25GeometriesLine(id, common_time, None, detail, invalid_mask,
                                                       scaletime=common_time)
            second_level_details[_id] = second_level
        # complete_signal_list.append((first_level_detail, second_level_details))
        # Logic
        lineAttrList = []
        numPoints = 150
        for lineAttrIndex in range(len(common_time)):
            lineAttrs = {}
            # Valid data is in between 0-16
            if numLineAttributes[lineAttrIndex] >= 0 and numLineAttributes[lineAttrIndex] < 17:
                for IdxLineAttributes in range(int(numLineAttributes[lineAttrIndex])):
                    line = {}
                    line['line'] = first_level_detail[IdxLineAttributes].line[lineAttrIndex]
                    headingYaw = np.zeros(numPoints)

                    for k in range(numPoints):
                        headingYaw[k] = second_level_details[IdxLineAttributes][k].headingYaw[lineAttrIndex]
                    line['headingYaw'] = headingYaw
                    lineAttrs[IdxLineAttributes] = line
            lineAttrList.append(lineAttrs)
        done = time.time()
        elapsed = done - start
        logger.info("Line attributes from road model fusion is completed in " + str(elapsed))
        return lineAttrList


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\pytch2_development\multimedia_signal_update\new_files_to_test\2025-03-25\mi5id5361__2025-03-25_13-59-20_Resim_2025.04.16_at_08.18.40.mf4"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    conti = manager_modules.calc('fill_flc25_line_attributes@aebs.fill', manager)
