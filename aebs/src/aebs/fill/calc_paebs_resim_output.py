# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import csv
import logging

from interface import iCalc

logger = logging.getLogger('')


class cFill(iCalc):
    """
    iCalc class that reads the PAEBS resimulation output/result values defined in
    two .csv files provided by the user.
    For this, the user can specify the two paths in the configuration file, which are then passed to the search modules
    by the Config Manager as a global parameter.
    A .csv file contains the values for the miles driven, which are totaled after they have been read out.
    The other .csv contains the results of the resimulation which are processed and returned together
    with the value for the miles driven.
    The init, check, fill methods are called by the module manager when this module is included
    as a dependency in other iInterface classes.
    """

    dep = ('calc_common_time-flr25',)

    def init(self):
        try:
            self.csvResimOutPath = self.global_params['csvResimOutPath']
            self.csvMileagePath = self.global_params['csvMileagePath']
        except:
            self.CsvPath = ''
            self.csvMileagePath = ''
            logger.error('Resim output data have been retrieved without valid path to a .csv file '
                         'within module: {}.'.format(__name__))

    def check(self):
        # Initialization
        if not self.csvResimOutPath or not self.csvMileagePath:
            logger.info("At least one .csv file path is not available.")
            pass
        data = []
        column_names = []
        mileage_data = []
        mileage_column_names = []

        # Read Mileage .csv file
        try:
            with open(self.csvMileagePath) as mileage_file:
                csv_file_object = csv.reader(mileage_file)
                column_list = next(csv_file_object)
                mileage_column_names = column_list[0].split(";")

                for row in csv_file_object:
                    mileage_data.append(row[0].split(";"))

        except IOError as exc:
            logger.warning('Failed to read mileage data from provided .csv-file.')

        # Read Resim Output .csv file
        try:
            with open(self.csvResimOutPath) as resim_file:
                csv_file_object = csv.reader(resim_file)
                column_list = next(csv_file_object)
                column_names = column_list[0].split(";")

                for row in csv_file_object:
                    data.append(row[0].split(";"))

        except IOError as exc:
            logger.error(
                "Resimulation output of PAEBS (.csv file) not found, check the provided path in the config file.")

        return data, column_names, mileage_column_names, mileage_data

    def fill(self, data, column_names, mileage_column_names, mileage_data):

        # Initialization
        paebs_events = []
        total_mileage = 0.0

        # Fetch Time Array
        time = self.modules.fill('calc_common_time-flr25')

        # Cumulate Miles
        if mileage_column_names:
            for value in mileage_data:
                total_mileage = total_mileage + float(value[2])
        total_mileage = round(total_mileage, 2)

        # Process Resim Output Data
        for value in data:
            paebs_event = {}
            for index, key in enumerate(column_names):
                paebs_event[key] = value[index]
            paebs_events.append(paebs_event)

        return paebs_events, time, total_mileage


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\paebs_evalresim\Fusion_AEBS_aResimulation_Helios\measurements\2022-04-07\mi5id5033__2022-04-07_08-20-21.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_common_time = manager_modules.calc('calc_paebs_resim_output@aebs.fill', manager)
    print (flr25_common_time)
