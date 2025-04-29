# -*- dataeval: init -*-

"""
:Name:
    search_acc_eval_dirk.py

:Type:
    Search script

:Full Path:
    dataevalaebs/src/acceval/search_acc_eval_dirk.py

:Sensors:
    FLR25

:Short Description:
    1) ACC KPI to check Wrong/Correct ACC target selection.
    2) Stores all such events in the database

:Large Description:
    To write an ACC KPI to check Wrong/Correct ACC target selection. Check status of the DIRK BUTTON (i.e. It can be Red / Green).
        1) Red button for wrong target selection.
        2) Green button for especially good selection (no every good selection shall be pressed)

:Dependencies:
    - calc_acc_eval_dirk@aebs.fill

:Output Data Image/s:
    N/A

:Event Name:
    ACC event

:Event Labels:
    1) Red Dirk Activate
    2) Green Dirk Activate

:Event Values:
    N/A

:Signals:
    sgs = [
            {
                "dirk_red_button": ("DIRK", "DFM_red_button"),
                "dirk_green_button": ("DIRK", "DFM_green_button"),
            },
         ]

.. note::
	For source code click on [source] tag beside functions
"""

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report
import numpy as np

class Search(iSearch):
    dep = {
        'function_deactivation_check': "calc_function_deactivation_check@aebs.fill"
    }

    def fill(self):
        time, valid_intervals, XBR_ExtAccelDem, XBR_ExtAccelDem_1, XBR_ExtAccelDem_2, AEBSState, aebs_brake_acceleration_demand = self.modules.fill(self.dep['function_deactivation_check'])

        event_votes = 'Function deactivation check'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'Function deactivation check', votes=votes)

        batch = self.get_batch()

        qua_group = 'Function Deactivation Check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        if valid_intervals is not None:
            intervals = maskToIntervals(valid_intervals)
            jumps = [[start] for start, end in intervals]

            for jump, interval in zip(jumps, intervals):
                idx = report.addInterval(interval)
                report.vote(idx, event_votes, "Function Deactivated")
                if (np.abs(XBR_ExtAccelDem) < 9).any():
                    report.set(idx, qua_group, 'CAN XBR', XBR_ExtAccelDem[jump])
                elif (np.abs(XBR_ExtAccelDem_1) < 9).any():
                    report.set(idx, qua_group, 'CAN XBR', XBR_ExtAccelDem_1[jump])
                elif (np.abs(XBR_ExtAccelDem_2) < 9).any():
                    report.set(idx, qua_group, 'CAN XBR', XBR_ExtAccelDem_2[jump])
                report.set(idx, qua_group, 'CAN AEBSState', AEBSState[jump])
                report.set(idx, qua_group, 'AEBS brake acceleration demand', aebs_brake_acceleration_demand[jump])

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
    
