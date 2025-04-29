# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import csv
import logging
import os
import glob
import ConfigParser
from measparser.filenameparser import FileNameParser

from interface import iCalc

logger = logging.getLogger('calc_aebs_resim2resim_output')


class cFill(iCalc):
    dep = ('calc_common_time-flr25',)

    def check(self):
        conf = ConfigParser.ConfigParser()
        CONFIG_PATH = os.path.join(os.path.dirname(__file__))
        conf.read(CONFIG_PATH.split('aebs')[0] + r"dataevalaebs\src\evalbot\botconfigs\config_templates\EnduranceRun_Conti_AEBS_delta_resim2resim.cfg")
        try:
            csvPath = conf.get('csv json path', 'csvPath')
        except:
            logger.info("csv file is not available")
            pass

        baseline_csv_data = []
        retest_csv_data = []
        baseline_csv_column_headers = []
        retest_csv_column_headers = []
        mileage_data = []
        mileage_column_names = []

        csv_file = glob.glob((os.path.join(csvPath, '*.csv')))
        try:
            for file in csv_file:
                if "mileage" in file:
                    with open(file) as csv_files:
                        csv_file_object = csv.reader(csv_files)
                        column_list = next(csv_file_object)
                        mileage_column_names = column_list[0].split(";")

                        for row in csv_file_object:
                            mileage_data.append(row[0].split(";"))
                else:
                    if baseline_csv_data:
                        with open(file) as csv_files:
                            csv_file_object = csv.reader(csv_files)
                            column_list = next(csv_file_object)
                            retest_csv_column_headers = column_list[0].split(";")

                            for row in csv_file_object:
                                retest_csv_data.append(row[0].split(";"))
                    else:
                        with open(file) as csv_files:
                            csv_file_object = csv.reader(csv_files)
                            column_list = next(csv_file_object)
                            baseline_csv_column_headers = column_list[0].split(";")

                            for row in csv_file_object:
                                baseline_csv_data.append(row[0].split(";"))
        except:
            logger.error("csv file not found.")

        return baseline_csv_data, baseline_csv_column_headers, retest_csv_data, retest_csv_column_headers, mileage_column_names, mileage_data

    def fill(self, baseline_csv_data, baseline_csv_column_headers, retest_csv_data, retest_csv_column_headers, mileage_column_names, mileage_data):
        time = self.modules.fill('calc_common_time-flr25')
        baseline_aebs_events = []
        retest_aebs_events = []
        resim_events = {}
        total_mileage = 0.0

        if mileage_column_names:
            for value in mileage_data:
                # for index, key in enumerate(mileage_column_names):
                total_mileage = total_mileage + float(value[2])
        total_mileage = round(total_mileage, 2)
        for value in baseline_csv_data:
            aebs_event = {}
            for index, key in enumerate(baseline_csv_column_headers):
                aebs_event[key] = value[index]
            baseline_aebs_events.append(aebs_event)
        resim_events['baseline_aebs_events'] =baseline_aebs_events

        # Read data for second csv file
        for value in retest_csv_data:
            aebs_event = {}
            for index, key in enumerate(retest_csv_column_headers):
                aebs_event[key] = value[index]
            retest_aebs_events.append(aebs_event)
        resim_events['retest_aebs_events'] = retest_aebs_events

        return baseline_aebs_events, retest_aebs_events, time, total_mileage


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\aebs_test\resim_2resim_report_generation\testing_files\2021-04-28\mi5id5390__2021-04-28_10-51-40.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_common_time = manager_modules.calc('calc_aebs_resim2resim_output@aebs.fill', manager)
    print (flr25_common_time)
