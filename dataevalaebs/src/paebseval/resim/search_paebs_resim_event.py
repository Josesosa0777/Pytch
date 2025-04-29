# -*- dataeval: init -*-

"""
:Name:
	search_detect_event.py
:Type:
	Search script

:Full Path:
	dataevalaebs/src/aebseval/resim/search_detect_event.py

:Sensors:
	FLR25

:Short Description:
	Resimulation is the procedure where user take .rrec measurement file as input and with new AEBS function checkpoint or parameter set and perform resimulation.
	It outputs .csv file which contains information about events , detected object attribute information and ego vehicle related information. This .csv file is used
	to perform resimulation endurance run in and this script will basically compare measurement endurance run events with .csv resimulation event.
	Categories:
	- If event detected in resimulation .csv file and not in measurement endurance run then it will be classified as "Resimulation Event".
	- If event detected by resimulation process and event detected by mesaurement endurance run is same (comparision based on event timestamps) then it is classified as "Common Event".
	- If event is only detected by measurement endurance run and not by resimulation process then it is classified as "Measurement Event".

:Large Description:
	Usage:
		- To compare mesurement event data with resimulation event.
		- Stores all such events in the database
	.. image:: ../images/search_detect_event_1.png

:Dependencies:
	- calc_radar_aebs_phases-flr25@aebs.fill
	- calc_aebs_resim_output@aebs.fill
	- set_egospeed-start@egoeval
	- set_flr25_aeb_track@trackeval

:Output Data Image/s:
	.. image:: ../images/search_detect_event_2.png
	.. image:: ../images/search_detect_event_3.png
	.. image:: ../images/search_detect_event_4.png


:Event:
    - PAEBS warnings
    - PAEBS Delta Event

:Event Labels:
    - Resimulation Event
    - Measurement Event

:Event Values:
    idx, 'ego vehicle', 'speed start', float(speed)

.. note::
    For source code click on [source] tag beside functions
"""

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report
from measparser.filenameparser import FileNameParser
import numpy as np

init_params = {
    'flc25': dict(
        phases='calc_paebs_phases-flc25@aebs.fill',
        paebs_resim='calc_paebs_resim_output@aebs.fill',
        delta_json='calc_paebs_delta_create_json@aebs.fill',
        algo='FLC25 Warning',
        opt_dep={
            'egospeedstart': 'set_egospeed-start@egoeval',
		    'paebtrack': 'set_paeb_track@trackeval',
        }
    ),
}

mps2kph = lambda v: v*3.6

COMMON_EVENT_FLAG = False
ACTIVATE_FLAG = False
EVENT_START_TIME_DIFF = 0.0

