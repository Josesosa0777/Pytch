# -*- dataeval: init -*-

"""
:Name:
    search_acc_torque_request.py

:Type:
    Search script

:Full Path:
    dataevalaebs/src/acceval/search_acc_torque_request.py

:Sensors:
    FLR25

:Short Description:
    1) To have smooth reaction and avoid oscillating intervention.
    2) Stores all such events in the database

:Large Description:
    To write an ACC KPI to have smooth reaction and avoid oscillating intervention.Accelerate and then brake immediately,
    or brake first then accelerate immediately
    Condition to check ACC Overreaction.
        1) Moment requirement directly after braking may max. x%.
    Logic:
        XBR_ExtAccelDem is positive for the first time after a negative than check 0.5s after this event
        that TSC1_ReqTorqueLimit_2A_00 is above 50% threshold.
        The threshold may have to be adjusted
        XBR_ExtAccelDem is negative for the first time then check 1s before this event that TSC1_ReqTorqueLimit_2A_00 is positive.

:Dependencies:
    - calc_acc_torque_request@aebs.fill

:Output Data Image/s:
    N/A

:Event Name:
    ACC event

:Event Labels:
    Torque Limit Above Threshold

:Event Values:
    N/A

:Signals:
    sgs = [
            {
                "AdaptiveCruiseCtrlMode": ("ACC1_2A", "ACC1_Mode_2A"),
                "TSC1_ReqTorqueLimit_2A": ("TSC1_2A_00", "TSC1_ReqTorqueLimit_2A_00"),
                "XBR_ExtAccelDem_2A": ("XBR_2A", "XBR_ExtAccelDem_2A"),
            },
         ]

.. note::
    For source code click on [source] tag beside functions
"""

import numpy as np
from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'ACC_torque_request_status': "calc_acc_torque_request@aebs.fill"
    }

    def fill(self):
        time, valid_data, signal_data, torque_limit_data = self.modules.fill(self.dep['ACC_torque_request_status'])

        valid_intervals = []
        event_votes = 'ACC event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'ACC event', votes=votes)
        # Add quantity
        batch = self.get_batch()

        qua_group = 'ACC check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        intervals = maskToIntervals(valid_data)

        for interval in intervals:
            end_index = interval[1]
            if signal_data[end_index] > 0:
                valid_timestamp = time[end_index] + 0.500
            else:
                valid_timestamp = time[end_index + 1] + 0.500
            index = np.argmax(time >= valid_timestamp)
            valid = (torque_limit_data[index] > 50)
            if valid:
                valid_intervals.append((end_index, index,))

        jumps = [[start] for start, end in valid_intervals]

        for jump, interval in zip(jumps, valid_intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "Torque Limit Above Threshold")
            report.set(idx, qua_group, 'torque limit above threshold', torque_limit_data[jump])

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
