# -*- dataeval: init -*-

import interface
import datavis

duration_query = \
"""
SELECT ei.end_time-ei.start_time
FROM entryintervals ei
JOIN entries en ON en.id = ei.entryid
JOIN modules mo ON mo.id = en.moduleid

JOIN interval2label i2l ON i2l.entry_intervalid = ei.id
JOIN labels la ON la.id = i2l.labelid
JOIN labelgroups lg ON lg.id = la.groupid

WHERE mo.class = "dataevalaebs.search_aebs_cascade.Search"
  AND lg.name = "AEBS cascade phase"
  AND la.name = :phase
"""


class View(interface.iView):
  def check(self):
    return

  def fill(self):
    return

  def view(self):
    client = datavis.MatplotlibNavigator(title="AEBS cascade phase durations")
    
    for i_ax, phase_name in enumerate(('warning', 'partial braking', 'emergency braking')):
      ax = client.fig.add_subplot(3, 1, i_ax+1)
      durations = self.batch.query(duration_query, phase=phase_name)
      for i, (dur,) in enumerate(durations):
        ax.plot((i,i), (0.0, dur))
    
    self.sync.addStaticClient(client)
    return
