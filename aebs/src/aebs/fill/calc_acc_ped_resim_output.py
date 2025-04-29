# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import csv
import logging
import os
import glob
from measparser.filenameparser import FileNameParser

from interface import iCalc

logger = logging.getLogger('calc_acc_ped_resim_output')

class cFill(iCalc):
    dep = ('calc_common_time-flr25',)

    def check(self):
        source = self.get_source()
        directory_path = os.path.dirname(os.path.dirname(source.FileName))
        data = []
        column_names = []

        csv_file = glob.glob(os.path.join(directory_path, '*.csv'))
        try:
            for file in csv_file:
                with open(file) as csv_files:
                    csv_file_object = csv.reader(csv_files)
                    column_list = next(csv_file_object)
                    column_names = column_list[0].split(";")

                    for row in csv_file_object:
                        data.append(row[0].split(";"))
        except:
            logger.error(
                "Resimulation output of ACC ped i.e csv file not found, Keep the csv file along with the measurement")

        return data, column_names

    def fill(self, data, column_names):
        time = self.modules.fill('calc_common_time-flr25')
        acc_ped_events = []

        for value in data:
            acc_ped_event = {}
            for index, key in enumerate(column_names):
                acc_ped_event[key] = value[index]
            acc_ped_events.append(acc_ped_event)

        return acc_ped_events, time


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\oliver_endurance_run\2021-04-21\mi5id787__2021-04-21_13-07-33.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_common_time = manager_modules.calc('calc_acc_ped_resim_output@aebs.fill', manager)
    print (flr25_common_time)
