# -*- dataeval: init -*-

"""
Finds intervals of different road types such as "city", "rural" and "highway".
The corresponding road type label and the driven distance will be stored with
the intervals.
"""

import numpy as np

import interface
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList
from aebs.proc.RoadTypeClassification import calcRoadTypes2

DIST_PLAU_ENABLE = True

class Search(interface.iSearch):
    dep = {
        'ego': 'calc_egomotion@aebs.fill',
        'drivdist': 'set_drivendistance@egoeval',
    }

    def fill(self):
        ego = self.modules.fill(self.dep['ego'])

        votes = self.batch.get_labelgroups('road type')
        report = Report(cIntervalList(ego.time), "Road types", votes=votes)

        if ego.ax.any():
            time = ego.time

            stopped, city, ruralRoad, highway = calcRoadTypes2(ego.vx, ego.yaw_rate, time)

            for road_type, road_intervals in [
                ("ego stopped", cIntervalList.fromMask(time, stopped)),
                ("city", cIntervalList.fromMask(time, city)),
                ("rural", cIntervalList.fromMask(time, ruralRoad)),
                ("highway", cIntervalList.fromMask(time, highway)),
            ]:
                for interval in road_intervals:
                    idx = report.addInterval(interval)
                    report.vote(idx, 'road type', road_type)

            set_driv_dist_for_report = self.modules.get_module(self.dep['drivdist'])
            set_driv_dist_for_report(report)

            if DIST_PLAU_ENABLE:
                # vd = Vehicle Distance
                vd_groups = [
                    {"vd": ("VD_00", "VD_TotVehDist_00")},
                    {"vd": ("VDHR_EE", "VDHR_HRTotVehDist_EE")},
                    {"vd": ("VDHR_17_s17", "VDHR_HRTotVehDist_17_s17")},
                    {"vd": ("VDHR_EE_sEE", "TotalVehiclaDistHighRes")},
                    {"vd": ("VDHR_EE_sEE", "VDHR_HRTotVehDist_EE")},
                    {"vd": ("VDHR_EE_sEE", "VDHR_TotalVehDistHR_EE")},
                    {"vd": ("VDHR", "VDHR_TotalVehDistHR")},
                    {"vd": ("VDHR_sEE", "VDHR_TotalVehDistHR_sEE")},
                    {"vd": ("CAN_MFC_Public_VDHR_EE", "VDHR_TotalVehDistHR_EE")},
                ]
                vd_group = self.source.selectLazySignalGroup(vd_groups)
                compare_distances(vd_group, ego, self.logger)
        else:
            self.logger.error("Skip measurement due to high difference in time array")
        return report

    def search(self, report):
        self.batch.add_entry(report)
        return


def compare_distances(vd_group, ego, logger):
    """
    Plausibility check for speed based and VD/VDHR message based distance
    calculations.
    """
    if 'vd' in vd_group:
        vd2 = vd_group.get_value('vd', ScaleTime=ego.time)
        tot_vd2 = vd2[-1] - vd2[0] if vd2.size > 0 else 0.0
        tot_vd1 = np.trapz(ego.vx, ego.time) / 1000.0  # [m] -> [km]
        if tot_vd1 > 1.0 and abs(1.0 - tot_vd2 / tot_vd1) > 0.1:  # 10% tolerance
            logger.warning(
                "Suspicious distances: VDHR=%.1f km, motion=%.1f km" %
                (tot_vd2, tot_vd1))
        else:
            logger.debug(
                "Calculated distances: VDHR=%.1f km, motion=%.1f km" %
                (tot_vd2, tot_vd1))
    else:
        logger.debug("No VD/VDHR signal found; distance plaucheck not possible")
    return
