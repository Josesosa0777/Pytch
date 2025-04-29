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


class Search(iSearch):
    dep = {
        'dirk_status': "calc_acc_eval_dirk@aebs.fill"
    }

    def fill(self):
        time, dirk_red_mask, dirk_green_mask, dirk_red_data, dirk_green_data = self.modules.fill(
            self.dep['dirk_status'])

        event_votes = 'ACC event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'ACC event', votes=votes)
        # Add quantity
        batch = self.get_batch()

        qua_group = 'ACC check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        # For Red Dirk Button

        intervals = maskToIntervals(dirk_red_mask)
        jumps = [[start] for start, end in intervals]

        for jump, interval in zip(jumps, intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "Red Dirk Activate")
            report.set(idx, qua_group, 'dirk_red_button', dirk_red_data[jump])

        # For Green Dirk Button

        intervals = maskToIntervals(dirk_green_mask)
        jumps = [[start] for start, end in intervals]

        for jump, interval in zip(jumps, intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "Green Dirk Activate")
            report.set(idx, qua_group, 'dirk_green_button', dirk_green_data[jump])

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
