# -*- dataeval: init -*-

import os

import matplotlib
import copy

from reportgen.kbendrun_conti_00_daily.reportgen_kbendrun_conti_daily import RESET_TABLE
from sqlalchemy import true

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from reportlab.lib import colors
from reportlab.platypus import Image, Spacer, PageBreak, Table, NextPageTemplate, FrameBreak
from reportlab.lib.pagesizes import cm

from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph, NonEmptyTableWithHeader, \
    italic, bold, grid_table_style
from pyutils.math import round2
from config.interval_header import cIntervalHeader
from measproc.batchsqlite import str_cell

from aebs.par import aebs_classif
from reportgen.common.analyze import Analyze
from reportgen.common.summaries import EventSummary, Summary, PIC_DIR
from reportgen.common.clients import Client, TrackNavigator, VideoNavigator
from reportgen.common.utils import vector2scalar
from aebs.fill.calc_radar_aebs_phases import Calc as Flr25Calc

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

ACC_DIRK_EVENT = None
#ACC_BREAKPEDAL_EVENTS = None
ACC_BRAKE_OVERHEAT = None
ACC_UNEXP_STRONG_BRAKE = None
ACC_SHUTDOWN = None
ACC_JERK_EVENT = None
#ACC_ECO_DRIVE_EVENTS = None
#ACC_EVAL_OVERREACTION_EVENTS = None
#ACC_TORQUE_REQUEST_EVENTS = None
#ACC_STRONG_BRAKE_REQ_EVENTS = None
#ACC_TAKE_OVER_REQ_EVENTS = None


