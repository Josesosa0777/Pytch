# -*- dataeval: init -*-

"""
:Name:
    search_acc_overheat.py

:Type:
    Search script

:Full Path:
    dataevalaebs/src/acceval/search_acc_overheat.py

:Sensors:
    FLR25

:Short Description:
    1) ACC shall avoid brake system overheat
    2) Stores all such events in the database with excessive ACC braking or mix control

:Large Description:
    To write an ACC KPI to check strong brake request from ACC.
    How to calculate:
        1) XBR_ExtAccelDem_0B_2A < 0
        2) TSC1_EngReqTorqueLimit > 0

:Dependencies:
    - calc_acc_overheat@aebs.fill

:Output Data Image/s:
    N/A

:Event Name:
    ACC event

:Event Labels:
    ACC brake overheat

:Event Values:
    N/A

:Signals:
    sgs = [
            {
                 "XBR_ExtAccelDem_0B_2A": ("XBR_0B_2A","XBR_ExtAccelDem_0B_2A"), < 0
                 "TSC1_EngReqTorqueLimit_00_2A": ("TSC1_00_2A","TSC1_EngReqTorqueLimit_00_2A"), > 0
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
        'acc_brake_overheat': "calc_acc_overheat@aebs.fill"
    }

    def fill(self):
        time, brake_overheat_mask, brake_overheat_data = self.modules.fill(self.dep['acc_brake_overheat'])

        event_votes = 'ACC event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'ACC event', votes=votes)
        # Add quantity
        batch = self.get_batch()

        qua_group = 'ACC check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        intervals = maskToIntervals(brake_overheat_mask)
        jumps = [[start] for start, end in intervals]

        for jump, interval in zip(jumps, intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "ACC brake overheat")
            report.set(idx, qua_group, 'ACC Brake overheat', brake_overheat_data[jump])

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return