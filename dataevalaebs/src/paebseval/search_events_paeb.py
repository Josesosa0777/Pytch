# -*- dataeval: init -*-

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, intervalsToMask, maskToIntervals
from measproc.report2 import Report
import numpy as np

init_params = {
    'flc25': dict(
        phases='calc_paebs_phases-flc25@aebs.fill',
        algo='FLC25 Warning',
        track='fill_flc25_paebs_debug@aebs.fill',
        calc_auto_false_pos_rate = 'calc_automated_false_positive_rate@paebseval.classif',
        opt_dep={
            'egospeedstart': 'set_egospeed-start@egoeval',
            # 'paebtrack': 'set_paeb_track@trackeval',
        }
    ),
    'paebs': dict(
        phases='calc_paebs_phases-paebs@aebs.fill',
        algo='FLC25 Warning',
        track='fill_flc25_paebs_debug@aebs.fill',
        calc_auto_false_pos_rate = 'calc_automated_false_positive_rate@paebseval.classif',
        opt_dep={
            'egospeedstart': 'set_egospeed-start@egoeval',
            # 'paebtrack': 'set_flr25_aeb_track@trackeval',
        }
    ),
}


class Search(iSearch):
    dep = {
        'phases': None,  # TBD in init()
    }
    optdep = None

    def init(self, phases, algo, track, calc_auto_false_pos_rate, opt_dep):
        self.optdep = opt_dep
        self.dep['phases'] = phases
        self.dep['track'] = track
        self.dep['calc_auto_false_pos_rate'] = calc_auto_false_pos_rate
        self.algo = algo
        return

    def check(self):
        modules = self.get_modules()
        tracks = modules.fill(self.dep['track'])
        phases = self.modules.fill(self.dep['phases'])
        intervals_auto_false_pos_rate, time_auto_false_rate = self.modules.fill(self.dep['calc_auto_false_pos_rate'])
        return tracks, phases, intervals_auto_false_pos_rate, time_auto_false_rate

    def fill(self, tracks, phases, intervals_auto_false_pos_rate, time_auto_false_rate):

        reports = []

        paebs_track = tracks.rescale(phases.time)[0]

        phase_votes = 'PAEBS cascade phase'  # using same label for PAEBS
        algo_votes = 'PAEBS algo'  # using same label for PAEBS
        mov_state_votes = 'PAEBS moving state'
        source_votes = 'PAEBS source'
        paebs_qua_names = 'PAEBS Debug'
        votes = self.batch.get_labelgroups(
            phase_votes, algo_votes, mov_state_votes, source_votes)
        names = self.batch.get_quanamegroups(paebs_qua_names)

        report = Report(cIntervalList(phases.time), 'PAEBS warnings',
                        votes=votes, names=names)  # using same label for PAEBS
        exclusive, cascade_phases = votes[phase_votes]

        levels = 5
        jumps, warnings = phases.merge_phases(levels)

        for jump, interval in zip(jumps, warnings):
            # Add Interval to SQL-DB
            idx = report.addInterval(interval)
            # Get Moving State
            mov_state_vote = self.defineMovingState(
                paebs_track.motion_state.data[jump][0], not bool(paebs_track.motion_state.mask[jump][0]),
                paebs_track.obj_type.data[jump][0], mov_state_votes, votes)
            # Get Source State
            source_vote = self.defineSource(
                paebs_track.obj_src.data[jump][0], not bool(paebs_track.obj_src.mask[jump][0]), source_votes, votes)
            # Add Votes for Interval to SQL-DB
            report.vote(idx, algo_votes, self.algo)
            report.vote(idx, phase_votes, cascade_phases[len(jump) - 1])
            report.vote(idx, mov_state_votes, mov_state_vote)
            report.vote(idx, source_votes, source_vote)
            # Add Quantities at Interval Start to SQL-DB
            report.set(idx, paebs_qua_names, 'collision probability',
                       paebs_track.collision_prob.data[jump][0])
            report.set(idx, paebs_qua_names, 'ttc',
                       paebs_track.ttc.data[jump][0])
            report.set(idx, paebs_qua_names, 'path distance',
                       paebs_track.dist_path.data[jump][0])
            report.set(idx, paebs_qua_names, 'cascade distance',
                       paebs_track.casc_dist.data[jump][0])
            report.set(idx, paebs_qua_names, 'internal state',
                       paebs_track.internal_state.data[jump][0])
            report.set(idx, paebs_qua_names, 'lane',
                       paebs_track.lane.data[jump][0])
            report.set(idx, paebs_qua_names, 'vx_ref',
                       paebs_track.vx_ref.data[jump][0])
            report.set(idx, paebs_qua_names, 'dx',
                       paebs_track.dx.data[jump][0])
            report.set(idx, paebs_qua_names, 'motion state',
                       paebs_track.motion_state.data[jump][0])
            report.set(idx, paebs_qua_names, 'object type',
                       paebs_track.obj_type.data[jump][0])
            report.set(idx, paebs_qua_names, 'source',
                       paebs_track.obj_src.data[jump][0])
            report.set(idx, paebs_qua_names, 'probability of existance',
                       paebs_track.prob_exist.data[jump][0])
            report.set(idx, paebs_qua_names, 'lane confidence',
                       paebs_track.lane_conf.data[jump][0])
            report.set(idx, paebs_qua_names, 'classification confidence',
                       paebs_track.class_conf.data[jump][0])

        # for qua in 'egospeedstart', 'paebtrack':
        #     if self.optdep[qua] in self.passed_optdep:
        #         set_qua_for_report = self.modules.get_module(self.optdep[qua])
        #         set_qua_for_report(report)
        #     else:
        #         self.logger.warning("Inactive module: %s" % self.optdep[qua])

        for qua in ['egospeedstart']:
            if self.optdep[qua] in self.passed_optdep:
                set_qua_for_report = self.modules.get_module(self.optdep[qua])
                set_qua_for_report(report)
            else:
                self.logger.warning("Inactive module: %s" % self.optdep[qua])

        reports.append(report)
        
        # VRU Detection

        report = Report(cIntervalList(phases.time), 'PAEBS VRU Detection')  # using same label for PAEBS

        try:
            jumps, intervals = self.examineVruDetection(
                [paebs_track._aoa_object_index_0, paebs_track._aoa_object_index_1, paebs_track._aoa_object_index_2])
        except:
            intervals = []

        for interval in intervals:
            idx = report.addInterval(interval)

        reports.append(report)
        
        # Automated false positive rate
        
        report = Report(cIntervalList(time_auto_false_rate), 'PAEBS Automated False Positive') 
        
        for interval in intervals_auto_false_pos_rate:
             idx = report.addInterval(interval)
             
        reports.append(report)

        return reports

    def search(self, reports):

        for report in reports:
            self.batch.add_entry(report)

        return

    def defineMovingState(self, motion_state, motion_state_valid, object_type, mov_state_votes, votes):
        valid_votes = votes[mov_state_votes][1]

        if (motion_state == 4) & (object_type == 3) & motion_state_valid & ('pedestrian crossing' in valid_votes):
            moving_state_vote = 'pedestrian crossing'
        elif (motion_state != 4) & (object_type == 3) & motion_state_valid & ('pedestrian not crossing' in valid_votes):
            moving_state_vote = 'pedestrian not crossing'
        elif (motion_state == 4) & (object_type == 5) & motion_state_valid & ('bicyclist crossing' in valid_votes):
            moving_state_vote = 'bicyclist crossing'
        elif (motion_state != 4) & (object_type == 5) & motion_state_valid & ('bicyclist not crossing' in valid_votes):
            moving_state_vote = 'bicyclist not crossing'
        else:
            moving_state_vote = 'undefined'

        return moving_state_vote

    def defineSource(self, source, source_valid, source_votes, votes):
        valid_votes = votes[source_votes][1]

        if (source == 0) & source_valid & ('Unknown' in valid_votes):
            source_vote = 'Unknown'
        elif (source == 1) & source_valid & ('Radar only' in valid_votes):
            source_vote = 'Radar only'
        elif (source == 2) & source_valid & ('Camera only' in valid_votes):
            source_vote = 'Camera only'
        elif (source == 3) & source_valid & ('Fused' in valid_votes):
            source_vote = 'Fused'
        else:
            source_vote = 'N/A'

        return source_vote

    def examineVruDetection(self, obj_detection_signals):

        tmp_res = np.full_like(obj_detection_signals[0], False, dtype=bool)

        for signal in obj_detection_signals:
            tmp_signal = np.where(signal != 255, True, False)
            tmp_res = tmp_res | tmp_signal

        intervals = maskToIntervals(tmp_res)
        jumps = [[start] for start, end in intervals]

        return jumps, intervals
