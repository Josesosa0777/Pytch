# -*- dataeval: init -*-
from collections import OrderedDict

import interface
import datavis
import logging
import os

import numpy as np

logger = logging.getLogger("view_sys_bitfield_event_status")

def_param = interface.NullParam

sgs = [
    {
        "AEBS1_AEBSState_2A": ("CAN_MFC_Public_AEBS1_2A", "AEBS1_AEBSState_2A"),

        "FLI2_LDWSState_E8": ("CAN_MFC_Public_FLI2_E8", "FLI2_LDWSState_E8"),

        "DM1_DTC1_E8": ("CAN_MFC_Public_DM1_E8", "DM1_DTC1_E8"),
        "DM1_DTC2_E8": ("CAN_MFC_Public_DM1_E8", "DM1_DTC2_E8"),
        "DM1_DTC3_E8": ("CAN_MFC_Public_DM1_E8", "DM1_DTC3_E8"),
        "DM1_DTC4_E8": ("CAN_MFC_Public_DM1_E8", "DM1_DTC4_E8"),
        "DM1_DTC5_E8": ("CAN_MFC_Public_DM1_E8", "DM1_DTC5_E8"),

        "FLI2_FwdLaneImagerStatus_E8": ("CAN_MFC_Public_FLI2_E8", "FLI2_FwdLaneImagerStatus_E8"),

        "DM1_DTC1_2A": ("CAN_MFC_Public_DM1_2A", "DM1_DTC1_2A"),
        "DM1_DTC2_2A": ("CAN_MFC_Public_DM1_2A", "DM1_DTC2_2A"),
        "DM1_DTC3_2A": ("CAN_MFC_Public_DM1_2A", "DM1_DTC3_2A"),
        "DM1_DTC4_2A": ("CAN_MFC_Public_DM1_2A", "DM1_DTC4_2A"),
        "DM1_DTC5_2A": ("CAN_MFC_Public_DM1_2A", "DM1_DTC5_2A"),

        "time": ("MFC5xx Device.FCU.VehDynSync", "MFC5xx_Device_FCU_VehDynSync_Longitudinal_Velocity"),
    },
]

dtcMappingFile_path = os.path.join(os.path.dirname(__file__), "dtc_mapping.txt")

dtcMappningDict = {}