class Search(iSearch):
    dep = {
        'phases': None,  # TBD in init()
    }
    optdep = None

    def init(self, phases, paebs_resim, delta_json, algo, opt_dep):
        self.optdep = opt_dep
        self.dep['phases'] = phases
        self.dep['paebs_resim'] = paebs_resim
        self.dep['delta_json'] = delta_json
        self.algo = algo
        return

    def fill(self):
        phases = self.modules.fill(self.dep['phases'])
        delta_json_file = self.modules.fill(self.dep['delta_json'])

        paebs_resim_event, time, total_mileage = self.modules.fill(self.dep['paebs_resim'])

        phase_votes = 'PAEBS cascade phase'
        paebs_resim_data = 'PAEBS resim phase'
        algo_votes = 'PAEBS algo'
        delta_data = 'Delta report data'
        votes = self.batch.get_labelgroups(phase_votes, algo_votes, paebs_resim_data, delta_data)

        exclusive, cascade_phases = votes[phase_votes]

        # AEBS Endurance Run
        levels = 5
        jumps, warnings = phases.merge_phases(levels)
        if warnings:
            report = Report(cIntervalList(phases.time), 'PAEBS warnings', votes=votes)
        else:
            report = Report(cIntervalList(phases.time), 'PAEBS Delta Event', votes=votes)

        for jump, interval in zip(jumps, warnings):
            idx = report.addInterval(interval)
            report.vote(idx, algo_votes, self.algo)
            report.vote(idx, phase_votes, cascade_phases[len(jump) - 1])

        for qua in 'egospeedstart', 'paebtrack':
            if self.optdep[qua] in self.passed_optdep:
                set_qua_for_report = self.modules.get_module(self.optdep[qua])
                set_qua_for_report(report)
            else:
                self.logger.warning("Inactive module: %s" % self.optdep[qua])

        # AEBS Resim Calculation
        try:
            measurement_file_name = FileNameParser(self.source.BaseName).date_underscore
        except:
            measurement_file_name = self.source.BaseName.replace('.', '-').replace('_at_', '_').rsplit('_', 2)[0]

        paebs_resim_valid_data = self.data_preprocessing(measurement_file_name, paebs_resim_event)

        paebs_resim_jumps = []
        paebs_resim_warnings = []
        type_of_event = []
        ego_speed = []
        threshold_value_to_compare_events = 4
        for item in paebs_resim_valid_data:
            interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), phases.time)
            paebs_resim_jumps.append([interval[0]])
            paebs_resim_warnings.append((interval[0], interval[1]))
            type_of_event.append(item["event type"])
            if 'ego_velocity_x' in item:
                ego_speed.append(item['ego_velocity_x'])
            elif 'ego_velocity_x_start' in item:
                ego_speed.append(item['ego_velocity_x_start'])

            # Common Event Calculation
        common_event, paebs_resim_warning_data, paebs_warning_data = self.match(warnings, paebs_resim_warnings, threshold_value_to_compare_events, phases.time)
        id = 0
        for resim_event_category,event_type  in zip(common_event, type_of_event):
            global COMMON_EVENT_FLAG
            COMMON_EVENT_FLAG = True
            report.vote(id, delta_data, "Common\n Event")

            if event_type == '0':
                report.vote(id, paebs_resim_data, "warning,\n crossing")
                report.set(id, 'ego vehicle', 'mileage', float(total_mileage))
                report.set(id, 'ego vehicle', 'event start time diff', EVENT_START_TIME_DIFF)
                id = id + 1
            elif event_type == '1':
                report.vote(id, paebs_resim_data, "partial braking,\n crossing")
                report.set(id, 'ego vehicle', 'mileage', float(total_mileage))
                report.set(id, 'ego vehicle', 'event start time diff', EVENT_START_TIME_DIFF)
                id = id + 1
            elif event_type == '2':
                report.vote(id, paebs_resim_data, "emergency braking,\n crossing")
                report.set(id, 'ego vehicle', 'mileage', float(total_mileage))
                report.set(id, 'ego vehicle', 'event start time diff', EVENT_START_TIME_DIFF)
                id = id + 1
            elif event_type == '3':
                report.vote(id, paebs_resim_data, "warning,\n not crossing")
                report.set(id, 'ego vehicle', 'mileage', float(total_mileage))
                report.set(id, 'ego vehicle', 'event start time diff', EVENT_START_TIME_DIFF)
                id = id + 1
            elif event_type == '4':
                report.vote(id, paebs_resim_data, "partial braking,\n not crossing")
                report.set(id, 'ego vehicle', 'mileage', float(total_mileage))
                report.set(id, 'ego vehicle', 'event start time diff', EVENT_START_TIME_DIFF)
                id = id + 1
            elif event_type == '5':
                report.vote(id, paebs_resim_data, "emergency braking,\n not crossing")
                report.set(id, 'ego vehicle', 'mileage', float(total_mileage))
                report.set(id, 'ego vehicle', 'event start time diff', EVENT_START_TIME_DIFF)
                id = id + 1

            # COMMON_EVENT_FLAG = False

        for jump, interval, event_type, speed in zip(paebs_resim_jumps, paebs_resim_warnings, type_of_event, ego_speed):
            idx = report.addInterval(interval)
            report.vote(idx, delta_data, "Resimulation\n Event")
            # report.vote(idx, algo_votes, algo)
            if event_type == '0':
                report.vote(idx, paebs_resim_data, "warning,\n not crossing")
                report.set(idx, 'ego vehicle', 'speed start', float(speed))
                report.set(idx, 'ego vehicle', 'mileage', float(total_mileage))
            elif event_type == '1':
                report.vote(idx, paebs_resim_data, "partial braking,\n not crossing")
                report.set(idx, 'ego vehicle', 'speed start', float(speed))
                report.set(idx, 'ego vehicle', 'mileage', float(total_mileage))
            elif event_type == '2':
                report.vote(idx, paebs_resim_data, "emergency braking,\n not crossing")
                report.set(idx, 'ego vehicle', 'speed start', float(speed))
                report.set(idx, 'ego vehicle', 'mileage', float(total_mileage))
            elif event_type == '3':
                report.vote(idx, paebs_resim_data, "warning,\n crossing")
                report.set(idx, 'ego vehicle', 'speed start', float(speed))
                report.set(idx, 'ego vehicle', 'mileage', float(total_mileage))
            elif event_type == '4':
                report.vote(idx, paebs_resim_data, "partial braking,\n crossing")
                report.set(idx, 'ego vehicle', 'speed start', float(speed))
                report.set(idx, 'ego vehicle', 'mileage', float(total_mileage))
            elif event_type == '5':
                report.vote(idx, paebs_resim_data, "emergency braking,\n crossing")
                report.set(idx, 'ego vehicle', 'speed start', float(speed))
                report.set(idx, 'ego vehicle', 'mileage', float(total_mileage))

        for id_3, resim_event_category in enumerate(paebs_warning_data):
            if COMMON_EVENT_FLAG:
                id_3 = id_3 + 1
            report.vote(id_3, delta_data, "Measurement\n Event")
            report.set(id_3, 'ego vehicle', 'mileage', float(total_mileage))

        return report

    def data_preprocessing(self,measurement_file_name,paebs_resim_event):
        valid_data_from_csv = []
    
        for rows_from_resim_csv in paebs_resim_event:
            measurement_name_from_csv = ""
            if 'camera' in rows_from_resim_csv['Measurement File']:
                measurement_name_from_csv = rows_from_resim_csv['Measurement File'].replace('.', '-').split('_camera')[0].replace('_at_', '_')
            elif 'radar' in rows_from_resim_csv['Measurement File']:
                measurement_name_from_csv = rows_from_resim_csv['Measurement File'].replace('.', '-').split('_radar')[0].replace('_at_', '_')
            if measurement_name_from_csv == measurement_file_name:
                valid_data_from_csv.append(rows_from_resim_csv)
        return valid_data_from_csv

    def get_index(self, interval, time):
        st_time, ed_time = interval
        st_time = st_time / 1000000.0
        ed_time = ed_time / 1000000.0
        start_index = (np.abs(time - st_time)).argmin()
        end_index = (np.abs(time - ed_time)).argmin()
        if start_index == end_index:
            end_index += 1
        return (start_index, end_index)

    def match(self, paebs_warning, resim_warning, threshold, time):
        common_events = []
        global ACTIVATE_FLAG
        if len(paebs_warning) > len(resim_warning):
            warnings_collection_1 = paebs_warning
            warnings_collection_2 = resim_warning
            ACTIVATE_FLAG = True
        else:
            warnings_collection_1 = resim_warning
            warnings_collection_2 = paebs_warning
            ACTIVATE_FLAG = False

        for i, warning_data_1 in enumerate(warnings_collection_1):
            resim_st, resim_ed = warning_data_1
            for j, warning_data_2 in enumerate(warnings_collection_2):
                aebs_st, paebs_ed = warning_data_2

                if abs(time[resim_st] - time[aebs_st]) <= threshold and abs(time[resim_ed] - time[paebs_ed-1]) <= threshold:
                    global EVENT_START_TIME_DIFF
                    EVENT_START_TIME_DIFF = (time[resim_st] - time[aebs_st])
                    if ACTIVATE_FLAG:
                        common_events.append(warning_data_2)
                        resim_warning.remove(warning_data_2)
                        paebs_warning.remove(warning_data_1)
                    else:
                        common_events.append(warning_data_1)
                        resim_warning.remove(warning_data_1)
                        paebs_warning.remove(warning_data_2)

        return common_events, resim_warning, paebs_warning

    def search(self, report):
        self.batch.add_entry(report)
        return
