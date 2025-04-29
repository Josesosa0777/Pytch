# -*- dataeval: init -*-

import os
import csv

from interface import iView
from datavis.MatplotlibNavigator import MatplotlibNavigator

TEST_SUMMARY_FILE = r"C:\KBData\sandbox\AEBS_C_AREL\temp\09_warndt_max_3.0s_wo_vrel_n_agents\sil_mbt_tc_summary.csv"

class View(iView):
  def check(self):
    assert os.path.isfile(TEST_SUMMARY_FILE), "`%s` does not exist" % TEST_SUMMARY_FILE
    return

  def fill(self):
    arel_on = {}
    arel_off = {}
    # parse file
    with open(TEST_SUMMARY_FILE, 'r') as f:
      reader = csv.DictReader(f, delimiter=';')
      for row in reader:
        name = row['Name']
        value = float( row['t(WP1)'] )
        if 'aOn' in name:
          arel_on[name] = value
        elif 'aOff' in name:
          arel_off[name] = value
        else:
          print 'Warning: unhandled name: %s' %name
    # create warning time differences
    deltas = []
    for name_on, value in arel_on.iteritems():
      name_off = name_on.replace('aOn', 'aOff')
      delta = value - arel_off[name_off]
      deltas.append(delta)
    return deltas

  def view(self, deltas):
    mn = MatplotlibNavigator("Delta time for warning start (t_arel_on - t_arel_off)")
    self.sync.addStaticClient(mn)
    ax = mn.fig.add_subplot(1,1,1)
    ax.hist(deltas)
    return
