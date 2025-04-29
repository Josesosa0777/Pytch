# -*- dataeval: init -*-
# -*- coding: utf-8 -*-


import numpy as np
from interface import iCalc
from metatrack import ObjectFromMessage
from primitives.bases import PrimitiveCollection
import logging

logger = logging.getLogger('fill_flc25_geometries_lines')
# TODO numLines is missing
FIRST_LEVEL_COUNT = 17
SECOND_LEVEL_COUNT = 150

signalTemplates_second_level_details = (

    # <editor-fold desc="lateralVariance">
    ("CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_linesI"
     "%dI_lateralVariance"),
    # <editor-fold desc="lateralVariance">
    # </editor-fold>
    # <editor-fold desc="points">
    ("CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_linesI%dI_pointsI"
     "%dI_fX"),
    ("CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_linesI%dI_pointsI"
     "%dI_fY"),
    ("CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_linesI%dI_pointsI"
     "%dI_fZ"),
    # </editor-fold>
)

signalTemplates_second_level_detailsh5 = (

    # <editor-fold desc="lateralVariance">
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_lines"
     "%d_lateralVariance"),
    # <editor-fold desc="lateralVariance">
    # </editor-fold>
    # <editor-fold desc="points">
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_lines%d_points"
     "%d_fX"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_lines%d_points"
     "%d_fY"),
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_lines%d_points"
     "%d_fZ"),
    # </editor-fold>
)


signalTemplates_first_level_detailsh5 = (
    # Length
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_lines%d_length"),
    # numPoints
    ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_lines"
     "%d_numPoints"),
)
signalTemplates_first_level_details = (
    # Length
    ("CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_linesI%dI_length"),
    # numPoints
    ("CEM_FDP_KB_M_p_RmfOutputIfMeas",
     "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_linesI"
     "%dI_numPoints"),
)

header_sgs = [{
    'numLines': ('CEM_FDP_KB_M_p_RmfOutputIfMeas',
                 'MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_numLines'),
},
    {
        'numLines': ('MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_RmfOutputIfMeas',
                     'MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_RmfOutputIfMeas_sGeometries_numLines'),
    }
]


def createMessageGroups_second_level_details(FIRST_LEVEL_COUNT, SECOND_LEVEL_COUNT, signalTemplates):
    messageGroups = []  # 0.16
    for n in xrange(FIRST_LEVEL_COUNT):
        # messageGroup = {}
        SubMessageGroups = []
        for m in xrange(SECOND_LEVEL_COUNT):
            signalDict = []
            messageGroup = {}
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
            messageGroup2 = {}
            for signalTemplate in signalTemplates_second_level_detailsh5:
                if signalTemplate[1].count('%d') == 1:
                    fullName = signalTemplate[1] % n
                    shortName = signalTemplate[1].split('_')[-1]
                    signal = fullName
                    signal_name = signal + '[:,' + str(m) + ']'
                    messageGroup2[shortName] = (signalTemplate[0], signal_name)
                else:
                    fullName = signalTemplate[1] % (n, m)
                    shortName = signalTemplate[1].split('_')[-1]
                    if '%d' in shortName:
                        shortName = shortName.split('%d')[0]
                    messageGroup2[shortName] = (signalTemplate[0], fullName)
            signalDict.append(messageGroup2)
            SubMessageGroups.append(signalDict)
        # SubMessageGroup.append()
        messageGroups.append(SubMessageGroups)
    return messageGroups


def createMessageGroups__first_level_details(FIRST_LEVEL_COUNT, signalTemplates):
    messageGroups_header = []
    for m in xrange(FIRST_LEVEL_COUNT):
        signalDict = []
        messageGroup = {}
        for signalTemplate in signalTemplates:
            fullName = signalTemplate[1] % m
            shortName = signalTemplate[1].split('_')[-1]
            messageGroup[shortName] = (signalTemplate[0], fullName)
        signalDict.append(messageGroup)
        messageGroup2 = {}
        for signalTemplate in signalTemplates_first_level_detailsh5:
            fullName = signalTemplate[1] % m
            shortName = signalTemplate[1].split('_')[-1]
            messageGroup2[shortName] = (signalTemplate[0], fullName)
        signalDict.append(messageGroup2)
        messageGroups_header.append(signalDict)
    return messageGroups_header


messageGroups_second_level_details = createMessageGroups_second_level_details(FIRST_LEVEL_COUNT, SECOND_LEVEL_COUNT,
                                                                              signalTemplates_second_level_details)
messageGroups_first_level_details = createMessageGroups__first_level_details(FIRST_LEVEL_COUNT,
                                                                             signalTemplates_first_level_details)


class FLC25GeometriesLine(ObjectFromMessage):
    _attribs = [tmpl[1].split('_')[-1] for tmpl in signalTemplates_first_level_details]
    second_level_details = ['lateralVariance', 'fX', 'fY', 'fZ']
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

    def id(self):
        data = np.repeat(np.uint8(self._id), self.time.size)
        arr = np.ma.masked_array(data, mask=self._invalid_mask)
        return arr

    def length(self):
        return self._length

    def numPoints(self):
        return self._numPoints

    def lateralVariance(self):
        return self._lateralVariance

    def fX(self):
        return self._fX

    def fY(self):
        return self._fY

    def fZ(self):
        return self._fZ


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
                second_level_detail_subGroup.append(self.source.selectSignalGroup(signal))
            second_level_detail_group.append(second_level_detail_subGroup)

        first_level_detail_group = []
        for sg in messageGroups_first_level_details:
            first_level_detail_group.append(self.source.selectSignalGroup(sg))
        header_group = source.selectSignalGroup(header_sgs)
        return second_level_detail_group, first_level_detail_group, header_group, commonTime

    def fill(self, second_level_detail_group, first_level_detail_group, header_group, common_time):
        import time
        start = time.time()
        complete_signal_list = []
        numLines = header_group.get_value("numLines", ScaleTime=common_time)
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
        lineList = []
        for lineIndex in range(len(common_time)):
            lines = {}
            # Valid numLines [0...19]
            if numLines[lineIndex] >=0 and numLines[lineIndex] < 20:
                for IdxLines in range(numLines[lineIndex]):
                    line = {}
                    numPoints = first_level_detail[IdxLines].numPoints[lineIndex]
                    x = np.zeros(numPoints)
                    y = np.zeros(numPoints)
                    y_var = np.zeros(numPoints)
                    if numLines[lineIndex] >= 0 and numLines[lineIndex] < 150:
                        for k in range(numPoints):
                            x[k] = second_level_details[IdxLines][k].fX[lineIndex]
                            y[k] = second_level_details[IdxLines][k].fY[lineIndex]
                            y_var[k] = second_level_details[IdxLines][k].lateralVariance[lineIndex]
                    line['x'] = x
                    line['y'] = y
                    line['y_var'] = y_var
                    line['length'] = first_level_detail[IdxLines].length[lineIndex]

                    lines[IdxLines] = line
            lineList.append(lines)
        done = time.time()
        elapsed = done - start
        logger.info("Geometries lines from road model fusion is completed in " + str(elapsed))
        return lineList


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"\\pu2w6474\shared-drive\transfer\shubham\measurements\FLC25_CEM_TPF_EM_New\mi5id787__2021-10-28_00-03-59.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    conti = manager_modules.calc('fill_flc25_geometries_lines@aebs.fill', manager)
    print(conti)
