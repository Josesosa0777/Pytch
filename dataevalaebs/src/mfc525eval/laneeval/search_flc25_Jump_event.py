# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'Lane_Width_Jump_event': "calc_flc25_Jumps_Event@aebs.fill"
    }

    def fill(self):
        time, LaneWidth_JumpEvent_masked_array, frontAxleSpeed_value = self.modules.fill(self.dep['Lane_Width_Jump_event'])

        event_votes = 'FLC25 LDWS'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 LDWS', votes=votes)

        batch = self.get_batch()
        qua_group = 'FLC25 LDWS'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)

        Jumps_Event_site_intervals = maskToIntervals(LaneWidth_JumpEvent_masked_array)
        jumps = [[start] for start, end in Jumps_Event_site_intervals]
        for jump, Jumps_Event_site_interval in zip(jumps, Jumps_Event_site_intervals):
            idx = report.addInterval(Jumps_Event_site_interval)
            report.vote(idx, event_votes, 'LaneWidthJump')  # Rahul you have work till here, check further
            report.set(idx, qua_group, 'FrontAxleSpeed', frontAxleSpeed_value[jump[0]])

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
