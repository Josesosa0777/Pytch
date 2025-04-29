# -*- dataeval: init -*-

"""
:Name:
    search_acc_brakepedal_override.py

:Type:
    Search script

:Full Path:
    dataevalaebs/src/acceval/search_acc_brakepedal_override.py

:Sensors:
    FLR25

:Short Description:
    1) To check Brakepedal Override by driver.
    2) Stores all such events in the database

:Large Description:
    To write an ACC KPI to check Brakepedal Override by driver.
    Filter out the the brake override event based on following signals:
        1) ACC mode
        2) brake pedal (Bremspedal)
    Logic:
        EBSBrkSw_0b is 1 & 500ms before the Switch became 1 AdaptiveCruiseCtrlMode is active (anything other than 0).

:Dependencies:
    - calc_acc_brakepedal_override@aebs.fill

:Output Data Image/s:
    N/A

:Event Name:
    ACC event

:Event Labels:
    Brakepedal Override

:Event Values:
    N/A

:Signals:
    sgs = [
            {
                 "AdaptiveCruiseCtrlMode": ("ACC1_2A", "ACC1_Mode_2A"),
                 "EBC1_EBSBrkSw_0B": ("EBC1_0B", "EBC1_EBSBrkSw_0B"),
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
        'brakepedal_override_status': "calc_acc_brakepedal_override@aebs.fill"
    }

    def fill(self):
        time, valid_data_mask, cruise_data = self.modules.fill(self.dep['brakepedal_override_status'])

        event_votes = 'ACC event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'ACC event', votes=votes)
        # Add quantity
        batch = self.get_batch()

        qua_group = 'ACC check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        intervals = maskToIntervals(valid_data_mask)
        valid_acc_modes = [1,2,3,4,5]
        valid_intervals = [id for id in intervals if cruise_data[id[0] - 0.500] in valid_acc_modes]

        jumps = [[start] for start, end in valid_intervals]

        for jump, interval in zip(jumps, valid_intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "Brakepedal Override")
            report.set(idx, qua_group, 'brakepedal override', cruise_data[jump])

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
