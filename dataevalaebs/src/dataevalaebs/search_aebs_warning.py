# -*- dataeval: init -*-
from collections import namedtuple

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report
from aebs.fill import calc_aebs_c_sil_phases

init_params = {
  'kb': dict(phases='calc_aebs_phases@aebs.fill', algo='FLR20 Prop Warning'),
  'trw': dict(phases='calc_trw_aebs_phases@aebs.fill', algo='TRW CM'),
  'flr20': dict(phases='calc_flr20_aebs_phases-radar@aebs.fill',
                algo='FLR20 Warning'),
  'aebs_c_silolmat': dict(phases='calc_aebs_c_silolmat_phases@aebs.fill',
                          algo='SIL KB AEBS'),
  'autobox': dict(phases='calc_flr20_aebs_phases-autobox@aebs.fill',
                  algo='Autobox Warning'),
  'AEBS_C_6_1__DEV_GENERAL_8_17_BRAKING': dict(phases='calc_aebs_c_sil_versions_phases-AEBS_C_6_1__DEV_GENERAL_8_17_BRAKING@aebseval.sim',
                  algo='SIL KB AEBS')
}

# expose all available dpvs for SIL simulation
init_params.update(
  ( '%s' %dpv, dict(phases='calc_aebs_c_sil_phases-%s@aebs.fill' %dpv, algo='SIL KB AEBS') ) for dpv in calc_aebs_c_sil_phases.init_params
)


class Search(iSearch):
  def init(self, phases, algo):
    self.dep = namedtuple('Dep', ['phases'])(phases)
    self.aeb = 'set_aeb_track'
    self.egomotion = 'set_ego_speed'
    self.optdep = self.egomotion, self.aeb
    self.algo = algo
    return

  def fill(self):
    modules = self.get_modules()
    phases = modules.fill(self.dep.phases)

    phase_votes = 'AEBS cascade phase'
    algo_votes = 'AEBS algo'
    batch = self.get_batch()
    votes = batch.get_labelgroups(phase_votes, algo_votes)
    report = Report(cIntervalList(phases.time), 'AEBS-warnings', votes=votes)
    exclusive, cascade_phases = votes[phase_votes]

    levels = 5
    jumps, warnings = phases.merge_phases(levels)
    for jump, interval in zip(jumps, warnings):
      idx = report.addInterval(interval)
      report.vote(idx, algo_votes, self.algo)
      report.vote(idx, phase_votes, cascade_phases[len(jump)-1])

    if self.egomotion in self.passed_optdep:
      modules.get_module(self.egomotion)(report)
    if self.aeb in self.passed_optdep:
      modules.get_module(self.aeb)(report)
    return report

  def search(self, report):
    batch = self.get_batch()
    batch.add_entry(report)
    return

