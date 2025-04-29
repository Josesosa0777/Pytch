# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import csv
import logging
import os
import glob
import ConfigParser
from measparser.filenameparser import FileNameParser

from interface import iCalc

logger = logging.getLogger('calc_aebs_resim_output')

class cFill(iCalc):
    dep = ('calc_common_time-flr25',)

    def check(self):
        conf = ConfigParser.ConfigParser()
        CONFIG_PATH = os.path.join(os.path.dirname(__file__))
        conf.read(CONFIG_PATH.split('aebs')[0] + r"dataevalaebs\src\evalbot\botconfigs\config_templates\EnduranceRun_Conti_AEBS_delta_resim.cfg")
        try:
            csvPath = conf.get('csv json path', 'csvPath')
        except:
            logger.info("csv file is not available")
            pass
        source = self.get_source()
        directory_path = os.path.dirname(os.path.dirname(source.FileName))
        data = []
        column_names = []
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
                elif "_aebs" in file:
                    with open(file) as csv_files:
                        csv_file_object = csv.reader(csv_files)
                        column_list = next(csv_file_object)
                        column_names = column_list[0].split(";")

                        for row in csv_file_object:
                            data.append(row[0].split(";"))
        except:
            logger.error(
                "Resimulation output of AEB i.e csv file not found, Keep the csv file along with the measurement")

        return data, column_names, mileage_column_names, mileage_data

    def fill(self, data, column_names, mileage_column_names, mileage_data):
        time = self.modules.fill('calc_common_time-flr25')
        aebs_events = []
        total_mileage = 0.0

        if mileage_column_names:
            for value in mileage_data:
                # for index, key in enumerate(mileage_column_names):
                total_mileage = total_mileage + float(value[2])
        total_mileage = round(total_mileage, 2)
        for value in data:
            aebs_event = {}
            for index, key in enumerate(column_names):
                aebs_event[key] = value[index]
            aebs_events.append(aebs_event)

        return aebs_events, time, total_mileage


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\aebs_test\new_csv\testing\test\2021-04-29\mi5id5390__2021-04-29_06-48-08.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_common_time = manager_modules.calc('calc_aebs_resim_output@aebs.fill', manager)
    print (flr25_common_time)
