# -*- dataeval: init -*-

"""
:Name:
    search_acc_take_over_req.py

:Type:
    Search script

:Full Path:
    dataevalaebs/src/acceval/search_acc_take_over_req.py

:Sensors:
    FLR25

:Short Description:
    1) To check take over request / distance alert signal.
    2) Stores all such events in the database

:Large Description:
    To write an ACC KPI to check take over request / distance alert signal.
    How to calculate:
        1) Filter out the active distance alert.
    Logic:
        ACCDistanceAlertSignal is other than 0.

:Dependencies:
    - calc_acc_take_over_req@aebs.fill

:Output Data Image/s:
    N/A

:Event Name:
    ACC event

:Event Labels:
    Take Over Request

:Event Values:
    N/A

:Signals:
    sgs = [
            {
                "take_over_request": ("ACC1_2A", "ACC1_DistanceAlert_2A"),
            },
         ]

.. note::
    For source code click on [source] tag beside functions
"""

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'take_over_request_status': "calc_acc_take_over_req@aebs.fill"
    }

    def fill(self):
        time, take_over_req_mask, take_over_req_data = self.modules.fill(self.dep['take_over_request_status'])

        event_votes = 'ACC event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'ACC event', votes=votes)
        # Add quantity
        batch = self.get_batch()

        qua_group = 'ACC check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        intervals = maskToIntervals(take_over_req_mask)
        jumps = [[start] for start, end in intervals]

        for jump, interval in zip(jumps, intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "Take Over Request")
            report.set(idx, qua_group, 'take over request', take_over_req_data[jump])

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
