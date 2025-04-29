# -*- dataeval: init -*-

"""
:Name:
    search_acc_eval_overreaction.py

:Type:
    Search script

:Full Path:
    dataevalaebs/src/acceval/search_acc_eval_overreaction.py

:Sensors:
    FLR25

:Short Description:
    1) To have smooth reaction and avoid oscillating intervention.
    2) Stores all such events in the database

:Large Description:
    To write an ACC KPI to have smooth reaction and avoid oscillating intervention.
    Condition to check ACC Overreaction.
        1) Brakes only if moment requirement previously remained NULL for at least 1 s.
    Logic:
        XBR_ExtAccelDem is negative for the first time then check 1s before this event that TSC1_ReqTorqueLimit_2A_00 is positive.

:Dependencies:
    - calc_acc_eval_overreaction@aebs.fill

:Output Data Image/s:
    N/A

:Event Name:
    ACC event

:Event Labels:
    ACC Overreaction

:Event Values:
    N/A

:Signals:
    sgs = [
            {
                "TSC1_ReqTorqueLimit_2A": ("TSC1_2A_00", "TSC1_ReqTorqueLimit_2A_00"),
                "XBR_ExtAccelDem_2A": ("XBR_2A", "XBR_ExtAccelDem_2A"),
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
        'ACC_overreaction_status': "calc_acc_eval_overreaction@aebs.fill"
    }

    def fill(self):
        time, valid_data_mask, valid_data, torque_limit_data = self.modules.fill(self.dep['ACC_overreaction_status'])

        event_votes = 'ACC event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'ACC event', votes=votes)
        # Add quantity
        batch = self.get_batch()

        qua_group = 'ACC check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        intervals = maskToIntervals(valid_data_mask)

        jumps = [[start] for start, end in intervals]

        for jump, interval in zip(jumps, intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "ACC Overreaction")
            report.set(idx, qua_group, 'acc overreaction', torque_limit_data[jump])

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
