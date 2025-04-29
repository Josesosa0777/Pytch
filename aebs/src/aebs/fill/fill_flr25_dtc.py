# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging

import numpy as np
import numpy.ma as ma
from interface import iCalc
from metatrack import ObjectFromMessage
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from primitives.bases import PrimitiveCollection

sgn_group = [
    {

        "AmberWarningLamp": ("DM1_2A_s2A", "DM1_AmberWarningLamp_2A"),
        "DM1_DTC1": ("DM1_2A_s2A", "DM1_DTC1_2A"),
        "DM1_DTC2": ("DM1_2A_s2A", "DM1_DTC2_2A"),
        "DM1_DTC3": ("DM1_2A_s2A", "DM1_DTC3_2A"),
        "DM1_DTC4": ("DM1_2A_s2A", "DM1_DTC4_2A"),
        "DM1_DTC5": ("DM1_2A_s2A", "DM1_DTC5_2A"),
        "DM1_OccuranceCount1": ("DM1_2A_s2A", "DM1_OccuranceCount1_2A"),
        "DM1_OccuranceCount2": ("DM1_2A_s2A", "DM1_OccuranceCount2_2A"),
        "DM1_OccuranceCount3": ("DM1_2A_s2A", "DM1_OccuranceCount3_2A"),
        "DM1_OccuranceCount4": ("DM1_2A_s2A", "DM1_OccuranceCount4_2A"),
        "DM1_OccuranceCount5": ("DM1_2A_s2A", "DM1_OccuranceCount5_2A"),
    },
    {
        "AmberWarningLamp": ("CAN_MFC_Public_DM1_2A", "DM1_AmberWarningLamp_2A"),
        "DM1_DTC1": ("CAN_MFC_Public_DM1_2A", "DM1_DTC1_2A"),
        "DM1_DTC2": ("CAN_MFC_Public_DM1_2A", "DM1_DTC2_2A"),
        "DM1_DTC3": ("CAN_MFC_Public_DM1_2A", "DM1_DTC3_2A"),
        "DM1_DTC4": ("CAN_MFC_Public_DM1_2A", "DM1_DTC4_2A"),
        "DM1_DTC5": ("CAN_MFC_Public_DM1_2A", "DM1_DTC5_2A"),
        "DM1_OccuranceCount1": ("CAN_MFC_Public_DM1_2A", "DM1_OccuranceCount1_2A"),
        "DM1_OccuranceCount2": ("CAN_MFC_Public_DM1_2A", "DM1_OccuranceCount2_2A"),
        "DM1_OccuranceCount3": ("CAN_MFC_Public_DM1_2A", "DM1_OccuranceCount3_2A"),
        "DM1_OccuranceCount4": ("CAN_MFC_Public_DM1_2A", "DM1_OccuranceCount4_2A"),
        "DM1_OccuranceCount5": ("CAN_MFC_Public_DM1_2A", "DM1_OccuranceCount5_2A"),
    },
    {
        "AmberWarningLamp": ("CAN_VEHICLE_DM1_2A","DM1_AmberWarningLamp_2A"),
        "DM1_DTC1": ("CAN_VEHICLE_DM1_2A","DM1_DTC1_2A"),
        "DM1_DTC2": ("CAN_VEHICLE_DM1_2A","DM1_DTC2_2A"),
        "DM1_DTC3": ("CAN_VEHICLE_DM1_2A","DM1_DTC3_2A"),
        "DM1_DTC4": ("CAN_VEHICLE_DM1_2A","DM1_DTC4_2A"),
        "DM1_DTC5": ("CAN_VEHICLE_DM1_2A","DM1_DTC5_2A"),
        "DM1_OccuranceCount1": ("CAN_VEHICLE_DM1_2A","DM1_OccuranceCount1_2A"),
        "DM1_OccuranceCount2": ("CAN_VEHICLE_DM1_2A","DM1_OccuranceCount2_2A"),
        "DM1_OccuranceCount3": ("CAN_VEHICLE_DM1_2A","DM1_OccuranceCount3_2A"),
        "DM1_OccuranceCount4": ("CAN_VEHICLE_DM1_2A","DM1_OccuranceCount4_2A"),
        "DM1_OccuranceCount5": ("CAN_VEHICLE_DM1_2A","DM1_OccuranceCount5_2A"),

    },
]


