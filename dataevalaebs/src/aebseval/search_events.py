# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report

init_params = {
  'kb': dict(
    phases='calc_aebs_phases@aebs.fill',
    algo='FLR21 Prop Warning'),
  'trw': dict(
    phases='calc_trw_aebs_phases@aebs.fill',
    algo='TRW CM'),
  'flr20': dict(
    phases='calc_flr20_aebs_phases-radar@aebs.fill',
    algo='FLR21 Warning'),
  'wabco': dict(
    phases='calc_flr20_aebs_phases-wabco@aebs.fill',
    algo='Wabco Warning'),
  'aebs_c_silolmat': dict(
    phases='calc_aebs_c_silolmat_phases@aebs.fill',
    algo='SIL KB AEBS'),
  'autobox': dict(
    phases='calc_flr20_aebs_phases-autobox@aebs.fill',
    algo='Autobox Warning'),
  'sil': dict(
    phases='calc_aebs_wrapper_phases@silkbaebs',
    algo='SIL KB AEBS'),
  'continental': dict(
    phases='calc_flr20_aebs_phases-continental@aebs.fill',
    algo='ARS430 Warning'),
}


class Search(iSearch):
  dep = {
    'phases': None,  # TBD in init()
  }
  optdep = {
    'egospeedstart': 'set_egospeed-start@egoeval',
    'aebtrack': 'set_flr20_aeb_track@trackeval',
  }
  
  def init(self, phases, algo):
    self.dep['phases'] = phases
    self.algo = algo
    return

  def fill(self):
    phases = self.modules.fill(self.dep['phases'])

    phase_votes = 'AEBS cascade phase'
    algo_votes = 'AEBS algo'
    votes = self.batch.get_labelgroups(phase_votes, algo_votes)
    report = Report(cIntervalList(phases.time), 'AEBS warnings', votes=votes)
    exclusive, cascade_phases = votes[phase_votes]

    levels = 5
    jumps, warnings = phases.merge_phases(levels)
    for jump, interval in zip(jumps, warnings):
      idx = report.addInterval(interval)
      report.vote(idx, algo_votes, self.algo)
      report.vote(idx, phase_votes, cascade_phases[len(jump)-1])

    for qua in 'egospeedstart', 'aebtrack':
      if self.optdep[qua] in self.passed_optdep:
        set_qua_for_report = self.modules.get_module(self.optdep[qua])
        set_qua_for_report(report)
      else:
        self.logger.warning("Inactive module: %s" % self.optdep[qua])
    return report

  def search(self, report):
    self.batch.add_entry(report)
    return