class AebsAnalyze(Analyze):
    optdep = dict(
        acc_dirk_events='analyze_acc_dirk_events-last_entries@acceval',
        #acc_brakepedal_events='analyze_acc_brakepedal_override-last_entries@acceval',
        #acc_eco_drive_events='analyze_acc_eco_drive_events-last_entries@acceval',
        #acc_eval_overreaction_events='analyze_acc_eval_overreaction-last_entries@acceval',
        #acc_torque_request_events='analyze_acc_torque_request-last_entries@acceval',
        acc_brake_overheat_events='analyze_acc_overheat-last_entries@acceval',
        acc_unexp_strong_brake='analyze_acc_braking-last_entries@acceval',
        acc_shutdown_events='analyze_acc_shutdown-last_entries@acceval',
        acc_jerk_events='analyze_acc_jerk-last_entries@acceval',
        #acc_strong_brake_req_events='analyze_acc_strong_brake_req-last_entries@acceval',
        #acc_take_over_req_events='analyze_acc_take_over_req-last_entries@acceval',
        dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
        dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
        dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
        dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@mfc525eval.daytime',
        # TODO Get signal for day time
    )

    query_files = {
        'acc_events': abspath('../../acceval/events_inttable_merged.sql'),
    }

    def fill(self):
        self.view_name = self.batch.create_table_from_last_entries(
            start_date=self.start_date, end_date=self.end_date)

        story = intro(
            "ACC field test evaluation report",
            """
            This is an automatically generated report, based on field tests with
            simultaneously measured forward-looking radar (FLR25).<br/>
            <br/>
            The output signals of ACC are analyzed and the
            relevant events are collected in this report.<br/>
            Results are presented in table format first, followed by the detailed
            overview of the individual events.<br/>
            """
        )
        story.append(PageBreak())
        story.extend(toc())
        story.append(PageBreak())

        story.extend(self.overall_summary())
        story.extend(self.explanation())
        summaries = [AccDirkEventSummary(self.batch, self.view_name),
                     #AccBrakepedalEventSummary(self.batch, self.view_name),
                     #AccEcoDriveEventSummary(self.batch, self.view_name),
                     #AccOverreactionEventSummary(self.batch, self.view_name),
                     #AccTorqueRequestEventSummary(self.batch, self.view_name),
                     #AccStrongBrakeRequestEventSummary(self.batch, self.view_name),
                     AccShutdownEventSummary(self.batch, self.view_name),
                     AccBrakeOverheatingEventSummary(self.batch, self.view_name),
                     AccJerkEventSummary(self.batch, self.view_name),
                     AccUnexpectedBrakingSummary(self.batch, self.view_name),]
                     #AccTakeOverRequestEventSummary(self.batch, self.view_name)]
        story.extend(self.summaries(summaries))
        story.extend(self.warnings(summaries))
        return story

    def overall_summary(self):
        def one_summary(story, start_date, end_date, index_fill):
            if start_date != end_date and start_date == '2000-01-01' and end_date == '2050-01-01':
                start_date, end_date = self.batch.get_measdate()
            # analyzed period - TODO: determine from measurement dates if not specified
            if start_date is not None and end_date is not None:
                from_to = '%s - %s' % (start_date, end_date)
            elif start_date is None and end_date is None:
                from_to = 'whole duration'
            elif start_date is None:
                from_to = 'until %s' % end_date
            else:  # end_date is None:
                from_to = 'from %s' % start_date
            story += [Paragraph('Analyzed time period: %s' % from_to),
                      Spacer(width=1 * cm, height=0.2 * cm), ]

            # driven distance and duration
            if (self.optdep['dur_vs_roadtype'] in self.passed_optdep and
                    self.optdep['dist_vs_roadtype'] in self.passed_optdep):
                roadt_dur = index_fill(self.modules.fill(self.optdep['dur_vs_roadtype']))
                roadt_dist = index_fill(self.modules.fill(self.optdep['dist_vs_roadtype']))

                # distance
                if roadt_dist.total > 0.0:
                    calc_dist_perc = lambda d: int(round2(d / roadt_dist.total * 100.0, 5.0))
                    story += [Paragraph(
                        'Total mileage: %s (ca. %d%% city, %d%% rural, %d%% highway)' %
                        (bold('%.1f km' % roadt_dist.total),
                         calc_dist_perc(roadt_dist['city']),
                         calc_dist_perc(roadt_dist['rural']),
                         calc_dist_perc(roadt_dist['highway']))), ]
                else:
                    story += [Paragraph('Total mileage: %s' % bold('%.1f km' % roadt_dist.total))]
                # duration
                if roadt_dur.total > 0.25:
                    calc_dist_perc = lambda d: int(round2(d / roadt_dur.total * 100.0, 5.0))
                    story += [Paragraph(
                        'Total duration: %s (ca. %d%% standstill, %d%% city, %d%% rural, %d%% highway)' %
                        (bold('%.1f hours' % roadt_dur.total),
                         calc_dist_perc(roadt_dur['ego stopped']),
                         calc_dist_perc(roadt_dur['city']),
                         calc_dist_perc(roadt_dur['rural']),
                         calc_dist_perc(roadt_dur['highway']))), ]
                else:
                    story += [Paragraph('Total duration: %s' % bold('%.1f hours' % roadt_dur.total))]
            else:
                self.logger.warning('Road type statistics not available')
                story += [Paragraph('Total duration: n/a'),
                          Paragraph('Total mileage: n/a'), ]
            # engine running
            if self.optdep['dur_vs_engine_onoff'] in self.passed_optdep:
                engine_dur = index_fill(self.modules.fill(self.optdep['dur_vs_engine_onoff']))
                if 'roadt_dur' in locals():
                    # plau check for durations of different sources
                    if roadt_dur.total > 0.25 and abs(1.0 - engine_dur.total / roadt_dur.total) > 0.02:  # 2% tolerance
                        self.logger.error("Different duration results: %.1f h (engine state) "
                                          "vs. %.1f h (road type)" % (engine_dur.total, roadt_dur.total))
                # duration
                if engine_dur.total > 0.0:
                    story += [Paragraph(
                        'Total duration: %.1f hours (%.1f%% engine running, %.1f%% engine off)' %
                        (engine_dur.total, 100.0 * engine_dur['yes'] / engine_dur.total,
                         100.0 * engine_dur['no'] / engine_dur.total)), ]
                else:
                    story += [Paragraph('Total duration: %.1f hours' % engine_dur.total)]
            else:
                self.logger.warning('Engine state statistics not available')
                story += [Paragraph('Total duration: n/a'), ]
            # daytime
            if self.optdep['dur_vs_daytime'] in self.passed_optdep:
                daytime_dur = index_fill(self.modules.fill(self.optdep['dur_vs_daytime']))
                if 'roadt_dur' in locals():
                    # plau check for durations of different sources
                    if roadt_dur.total > 0.25 and abs(1.0 - daytime_dur.total / roadt_dur.total) > 0.02:  # 2% tolerance
                        self.logger.error("Different duration results: %.1f h (daytime) "
                                          "vs. %.1f h (road type)" % (daytime_dur.total, roadt_dur.total))
                # duration
                if daytime_dur.total > 0.0:
                    calc_dist_perc = lambda d: int(round2(d / daytime_dur.total * 100.0, 5.0))
                    story += [Paragraph(
                        'Total duration: %.1f hours (ca. %d%% day, %d%% night, %d%% dusk)' %
                        (daytime_dur.total,
                         calc_dist_perc(daytime_dur['day']),
                         calc_dist_perc(daytime_dur['night']),
                         calc_dist_perc(daytime_dur['dusk']))), ]
                else:
                    story += [Paragraph('Total duration: %.1f hours' % daytime_dur.total)]
            else:
                self.logger.warning('Daytime statistics not available')
                story += [Paragraph('Total duration: n/a'), ]
            # common remark
            story += [Paragraph(italic('Remark: Percentage values with "ca." are '
                                       'rounded to nearest 5.'), fontsize=8),
                      Spacer(width=1 * cm, height=0.2 * cm), ]

            # Radar Reset event table
            if (self.optdep['acc_dirk_events'] in self.passed_optdep):
                reset_ei_ids = index_fill(self.modules.fill(self.optdep['acc_dirk_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['acc_events'])
                acc_dirk_table_internal = self.batch.get_table_dict(header1, reset_ei_ids,
                                                                    sortby=[('measurement', True),
                                                                            ('start [s]', True)])
                global ACC_DIRK_EVENT
                ACC_DIRK_EVENT = acc_dirk_table_internal
                story += [Paragraph('Total number of acc dirk events: %d' % len(ACC_DIRK_EVENT))]
            """
            #ACC Brakepedal Event
            if (self.optdep['acc_brakepedal_events'] in self.passed_optdep):
                reset_ei_ids = index_fill(self.modules.fill(self.optdep['acc_brakepedal_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['acc_events'])
                acc_brakepedal_table_internal = self.batch.get_table_dict(header1, reset_ei_ids,
                                                                          sortby=[('measurement', True),
                                                                                  ('start [s]', True)])
                global ACC_BREAKPEDAL_EVENTS
                ACC_BREAKPEDAL_EVENTS = acc_brakepedal_table_internal
                story += [Paragraph('Total number of acc brakepedal events: %d' % len(ACC_BREAKPEDAL_EVENTS))]
           
            #ACC echo drive
            if (self.optdep['acc_eco_drive_events'] in self.passed_optdep):
                num_of_obj_ei_ids = index_fill(self.modules.fill(self.optdep['acc_eco_drive_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['acc_events'])
                acc_eco_drive_table_internal = self.batch.get_table_dict(header1, num_of_obj_ei_ids,
                                                                         sortby=[('measurement', True),
                                                                                 ('start [s]', True)])
                global ACC_ECO_DRIVE_EVENTS
                ACC_ECO_DRIVE_EVENTS = acc_eco_drive_table_internal
                story += [Paragraph('Total number of acc eco drive events: %d' % len(ACC_ECO_DRIVE_EVENTS))]

            # lane change table
            if self.optdep['acc_eval_overreaction_events'] in self.passed_optdep:
                lane_change_ei_ids = index_fill(self.modules.fill(self.optdep['acc_eval_overreaction_events']))
                header = cIntervalHeader.fromFileName(self.query_files['acc_events'])
                acc_eval_overreaction_table = self.batch.get_table_dict(header, lane_change_ei_ids,
                                                                        sortby=[('measurement', True),
                                                                                ('start [s]', True)])
                global ACC_EVAL_OVERREACTION_EVENTS
                ACC_EVAL_OVERREACTION_EVENTS = acc_eval_overreaction_table
                story += [Paragraph('Total number of acc overreaction events: %d' % len(ACC_EVAL_OVERREACTION_EVENTS))]

            if self.optdep['acc_torque_request_events'] in self.passed_optdep:
                lane_quality_ei_ids = index_fill(self.modules.fill(self.optdep['acc_torque_request_events']))
                header = cIntervalHeader.fromFileName(self.query_files['acc_events'])
                acc_torque_request_table = self.batch.get_table_dict(header, lane_quality_ei_ids,
                                                                     sortby=[('measurement', True),
                                                                             ('start [s]', True)])
                global ACC_TORQUE_REQUEST_EVENTS
                ACC_TORQUE_REQUEST_EVENTS = acc_torque_request_table
                story += [Paragraph('Total number of acc torque request events: %d' % len(ACC_TORQUE_REQUEST_EVENTS))]
            """
                #unexpected strong braking events
            if (self.optdep['acc_unexp_strong_brake'] in self.passed_optdep):
                    reset_ei_ids = index_fill(self.modules.fill(self.optdep['acc_unexp_strong_brake']))
                    header1 = cIntervalHeader.fromFileName(self.query_files['acc_events'])
                    acc_unexp_brake_table_internal = self.batch.get_table_dict(header1, reset_ei_ids,
                                                                               sortby=[('measurement', True),
                                                                                       ('start [s]', True)])
                    global ACC_UNEXP_STRONG_BRAKE
                    ACC_UNEXP_STRONG_BRAKE = acc_unexp_brake_table_internal
                    story += [Paragraph(
                        'Total number of acc unexpected strong braking events: %d' % len(ACC_UNEXP_STRONG_BRAKE))]

            #Acc brake overheat
            if (self.optdep['acc_brake_overheat_events'] in self.passed_optdep):
                num_of_obj_ei_ids = index_fill(self.modules.fill(self.optdep['acc_brake_overheat_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['acc_events'])
                acc_brake_overheat_table_internal = self.batch.get_table_dict(header1, num_of_obj_ei_ids,
                                                                         sortby=[('measurement', True),
                                                                                 ('start [s]', True)])
                global ACC_BRAKE_OVERHEAT
                ACC_BRAKE_OVERHEAT = acc_brake_overheat_table_internal
                story += [Paragraph('Total number of acc brake overheat: %d' % len(ACC_BRAKE_OVERHEAT))]

            # Acc shutdown
            if (self.optdep['acc_shutdown_events'] in self.passed_optdep):
                num_of_obj_ei_ids = index_fill(self.modules.fill(self.optdep['acc_shutdown_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['acc_events'])
                acc_shutdown_table_internal = self.batch.get_table_dict(header1, num_of_obj_ei_ids,
                                                                        sortby=[('measurement', True),
                                                                                ('start [s]', True)])
                global ACC_SHUTDOWN
                ACC_SHUTDOWN = acc_shutdown_table_internal
                story += [Paragraph('Total number of acc shutdown events: %d' % len(ACC_SHUTDOWN))]

            # Acc negative jerk
            if (self.optdep['acc_jerk_events'] in self.passed_optdep):
                num_of_obj_ei_ids = index_fill(self.modules.fill(self.optdep['acc_jerk_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['acc_events'])
                acc_jerk_table_internal = self.batch.get_table_dict(header1, num_of_obj_ei_ids,
                                                                        sortby=[('measurement', True),
                                                                                ('start [s]', True)])
                global ACC_JERK_EVENT
                ACC_JERK_EVENT = acc_jerk_table_internal
                story += [Paragraph('Total number of acc Jerk events: %d' % len(ACC_JERK_EVENT))]

            """
            if self.optdep['acc_strong_brake_req_events'] in self.passed_optdep:
                lane_quality_ei_ids = index_fill(self.modules.fill(self.optdep['acc_strong_brake_req_events']))
                header = cIntervalHeader.fromFileName(self.query_files['acc_events'])
                acc_strong_brake_req_table = self.batch.get_table_dict(header, lane_quality_ei_ids,
                                                                       sortby=[('measurement', True),
                                                                               ('start [s]', True)])
                global ACC_STRONG_BRAKE_REQ_EVENTS
                ACC_STRONG_BRAKE_REQ_EVENTS = acc_strong_brake_req_table
                story += [
                    Paragraph('Total number of acc strong brake request events: %d' % len(ACC_STRONG_BRAKE_REQ_EVENTS))]

            if self.optdep['acc_take_over_req_events'] in self.passed_optdep:
                lane_blockage_ei_ids = index_fill(self.modules.fill(self.optdep['acc_take_over_req_events']))
                header = cIntervalHeader.fromFileName(self.query_files['acc_events'])
                acc_take_over_req_table = self.batch.get_table_dict(header, lane_blockage_ei_ids,
                                                                    sortby=[('measurement', True), ('start [s]', True)])
                global ACC_TAKE_OVER_REQ_EVENTS
                ACC_TAKE_OVER_REQ_EVENTS = acc_take_over_req_table
                story += [
                    Paragraph('Total number of acc take over request events: %d' % len(ACC_TAKE_OVER_REQ_EVENTS))]
            """
            return

        story = [IndexedParagraph('Overall summary', style='Heading1')]

        story += [IndexedParagraph('Cumulative results', style='Heading2')]
        index_fill = lambda fill: fill.all
        one_summary(story, self.start_date, self.end_date, index_fill)

        if 'datelist' in self.global_params:
            story += [IndexedParagraph('Latest results', style='Heading2')]
            index_fill = lambda fill: fill.values()[-1]
            middatelist = self.global_params.get('datelist', "").split()
            one_summary(story, middatelist[-1], self.end_date, index_fill)

        story += [PageBreak()]
        return story

    def aebs_event_classification(self):
        story = [IndexedParagraph('AEBS event classification', style='Heading1')]

        m_plot = lambda m: self.module_plot(m,
                                            windgeom="500x300+0+0", width=60.0, height=60.0, unit=1.0, kind='%')
        table_style = [
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]
        story += [Table([
            [m_plot("view_count_vs_phase_stats_flr25-bar_mergedcount@aebseval.classif"),
             m_plot("view_count_vs_movstate_stats_flr25-bar_mergedcount@aebseval.classif")],
            [m_plot("view_count_vs_severity_stats_flr25-bar_mergedcount@aebseval.classif"),
             m_plot("view_count_vs_cause_maingroup_stats_flr25-bar_mergedcount@aebseval.classif")],
        ], style=table_style)]

        story += [PageBreak()]
        return story

    def faults(self, summaries, module_name=None):
        story = [
            IndexedParagraph('FLC25 faults', style='Heading1'),
            NextPageTemplate('LandscapeTable'),
        ]
        if module_name is not None:
            story.insert(1, self.module_plot(module_name))
            story.append(PageBreak())
        for summary in summaries:
            story.append(IndexedParagraph(summary.title, style='Heading2'))
            story.append(summary.get_table(link_pattern=self.EVENT_LINK,
                                           link_heading='Heading2')),
            story.append(PageBreak())
        return story

    def flr25_faults(self, summaries, module_name=None):
        story = [
            IndexedParagraph('FLR25 faults', style='Heading1'),
            NextPageTemplate('LandscapeTable'),
        ]
        if module_name is not None:
            story.insert(1, self.module_plot(module_name))
            story.append(PageBreak())
        for summary in summaries:
            story.append(IndexedParagraph(summary.title, style='Heading2'))
            story.append(summary.get_table(link_pattern=self.EVENT_LINK,
                                           link_heading='Heading2')),
            story.append(PageBreak())
        return story

    def events(self, summary):
        statuses = ['fillFLR25_ACC@aebs.fill']
        statuses.extend(summary.statuses)
        groups = ['FLR25', 'moving', 'stationary', 'stopped']
        groups.extend(summary.groups)

        story = summary.get_tracknav_legend()

        for meas, warnings in summary.iteritems():
            manager = self.clone_manager()
            manager.strong_time_check = False  # TODO: make default behavior with warning
            manager.set_measurement(meas)
            manager.build(summary.modules, status_names=statuses,
                          visible_group_names=groups, show_navigators=False)
            sync = manager.get_sync()
            for warning in warnings:
                title = self.EVENT_LINK % (os.path.basename(meas), warning['start'])
                story.extend([
                    NextPageTemplate(self.warningtemplate),
                    PageBreak(),
                    IndexedParagraph(title, style='Heading2'),
                    FrameBreak(),
                    Paragraph(summary.explanation % warning, style='Normal'),
                ])
                sync.seek(warning['start'])
                manager.set_roi(warning['start'], warning['end'], color='y',
                                pre_offset=5.0, post_offset=5.0)
                for module_name, client in summary.modules.iteritems():
                    story.append(client(sync, module_name))
                    story.append(FrameBreak())
                if summary.modules: story.pop(-1)  # remove last FrameBreak
            manager.close()
        return story


class AccDirkSummary(EventSummary):
    def init(self, batch, view_name):
        data = ACC_DIRK_EVENT

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                acc=vector2scalar(row['ACC event']),
                type=vector2scalar(row['ACC issue type']),
                cause=vector2scalar(row['ACC event cause']),
                counter= row['dirk_red_button'] if row['ACC event'][0] == 'Red Dirk Activate' else row['dirk_green_button'],
                comment=row['comment']
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('acc', 'acc event\n\n'),
            ('counter', 'counter\n\n'),

        ])
        return

class AccNegJerk(EventSummary):
    def init(self, batch, view_name):
        data = ACC_JERK_EVENT

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                acc=vector2scalar(row['ACC event']),
                type=vector2scalar(row['ACC issue type']),
                cause=vector2scalar(row['ACC event cause']),
                comment=row['comment']
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n'),
            ('duration', 'duration\n[s]\n'),
            ('acc', 'acc event\n\n'),

        ])
        return

"""
class AccStrongBrakeRequestSummary(EventSummary):
    def init(self, batch, view_name):
        data = ACC_STRONG_BRAKE_REQ_EVENTS

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                acc=vector2scalar(row['ACC event']),
                type=vector2scalar(row['ACC issue type']),
                cause=vector2scalar(row['ACC event cause']),
                comment=row['comment']
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n'),
            ('duration', 'duration\n[s]\n'),
            ('acc', 'acc event\n\n'),
        ])
        return
"""
class AccUnexpBrakeSummary(EventSummary):
    def init(self, batch, view_name):
        data = ACC_UNEXP_STRONG_BRAKE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                acc=vector2scalar(row['ACC event']),
                type=vector2scalar(row['ACC issue type']),
                cause=vector2scalar(row['ACC event cause']),
                comment=row['comment']
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n'),
            ('duration', 'duration\n[s]\n'),
            ('acc', 'acc event\n\n'),

        ])
        return

class AccShutdown(EventSummary):
    def init(self, batch, view_name):
        data = ACC_SHUTDOWN

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                acc=vector2scalar(row['ACC event']),
                type=vector2scalar(row['ACC issue type']),
                cause=vector2scalar(row['ACC event cause']),
                comment=row['comment']
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n'),
            ('duration', 'duration\n[s]\n'),
            ('acc', 'acc event\n\n'),

        ])
        return
"""
class AccTakeOverRequestSummary(EventSummary):
    def init(self, batch, view_name):
        data = ACC_TAKE_OVER_REQ_EVENTS

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                acc=vector2scalar(row['ACC event']),
                type=vector2scalar(row['ACC issue type']),
                cause=vector2scalar(row['ACC event cause']),
                comment=row['comment']
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n'),
            ('duration', 'duration\n[s]\n'),
            ('acc', 'acc event\n\n'),
        ])
        return


class AccEcoDriveSummary(EventSummary):
    def init(self, batch, view_name):
        data = ACC_ECO_DRIVE_EVENTS

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                acc=vector2scalar(row['ACC event']),
                type=vector2scalar(row['ACC issue type']),
                cause=vector2scalar(row['ACC event cause']),
                comment=row['comment']
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n'),
            ('duration', 'duration\n[s]\n'),
            ('acc', 'acc event\n\n'),
        ])
        return


class AccOverreactionSummary(EventSummary):
    def init(self, batch, view_name):
        data = ACC_EVAL_OVERREACTION_EVENTS

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                acc=vector2scalar(row['ACC event']),
                type=vector2scalar(row['ACC issue type']),
                cause=vector2scalar(row['ACC event cause']),
                comment=row['comment']
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n'),
            ('duration', 'duration\n[s]\n'),
            ('acc', 'acc event\n\n'),
        ])
        return


class AccTorqueRequestSummary(EventSummary):
    def init(self, batch, view_name):
        data = ACC_TORQUE_REQUEST_EVENTS

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                acc=vector2scalar(row['ACC event']),
                type=vector2scalar(row['ACC issue type']),
                cause=vector2scalar(row['ACC event cause']),
                comment=row['comment']
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n'),
            ('duration', 'duration\n[s]\n'),
            ('acc', 'acc event\n\n'),
        ])
        return

class AccBrakepedalSummary(EventSummary):
    def init(self, batch, view_name):
        data = ACC_BREAKPEDAL_EVENTS

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                acc=vector2scalar(row['ACC event']),
                type=vector2scalar(row['ACC issue type']),
                cause=vector2scalar(row['ACC event cause']),
                comment=row['comment']
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n'),
            ('duration', 'duration\n[s]\n'),
            ('acc', 'acc event\n\n'),
        ])
        return
"""

class AccBrkOverheat(EventSummary):
    def init(self, batch, view_name):
        data = ACC_BRAKE_OVERHEAT

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                acc=vector2scalar(row['ACC event']),
                type=vector2scalar(row['ACC issue type']),
                cause=vector2scalar(row['ACC event cause']),
                comment=row['comment']
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n'),
            ('duration', 'duration\n[s]\n'),
            ('acc', 'acc event\n\n'),
        ])
        return

class AccDirkEventSummary(AccDirkSummary):
    title = " ACC Dirk Events Details"
    explanation = """
			   ACC Dirk Event: %s - Event Duration: %s sec, cause: %s
				""" \
                  % ('%(acc)s', '%(duration).2f', '%(cause)s')

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.acc_im, 'ACC track'),
    ]

    extra_modules = [
        ('view_acc_common_signals@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
        ('view_acc_common_signals2@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
    ]

    statuses = ['fillFLR25_ACC@aebs.fill']
    groups = ['FLR25', 'moving', 'stationary', 'stopped']

"""
class AccStrongBrakeRequestEventSummary(AccStrongBrakeRequestSummary):
    title = " ACC Strong Brake Request Events Details"
    explanation = ACC Strong Brake Request Event: %s - Event Duration: %s sec, cause: %s \
                  % ('%(acc)s', '%(duration).2f', '%(cause)s')

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.acc_im, 'ACC track'),
    ]

    extra_modules = [
        ('view_flc25_acc_driveract_hmi-TESTER@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
    ]

    statuses = ['fillFLR25_ACC@aebs.fill']
    groups = ['FLR25', 'moving', 'stationary', 'stopped']
    
"""

class AccUnexpectedBrakingSummary(AccUnexpBrakeSummary):
    title = " ACC Unexpected Strong Braking Events"
    explanation = """
			   ACC unexpected strong braking Event: %s - Event Duration: %s sec, cause: %s
				""" \
                  % ('%(acc)s', '%(duration).2f', '%(cause)s')

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.acc_im, 'ACC track'),
    ]

    extra_modules = [
        ('view_acc_common_signals@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
        ('view_acc_common_signals2@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
    ]

    statuses = ['fillFLR25_ACC@aebs.fill']
    groups = ['FLR25', 'moving', 'stationary', 'stopped']

class AccShutdownEventSummary(AccShutdown):
    title = " ACC Shutdown Events Details"
    explanation = """
			   ACC Shutdown Events : %s - Event Duration: %s sec, cause: %s
				""" \
                  % ('%(acc)s', '%(duration).2f', '%(cause)s')

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.acc_im, 'ACC track'),
    ]

    extra_modules = [
        ('view_acc_common_signals@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
        ('view_acc_common_signals2@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
    ]

    statuses = ['fillFLR25_ACC@aebs.fill']
    groups = ['FLR25', 'moving', 'stationary', 'stopped']

"""
class AccTakeOverRequestEventSummary(AccTakeOverRequestSummary):
    title = " ACC Take Over Request Events Details"
    explanation = ACC Take Over Request Event: %s - Event Duration: %s sec, cause: %s \
                  % ('%(acc)s', '%(duration).2f', '%(cause)s')

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.acc_im, 'ACC track'),
    ]

    extra_modules = [
        ('view_flc25_acc_driveract_hmi-TESTER@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
    ]

    statuses = ['fillFLR25_ACC@aebs.fill']
    groups = ['FLR25', 'moving', 'stationary', 'stopped']


class AccEcoDriveEventSummary(AccEcoDriveSummary):
    title = " ACC Eco Drive Events Details"
    explanation = ACC Eco Drive Event: %s - Event Duration: %s sec, cause: %s \
                  % ('%(acc)s', '%(duration).2f', '%(cause)s')

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.acc_im, 'ACC track'),
    ]

    extra_modules = [
        ('view_flc25_acc_driveract_hmi-TESTER@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
    ]

    statuses = ['fillFLR25_ACC@aebs.fill']
    groups = ['FLR25', 'moving', 'stationary', 'stopped']

"""
class AccBrakeOverheatingEventSummary(AccBrkOverheat):
    title = " ACC Brake Overheat Events Details"
    explanation = """
			   ACC Brake Overheat Events : %s - Event Duration: %s sec, cause: %s
				""" \
                  % ('%(acc)s', '%(duration).2f', '%(cause)s')

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.acc_im, 'ACC track'),
    ]

    extra_modules = [
        ('view_acc_common_signals@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
        ('view_acc_common_signals2@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
    ]

    statuses = ['fillFLR25_ACC@aebs.fill']
    groups = ['FLR25', 'moving', 'stationary', 'stopped']

class AccJerkEventSummary(AccNegJerk):
    title = " ACC Negative Jerk Events Details"
    explanation = """
			   ACC Jerk Events : %s - Event Duration: %s sec, cause: %s
				""" \
                  % ('%(acc)s', '%(duration).2f', '%(cause)s')

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.acc_im, 'ACC track'),
    ]

    extra_modules = [
        ('view_acc_common_signals@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
        ('view_acc_common_signals2@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
    ]

    statuses = ['fillFLR25_ACC@aebs.fill']
    groups = ['FLR25', 'moving', 'stationary', 'stopped']

"""
class AccOverreactionEventSummary(AccOverreactionSummary):
    title = " ACC Overreaction Events Details"
    explanation = ACC Overreaction Eco Drive Event: %s - Event Duration: %s sec, cause: %s \
                  % ('%(acc)s', '%(duration).2f', '%(cause)s')

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.acc_im, 'ACC track'),
    ]

    extra_modules = [
        ('view_flc25_acc_driveract_hmi-TESTER@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
    ]

    statuses = ['fillFLR25_ACC@aebs.fill']
    groups = ['FLR25', 'moving', 'stationary', 'stopped']


class AccTorqueRequestEventSummary(AccTorqueRequestSummary):
    title = " ACC Torque Request Events Details"
    explanation = ACC Torque Request Event: %s - Event Duration: %s sec, cause: %s\
                  % ('%(acc)s', '%(duration).2f', '%(cause)s' )
    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.acc_im, 'ACC track'),
    ]

    extra_modules = [
        ('view_flc25_acc_driveract_hmi-TESTER@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
    ]

    statuses = ['fillFLR25_ACC@aebs.fill']
    groups = ['FLR25', 'moving', 'stationary', 'stopped']

class AccBrakepedalEventSummary(AccBrakepedalSummary):
    title = " ACC Brakepedal Events Details"
    explanation = ACC Brakepedal Event: %s - Event Duration: %s sec, cause: %s \
                  % ('%(acc)s', '%(duration).2f', '%(cause)s')

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.acc_im, 'ACC track'),
    ]

    extra_modules = [
        ('view_flc25_acc_driveract_hmi-TESTER@acceval',
         Client('view_flc25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
    ]

    statuses = ['fillFLR25_ACC@aebs.fill']
    groups = ['FLR25', 'moving', 'stationary', 'stopped']
    
"""

if __name__ == '__main__':
    from reportgen.common.main import main

    main(os.path.abspath(__file__))
