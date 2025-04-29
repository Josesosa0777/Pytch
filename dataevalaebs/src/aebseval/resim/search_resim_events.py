# -*- dataeval: init -*-
import numpy as np
from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report
from measparser.filenameparser import FileNameParser


class Search(iSearch):
    dep = {
        'aebs_resim': "calc_aebs_resim_output@aebs.fill"
    }

    def fill(self):
        acc_ped_events, time = self.modules.fill(self.dep['aebs_resim'])

        try:
            file_name = FileNameParser(self.source.BaseName).date_underscore
        except:
            file_name = self.source.BaseName.replace('.', '-').replace('_at_', '_').rsplit('_', 2)[0]
        # valid_intervals = []
        valid_data = self.data_preprocessing(file_name,acc_ped_events)
        event_votes = 'AEBS resim phase'
        # algo_votes = 'AEBS algo'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'AEBS event', votes=votes)
        # Add quantity
        batch = self.get_batch()
        # cascade_phases = votes[event_votes]
        # algo = 'FLR21 Warning'
        jumps = []
        warnings = []
        type_of_event = []
        # levels = 5
        for item in valid_data:
            interval = self.get_index((long(item["Start Time Abs"]), long(item["End Time Abs"]),), time)
            jumps.append([interval[0]])
            warnings.append((interval[0], interval[1]))
            type_of_event.append(item["event type"])

        # jumps, warnings, boolean_state = phases.merge_phases(levels)
        for jump, interval, event_type in zip(jumps, warnings, type_of_event):
            idx = report.addInterval(interval)
            # report.vote(idx, algo_votes, algo)
            if event_type == '0':
                report.vote(idx, event_votes, 'warning,\n stationary target')
            elif event_type == '1':
                report.vote(idx, event_votes, "partial braking,\n stationary target")
            elif event_type == '2':
                report.vote(idx, event_votes, "emergency braking,\n stationary target")
            elif event_type == '3':
                report.vote(idx, event_votes, "warning,\n moving target")
            elif event_type == '4':
                report.vote(idx, event_votes, "partial braking,\n moving target")
            elif event_type == '5':
                report.vote(idx, event_votes, "emergency braking,\n moving target")

        return report

    def data_preprocessing(self,file_name,acc_ped_events):
        valid_data = []

        for files in acc_ped_events:
            name = ""
            if 'camera' in files['Measurement File']:
                name = files['Measurement File'].replace('.', '-').split('_camera')[0].replace('_at_', '_')
            elif 'radar' in files['Measurement File']:
                name = files['Measurement File'].replace('.', '-').split('_radar')[0].replace('_at_', '_')

            if name == file_name:
                valid_data.append(files)
        return valid_data

    def get_index(self, interval, time):
        st_time, ed_time = interval
        st_time = st_time / 1000000.0
        ed_time = ed_time / 1000000.0
        start_index = (np.abs(time - st_time)).argmin()
        end_index = (np.abs(time - ed_time)).argmin() + 1
        if start_index == end_index:
            end_index += 1
        return (start_index, end_index)

    def search(self, report):
        self.batch.add_entry(report)
        return