class Dm1Dtc(ObjectFromMessage):
    # attribs = [k for d,s in signalTemplates_DTClist2 for k in key_tmpl if k in s]
    attribs = [k for k in sgn_group[0].keys()]
    _attribs = tuple(attribs)
    _reserved_names = ObjectFromMessage._reserved_names + ('get_selection_timestamp',)

    def __init__(self, id, time, source, group, invalid_mask, scaletime=None):
        self._invalid_mask = invalid_mask
        self._group = group
        super(Dm1Dtc, self).__init__(id, time, None, None, scaleTime=None)
        return

    def _create(self, signalName):
        value = self._group.get_value(signalName, ScaleTime=self.time)
        mask = ~self._invalid_mask
        out = np.ma.masked_all_like(value)
        out.data[mask] = value[mask]
        out.mask &= ~mask
        return out

    def AmberWarningLamp(self):
        return self._AmberWarningLamp

    def DM1_DTC1(self):
        return self._DM1_DTC1

    def DM1_DTC2(self):
        return np.nan_to_num(self._DM1_DTC2)

    def DM1_DTC3(self):
        return np.nan_to_num(self._DM1_DTC3)

    def DM1_DTC4(self):
        return np.nan_to_num(self._DM1_DTC4)

    def DM1_DTC5(self):
        return np.nan_to_num(self._DM1_DTC5)

    def DM1_OccuranceCount1(self):
        return self._DM1_OccuranceCount1

    def DM1_OccuranceCount2(self):
        return np.nan_to_num(self._DM1_OccuranceCount2)

    def DM1_OccuranceCount3(self):
        return np.nan_to_num(self._DM1_OccuranceCount3)

    def DM1_OccuranceCount4(self):
        return np.nan_to_num(self._DM1_OccuranceCount4)

    def DM1_OccuranceCount5(self):
        return np.nan_to_num(self._DM1_OccuranceCount5)

    def merged_dtc_data(self):
        return np.column_stack((self._DM1_DTC1, self._DM1_DTC2, self._DM1_DTC3, self._DM1_DTC4, self._DM1_DTC5))

    def merged_occurance_cntr(self):
        return np.column_stack((self._DM1_OccuranceCount1, self._DM1_OccuranceCount2, self._DM1_OccuranceCount3,
                                self._DM1_OccuranceCount4, self._DM1_OccuranceCount5))

    def get_unique_dtc_counts(self):
        all_dtcs = np.concatenate((self.DM1_DTC1, self.DM1_DTC2, self.DM1_DTC3, self.DM1_DTC4, self.DM1_DTC5))
        unique_dtcs = np.unique(all_dtcs)
        dtc_counter = {}
        for dtc_id in unique_dtcs[unique_dtcs != 0]:
            dtc_indexes = np.where(self.merged_dtc_data == dtc_id)
            first_row = dtc_indexes[0][0]
            first_col = dtc_indexes[1][0]
            last_row = dtc_indexes[0][-1]
            last_col = dtc_indexes[1][-1]
            dtc_counter[dtc_id] = self.merged_occurance_cntr[last_row][last_col] - \
                                  self.merged_occurance_cntr[first_row][first_col] + 1
        return dtc_counter

    def get_dtc_intervals(self):
        dtc1 = np.where(self.DM1_DTC1[:-1] != self.DM1_DTC1[1:])[0] + 1
        dtc2 = np.where(self.DM1_DTC2[:-1] != self.DM1_DTC2[1:])[0] + 1
        dtc3 = np.where(self.DM1_DTC3[:-1] != self.DM1_DTC3[1:])[0] + 1
        dtc4 = np.where(self.DM1_DTC4[:-1] != self.DM1_DTC4[1:])[0] + 1
        dtc5 = np.where(self.DM1_DTC5[:-1] != self.DM1_DTC5[1:])[0] + 1

        return [dtc1, dtc2, dtc3, dtc4, dtc5]


class Calc(iCalc):
    dep = 'calc_common_time-flr25',

    def check(self):
        modules = self.get_modules()
        source = self.get_source()
        commonTime = modules.fill(self.dep[0])
        groups = self.source.selectSignalGroup(sgn_group)
        return groups, commonTime

    def fill(self, groups, common_time):
        dm1_data = PrimitiveCollection(common_time)
        amber_warning_lamp = groups.get_value("AmberWarningLamp", ScaleTime=common_time)
        invalid_mask = (amber_warning_lamp == 255) | (np.isnan(amber_warning_lamp))
        if np.all(invalid_mask):
            logging.warning("Error: {} :Measurement does not contain DTC object data".format(self.source.FileName))
        dm1_data = Dm1Dtc(0, common_time, None, groups, invalid_mask, scaletime=common_time)
        return dm1_data


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"\\corp.knorr-bremse.com\str\Measure\DAS\ConvertedMeas_Xcellis\FER\AEBS\F30\FMAX_5506\FC243202_FU242990\2024-12-11\mi5id5506__2024-12-11_15-14-13.h5"
    # meas_path = r"X:\eval_team\meas\conti\fcw\2020-08-17\FCW__2020-08-17_11-11-01.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    conti = manager_modules.calc('fill_flr25_dtc@aebs.fill', manager)
    print(conti)
