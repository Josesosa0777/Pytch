# -*- dataeval: init -*-

from collections import namedtuple

from interface.Interfaces import iCalc
from aebs.labeling.track import labelMovState, labelAssoState

class Calc(iCalc):
  dep = namedtuple('Dep', ['aeb'])('fill_flr25_aeb_track@aebs.fill')

  def __call__(self, report):
    batch = self.get_batch()
    moving_votes = 'moving state' # labelMovState
    asso_votes = 'asso state'     # labelAssoState
    problem_votes = 'AEBS problem'
    votes = batch.get_labelgroups(moving_votes, asso_votes, problem_votes)
    report.addVoteGroups(votes)

    qua_group = 'target'
    quas = batch.get_quanamegroup(qua_group)
    report.setNames(qua_group, quas)

    t = report.intervallist.Time
    aeb = self.get_modules().fill(self.dep.aeb)
    aeb = aeb.rescale(t)

    for idx, (start, end) in report.iterIntervalsWithId():
        labelMovState(report, idx, aeb, (start, start + 1), wholetime=False)
        labelAssoState(report, idx, aeb, (start, start + 1), wholetime=False)

        report.set(idx, qua_group, 'dx start', aeb.dx[start])
        report.set(idx, qua_group, 'vx start', aeb.vx[start])
        report.set(idx, qua_group, 'ax start', aeb.ax[start])
        try:
            aeb_start = aeb.get_selection_timestamp(start)
        except ValueError:
            report.vote(idx, problem_votes, 'warning w/o object')
        else:
            report.set(idx, qua_group, 'dx aeb', aeb.dx[aeb_start])
            duration = t[start] - t[aeb_start]
            report.set(idx, qua_group, 'pure aeb duration', duration)
    return
