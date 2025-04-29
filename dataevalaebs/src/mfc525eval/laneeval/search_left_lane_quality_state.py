# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.lane_quality_state import lane_quality_dict


class Search(iSearch):
    optdep = {
        'egospeedstart': 'set_egospeed-start@egoeval',
        'egospeedmin': 'set_egospeed-min@egoeval',
        'drivdist': 'set_drivendistance@egoeval',
    }

    sgs = [
        {
            "ego_left_quality": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_quality"),
            "ego_right_quality": ("LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_quality")
        },
        {
            "ego_left_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_quality"),
            "ego_right_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_quality")
        },
        {
            "ego_left_quality": ("MFC5xx_Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_quality"),
            "ego_right_quality": ("MFC5xx_Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_quality"),
        },
        {
            "ego_left_quality": (
                "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.left.quality"),
            "ego_right_quality": (
                "MFC5xx Device.LD.LdOutput", "MFC5xx Device.LD.LdOutput.road.ego.right.quality"),
        },
    ]

    def check(self):
        group = self.source.selectSignalGroup(self.sgs)
        return group

    def fill(self, group):
        # get signals
        _, left_quality = group.get_signal("ego_left_quality")
        t, right_quality = group.get_signal("ego_right_quality")

        # init report
        title = "FLC25 lane state"
        votes = self.batch.get_labelgroups(title)
        report = Report(cIntervalList(t), title, votes=votes)

        # find intervals
        quality_25_mask = (0 <= left_quality) & (left_quality < 26)
        quality_50_mask = (25 < left_quality) & (left_quality < 51)
        quality_75_mask = (50 < left_quality) & (left_quality < 76)
        quality_100_mask = (75 < left_quality) & (left_quality < 101)

        for st, end in maskToIntervals(quality_25_mask):
            index = report.addInterval((st, end))
            report.vote(index, title, '0..25')

        for st, end in maskToIntervals(quality_50_mask):
            index = report.addInterval((st, end))
            report.vote(index, title, '26..50')

        for st, end in maskToIntervals(quality_75_mask):
            index = report.addInterval((st, end))
            report.vote(index, title, '51..75')

        for st, end in maskToIntervals(quality_100_mask):
            index = report.addInterval((st, end))
            report.vote(index, title, '76..100')
        report.sort()
        # set general quantities
        for qua in 'drivdist', 'egospeedmin', 'egospeedstart':
            if self.optdep[qua] in self.passed_optdep:
                set_qua_for_report = self.modules.get_module(self.optdep[qua])
                set_qua_for_report(report)
            else:
                self.logger.warning("Inactive module: %s" % self.optdep[qua])
        return report

    def search(self, report):
        self.batch.add_entry(report, result=self.PASSED)
        return


'''
    for value in np.unique(left_quality):
      mask = left_quality == value
      key = 0
      if value < 26:
        key = 1
      elif value < 51:
        key = 2
      elif value < 76:
        key = 3
      elif value < 101:
        key = 4
      label = lane_quality_dict[key]
      for st,end in maskToIntervals(mask):
        index = report.addInterval( (st,end) )
        report.vote(index, title, label)
  '''
