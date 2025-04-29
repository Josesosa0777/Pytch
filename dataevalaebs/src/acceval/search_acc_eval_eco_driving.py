# -*- dataeval: init -*-

"""
:Name:
    search_acc_eval_eco_driving.py

:Type:
    Search script

:Full Path:
    dataevalaebs/src/acceval/search_acc_eval_eco_driving.py

:Sensors:
    FLR25

:Short Description:
    1) ACC KPI to find Economic Driving condition
    2) Stores all such events in the database

:Large Description:
    To write an ACC KPI to find Economic Driving condition (i.e. Pushing the brakes only if necessary (no short interventions))
    Condition to check Economic Driving condition.
        1) brake intervention less than 1 second
    Logic:
        XBR_ExtAccelDem_2A is negative for less than 1s.

:Dependencies:
    - calc_acc_eval_eco_driving@aebs.fill

:Output Data Image/s:
    N/A

:Event Name:
    ACC event

:Event Labels:
    Economic Driving

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
        'eco_driving_status': "calc_acc_eval_eco_driving@aebs.fill"
    }

    def fill(self):
        time, ext_accel_maks, req_torque_limit_mask, ext_accel_dem_data = self.modules.fill(self.dep['eco_driving_status'])

        event_votes = 'ACC event'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'ACC event', votes=votes)
        # Add quantity
        batch = self.get_batch()

        qua_group = 'ACC check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        xbr_intervals = maskToIntervals(ext_accel_maks)
        torque_limit_intervals = maskToIntervals(req_torque_limit_mask)
        intervals = xbr_intervals + torque_limit_intervals
        interval = [time_interval for time_interval in intervals if time[time_interval[1]] - time[time_interval[0]] < 1]
        jumps = [[start] for start, end in interval]

        for jump, interval in zip(jumps, intervals):
            idx = report.addInterval(interval)
            report.vote(idx, event_votes, "Economic Driving")
            report.set(idx, qua_group, 'economic_driving', ext_accel_dem_data[jump])

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
