# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import json
import glob
import os
from os.path import expanduser

import logging
import interface
import ConfigParser


class Calc(interface.iCalc):
	dep = ('calc_common_time-flc25',)

	def check(self):
		signal_data = []
		signal_group = {}
		jsonPath = ''
		device_name = "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t"
		signal_name = 'MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_s'

		logger = logging.getLogger('')
		conf = ConfigParser.ConfigParser()
		CONFIG_PATH = os.path.join(os.path.dirname(__file__))
		conf.read(CONFIG_PATH.split('aebs')[0] + r"dataevalaebs\src\evalbot\botconfigs\config_templates\EnduranceRun_Conti_AEBS_delta_resim.cfg")

		try:
			jsonPath = conf.get('csv json path', 'jsonPath')
		except:
			logger.info("json file is not available")
		json_param_files = open(glob.glob((os.path.join(jsonPath, '*.json')))[0])

		resim_parameters = json.load(json_param_files)

		for key, val in resim_parameters.iteritems():
			if key != 'resim_framework':
				for param, value in val.iteritems():
					signals = signal_name + key + '_' + param
					signal_group[str(param)] = (device_name, str(signals))
		signal_data.append(signal_group)
		source = self.get_source()
		filtered, errors = source._filterSignalGroups(signal_data)
		group = source.selectSignalGroup(filtered)

		return filtered, group

	def fill(self, filtered, group):
		time = self.modules.fill('calc_common_time-flc25')
		rescale_kwargs = {'ScaleTime': time}
		valid_signals = {}

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
