# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
"""
For Ford truck data TSRAlone signals are need to be use for EU&TUR instaed CAN signals

CAN Signals which should be displayed in Report for EU & TUR:

PropTSRAlone.TSRSpeedLimit1
PropTSRAlone.TSRSpeedLimit1Supplementary
PropTSRAlone.TSRSpeedLimit2
PropTSRAlone.TSRSpeedLimitElectronic
PropTSRAlone.TSRNoPassingRestriction
PropTSRAlone.TSR_CountryCode_E8_sE8"

"""

import os
import sys

import numpy as np

from interface import iCalc
from measproc.IntervalList import maskToIntervals

sgs = [

    {
        "TSR_SpeedLimit1_E8_sE8": ("PropTSRAlone_E8", "TSR_SpeedLimit1_E8_sE8"),
        "TSR_SpeedLimit1Supplementary_E8_sE8": ("PropTSRAlone_E8", "TSR_SpeedLimit1Supplementary_E8_sE8"),
        "TSR_SpeedLimit2_E8_sE8": ("PropTSRAlone_E8", "TSR_SpeedLimit2_E8_sE8"),
        "TSR_SpeedLimitElectronic_E8_sE8": ("PropTSRAlone_E8", "TSR_SpeedLimitElectronic_E8_sE8"),
        "TSR_NoPassingRestriction_E8_sE8": ("PropTSRAlone_E8", "TSR_NoPassingRestriction_E8_sE8"),
        "TSR_CountryCode_E8_sE8": ("PropTSRAlone_E8","TSR_CountryCode_E8_sE8"),
    }

]


class cFill(iCalc):

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        tsr_alone_signals = {}
        if 'TSR_SpeedLimit1Supplementary_E8_sE8' in group:
            tsr_alone_signals['TSR_SpeedLimit1Supplementary_E8_sE8'] = group.get_signal('TSR_SpeedLimit1Supplementary_E8_sE8')

        if 'TSR_SpeedLimit2_E8_sE8' in group:
            tsr_alone_signals['TSR_SpeedLimit2_E8_sE8'] = group.get_signal('TSR_SpeedLimit2_E8_sE8')

        if 'TSR_SpeedLimitElectronic_E8_sE8' in group:
            tsr_alone_signals['TSR_SpeedLimitElectronic_E8_sE8'] = group.get_signal('TSR_SpeedLimitElectronic_E8_sE8')

        if 'TSR_NoPassingRestriction_E8_sE8' in group:
            tsr_alone_signals['TSR_NoPassingRestriction_E8_sE8'] = group.get_signal('TSR_NoPassingRestriction_E8_sE8')

        if 'TSR_CountryCode_E8_sE8' in group:
            tsr_alone_signals['TSR_CountryCode_E8_sE8'] = group.get_signal('TSR_CountryCode_E8_sE8')

        if 'TSR_SpeedLimit1_E8_sE8' in group:
            time, values = group.get_signal('TSR_SpeedLimit1_E8_sE8')
            # tsr_alone_signals['SpeedLimit1']
            masked_values = (values == 0) | (values == 33) | (values == 34) | (values == 37) | (values == 38) | (values == 39) | (values == 41) | (values == 40) | (values == 62) | (values == 63)

            masked_values_intervals = maskToIntervals(masked_values)
            new_speedlimit_values = values
            new_speedlimit_values.flags['WRITEABLE'] = True
            for start, end in masked_values_intervals:
                new_speedlimit_values[start:end] = 0

            # arr =new_speedlimit_values
            #
            # mapping = {1: "5", 2: "10", 3: "15", 4: "20", 5: "25", 6: "30", 7: "35", 8: "40", 9: '45', 10: "50", 11: "55",
            #            12: "60", 13: "65", \
            #            14: "70", 15: "75", 16: "80", 17: "85", 18: "90", 19: "95", 20: "100", 21: "105", 22: "110",
            #            23: "115", 24: "120", 25: "125", \
            #            26: "130", 27: "135", 28: "140", 29: "282", 30: "282", 31: "310", 32: "311", 35: "331", 36: "336"}
            #
            # for val in mapping.keys():
            #     idx = np.where(new_speedlimit_values == val)
            #     if len(idx[0]) != 0:
            #         new_speedlimit_values[idx[0][0]:(idx[0][-1] + 1)] = mapping[val]


            tsr_alone_signals['TSR_SpeedLimit1_E8_sE8'] = time, new_speedlimit_values

        return tsr_alone_signals


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\TSR\Ford_KBKPI_EU_Turkey\measurement\2022-08-02\mi5id5461__2022-08-02_11-19-29_tsrresim.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_common_time = manager_modules.calc('Calc_PropTSRAlone@aebs.fill', manager)
    print flr25_common_time
