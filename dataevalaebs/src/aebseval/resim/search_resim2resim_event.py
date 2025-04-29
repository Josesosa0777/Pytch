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
    - AEBS warnings
    - AEBS Delta Event

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
    'flr25': dict(
        aebs_resim='calc_aebs_resim2resim_output@aebs.fill',
    ),
}

mps2kph = lambda v: v*3.6

COMMON_EVENT_FLAG = False
ACTIVATE_FLAG = False
EVENT_START_TIME_DIFF = 0.0

class Search(iSearch):
    dep = {
        'aebs_resim': None,  # TBD in init()
    }

    def init(self,  aebs_resim):
        self.dep['aebs_resim'] = aebs_resim
        return

    def fill(self):
        baseline_aebs_events, retest_aebs_events, time, total_mileage= self.modules.fill(self.dep['aebs_resim'])
        aebs_resim_data = 'AEBS resim phase'
        delta_data = 'Delta report data'
        votes = self.batch.get_labelgroups(aebs_resim_data, delta_data)
        report = Report(cIntervalList(time), 'AEBS Delta Event', votes=votes)

        qua_group = 'ego vehicle'
        quas = self.batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        try:
            measurement_file_name = FileNameParser(self.source.BaseName).date_underscore
        except:
            measurement_file_name = self.source.BaseName.replace('.', '-').replace('_at_', '_').rsplit('_', 2)[0]
        valid_intervals = {}

        resim_event_dict = self.data_preprocessing(measurement_file_name, baseline_aebs_events, retest_aebs_events,)

        threshold_value_to_compare_events = 4
        for key, value in resim_event_dict.iteritems():
            events = []
            aebs_resim_jumps = []
            aebs_resim_warnings = []
            type_of_event = []
            ego_speed = []
            for item in value:
                interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), time)
                aebs_resim_jumps.append([interval[0]])
                events.append(aebs_resim_jumps)
                aebs_resim_warnings.append((interval[0], interval[1]))
                events.append(aebs_resim_warnings)
                type_of_event.append(item["event type"])
                events.append(type_of_event)
                if 'ego_velocity_x' in item:
                    ego_speed.append(item['ego_velocity_x'])
                elif 'ego_velocity_x_start' in item:
                    ego_speed.append(item['ego_velocity_x_start'])
                events.append(ego_speed)
            valid_intervals[key] = events

        common_event, intervals = self.match(valid_intervals, threshold_value_to_compare_events, time)

        for resim_event_category in common_event:
            id = report.addInterval(resim_event_category)
            global COMMON_EVENT_FLAG
            COMMON_EVENT_FLAG = True
            report.vote(id, delta_data, "Common\n Event")

            event_type = valid_intervals['baseline_aebs_events'][2][0]
            speed = valid_intervals['baseline_aebs_events'][3][0]
            if event_type == '0':
                report.vote(id, aebs_resim_data, "warning,\n stationary target")
                report.set(id, qua_group, 'speed start', float(speed))
                report.set(id, qua_group, 'mileage', float(total_mileage))
                report.set(id, qua_group, 'event start time diff', EVENT_START_TIME_DIFF)
                id = id + 1
            elif event_type == '1':
                report.vote(id, aebs_resim_data, "partial braking,\n stationary target")
                report.set(id, qua_group, 'speed start', float(speed))
                report.set(id, qua_group, 'mileage', float(total_mileage))
                report.set(id, qua_group, 'event start time diff', EVENT_START_TIME_DIFF)
                id = id + 1
            elif event_type == '2':
                report.vote(id, aebs_resim_data, "emergency braking,\n stationary target")
                report.set(id, qua_group, 'speed start', float(speed))
                report.set(id, qua_group, 'mileage', float(total_mileage))
                report.set(id, qua_group, 'event start time diff', EVENT_START_TIME_DIFF)
                id = id + 1
            elif event_type == '3':
                report.vote(id, aebs_resim_data, "warning,\n moving target")
                report.set(id, qua_group, 'speed start', float(speed))
                report.set(id, qua_group, 'mileage', float(total_mileage))
                report.set(id, qua_group, 'event start time diff', EVENT_START_TIME_DIFF)
                id = id + 1
            elif event_type == '4':
                report.vote(id, aebs_resim_data, "partial braking,\n moving target")
                report.set(id, qua_group, 'speed start', float(speed))
                report.set(id, qua_group, 'mileage', float(total_mileage))
                report.set(id, qua_group, 'event start time diff', EVENT_START_TIME_DIFF)
                id = id + 1
            elif event_type == '5':
                report.vote(id, aebs_resim_data, "emergency braking,\n moving target")
                report.set(id, qua_group, 'speed start', float(speed))
                report.set(id, qua_group, 'mileage', float(total_mileage))
                report.set(id, qua_group, 'event start time diff', EVENT_START_TIME_DIFF)
                id = id + 1

        if not common_event:
            if intervals['baseline_aebs_events']:
                idx = report.addInterval(intervals['baseline_aebs_events'][1][0])
                report.vote(idx, delta_data, "Baseline")
                event_type = intervals['baseline_aebs_events'][2][0]
                speed = intervals['baseline_aebs_events'][3][0]
            elif intervals['retest_aebs_events']:
                idx = report.addInterval(intervals['retest_aebs_events'][1][0])
                report.vote(idx, delta_data, "Retest")
                event_type = intervals['retest_aebs_events'][2][0]
                speed = intervals['retest_aebs_events'][3][0]

            if event_type == '0':
                report.vote(idx, aebs_resim_data, "warning,\n stationary target")
                report.set(idx, qua_group, 'speed start', float(speed))
                report.set(idx, qua_group, 'mileage', float(total_mileage))
            elif event_type == '1':
                report.vote(idx, aebs_resim_data, "partial braking,\n stationary target")
                report.set(idx, qua_group, 'speed start', float(speed))
                report.set(idx, qua_group, 'mileage', float(total_mileage))
            elif event_type == '2':
                report.vote(idx, aebs_resim_data, "emergency braking,\n stationary target")
                report.set(idx, qua_group, 'speed start', float(speed))
                report.set(idx, qua_group, 'mileage', float(total_mileage))
            elif event_type == '3':
                report.vote(idx, aebs_resim_data, "warning,\n moving target")
                report.set(idx, qua_group, 'speed start', float(speed))
                report.set(idx, qua_group, 'mileage', float(total_mileage))
            elif event_type == '4':
                report.vote(idx, aebs_resim_data, "partial braking,\n moving target")
                report.set(idx, qua_group, 'speed start', float(speed))
                report.set(idx, qua_group, 'mileage', float(total_mileage))
            elif event_type == '5':
                report.vote(idx, aebs_resim_data, "emergency braking,\n moving target")
                report.set(idx, qua_group, 'speed start', float(speed))
                report.set(idx, qua_group, 'mileage', float(total_mileage))

        return report

    def data_preprocessing(self,measurement_file_name, baseline_aebs_events, retest_aebs_events):
        resim_event_dict = {}
        resim_event_dict['baseline_aebs_events'] = baseline_aebs_events
        resim_event_dict['retest_aebs_events'] =  retest_aebs_events

        for key, value in resim_event_dict.iteritems():
            valid_data_from_csv = []
            for resim_data in value:
                measurement_name_from_csv = ""
                if 'camera' in resim_data['Measurement File']:
                    measurement_name_from_csv = \
                    resim_data['Measurement File'].replace('.', '-').split('_camera')[0].replace('_at_', '_')
                elif 'radar' in resim_data['Measurement File']:
                    measurement_name_from_csv = \
                    resim_data['Measurement File'].replace('.', '-').split('_radar')[0].replace('_at_', '_')
                if measurement_name_from_csv == measurement_file_name:
                    valid_data_from_csv.append(resim_data)
            resim_event_dict[key] = valid_data_from_csv

        return resim_event_dict

    def get_index(self, interval, time):
        st_time, ed_time = interval
        st_time = st_time / 1000000.0
        ed_time = ed_time / 1000000.0
        start_index = (np.abs(time - st_time)).argmin()
        end_index = (np.abs(time - ed_time)).argmin()+1
        if start_index == end_index:
            end_index += 1
        return (start_index, end_index)

    def match(self, valid_intervals, threshold, time):
        common_events = []
        global ACTIVATE_FLAG
        if len(valid_intervals['baseline_aebs_events']) > len(valid_intervals['retest_aebs_events']):
            try:
                baseline_warnings_collection = valid_intervals['baseline_aebs_events'][1]
            except:
                baseline_warnings_collection = valid_intervals['baseline_aebs_events']
            try:
                retest_warnings_collection = valid_intervals['retest_aebs_events'][1]
            except:
                retest_warnings_collection = valid_intervals['retest_aebs_events']
            ACTIVATE_FLAG = True
        else:
            try:
                retest_warnings_collection = valid_intervals['baseline_aebs_events'][1]
            except:
                retest_warnings_collection = valid_intervals['baseline_aebs_events']
            try:
                baseline_warnings_collection = valid_intervals['retest_aebs_events'][1]
            except:
                baseline_warnings_collection = valid_intervals['retest_aebs_events']
            ACTIVATE_FLAG = False

        for i, warning_data_1 in enumerate(baseline_warnings_collection):
            resim_st, resim_ed = warning_data_1
            for j, warning_data_2 in enumerate(retest_warnings_collection):
                aebs_st, aebs_ed = warning_data_2

                if abs(time[resim_st] - time[aebs_st]) <= threshold and abs(time[resim_ed] - time[aebs_ed-1]) <= threshold:
                    global EVENT_START_TIME_DIFF
                    EVENT_START_TIME_DIFF = (time[resim_st] - time[aebs_st])
                    if ACTIVATE_FLAG:
                        common_events.append(warning_data_2)
                        valid_intervals['retest_aebs_events'][1].remove(warning_data_2)
                        valid_intervals['baseline_aebs_events'][1].remove(warning_data_1)
                    else:
                        common_events.append(warning_data_1)
                        valid_intervals['retest_aebs_events'][1].remove(warning_data_1)
                        valid_intervals['baseline_aebs_events'][1].remove(warning_data_2)

        return common_events, valid_intervals

    def search(self, report):
        self.batch.add_entry(report)
        return
