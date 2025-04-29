# -*- dataeval: init -*-

"""
:Name:
    search_acc_strong_brake_req.py

:Type:
    Search script

:Full Path:
    dataevalaebs/src/acceval/search_acc_strong_brake_req.py

:Sensors:
    FLR25

:Short Description:
    1) To check strong break request from ACC.
    2) Stores all such events in the database

:Large Description:
    To write an ACC KPI to check strong break request from ACC.
    How to calculate:
        1) XBR bigger than 2.5 m/s2 (ACC maximum XBR is 3.5 m/s2).
    Logic:
        XBR_ExtAccelDem is smaller than -2.5

:Dependencies:
    - calc_acc_strong_brake_req@aebs.fill

:Output Data Image/s:
    N/A

:Event Name:
    ACC event

:Event Labels:
    Strong Brake Request

:Event Values:
    N/A

:Signals:
    sgs = [
            {
                 "strong_brake_request": ("XBR_2A", "XBR_ExtAccelDem_2A"),
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
        'strong_brake_request_status': "calc_acc_strong_brake_req@aebs.fill"
    }

    def fill(self):
        time, strong_brake_mask, strong_brake_data = self.modules.fill(self.dep['strong_brake_request_status'])

        event_votes = 'ACC event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'ACC event', votes=votes)
        # Add quantity
        batch = self.get_batch()

        qua_group = 'ACC check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        intervals = maskToIntervals(strong_brake_mask)
        jumps = [[start] for start, end in intervals]

        for jump, interval in zip(jumps, intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "Strong Brake Request")
            report.set(idx, qua_group, 'strong brake request', strong_brake_data[jump])

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