class View(interface.iView):

    def check(self):

        sys_bitfield_event = []
        event_status = {}
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
            # return group

        dtcMappingFile = open(dtcMappingFile_path, 'r')

        for line in dtcMappingFile:
            dtc_id, dtc_name = line.strip().split('=')
            dtcMappningDict[dtc_id.strip().lower()] = dtc_name.strip()

        # if 'time' in group:
        commonTime = group.get_time('time')

        if 'AEBS1_AEBSState_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("AEBS1_AEBSState_2A", ScaleTime=commonTime)
            event_status['bitfield_status'] = (value00 == 14).astype(int)
            # event_status['DTC in DEC'] = np.array(
            #     ['' if value == '0x0' else '' for value in
            #      [hex(int(value)) for value in event_status['bitfield_status']]])
            # event_status['DTC in HEX'] = np.array(
            #     ['' if value == '0x0' else '' for value in
            #      [hex(int(value)) for value in event_status['bitfield_status']]])
            event_status['DTC Name'] = np.array(
                ['' if value == '0x0' else '' for value in
                 [hex(int(value)) for value in event_status['bitfield_status']]])
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("AEBS1_AEBSState_2A", len(commonTime))
            sys_bitfield_event.append(event_status)
            event_status = {}

        if 'FLI2_LDWSState_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_LDWSState_E8", ScaleTime=commonTime)
            event_status['bitfield_status'] = (value00 == 14).astype(int)
            # event_status['DTC in DEC'] = np.array(
            #     ['' if value == '0x0' else '' for value in
            #      [hex(int(value)) for value in event_status['bitfield_status']]])
            # event_status['DTC in HEX'] = np.array(
            #     ['' if value == '0x0' else '' for value in
            #      [hex(int(value)) for value in event_status['bitfield_status']]])
            event_status['DTC Name'] = np.array(
                ['' if value == '0x0' else '' for value in
                 [hex(int(value)) for value in event_status['bitfield_status']]])
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("FLI2_LDWSState_E8", len(commonTime))
            sys_bitfield_event.append(event_status)
            event_status = {}

        if 'DM1_DTC1_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC1_E8", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                event_status['bitfield_status'] = value00
            else:
                event_status['bitfield_status'] = (value00 != 0).astype(int)
                # event_status['DTC in DEC'] = value00
                # event_status['DTC in HEX'] = np.array([hex(int(x)) for x in value00])
                event_status['DTC Name'] = np.array(
                    [dtcMappningDict[str(x)] if x != '0x0' else '' for x in np.array([hex(int(x)) for x in value00])])
                # hex(int(row['DTC in DEC'])
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("DM1_DTC1_E8", len(commonTime))
            sys_bitfield_event.append(event_status)
            event_status = {}

        if 'DM1_DTC2_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC2_E8", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                event_status['bitfield_status'] = np.zeros(len(commonTime), dtype=int)
                # event_status['DTC in DEC'] = event_status['bitfield_status']
                # event_status['DTC in HEX'] = np.array([hex(int(x)) for x in event_status['bitfield_status']])
                event_status['DTC Name'] = np.array(
                    [dtcMappningDict[str(x)] if x != '0x0' else '' for x in
                     np.array([hex(int(x)) for x in event_status['bitfield_status']])])
            else:
                event_status['bitfield_status'] = (value00 != 0).astype(int)
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("DM1_DTC2_E8", len(commonTime))
            sys_bitfield_event.append(event_status)
            event_status = {}

        if 'DM1_DTC3_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC3_E8", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                event_status['bitfield_status'] = np.zeros(len(commonTime), dtype=int)
                # event_status['DTC in DEC'] = event_status['bitfield_status']
                # event_status['DTC in HEX'] = np.array([hex(int(x)) for x in event_status['bitfield_status']])
                event_status['DTC Name'] = np.array(
                    [dtcMappningDict[str(x)] if x != '0x0' else '' for x in
                     np.array([hex(int(x)) for x in event_status['bitfield_status']])])
            else:
                event_status['bitfield_status'] = (value00 != 0).astype(int)
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("DM1_DTC3_E8", len(commonTime))
            sys_bitfield_event.append(event_status)
            event_status = {}

        if 'DM1_DTC4_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC4_E8", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                event_status['bitfield_status'] = np.zeros(len(commonTime), dtype=int)
                # event_status['DTC in DEC'] = event_status['bitfield_status']
                # event_status['DTC in HEX'] = np.array([hex(int(x)) for x in event_status['bitfield_status']])
                event_status['DTC Name'] = np.array(
                    [dtcMappningDict[str(x)] if x != '0x0' else '' for x in
                     np.array([hex(int(x)) for x in event_status['bitfield_status']])])
            else:
                event_status['bitfield_status'] = (value00 != 0).astype(int)
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("DM1_DTC4_E8", len(commonTime))
            sys_bitfield_event.append(event_status)
            event_status = {}

        if 'DM1_DTC5_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC5_E8", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                event_status['bitfield_status'] = np.zeros(len(commonTime), dtype=int)
                # event_status['DTC in DEC'] = event_status['bitfield_status']
                # event_status['DTC in HEX'] = np.array([hex(int(x)) for x in event_status['bitfield_status']])
                event_status['DTC Name'] = np.array(
                    [dtcMappningDict[str(x)] if x != '0x0' else '' for x in
                     np.array([hex(int(x)) for x in event_status['bitfield_status']])])
            else:
                event_status['bitfield_status'] = (value00 != 0).astype(int)
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("DM1_DTC5_E8", len(commonTime))
            sys_bitfield_event.append(event_status)
            event_status = {}

        if 'FLI2_FwdLaneImagerStatus_E8' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FLI2_FwdLaneImagerStatus_E8",
                                                                 ScaleTime=commonTime)
            event_status['bitfield_status'] = (value00 > 1).astype(int)
            # event_status['DTC in DEC'] = np.array(
            #     ['' if value == '0x0' else '' for value in
            #      [hex(int(value)) for value in event_status['bitfield_status']]])
            # event_status['DTC in HEX'] = np.array(
            #     ['' if value == '0x0' else '' for value in
            #      [hex(int(value)) for value in event_status['bitfield_status']]])
            event_status['DTC Name'] = np.array(
                ['' if value == '0x0' else '' for value in
                 [hex(int(value)) for value in event_status['bitfield_status']]])
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("FLI2_FwdLaneImagerStatus_E8", len(commonTime))
            sys_bitfield_event.append(event_status)
            event_status = {}

        if 'DM1_DTC1_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC1_2A", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                event_status['bitfield_status'] = value00
            else:
                event_status['bitfield_status'] = (value00 != 0).astype(int)
                # event_status['DTC in DEC'] = value00
                # event_status['DTC in HEX'] = np.array([hex(int(x)) for x in value00])
                event_status['DTC Name'] = np.array(
                    [dtcMappningDict[str(x)] if x != '0x0' else '' for x in np.array([hex(int(x)) for x in value00])])
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("DM1_DTC1_2A", len(commonTime))
            sys_bitfield_event.append(event_status)
            event_status = {}

        if 'DM1_DTC2_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC2_2A", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                event_status['bitfield_status'] = np.zeros(len(commonTime), dtype=int)
                # event_status['DTC in DEC'] = event_status['bitfield_status']
                # event_status['DTC in HEX'] = np.array([hex(int(x)) for x in event_status['bitfield_status']])
                event_status['DTC Name'] = np.array(
                    [dtcMappningDict[str(x)] if x != '0x0' else '' for x in
                     np.array([hex(int(x)) for x in event_status['bitfield_status']])])
            else:
                event_status['bitfield_status'] = (value00 != 0).astype(int)
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("DM1_DTC2_2A", len(commonTime))
            sys_bitfield_event.append(event_status)
            event_status = {}

        if 'DM1_DTC3_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC3_2A", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                event_status['bitfield_status'] = np.zeros(len(commonTime), dtype=int)
                # event_status['DTC in DEC'] = event_status['bitfield_status']
                # event_status['DTC in HEX'] = np.array([hex(int(x)) for x in event_status['bitfield_status']])
                event_status['DTC Name'] = np.array(
                    [dtcMappningDict[str(x)] if x != '0x0' else '' for x in
                     np.array([hex(int(x)) for x in event_status['bitfield_status']])])
            else:
                event_status['bitfield_status'] = (value00 != 0).astype(int)
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("DM1_DTC3_2A", len(commonTime))
            sys_bitfield_event.append(event_status)
            event_status = {}

        if 'DM1_DTC4_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC4_2A", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                event_status['bitfield_status'] = np.zeros(len(commonTime), dtype=int)
                # event_status['DTC in DEC'] = event_status['bitfield_status']
                # event_status['DTC in HEX'] = np.array([hex(int(x)) for x in event_status['bitfield_status']])
                event_status['DTC Name'] = np.array(
                    [dtcMappningDict[str(x)] if x != '0x0' else '' for x in
                     np.array([hex(int(x)) for x in event_status['bitfield_status']])])
            else:
                event_status['bitfield_status'] = (value00 != 0).astype(int)
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("DM1_DTC4_2A", len(commonTime))
            sys_bitfield_event.append(event_status)
            event_status = {}

        if 'DM1_DTC5_2A' in group:
            time00, value00, unit00 = group.get_signal_with_unit("DM1_DTC5_2A", ScaleTime=commonTime)
            if np.any(np.isnan(value00)):
                event_status['bitfield_status'] = np.zeros(len(commonTime), dtype=int)
                # event_status['DTC in DEC'] = event_status['bitfield_status']
                # event_status['DTC in HEX'] = np.array([hex(int(x)) for x in event_status['bitfield_status']])
                event_status['DTC Name'] = np.array(
                    [dtcMappningDict[str(x)] if x != '0x0' else '' for x in
                     np.array([hex(int(x)) for x in event_status['bitfield_status']])])
            else:
                event_status['bitfield_status'] = (value00 != 0).astype(int)
            event_status["valid"] = np.ones_like(commonTime, dtype=bool)
            event_status['event_name'] = np.repeat("DM1_DTC5_2A", len(commonTime))
            sys_bitfield_event.append(event_status)
            # event_status = {}

        table_headers_mapping = OrderedDict(
            [
                ("event_name", "Event Name"),
                ("bitfield_status", "Bitfield Status"),
                # ("DTC in DEC", "dtc_in_dec"),
                # ("DTC in HEX", "dtc_in_hex"),
                ("DTC Name", "DTC Description"),
            ]
        )

        return commonTime, sys_bitfield_event, table_headers_mapping

    def view(self, commonTime, sys_bitfield_event, table_headers_mapping):
        table_nav = datavis.cTableNavigator(title="sys_bitfield_event")
        self.sync.addClient(table_nav)
        table_nav.addtabledata(commonTime, sys_bitfield_event, table_headers_mapping)


if __name__ == "__main__":
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Python_Toolchain_2\Evaluation_data\sys_bitfield_event\mi5id5506__2024-06-26_09-43-26.h5"
    config, manager, manager_modules = init_dataeval(["-m", meas_path])
    manager.build(["view_sys_bitfield_event_status@dataevalaebs"], show_navigators=True)
    print("Done")
