# -*- dataeval: init -*-
import sys

from interface.Interfaces import iAnalyze

init_params = {
  'all': dict(date=None, algo='SIL KB AEBS')
}

class Analyze(iAnalyze):
  def init(self, date, algo):
    self.date = date
    self.algo = algo
    return

  def fill(self):
    batch = self.get_batch()
    view_name = batch.create_table_from_last_entries(date=self.date)

    ids = [idx for idx,  in batch.query("""
      SELECT entryintervals.id FROM %s en
        JOIN entryintervals ON
             entryintervals.entryid = en.id
        JOIN modules ON
             modules.id = en.moduleid

        JOIN interval2label phase_i2l ON
                            phase_i2l.entry_intervalid = entryintervals.id
        JOIN labels phase ON
                    phase.id = phase_i2l.labelid
        JOIN labelgroups phase_labelgroups ON
                         phase_labelgroups.id = phase.groupid

        JOIN interval2label algo_i2l ON
                            algo_i2l.entry_intervalid = entryintervals.id
        JOIN labels algo ON
                    algo.id = algo_i2l.labelid
        JOIN labelgroups algo_labelgroups ON
                         algo_labelgroups.id = algo.groupid

      WHERE modules.class = :class_name
        AND en.title = :title
        AND phase_labelgroups.name = :phase_group
        AND phase.name != :phase
        AND phase_labelgroups.name = :phase_group
        AND phase.name != :phase
        AND algo_labelgroups.name = :algo_group
        AND algo.name = :algo
      """ % view_name,

      class_name='dataevalaebs.search_aebs_warning.Search',
      title='AEBS-warnings',
      phase_group='KB AEBS suppression phase',
      phase='cancelled',
      algo_group='AEBS algo',
      algo=self.algo,
    )]
    print >> sys.stderr, '%d intervalls are added' % len(ids)
    sys.stderr.flush()
    return view_name, ids

  def analyze(self, view_name, ids):
    self.interval_table.addIntervals(ids)
    return

