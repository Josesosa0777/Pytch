# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report

import numpy as np


class Search(iSearch):
    dep = {
        'sys_bitfield_status': "calc_sys_bitfield_event@aebs.fill"
    }

    def fill(self):
        time, bitfield_AEBSState, bitfield_LDWSState, bitfield_DTC1_E8, bitfield_DTC2_E8, bitfield_DTC3_E8, \
        bitfield_DTC4_E8, bitfield_DTC5_E8, bitfield_FwdLaneImagerStatus_E8, bitfield_DTC1_2A, bitfield_DTC2_2A, \
        bitfield_DTC3_2A, bitfield_DTC4_2A, bitfield_DTC5_2A = self.modules.fill(
            self.dep['sys_bitfield_status'])

        event_votes = 'Sys_Bitfield event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'Sys_Bitfield event', votes=votes)
        report_intervals = []
        # get_intervals for all bitfield values
        AEBSState_intervals = maskToIntervals(bitfield_AEBSState)

        LDWSState_intervals = maskToIntervals(bitfield_LDWSState)
        if bool(LDWSState_intervals):
            AEBSState_intervals.append(LDWSState_intervals[0])
        DTC1_E8_intervals = maskToIntervals(bitfield_DTC1_E8)
        if bool(DTC1_E8_intervals):
            AEBSState_intervals.append(DTC1_E8_intervals[0])
        DTC2_E8_intervals = maskToIntervals(bitfield_DTC2_E8)
        if bool(DTC2_E8_intervals):
            AEBSState_intervals.append(DTC2_E8_intervals[0])
        DTC3_E8_intervals = maskToIntervals(bitfield_DTC3_E8)
        if bool(DTC3_E8_intervals):
            AEBSState_intervals.append(DTC3_E8_intervals[0])
        DTC4_E8_intervals = maskToIntervals(bitfield_DTC4_E8)
        if bool(DTC4_E8_intervals):
            AEBSState_intervals.append(DTC4_E8_intervals[0])
        DTC5_E8_intervals = maskToIntervals(bitfield_DTC5_E8)
        if bool(DTC5_E8_intervals):
            AEBSState_intervals.append(DTC5_E8_intervals[0])
        FwdLaneImagerStatus_E8_intervals = maskToIntervals(bitfield_FwdLaneImagerStatus_E8)
        if bool(FwdLaneImagerStatus_E8_intervals):
            AEBSState_intervals.append(FwdLaneImagerStatus_E8_intervals[0])
        DTC1_2A_intervals = maskToIntervals(bitfield_DTC1_2A)
        if bool(DTC1_2A_intervals):
            AEBSState_intervals.append(DTC1_2A_intervals[0])
        DTC2_2A_intervals = maskToIntervals(bitfield_DTC2_2A)
        if bool(DTC2_2A_intervals):
            AEBSState_intervals.append(DTC2_2A_intervals[0])
        DTC3_2A_intervals = maskToIntervals(bitfield_DTC3_2A)
        if bool(DTC3_2A_intervals):
            AEBSState_intervals.append(DTC3_2A_intervals[0])
        DTC4_2A_intervals = maskToIntervals(bitfield_DTC4_2A)
        if bool(DTC4_2A_intervals):
            AEBSState_intervals.append(DTC4_2A_intervals[0])
        DTC5_2A_intervals = maskToIntervals(bitfield_DTC5_2A)
        if bool(DTC5_2A_intervals):
            AEBSState_intervals.append(DTC5_2A_intervals[0])

        jumps = [start for start, end in AEBSState_intervals]
        interval_dict = {start: end for start, end in AEBSState_intervals}
        jumps.sort()

        check_valid_event_intervals = {idx: difference for idx, difference in
                                       enumerate([time[list2] - time[jumps[0]] for list2 in jumps]) if difference > 5}
        if len(jumps)>0:
            if len(check_valid_event_intervals) > 0:
                for key, value in check_valid_event_intervals.iteritems():
                    report_intervals.append([jumps[key],interval_dict[jumps[key]]])
                # jumps_interval = [[start] for start, end in report_intervals]
                for id, event_interval in enumerate(report_intervals):
                    idx = report.addInterval(event_interval)
                    report.vote(idx, event_votes, "sys_bitfield_event")
            else:
                report_intervals.append((jumps[0], interval_dict[jumps[0]]))
                for id, event_interval in enumerate(report_intervals):
                    idx = report.addInterval(event_interval)
                    report.vote(idx, event_votes, "sys_bitfield_event")
        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
