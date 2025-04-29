# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import glob
import json
import logging
import os
from os.path import expanduser

import interface

logger = logging.getLogger('')


class Calc(interface.iCalc):
    """
    iCalc class that reads the PAEBS parameters (i.e. parameter names and parameter values) defined in
    a .json file created by the user. These parameters are searched for as signals in the measurement file
    currently loaded in the module manager and the values recorded there are retrieved.
    The parameters actually found in the measurement file and their values stored there are saved in a
    temporary .json file in the user directory so that they can be read later by the report generator.
    The path to the .json file originally created by the user is specified in the configuration file and
    passed to the search modules by the Config Manager as a global parameter.
    The init, check, fill methods are called by the module manager when this module is included
    as a dependency in other iInterface classes.
    """

    dep = ('calc_common_time-flc25',)

    def init(self):
        try:
            self.JsonPath = self.global_params['json']
        except:
            self.JsonPath = ''
            logger.error('Resim output data have been retrieved without valid path to a .csv file '
                         'within module: {}.'.format(__name__))

    def check(self):
        # Params
        DEVICE = "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t"
        SIGNAL = 'MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_s'

        # Initialization
        signal_data = []
        signal_group = {}

        # Parse .json-File
        status_json_read = False
        try:
            jsonPath = self.JsonPath
            with open(jsonPath) as json_param_file:
                try:
                    resim_parameters = json.load(json_param_file)
                    status_json_read = True
                except AttributeError as exc:
                    logger.warning("Content of parameter .json file is not parsable!")
                except TypeError as exc:
                    logger.warning("Content of parameter .json file is not parsable!")
        except IOError as exc:
            logger.warning("Provided parameter .json file is not existing!")
        finally:
            if not status_json_read:
                resim_parameters = {}

        # Create Param Signal Group
        for key, val in resim_parameters.iteritems():
            if key != 'resim_framework':
                for param, value in val.iteritems():
                    signals = SIGNAL + key + '_' + param
                    signal_group[str(param)] = (DEVICE, str(signals))
        signal_data.append(signal_group)

        # Check Signal Validity from Measurement
        source = self.get_source()
        filtered, errors = source._filterSignalGroups(signal_data)
        group = source.selectSignalGroup(filtered)

        return filtered, group

    def fill(self, filtered, group):
        # Get Time Array
        time = self.modules.fill('calc_common_time-flc25')
        rescale_kwargs = {'ScaleTime': time}
        valid_signals = {}

        # Write temporary .json file with valid parameter name-value pairs
        for val in filtered:
            for key, value in val.iteritems():
                signal_time, signal_value, signal_unit = group.get_signal_with_unit(key, **rescale_kwargs)
                valid_signals[key] = str(signal_value[0])

        home_user_path = expanduser("~")
        json_file_path = (home_user_path + r'\measurement_valid_signals.json')

        with open(json_file_path, "w") as outfile:
            json.dump(valid_signals, outfile)

        return


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\paebs_evalresim\Fusion_AEBS_aResimulation_Helios\measurements\2022-04-08\mi5id5033__2022-04-08_09-19-14.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_common_time = manager_modules.calc('calc_delta_create_json@aebs.fill', manager)
    print flr25_common_time
