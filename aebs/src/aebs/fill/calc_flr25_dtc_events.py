# -*- dataeval: init -*-
import numpy as np
from interface import iCalc


class cFill(iCalc):
	dep = ('fill_flr25_dtc', 'fill_flr25_dem_chronostack',)

	def check(self):
		modules = self.get_modules()
		dm1_data = modules.fill("fill_flr25_dtc")
		dem_event_data = modules.fill("fill_flr25_dem_chronostack")
		return dm1_data, dem_event_data

	def fill(self, dm1_data, dem_event_data):

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

		def get_active_dem_events(indice):
			dem_events = '1'
			for k, dem in dem_event_data.items():
				if dem.EventStatusEx[indice] % 2:
					dem_events = dem_events + '%03d' % dem.EventId[indice]
					#dem_events.append(dem.EventId[indice])
					#dem_events.append((k, dem.EventId[indice]))
			return dem_events

		#dtc1 = np.concatenate((np.array([0]),np.where(dm1_data.DM1_DTC1[:-1] != dm1_data.DM1_DTC1[1:])[0]+1),axis=0)
		#dtc1_vals = dm1_data.DM1_DTC1[dtc1]

		dtc1 = np.concatenate((np.array([0]),np.where(dm1_data.DM1_DTC1[:-1] != dm1_data.DM1_DTC1[1:])[0]+1),axis=0)
		dtc2 = np.concatenate((np.array([0]),np.where(dm1_data.DM1_DTC2[:-1] != dm1_data.DM1_DTC2[1:])[0]+1),axis=0)
		dtc3 = np.concatenate((np.array([0]),np.where(dm1_data.DM1_DTC3[:-1] != dm1_data.DM1_DTC3[1:])[0]+1),axis=0)
		dtc4 = np.concatenate((np.array([0]),np.where(dm1_data.DM1_DTC4[:-1] != dm1_data.DM1_DTC4[1:])[0]+1),axis=0)
		dtc5 = np.concatenate((np.array([0]),np.where(dm1_data.DM1_DTC5[:-1] != dm1_data.DM1_DTC5[1:])[0]+1),axis=0)

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
			current_dtc.append(get_active_dem_events(indice))
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
			current_dtc.append(get_active_dem_events(indice))
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
			current_dtc.append(get_active_dem_events(indice))
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
			current_dtc.append(get_active_dem_events(indice))
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
			current_dtc.append(get_active_dem_events(indice))
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
		dm1_info_struct['valid_warning_mask'] = dm1_data.AmberWarningLamp > 0

		return timestamps, dm1_info_struct