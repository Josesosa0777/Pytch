# -*- dataeval: init -*-

"""
Search for events of braking primary target.
"""

import interface
from measproc import cIntervalList
from measproc.report2 import Report

AX_THRESHOLD = -1.0

class Search(interface.iSearch):
  dep = "fill_flr20_aeb_track@aebs.fill", "calc_flr20_egomotion@aebs.fill"
  
  def fill(self):
    # load fills
    track = self.modules.fill(self.dep[0])
    time = track.time
    ego_motion = self.modules.fill(self.dep[1]).rescale(time)
    
    # create report
    names = self.batch.get_quanamegroups('ego vehicle', 'target')
    report = Report(cIntervalList(time), "Braking vehicle", names=names)
    
    # add intervals
    intvals = cIntervalList.fromMask(time, track.ax_abs < AX_THRESHOLD)
    intvals = intvals.merge(1.0)  # smooth
    intvals = intvals.intersect(track.alive_intervals)
    for st, end in intvals:
      index = report.addInterval([st, end])
      report.set(index, 'target', 'ax avg', track.ax_abs[st:end].mean())
      report.set(index, 'target', 'ax std', track.ax_abs[st:end].std())
      report.set(index, 'target', 'ax min', track.ax_abs[st:end].min())
      report.set(index, 'target', 'ax max', track.ax_abs[st:end].max())
      report.set(index, 'ego vehicle', 'speed', ego_motion.vx[st:end].mean())
    return report
  
  def search(self, report):
    self.batch.add_entry(report, result=self.PASSED)
    return
