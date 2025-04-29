# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'sensor_status': "calc_flc25_sensor_states@aebs.fill"
    }

    def fill(self):
        time, cam_status, radar_status= self.modules.fill(self.dep['sensor_status'])

        event_votes = 'FLC25 Sensor state'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(time), 'FLC25 Sensor state', votes=votes)


        camera_status_intervals = maskToIntervals(cam_status)
        jumps = [[start] for start, end in camera_status_intervals]
        for jump, sensor_status_interval in zip(jumps, camera_status_intervals):
            idx = report.addInterval(sensor_status_interval)
            report.vote(idx, event_votes, "CAMERA DEGRADED")

        radar_status_intervals = maskToIntervals(radar_status)
        jumps = [[start] for start, end in radar_status_intervals]
        for jump, sensor_status_interval in zip(jumps, radar_status_intervals):
            idx = report.addInterval(sensor_status_interval)
            report.vote(idx, event_votes, "RADAR DEGRADED")

        return report

    def search(self, report):
        self.batch.add_entry(report)
        return
