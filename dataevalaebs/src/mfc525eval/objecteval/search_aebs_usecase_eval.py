# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
    dep = {
        'calc_aebs_usecase_eval': "calc_aebs_usecase_eval@aebs.fill"
    }

    def fill(self):
        common_time, aebs_eval = self.modules.fill(self.dep['calc_aebs_usecase_eval'])
        event_votes = 'AEBS Usecase'
        votes = self.batch.get_labelgroups(event_votes)
        report = Report(cIntervalList(common_time), 'AEBS Usecase', votes = votes)
        batch = self.get_batch()

        qua_group = 'AEBS Usecase check'
        quas = batch.get_quanamegroup(qua_group)
        report.setNames(qua_group, quas)
        
        idx = report.addInterval((0,common_time.size))#hier soll der Intervall berechnet werden 
        report.vote(idx, event_votes, "AEBS Usecase eval")
        report.set(idx, qua_group, 'ego_vx_at_warning', aebs_eval['ego_vx_at_warning'])
        report.set(idx, qua_group, 'aebs_obj_vx_at_warning', aebs_eval['aebs_obj_vx_at_warning'])
        report.set(idx, qua_group, 'dx_warning', aebs_eval['dx_warning'])
        report.set(idx, qua_group, 'dx_braking', aebs_eval['dx_braking'])
        report.set(idx, qua_group, 'dx_emergency', aebs_eval['dx_emergency'])
        report.set(idx, qua_group, 't_warning', aebs_eval['t_warning'])
        report.set(idx, qua_group, 'dx_stopping', aebs_eval['dx_stopping'])
        report.set(idx, qua_group, 'ego_vx_stopping', aebs_eval['ego_vx_stopping'])
        return report

    def search(self, report):
        self.batch.add_entry(report)
        return