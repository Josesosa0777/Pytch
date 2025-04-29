# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np
from interface import iCalc
from PySide import QtGui
import os
import re
import logging

logger = logging.getLogger('fill_dem_events')

MESSAGE_NUM = 30

signalTemplates = (
    ("MFC5xx Device.DEM.Dem_EventMemoryPrimary", "MFC5xx_Device_DEM_Dem_EventMemoryPrimary%d_EntryDataPos"),
    ("MFC5xx Device.DEM.Dem_EventMemoryPrimary", "MFC5xx_Device_DEM_Dem_EventMemoryPrimary%d_EntryStatus"),
    ("MFC5xx Device.DEM.Dem_EventMemoryPrimary", "MFC5xx_Device_DEM_Dem_EventMemoryPrimary%d_EventId"),
    ("MFC5xx Device.DEM.Dem_EventMemoryPrimary", "MFC5xx_Device_DEM_Dem_EventMemoryPrimary%d_OccCtr"),
    ("MFC5xx Device.DEM.Dem_EventMemoryPrimary", "MFC5xx_Device_DEM_Dem_EventMemoryPrimary%d_OccOrder"),
)

signalTemplates_2 = (
    ("Dem_EventMemoryPrimary", "MFC5xx_Device_DEM_Dem_EventMemoryPrimaryI%dI_EntryDataPos"),
    ("Dem_EventMemoryPrimary", "MFC5xx_Device_DEM_Dem_EventMemoryPrimaryI%dI_EntryStatus"),
    ("Dem_EventMemoryPrimary", "MFC5xx_Device_DEM_Dem_EventMemoryPrimaryI%dI_EventId"),
    ("Dem_EventMemoryPrimary", "MFC5xx_Device_DEM_Dem_EventMemoryPrimaryI%dI_OccCtr"),
    ("Dem_EventMemoryPrimary", "MFC5xx_Device_DEM_Dem_EventMemoryPrimaryI%dI_OccOrder"),
)


def createMessageGroups(MESSAGE_NUM, signalTemplates, signalTemplates_2):
    messageGroups = []
    for m in xrange(MESSAGE_NUM):
        messageGroup = {}
        signalDict = []
        for signalTemplate in signalTemplates:
            fullName = signalTemplate[1] % m
            shortName = signalTemplate[1].split('_')[-1]
            messageGroup[shortName] = (signalTemplate[0], fullName)
        signalDict.append(messageGroup)
        messageGroup2 = {}
        for signalTemplate in signalTemplates_2:
            fullName = signalTemplate[1] % m
            shortName = signalTemplate[1].split('_')[-1]
            messageGroup2[shortName] = (signalTemplate[0], fullName)
        signalDict.append(messageGroup2)
        messageGroups.append(signalDict)
    return messageGroups


messageGroups = createMessageGroups(MESSAGE_NUM, signalTemplates, signalTemplates_2)


class Calc(iCalc):
    dep = 'calc_common_time-flr25',

    def selectFile(self, File):
        self.SelectedFile, = File
        return

    def check(self):
        source = self.get_source()
        self.SelectedFile = ""
        Dialog = QtGui.QFileDialog()
        Dir = os.path.dirname(self.source.FileName)
        Dialog.setDirectory(Dir)
        Dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        Dialog.filesSelected.connect(self.selectFile)
        Dialog.exec_()
        a2l_file_path = self.SelectedFile

        if not os.path.exists(a2l_file_path) or not a2l_file_path.endswith(".a2l"):
            logger.critical("a2l file is missing at path. Please selct correct file.")
            raise ValueError("missing a2l dependency file")

        modules = self.get_modules()
        # source = self.get_source()
        commonTime = modules.fill(self.dep[0])
        detailed_groups = []
        try:
            # for i in range(MESSAGE_NUM):
            #     detailed_groups.append(source.selectSignalGroup([messageGroups[i]]))
            for id, values in enumerate(messageGroups):
                for idx, value in enumerate(values):
                    try:
                        detailed_groups.append(source.selectSignalGroup([value]))
                    except:
                        pass
            event_data = {}
            with open(a2l_file_path) as infile:
                start_flag = False
                for line in infile:
                    result = re.search(r"TAB_VERB 520", line)
                    if result:
                        start_flag = True
                        continue
                    if start_flag:
                        result1 = re.search(r"/end COMPU_VTAB", line)
                        if result1:
                            break
                        else:
                            event_ = re.sub('\s+', ' ', line).strip().split()
                            event_data[event_[0]] = event_[1].lstrip('"').rstrip('"')
        except:
            pass
        return detailed_groups, commonTime, event_data

    def fill(self, detailed_groups, common_time,event_data):
        demSignalInfo = []
        for i, group in enumerate(detailed_groups):
            dem_events = np.zeros(common_time.shape, dtype='|S6')
            demSignal = {}

            group.all_aliases.sort()
            signal_aliases = group.all_aliases

            # Read signals
            EntryDataPos = group.get_value(signal_aliases[0], ScaleTime=common_time)
            EntryStatus = group.get_value(signal_aliases[1], ScaleTime=common_time)
            OccCtr = group.get_value(signal_aliases[3], ScaleTime=common_time)
            OccOrder = group.get_value(signal_aliases[4], ScaleTime=common_time)
            EventId = group.get_value(signal_aliases[2], ScaleTime=common_time)

            # Identify dem event from eventID signal
            try:
                if EventId[0] == 0:  # This might have some meaning
                    event_id = hex(0)
                    description = ""
                else:
                    event_id = hex(EventId[0])
                    description = event_data[str(EventId[0])]

            except:
                event_id = hex(EventId[0])
                description = ""
                logger.info(
                    "Missing event name in a2l file for an event id: {}".format(EventId[0]))

            dem_event = np.where(EventId == EventId[0], description, 'U')
            dem_events[0:len(common_time)] = event_id

            demSignal['EntryDataPos'] = EntryDataPos
            demSignal['EntryStatus'] = EntryStatus
            demSignal['EventId DEC'] = EventId
            demSignal['EventId HEX'] = dem_events
            demSignal['DEM Event'] = dem_event
            demSignal['OccCtr'] = OccCtr
            demSignal['OccOrder'] = OccOrder
            demSignal["valid"] = np.ones_like(common_time, dtype=bool)

            demSignalInfo.append(demSignal)

        return common_time, demSignalInfo


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\DEM_meas\HMC-QZ-STR__2020-11-24_09-46-17.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    demSignalInfo = manager_modules.calc('fill_dem_events@aebs.fill', manager)
    print(demSignalInfo)
