# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report
import numpy as np

init_params = {
    'flr25': dict(
        phases='calc_radar_fcw_phases-flr25@aebs.fill',
        algo='FLR25 Warning',
        opt_dep={
            'egospeedstart': 'set_egospeed-start@egoeval',
            'aebtrack': 'set_flr25_aeb_track@trackeval'
        }),
}


class Search(iSearch):
    dep = {
        'phases': None,  # TBD in init()
    }
    optdep = None

    def init(self, phases, algo, opt_dep):
        self.optdep = opt_dep
        self.dep['phases'] = phases
        self.algo = algo
        return

    def fill(self):
        phases = self.modules.fill(self.dep['phases'])

        phase_votes = 'FCW cascade phase'
        algo_votes = 'AEBS algo'
        votes = self.batch.get_labelgroups(phase_votes, algo_votes)
        report = Report(cIntervalList(phases.time), 'FCW warnings', votes=votes)
        exclusive, cascade_phases = votes[phase_votes]

        levels = 5
        jumps, warnings, boolean_state = phases.merge_phases(levels)
        for jump, interval in zip(jumps, warnings):
            idx = report.addInterval(interval)
            report.vote(idx, algo_votes, self.algo)
            if boolean_state:
                report.vote(idx, phase_votes, cascade_phases[len(jump)])
            else:
                report.vote(idx, phase_votes, cascade_phases[len(jump) - 1])

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
