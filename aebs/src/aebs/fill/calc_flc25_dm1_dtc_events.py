# -*- dataeval: init -*-
import numpy as np
from interface import iCalc


class cFill(iCalc):
    dep = ('fill_flc25_dtc')

    def check(self):
        modules = self.get_modules()
        dm1_data = modules.fill("fill_flc25_dtc")
        return dm1_data

    def fill(self, dm1_data):

        timestamps = dm1_data.time
        dm1_info_struct = {}
        dm1_info_struct['AmberWarningLamp'] = dm1_data.AmberWarningLamp
        dm1_info_struct['DTC1'] = dm1_data.DM1_DTC1
        dm1_info_struct['DTC2'] = dm1_data.DM1_DTC2
        dm1_info_struct['DTC3'] = dm1_data.DM1_DTC3
        dm1_info_struct['DTC4'] = dm1_data.DM1_DTC4
        dm1_info_struct['DTC5'] = dm1_data.DM1_DTC5
        dm1_info_struct['dtc_occurence_cntr1'] = dm1_data.DM1_OccuranceCount1
        dm1_info_struct['dtc_occurence_cntr2'] = dm1_data.DM1_OccuranceCount2
        dm1_info_struct['dtc_occurence_cntr3'] = dm1_data.DM1_OccuranceCount3
        dm1_info_struct['dtc_occurence_cntr4'] = dm1_data.DM1_OccuranceCount4
        dm1_info_struct['dtc_occurence_cntr5'] = dm1_data.DM1_OccuranceCount5

        dtc1 = np.concatenate((np.array([0]), np.where(dm1_data.DM1_DTC1[:-1] != dm1_data.DM1_DTC1[1:])[0] + 1), axis=0)
        dtc2 = np.concatenate((np.array([0]), np.where(dm1_data.DM1_DTC2[:-1] != dm1_data.DM1_DTC2[1:])[0] + 1), axis=0)
        dtc3 = np.concatenate((np.array([0]), np.where(dm1_data.DM1_DTC3[:-1] != dm1_data.DM1_DTC3[1:])[0] + 1), axis=0)
        dtc4 = np.concatenate((np.array([0]), np.where(dm1_data.DM1_DTC4[:-1] != dm1_data.DM1_DTC4[1:])[0] + 1), axis=0)
        dtc5 = np.concatenate((np.array([0]), np.where(dm1_data.DM1_DTC5[:-1] != dm1_data.DM1_DTC5[1:])[0] + 1), axis=0)

        dtc_history = []
        dtc_history_ts = []
        for indice in dtc1:
            current_dtc = []
            dtc_check = []
            dtc_check.append(int(dm1_data.DM1_DTC1[indice]))
            dtc_check.append(int(dm1_data.DM1_OccuranceCount1[indice]))
            current_dtc.append(int(dm1_data.DM1_DTC1[indice]))
            current_dtc.append(int(dm1_data.DM1_OccuranceCount1[indice]))
            current_dtc.append(timestamps[indice])
            current_dtc.append(indice)
            if dtc_check not in dtc_history:
                dtc_history.append(dtc_check)
                dtc_history_ts.append(current_dtc)

        for indice in dtc2:
            current_dtc = []
            dtc_check = []
            dtc_check.append(int(dm1_data.DM1_DTC2[indice]))
            dtc_check.append(int(dm1_data.DM1_OccuranceCount2[indice]))
            current_dtc.append(int(dm1_data.DM1_DTC2[indice]))
            current_dtc.append(int(dm1_data.DM1_OccuranceCount2[indice]))
            current_dtc.append(timestamps[indice])
            current_dtc.append(indice)
            if dtc_check not in dtc_history:
                dtc_history.append(dtc_check)
                dtc_history_ts.append(current_dtc)

        for indice in dtc3:
            current_dtc = []
            dtc_check = []
            dtc_check.append(int(dm1_data.DM1_DTC3[indice]))
            dtc_check.append(int(dm1_data.DM1_OccuranceCount3[indice]))
            current_dtc.append(int(dm1_data.DM1_DTC3[indice]))
            current_dtc.append(int(dm1_data.DM1_OccuranceCount3[indice]))
            current_dtc.append(timestamps[indice])
            current_dtc.append(indice)
            if dtc_check not in dtc_history:
                dtc_history.append(dtc_check)
                dtc_history_ts.append(current_dtc)

        for indice in dtc4:
            current_dtc = []
            dtc_check = []
            dtc_check.append(int(dm1_data.DM1_DTC4[indice]))
            dtc_check.append(int(dm1_data.DM1_OccuranceCount4[indice]))
            current_dtc.append(int(dm1_data.DM1_DTC4[indice]))
            current_dtc.append(int(dm1_data.DM1_OccuranceCount4[indice]))
            current_dtc.append(timestamps[indice])
            current_dtc.append(indice)
            if dtc_check not in dtc_history:
                dtc_history.append(dtc_check)
                dtc_history_ts.append(current_dtc)

        for indice in dtc5:
            current_dtc = []
            dtc_check = []
            dtc_check.append(int(dm1_data.DM1_DTC5[indice]))
            dtc_check.append(int(dm1_data.DM1_OccuranceCount5[indice]))
            current_dtc.append(int(dm1_data.DM1_DTC5[indice]))
            current_dtc.append(int(dm1_data.DM1_OccuranceCount5[indice]))
            current_dtc.append(timestamps[indice])
            current_dtc.append(indice)
            if dtc_check not in dtc_history:
                dtc_history.append(dtc_check)
                dtc_history_ts.append(current_dtc)

        dtc_history_ts = sorted(dtc_history_ts, key=lambda x: x[2])
        invalid_dtc_id = 0
        for dtc in dtc_history_ts:
            if invalid_dtc_id == dtc[0]:
                dtc_history_ts.remove(dtc)
        dm1_info_struct['dtc_history'] = dtc_history_ts
        dm1_info_struct['dtc_counter'] = dm1_data.get_unique_dtc_counts

        return timestamps, dm1_info_struct


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r'\\corp.knorr-bremse.com\str\Measure\DAS\ConvertedMeas_Xcellis\FER\AEBS\F30\FMAX_5506\FC232295_FU232260\2023-08-21\mi5id5506__2023-08-21_18-08-06.h5'
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_flc25_dm1__dtc_events@aebs.fill', manager)