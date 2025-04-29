# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import csv
import glob
import logging
import os
import openpyxl

from interface import iCalc

logger = logging.getLogger('calc_database_hits_from_yaca')


class cFill(iCalc):
    dep = ('calc_common_time-flr25',)

    def check(self):
        source = self.get_source()
        directory_path = os.path.dirname(os.path.dirname(source.FileName))
        data = []
        column_names = []
        excel_data = []
        excel_column = []

        csv_file = glob.glob((os.path.join(directory_path, '*.csv')))

        excel_file = glob.glob((os.path.join(directory_path, '*.xlsx')))

        try:
            for file in csv_file:
                logger.warning("Reading database hits from {} file".format(file))
                with open(file) as csv_files:
                    csv_file_object = csv.reader(csv_files)
                    column_list = next(csv_file_object)
                    column_names = [col.strip() for col in column_list]

                    for row in csv_file_object:
                        data.append(row)

            if excel_file is not None:
                workbook = openpyxl.load_workbook(excel_file[0])
                sheet = workbook.active

                for i, row_data in enumerate(sheet.iter_rows(values_only=True)):
                    if i == 0:
                        excel_column =list(row_data)
                    else:
                        excel_data.append(list(row_data))
        except:
            logger.error(
                "YACA database hits csv not found.")

        return data, column_names, excel_data, excel_column

    def fill(self, data, column_names, excel_data, excel_column):
        time = self.modules.fill('calc_common_time-flr25')
        yaca_hits = []

        for value in data:
            aebs_event = {}
            for index, key in enumerate(column_names):
                aebs_event[key] = value[index]
            yaca_hits.append(aebs_event)

        yaca_hits_database = []
        for values in excel_data:
            events = {}
            for index, key in enumerate(excel_column):
                events[key] = values[index]
            yaca_hits_database.append(events)

        for id, value in enumerate(yaca_hits_database):
            if yaca_hits_database[id]['CanBasename'] == yaca_hits[id]['DateTime']:
                yaca_hits[id]['Verdict'] = str(yaca_hits_database[id]['Verdict'])
                yaca_hits[id]['Status'] = str(yaca_hits_database[id]['Status'])

        return yaca_hits, time


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path =r"C:\KBData\Measurement\bendix_requirment\sample_meas\2021-05-24\2021.05.24_at_09.49.10_radar-mi_5031.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_common_time = manager_modules.calc('calc_database_hits_from_yaca@aebs.fill', manager)
    print (flr25_common_time)


