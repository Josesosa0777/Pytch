# -*- dataeval: init -*-

import numpy as np
import csv
import os

from interface import iSearch


class Search(iSearch):
  sgs = [
    {
        "TpfOutputIfMeas_sSigHeader_uiCycleCounter": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas",
        "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_sSigHeader_uiCycleCounter"),
        "LdOutput_sigHeader_uiCycleCounter": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_sigHeader_uiCycleCounter"),

    },
    {
      "TpfOutputIfMeas_sSigHeader_uiCycleCounter": ("CEM_FDP_KB_M_p_TpfOutputIfMeas",
      "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_TpfOutputIfMeas_sSigHeader_uiCycleCounter"),
      "LdOutput_sigHeader_uiCycleCounter": ("LdOutput", "MFC5xx_Device_LD_LdOutput_sigHeader_uiCycleCounter"),

    }
]
  
  def check(self):
    group = self.source.selectSignalGroup(self.sgs)
    return group

  def fill(self, group):

    TpfOutputIfMeas_uiCycleCounter_list = []
    TpfOutputIfMeas_uiCycleCounter_dict = {}

    LdOutput_uiCycleCounter_list = []
    LdOutput_uiCycleCounter_dict = {}

    field_names = ['Measurement_fileName', 'sampleTime(55ms-65ms)','sampleTime(110ms-130ms)','sampleTime(165ms-195ms)','sampleTime(220ms-260ms)',
                   'sampleTime(275ms-325ms)','sampleTime(330ms-390ms)','sampleTime(385ms-455ms)']

    TpfOutputIfMeas_csv_file_name = str(os.path.dirname(os.path.dirname(self.source.FileName)) + '\TpfOutputIfMeas_sSigHeader_uiCycleCounter.csv')
    LdOutput_csv_file_name = str(os.path.dirname(os.path.dirname(self.source.FileName)) + '\LdOutput_sigHeader_uiCycleCounter.csv')

    measurement_file_name = self.source.BaseName
    TpfOutputIfMeas_uiCycleCounter_time, TpfOutputIfMeas_uiCycleCounter_values, TpfOutputIfMeas_uiCycleCounter_unit = group.get_signal_with_unit("TpfOutputIfMeas_sSigHeader_uiCycleCounter")
    LdOutput_uiCycleCounter_time, LdOutput_uiCycleCounter_values, LdOutput_uiCycleCounter_unit = group.get_signal_with_unit(
        "LdOutput_sigHeader_uiCycleCounter")

    TpfOutputIfMeas_uiCycleCounter_dict['Measurement_fileName'] = measurement_file_name
    TpfOutputIfMeas_uiCycleCounter_dict['sampleTime(55ms-65ms)'] = np.sum(
        (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 > 55) & (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 < 65))
    TpfOutputIfMeas_uiCycleCounter_dict['sampleTime(110ms-130ms)'] = np.sum(
        (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 > 110) & (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 < 130))
    TpfOutputIfMeas_uiCycleCounter_dict['sampleTime(165ms-195ms)'] = np.sum(
        (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 > 165) & (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 < 195))
    TpfOutputIfMeas_uiCycleCounter_dict['sampleTime(220ms-260ms)'] = np.sum(
        (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 > 220) & (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 < 260))
    TpfOutputIfMeas_uiCycleCounter_dict['sampleTime(275ms-325ms)'] = np.sum(
        (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 > 275) & (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 < 325))
    TpfOutputIfMeas_uiCycleCounter_dict['sampleTime(330ms-390ms)'] = np.sum(
        (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 > 330) & (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 < 390))
    TpfOutputIfMeas_uiCycleCounter_dict['sampleTime(385ms-455ms)'] = np.sum(
        (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 > 385) & (np.diff(TpfOutputIfMeas_uiCycleCounter_time) * 1000 < 455))
    TpfOutputIfMeas_uiCycleCounter_list.append(TpfOutputIfMeas_uiCycleCounter_dict)

    with open(TpfOutputIfMeas_csv_file_name, 'a') as csvfile:
        file_is_empty = os.stat(TpfOutputIfMeas_csv_file_name).st_size == 0
        writer = csv.DictWriter(csvfile, fieldnames=field_names, lineterminator='\n')
        if file_is_empty:
            writer.writeheader()
        writer.writerows(TpfOutputIfMeas_uiCycleCounter_list)
        csvfile.close()

    LdOutput_uiCycleCounter_dict['Measurement_fileName'] = measurement_file_name
    LdOutput_uiCycleCounter_dict['sampleTime(55ms-65ms)'] = np.sum(
        (np.diff(LdOutput_uiCycleCounter_time) * 1000 > 55) & (
                    np.diff(LdOutput_uiCycleCounter_time) * 1000 < 65))
    LdOutput_uiCycleCounter_dict['sampleTime(110ms-130ms)'] = np.sum(
        (np.diff(LdOutput_uiCycleCounter_time) * 1000 > 110) & (
                    np.diff(LdOutput_uiCycleCounter_time) * 1000 < 130))
    LdOutput_uiCycleCounter_dict['sampleTime(165ms-195ms)'] = np.sum(
        (np.diff(LdOutput_uiCycleCounter_time) * 1000 > 165) & (
                    np.diff(LdOutput_uiCycleCounter_time) * 1000 < 195))
    LdOutput_uiCycleCounter_dict['sampleTime(220ms-260ms)'] = np.sum(
        (np.diff(LdOutput_uiCycleCounter_time) * 1000 > 220) & (
                    np.diff(LdOutput_uiCycleCounter_time) * 1000 < 260))
    LdOutput_uiCycleCounter_dict['sampleTime(275ms-325ms)'] = np.sum(
        (np.diff(LdOutput_uiCycleCounter_time) * 1000 > 275) & (
                    np.diff(LdOutput_uiCycleCounter_time) * 1000 < 325))
    LdOutput_uiCycleCounter_dict['sampleTime(330ms-390ms)'] = np.sum(
        (np.diff(LdOutput_uiCycleCounter_time) * 1000 > 330) & (
                    np.diff(LdOutput_uiCycleCounter_time) * 1000 < 390))
    LdOutput_uiCycleCounter_dict['sampleTime(385ms-455ms)'] = np.sum(
        (np.diff(LdOutput_uiCycleCounter_time) * 1000 > 385) & (
                    np.diff(LdOutput_uiCycleCounter_time) * 1000 < 455))
    LdOutput_uiCycleCounter_list.append(LdOutput_uiCycleCounter_dict)

    with open(LdOutput_csv_file_name, 'a') as csvfile:
        file_is_empty = os.stat(LdOutput_csv_file_name).st_size == 0
        writer = csv.DictWriter(csvfile, fieldnames=field_names, lineterminator='\n')
        if file_is_empty:
            writer.writeheader()
        writer.writerows(LdOutput_uiCycleCounter_list)
        csvfile.close()

    return
