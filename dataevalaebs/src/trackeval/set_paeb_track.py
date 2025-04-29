# -*- dataeval: init -*-

from collections import namedtuple

from interface.Interfaces import iCalc
from aebs.labeling.track import labelMovState, labelAssoState

class Calc(iCalc):
  dep = namedtuple('Dep', ['paebs'])('fill_flc25_paebs_aoaoutput_tracks@aebs.fill')

  def __call__(self, report):
    batch = self.get_batch()
    moving_votes = 'moving state' # labelMovState
    asso_votes = 'asso state'     # labelAssoState
    problem_votes = 'PAEBS problem'
    votes = batch.get_labelgroups(moving_votes, asso_votes, problem_votes)
    report.addVoteGroups(votes)

    qua_group = 'target'
    quas = batch.get_quanamegroup(qua_group)
    report.setNames(qua_group, quas)

    t = report.intervallist.Time
    paebs = self.get_modules().fill(self.dep.paebs)
    paebs = paebs.rescale(t)

    for ind, paeb in paebs.items():

        for idx, (start, end) in report.iterIntervalsWithId():
            labelMovState(report, idx, paeb, (start, start + 1), wholetime=False)
            # labelAssoState(report, idx, paeb, (start, start + 1), wholetime=False)

            report.set(idx, qua_group, 'dx start', paeb.dx[start])
            report.set(idx, qua_group, 'vx start', paeb.vx[start])
            try:
                paeb_start = paeb.get_selection_timestamp(start)
            except ValueError:
                report.vote(idx, problem_votes, 'warning w/o object')
            else:
                report.set(idx, qua_group, 'dx paeb', paeb.dx[paeb_start])
                duration = t[start] - t[paeb_start]
                report.set(idx, qua_group, 'pure paeb duration', duration)
    return
