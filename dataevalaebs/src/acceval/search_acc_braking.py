# -*- dataeval: init -*-

"""
:Name:
    search_acc_strong_brake_req.py

:Type:
    Search script

:Full Path:
    dataevalaebs/src/acceval/search_acc_braking.py

:Sensors:
    FLR25

:Short Description:
    1) ACC shall avoid unexpected strong braking
    2) Stores all such events in the database with video clips 5s before and after event

:Large Description:
    To write an ACC KPI to check strong brake request from ACC.
    How to calculate:
        1) ACC1_ACCMode_2A = 2 (distance control)
        2) XBR_ExtAccelDem_0B_2A > 3 m/s2

:Dependencies:
    - calc_acc_braking@aebs.fill

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
                 "XBR_ExtAccelDem_0B_2A": ("XBR_0B_2A","XBR_ExtAccelDem_0B_2A"), > -3.5 m/s2
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
        'unexpected_strong_braking': "calc_acc_braking@aebs.fill"
    }

    def fill(self):
        time, unexp_strong_brake_mask, unexp_strong_brake_data = self.modules.fill(self.dep['unexpected_strong_braking'])

        event_votes = 'ACC event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'ACC event', votes=votes)
        # Add quantity
        batch = self.get_batch()

        qua_group = 'ACC check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        intervals = maskToIntervals(unexp_strong_brake_mask)
        jumps = [[start] for start, end in intervals]

        for jump, interval in zip(jumps, intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "Unexpected strong brake")
            report.set(idx, qua_group, 'unexp strong brake', unexp_strong_brake_data[jump])

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return