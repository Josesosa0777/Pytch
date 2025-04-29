# -*- dataeval: init -*-

import os

import matplotlib
import copy

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

AEBS_TABLE = None
WL_TABLE = None
ABS_AND_RSP_TABLE = None
P21_OR_P22_DIFF_TABLE = None
NO_BRAKING_TABLE = None
WHEELSPEED_SUSPICIOUS_TABLE = None
ILVL_OUT_DRIVING_LEVEL_TABLE = None

class AebsAnalyze(Analyze):
    optdep = dict(
        aebs_events='analyze_events_merged_FLR25-last_entries@aebseval',
        wl_active='analyze_trailer_wl_active-last_entries@trailereval',
        abs_and_rsp_active="analyze_trailer_abs_and_rsp_active-last_entries@trailereval",
        p21_or_p22_diff="analyze_trailer_p21_or_p22_diff-last_entries@trailereval",
        no_braking="analyze_trailer_no_braking-last_entries@trailereval",
        wheelspeed_suspicious="analyze_trailer_wheelspeed_suspicious-last_entries@trailereval",
        ilvl_out_of_driving_level="analyze_trailer_ilvl_out_of_driving_level-last_entries@trailereval",
        count_vs_aebs_severity='view_count_vs_severity_stats_flr25-print_mergedcount@aebseval.classif',
        smess_faults='analyze_smess_faults-last_entries@flr20eval.faults',
        a087_faults='analyze_a087_faults-last_entries@flr20eval.faults',  # TODO merge crash event script
        flc20_spec_statuses='analyze_issues-last_entries@mfc525eval.sensorstatus',
        dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
        dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
        dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
        dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@mfc525eval.daytime',
        # TODO Get signal for day time
        dur_vs_inlane_tr0='view_quantity_vs_inlane_flr20_tr0_stats-print_duration@trackeval.inlane',
        dur_vs_inlane_tr0_fused='view_quantity_vs_inlane_flr20_tr0_fused_stats-print_duration@trackeval.inlane',
        dist_vs_inlane_tr0='view_quantity_vs_inlane_flr20_tr0_stats-print_mileage@trackeval.inlane',
        dist_vs_inlane_tr0_fused='view_quantity_vs_inlane_flr20_tr0_fused_stats-print_mileage@trackeval.inlane',
    )

    query_files = {
        'aebs_events': abspath('../../aebseval/events_inttable.sql'),
        'wl_active': abspath('../../trailereval/trailer_evaluation_inttable.sql'),
    }

    def fill(self):
        self.view_name = self.batch.create_table_from_last_entries(
            start_date=self.start_date, end_date=self.end_date)

        story = intro(
            "GTATRL 13045 automatic field test evaluation report",
            """ """
        )
        story.append(PageBreak())
        story.extend(toc())
        story.append(PageBreak())

        story.extend(self.overall_summary())
        story.extend(self.explanation())
        summaries = [WlSummary(self.batch, self.view_name),FASummary(self.batch, self.view_name),P21P22Summary(self.batch, self.view_name),
                     NBSummary(self.batch, self.view_name),WSSummary(self.batch, self.view_name), DLSummary(self.batch, self.view_name)]
        story.extend(self.summaries(summaries))
        story.extend(self.warnings(summaries))
        return story

    def overall_summary(self):
        def one_summary(story, start_date, end_date, index_fill):
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

            # in-lane obstacle detected
            # if (self.optdep['dur_vs_inlane_tr0'] in self.passed_optdep and
            #         self.optdep['dur_vs_inlane_tr0_fused'] in self.passed_optdep and
            #         self.optdep['dist_vs_inlane_tr0'] in self.passed_optdep and
            #         self.optdep['dist_vs_inlane_tr0_fused'] in self.passed_optdep and
            #         'roadt_dur' in locals() and 'roadt_dist' in locals()):
            #     if roadt_dur.total > 0.25 and roadt_dist.total > 0.0:
            #         inlane_dur = index_fill(self.modules.fill(self.optdep['dur_vs_inlane_tr0']))
            #         inlane_fused_dur = index_fill(self.modules.fill(self.optdep['dur_vs_inlane_tr0_fused']))
            #         inlane_dist = index_fill(self.modules.fill(self.optdep['dist_vs_inlane_tr0']))
            #         inlane_fused_dist = index_fill(self.modules.fill(self.optdep['dist_vs_inlane_tr0_fused']))
            #         inlane_dur_perc = inlane_dur.total / roadt_dur.total * 100.0
            #         inlane_fused_dur_perc = inlane_fused_dur.total / roadt_dur.total * 100.0
            #         inlane_dist_perc = inlane_dist.total / roadt_dist.total * 100.0
            #         inlane_fused_dist_perc = inlane_fused_dist.total / roadt_dist.total * 100.0
            #         story += [Paragraph('In-lane obstacle presence: %.0f%% / %.0f%% (duration / mileage)' % (
            #         inlane_dur_perc, inlane_dist_perc)),
            #                   Paragraph('Fused in-lane obstacle presence: %.0f%% / %.0f%% (duration / mileage)' % (
            #                   inlane_fused_dur_perc, inlane_fused_dist_perc)),
            #                   Spacer(width=1 * cm, height=0.2 * cm), ]
            #     else:
            #         story += [Paragraph('In-lane obstacle presence: n/a'),
            #                   Paragraph('Fused in-lane obstacle presence: n/a'),
            #                   Spacer(width=1 * cm, height=0.2 * cm), ]
            # else:
            #     self.logger.warning('In-lane obstacle presence not available')
            #     story += [Paragraph('In-lane obstacle presence: n/a'),
            #               Paragraph('Fused in-lane obstacle presence: n/a'),
            #               Spacer(width=1 * cm, height=0.2 * cm), ]

            if self.optdep['wl_active'] in self.passed_optdep:
                wl_active_ei_ids = index_fill(self.modules.fill(self.optdep['wl_active']))
                header = cIntervalHeader.fromFileName(self.query_files['wl_active'])
                table = self.batch.get_table_dict(header, wl_active_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global WL_TABLE
                WL_TABLE = table
                story += [Paragraph('Total number of WL active events: %d' % len(table))]

            if self.optdep['abs_and_rsp_active'] in self.passed_optdep:
                abs_and_rsp_active_ei_ids = index_fill(self.modules.fill(self.optdep['abs_and_rsp_active']))
                header = cIntervalHeader.fromFileName(self.query_files['wl_active'])
                table = self.batch.get_table_dict(header, abs_and_rsp_active_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global ABS_AND_RSP_TABLE
                ABS_AND_RSP_TABLE = table
                story += [Paragraph('Total number of ABS & RSP Flag active events: %d' % len(table))]

            if self.optdep['p21_or_p22_diff'] in self.passed_optdep:
                p21_or_p22_diff_ei_ids = index_fill(self.modules.fill(self.optdep['p21_or_p22_diff']))
                header = cIntervalHeader.fromFileName(self.query_files['wl_active'])
                table = self.batch.get_table_dict(header, p21_or_p22_diff_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global P21_OR_P22_DIFF_TABLE
                P21_OR_P22_DIFF_TABLE = table
                story += [Paragraph('Total number of P21 or P22 difference events: %d' % len(table))]

            if self.optdep['no_braking'] in self.passed_optdep:
                no_braking_ei_ids = index_fill(self.modules.fill(self.optdep['no_braking']))
                header = cIntervalHeader.fromFileName(self.query_files['wl_active'])
                table = self.batch.get_table_dict(header, no_braking_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global NO_BRAKING_TABLE
                NO_BRAKING_TABLE = table
                story += [Paragraph('Total number of no braking events: %d' % len(table))]

            if self.optdep['wheelspeed_suspicious'] in self.passed_optdep:
                wheelspeed_suspicious_ei_ids = index_fill(self.modules.fill(self.optdep['wheelspeed_suspicious']))
                header = cIntervalHeader.fromFileName(self.query_files['wl_active'])
                table = self.batch.get_table_dict(header, wheelspeed_suspicious_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global WHEELSPEED_SUSPICIOUS_TABLE
                WHEELSPEED_SUSPICIOUS_TABLE = table
                story += [Paragraph('Total number of ABS & RSP Flag active events: %d' % len(table))]

            if self.optdep['ilvl_out_of_driving_level'] in self.passed_optdep:
                ilvl_out_of_driving_level_ei_ids = index_fill(self.modules.fill(self.optdep['ilvl_out_of_driving_level']))
                header = cIntervalHeader.fromFileName(self.query_files['wl_active'])
                table = self.batch.get_table_dict(header, ilvl_out_of_driving_level_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global ILVL_OUT_DRIVING_LEVEL_TABLE
                ILVL_OUT_DRIVING_LEVEL_TABLE = table
                story += [Paragraph('Total number of iLvl out of driving level events: %d' % len(table))]

            # AEBS warning rate
            # if (self.optdep['aebs_events'] in self.passed_optdep and
            #         self.optdep['count_vs_aebs_severity'] in self.passed_optdep):
            #     aebs_ei_ids = index_fill(self.modules.fill(self.optdep['aebs_events']))
            #     header = cIntervalHeader.fromFileName(self.query_files['aebs_events'])
            #     table = self.batch.get_table_dict(header, aebs_ei_ids,
            #                                       sortby=[('measurement', True), ('start [s]', True)])
            #     global AEBS_TABLE
            #     AEBS_TABLE = table
            #
            #     aebs_count = index_fill(self.modules.fill(self.optdep['count_vs_aebs_severity']))
            #
            #     tot_aebs = len(table)
            #     story += [Paragraph('Total number of AEBS events: %d' % tot_aebs)]
            #     if 'roadt_dist' in locals() and roadt_dist.total > 0.0:
            #         tot_rate = float(tot_aebs) / roadt_dist.total * 1000.0
            #         false_rate = float(aebs_count['1-False alarm']) / roadt_dist.total * 5000.0
            #         ques_rate = float(aebs_count['2-Questionable false alarm']) / roadt_dist.total * 400.0
            #         story += [Paragraph('AEBS warning rate - overall: <b>%.1f events / 1000 km</b>' % tot_rate),
            #                   Paragraph('AEBS warning rate - 1-False alarm: <b>%.1f events / 5000 km</b>' % false_rate),
            #                   Paragraph(
            #                       'AEBS warning rate - 2-Questionable false alarm: <b>%.1f events / 400 km</b>' % ques_rate),
            #                   Spacer(width=1 * cm, height=0.2 * cm), ]
            #     else:
            #         story += [Paragraph('AEBS warning rate: n/a'),
            #                   Spacer(width=1 * cm, height=0.2 * cm), ]
            # else:
            #     story += [Paragraph('Total number of AEBS events: n/a'),
            #               Paragraph('AEBS warning rate: n/a'),
            #               Spacer(width=1 * cm, height=0.2 * cm), ]

            # system performance
            # m_plot = lambda m: self.module_plot(m,
            #                                     windgeom="250x200+0+0", width=60.0, height=60.0, unit=1.0, kind='%',
            #                                     overwrite_start_end=True, start_date=start_date, end_date=end_date)
            # table_style = [
            #     ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            #     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            # ]
            # story += [Table([
            #     [m_plot("view_quantity_vs_systemstate_stats_flr25-pie_duration@aebseval.systemstate"),
            #      m_plot("view_quantity_vs_sensorstatus_stats-pie_duration@mfc525eval.sensorstatus")],
            # ], style=table_style)]

            story.append(Spacer(width=1 * cm, height=0.5 * cm))

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

    def events(self, summary):
        statuses = []
        statuses.extend(summary.statuses)
        groups = []
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

class WlactiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = WL_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-NO_LANES@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-NO_LANES@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class FlagActiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = ABS_AND_RSP_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-NO_LANES@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-NO_LANES@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

class DiffSummary(EventSummary):
    def init(self, batch, view_name):
        data = P21_OR_P22_DIFF_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-NO_LANES@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-NO_LANES@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

class NoBrakingSummary(EventSummary):
    def init(self, batch, view_name):
        data = NO_BRAKING_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-NO_LANES@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-NO_LANES@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

class WheelSpeedSuspiciousSummary(EventSummary):
    def init(self, batch, view_name):
        data = WHEELSPEED_SUSPICIOUS_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-NO_LANES@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-NO_LANES@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

class ILVLSummary(EventSummary):
    def init(self, batch, view_name):
        data = ILVL_OUT_DRIVING_LEVEL_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-NO_LANES@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-NO_LANES@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

class WlSummary(WlactiveSummary):
    title = "WL active event details"
    explanation = """ WL active event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    EventSummary.stat_im = Image(os.path.join(PIC_DIR, 'flr25_stationary_legend.png'),
                                 width=0.5 * cm, height=0.5 * cm)
    EventSummary.mov_im = Image(os.path.join(PIC_DIR, 'flr25_moving_legend.png'),
                                width=0.5 * cm, height=0.5 * cm)

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.aeb_im, 'AEB track'),
    ]

    extra_modules = [
        ('view_trailer_wl_active@trailereval',
         Client('WL active', '640x700+0+0', 11, 12, cm)),
    ]

class FASummary(FlagActiveSummary):
    title = "ABS and RSP Flag active events"
    explanation = """BS and RSP Flag Event: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')

    EventSummary.stat_im = Image(os.path.join(PIC_DIR, 'flr25_stationary_legend.png'),
                                 width=0.5 * cm, height=0.5 * cm)
    EventSummary.mov_im = Image(os.path.join(PIC_DIR, 'flr25_moving_legend.png'),
                                width=0.5 * cm, height=0.5 * cm)

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.aeb_im, 'AEB track'),
    ]

    extra_modules = [
        ('view_trailer_abs_and_rsp_active@trailereval',
         Client('ABS and RSP Flag Active', '640x700+0+0', 11, 12, cm)),
    ]

class P21P22Summary(DiffSummary):
    title = "P21 or P22 difference events."
    explanation = """P21 or P22 event: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')

    EventSummary.stat_im = Image(os.path.join(PIC_DIR, 'flr25_stationary_legend.png'),
                                 width=0.5 * cm, height=0.5 * cm)
    EventSummary.mov_im = Image(os.path.join(PIC_DIR, 'flr25_moving_legend.png'),
                                width=0.5 * cm, height=0.5 * cm)

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.aeb_im, 'AEB track'),
    ]

    extra_modules = [
        ('view_trailer_p21_or_p22_diff@trailereval',
         Client('P21 or P22 Diff.', '640x700+0+0', 11, 12, cm)),
    ]

class NBSummary(NoBrakingSummary):
    title = "No Braking event details"
    explanation = """No Braking event: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')

    EventSummary.stat_im = Image(os.path.join(PIC_DIR, 'flr25_stationary_legend.png'),
                                 width=0.5 * cm, height=0.5 * cm)
    EventSummary.mov_im = Image(os.path.join(PIC_DIR, 'flr25_moving_legend.png'),
                                width=0.5 * cm, height=0.5 * cm)

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.aeb_im, 'AEB track'),
    ]

    extra_modules = [
        ('view_trailer_no_braking@trailereval',
         Client('No Braking', '640x700+0+0', 11, 12, cm)),
    ]

class WSSummary(WheelSpeedSuspiciousSummary):
    title = "Wheelspeed Suspicious event details"
    explanation = """Wheelspeed Suspicious event: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')

    EventSummary.stat_im = Image(os.path.join(PIC_DIR, 'flr25_stationary_legend.png'),
                                 width=0.5 * cm, height=0.5 * cm)
    EventSummary.mov_im = Image(os.path.join(PIC_DIR, 'flr25_moving_legend.png'),
                                width=0.5 * cm, height=0.5 * cm)

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.aeb_im, 'AEB track'),
    ]

    extra_modules = [
        ('view_trailer_wheelspeed_suspicious@trailereval',
         Client('Wheelspeed Suspicious', '640x700+0+0', 11, 12, cm)),
    ]

class DLSummary(ILVLSummary):
    title = "iLvl out of driving level event details"
    explanation = """iLvl out of driving level event: %s,  Event Duration: %s""" % ('%(event)s', '%(duration)s')

    EventSummary.stat_im = Image(os.path.join(PIC_DIR, 'flr25_stationary_legend.png'),
                                 width=0.5 * cm, height=0.5 * cm)
    EventSummary.mov_im = Image(os.path.join(PIC_DIR, 'flr25_moving_legend.png'),
                                width=0.5 * cm, height=0.5 * cm)

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.aeb_im, 'AEB track'),
    ]

    extra_modules = [
        ('view_trailer_ilvl_out_of_driving_level@trailereval',
         Client('Wheelspeed Suspicious', '640x700+0+0', 11, 12, cm)),
    ]

if __name__ == '__main__':
    from reportgen.common.main import main

    main(os.path.abspath(__file__))
