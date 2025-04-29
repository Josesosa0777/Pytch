# -*- dataeval: init -*-

import os

import matplotlib
import copy
from reportgen.kbendrun_conti_00_daily.reportgen_kbendrun_conti_daily import RESET_TABLE

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from reportlab.lib import colors
from reportlab.platypus import Image, Spacer, PageBreak, Table, NextPageTemplate, FrameBreak, BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.pagesizes import inch, cm, A4, A3, landscape

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

RESET_TABLE = None
AEBS_TABLE = None
CORRUPT_MEAS_TABLE = None

class AebsAnalyze(Analyze):
    optdep = dict(
        aebs_events='analyze_events_merged_FLR25-last_entries@aebseval',
        camera_reset_events='analyze_flc25_camera_reset_events-last_entries@mfc525eval.faults',
        count_vs_aebs_severity='view_count_vs_severity_stats_flr25-print_mergedcount@aebseval.classif',
        dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
        dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
        dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
        dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@mfc525eval.daytime',
        corrupt_meas_event="analyze_events_to_find_corrupt_meas-last_entries@aebseval",
        # TODO Get signal for day time
        dur_vs_inlane_tr0='view_quantity_vs_inlane_flr20_tr0_stats-print_duration@trackeval.inlane',
        dur_vs_inlane_tr0_fused='view_quantity_vs_inlane_flr20_tr0_fused_stats-print_duration@trackeval.inlane',
        dist_vs_inlane_tr0='view_quantity_vs_inlane_flr20_tr0_stats-print_mileage@trackeval.inlane',
        dist_vs_inlane_tr0_fused='view_quantity_vs_inlane_flr20_tr0_fused_stats-print_mileage@trackeval.inlane',
    )

    query_files = {
        'aebs_events': abspath('../../aebseval/events_inttable.sql'),
        'camera_reset_events': abspath('../../mfc525eval/faults/flc25_camera_reset_inittable.sql'),
        'corrupt_meas_event': abspath('../../aebseval/events_inttable_to_get_corrupt_meas.sql'),
    }

    def analyze(self, story):  # overwritten function to individualize report for Aebs
        doc = self.get_doc('dataeval.simple', pagesize=A4,
                           header="Strictly confidential")
        addPageTemplates(doc)
        doc.multiBuild(story)
        return

    def fill(self):
        self.view_name = self.batch.create_table_from_last_entries(
            start_date=self.start_date, end_date=self.end_date)

        story = intro(
            "MFC field test evaluation report",
            """
			This is an automatically generated report, based on field tests with
			simultaneously measured forward-looking radar (FLR25) and camera (MFC525)
			sensors.<br/>
			<br/>
			The output signals of MFC are analyzed and the
			relevant events are collected in this report.<br/>
			Statistical results are presented first, followed by the detailed
			overview of the individual events.<br/>
			"""
        )
        story.append(PageBreak())
        story.extend(toc())
        story.append(PageBreak())

        story.extend(self.overall_summary())
        story.extend(self.explanation())
        story.extend(self.aebs_event_classification())
        summaries = [Flr25Summary(self.batch, self.view_name)]
        story.extend(self.summaries(summaries))
        story.extend(self.warnings(summaries))
        fault_summaries = [CameraResetTimeline(self.batch, self.view_name)]
        story.extend(self.faults(fault_summaries))
        flc25_corrupt_meas_summary = [CorruptMeasSummary(self.batch, self.view_name)]
        story.extend(self.flc25_corrupt_meas_summary(flc25_corrupt_meas_summary))
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
            # else:
            # self.logger.warning('Road type statistics not available')
            # story += [Paragraph('Total duration: n/a'),
            # Paragraph('Total mileage: n/a'),]
            # engine running
            # if self.optdep['dur_vs_engine_onoff'] in self.passed_optdep:
            # engine_dur = index_fill(self.modules.fill(self.optdep['dur_vs_engine_onoff']))
            # if 'roadt_dur' in locals():
            # plau check for durations of different sources
            # if roadt_dur.total > 0.25 and abs(1.0 - engine_dur.total/roadt_dur.total) > 0.02:  # 2% tolerance
            # self.logger.error("Different duration results: %.1f h (engine state) "
            # "vs. %.1f h (road type)" % (engine_dur.total, roadt_dur.total))
            # duration
            # if engine_dur.total > 0.0:
            # tory += [Paragraph(
            # 'Total duration: %.1f hours (%.1f%% engine running, %.1f%% engine off)'%
            # (engine_dur.total, 100.0 * engine_dur['yes']/engine_dur.total, 100.0 * engine_dur['no']/engine_dur.total)),]
            # else:
            # story += [Paragraph('Total duration: %.1f hours' % engine_dur.total)]
            # else:
            # self.logger.warning('Engine state statistics not available')
            # story += [Paragraph('Total duration: n/a'),]
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
            # else:
            # self.logger.warning('Daytime statistics not available')
            # story += [Paragraph('Total duration: n/a'),]
            # common remark
            story += [Paragraph(italic('Remark: Percentage values with "ca." are '
                                       'rounded to nearest 5.'), fontsize=8),
                      Spacer(width=1 * cm, height=0.2 * cm), ]

            # in-lane obstacle detected
            if (self.optdep['dur_vs_inlane_tr0'] in self.passed_optdep and
                    self.optdep['dur_vs_inlane_tr0_fused'] in self.passed_optdep and
                    self.optdep['dist_vs_inlane_tr0'] in self.passed_optdep and
                    self.optdep['dist_vs_inlane_tr0_fused'] in self.passed_optdep and
                    'roadt_dur' in locals() and 'roadt_dist' in locals()):
                if roadt_dur.total > 0.25 and roadt_dist.total > 0.0:
                    inlane_dur = index_fill(self.modules.fill(self.optdep['dur_vs_inlane_tr0']))
                    inlane_fused_dur = index_fill(self.modules.fill(self.optdep['dur_vs_inlane_tr0_fused']))
                    inlane_dist = index_fill(self.modules.fill(self.optdep['dist_vs_inlane_tr0']))
                    inlane_fused_dist = index_fill(self.modules.fill(self.optdep['dist_vs_inlane_tr0_fused']))
                    inlane_dur_perc = inlane_dur.total / roadt_dur.total * 100.0
                    inlane_fused_dur_perc = inlane_fused_dur.total / roadt_dur.total * 100.0
                    inlane_dist_perc = inlane_dist.total / roadt_dist.total * 100.0
                    inlane_fused_dist_perc = inlane_fused_dist.total / roadt_dist.total * 100.0
                # story += [Paragraph('In-lane obstacle presence: %.0f%% / %.0f%% (duration / mileage)' % (inlane_dur_perc, inlane_dist_perc)),
                # Paragraph('Fused in-lane obstacle presence: %.0f%% / %.0f%% (duration / mileage)' % (inlane_fused_dur_perc, inlane_fused_dist_perc)),
                # Spacer(width=1*cm, height=0.2*cm),]
            # else:
            # story += [Paragraph('In-lane obstacle presence: n/a'),
            # Paragraph('Fused in-lane obstacle presence: n/a'),
            # Spacer(width=1*cm, height=0.2*cm),]
            # else:
            # self.logger.warning('In-lane obstacle presence not available')
            # story += [Paragraph('In-lane obstacle presence: n/a'),
            # Paragraph('Fused in-lane obstacle presence: n/a'),
            # Spacer(width=1*cm, height=0.2*cm),]

            # Radar Reset event table
            if (self.optdep['camera_reset_events'] in self.passed_optdep):
                reset_ei_ids = index_fill(self.modules.fill(self.optdep['camera_reset_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['camera_reset_events'])
                camera_table_internal = self.batch.get_table_dict(header1, reset_ei_ids,
                                                                  sortby=[('measurement', True), ('start [s]', True)])
                global RESET_TABLE
                RESET_TABLE = camera_table_internal

            # AEBS warning rate
            if (self.optdep['aebs_events'] in self.passed_optdep and
                    self.optdep['count_vs_aebs_severity'] in self.passed_optdep):
                aebs_ei_ids = index_fill(self.modules.fill(self.optdep['aebs_events']))
                header = cIntervalHeader.fromFileName(self.query_files['aebs_events'])
                table = self.batch.get_table_dict(header, aebs_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global AEBS_TABLE
                AEBS_TABLE = table
                WARNING_RATING_UNLABEL_CNT = 0
                aebs_count = index_fill(self.modules.fill(self.optdep['count_vs_aebs_severity']))

                for i in range(len(table)):
                    try:
                        if not table[i]['warning rating scale']:
                            WARNING_RATING_UNLABEL_CNT += 1
                    except Exception as e:
                        pass

                tot_aebs = len(table)
                story += [Paragraph('Total number of AEBS events: %d' % tot_aebs)]

                story += [Paragraph('Total unlabeled events : %s' % WARNING_RATING_UNLABEL_CNT),
                          Spacer(width=1 * cm, height=0.2 * cm), ]

                if 'roadt_dist' in locals() and roadt_dist.total > 0.0:
                    tot_rate = float(tot_aebs) / roadt_dist.total * 1000.0
                    false_rate = float(aebs_count['1-False alarm']) / roadt_dist.total * 1000.0
                    ques_rate = float(aebs_count['2-Questionable false alarm']) / roadt_dist.total * 1000.0
                    story += [Paragraph('AEBS warning rate - overall: <b>%.1f events / 1000 km</b>' % tot_rate),
                              Paragraph('AEBS warning rate - 1-False alarm: <b>%.1f events / 1000 km</b>' % false_rate),
                              Paragraph(
                                  'AEBS warning rate - 2-Questionable false alarm: <b>%.1f events / 1000 km</b>' % ques_rate),
                              Spacer(width=1 * cm, height=0.2 * cm), ]
                else:
                    story += [Paragraph('AEBS warning rate: n/a'),
                              Spacer(width=1 * cm, height=0.2 * cm), ]
            else:
                story += [Paragraph('Total number of AEBS events: n/a'),
                          Paragraph('AEBS warning rate: n/a'),
                          Spacer(width=1 * cm, height=0.2 * cm), ]

            if (self.optdep['corrupt_meas_event'] in self.passed_optdep):
                corrupt_meas_ei_ids = index_fill(self.modules.fill(self.optdep['corrupt_meas_event']))
                header1 = cIntervalHeader.fromFileName(self.query_files['corrupt_meas_event'])
                corrupt_meas_table = self.batch.get_table_dict(header1, corrupt_meas_ei_ids,
                                                               sortby=[('measurement', True), ('start [s]', True)])
                global CORRUPT_MEAS_TABLE
                CORRUPT_MEAS_TABLE = corrupt_meas_table

            # system performance
            m_plot = lambda m: self.module_plot(m,
                                                windgeom="250x200+0+0", width=60.0, height=60.0, unit=1.0, kind='%',
                                                overwrite_start_end=True, start_date=start_date, end_date=end_date)
            table_style = [
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]
            story += [Table([
                [m_plot("view_quantity_vs_systemstate_stats_flr25-pie_duration@aebseval.systemstate"),
                 m_plot("view_quantity_vs_sensorstatus_stats-pie_duration@mfc525eval.sensorstatus")],
            ], style=table_style)]

            story.append(Spacer(width=1 * cm, height=0.5 * cm))

            # story += [ Table([
            # [m_plot("view_quantity_vs_left_lane_quality_stats-pie_duration@mfc525eval.laneeval"),
            # m_plot("view_quantity_vs_right_lane_quality_stats-pie_duration@mfc525eval.laneeval")],
            # ], style=table_style) ]

            story += [self.module_plot(
                "view_quantity_vs_camera_reset_stats-bar_count@mfc525eval.faults",
                windgeom="1000x300+0+0", width=50.0, height=50.0, unit=1.0, kind='%')]

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

    def flc25_corrupt_meas_summary(self, summaries, module_name=None):
        story = [
            IndexedParagraph('Corrupt Measurement Summary', style='Heading1'),
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
        statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
        statuses.extend(summary.statuses)
        groups = ['FLC25', 'moving', 'stationary', 'stopped']
        groups.extend(summary.groups)

        story = summary.get_tracknav_legend()

        for meas, warnings in summary.iteritems():
            manager = self.clone_manager()
            manager.strong_time_check = False  # TODO: make default behavior with warning
            manager.set_measurement(meas)
            modules_in_event = copy.deepcopy(summary.modules)
            manager.build(modules_in_event, status_names=statuses,
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
                modules_in_warnings = copy.deepcopy(summary.modules)
                for module_name, client in modules_in_warnings.iteritems():
                    story.append(client(sync, module_name))
                    story.append(FrameBreak())
                if summary.modules: story.pop(-1)  # remove last FrameBreak
            manager.close()
        return story


class AebsSummary(EventSummary):
    def init(self, batch, view_name):
        data = AEBS_TABLE

        for row in data:
            comment_user = str(row['comment'])
            if len(comment_user) > 250:
                comment_user = comment_user[0:249] + '...[to be continued]...'
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                phase=vector2scalar(row['cascade phase']),
                moving=vector2scalar(row['moving state']),
                asso=vector2scalar(row['asso state']),
                speed=row['ego speed [km/h]'],
                target_dx=row['dx [m]'],
                rating=vector2scalar(row['warning rating scale']),
                cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                comment=comment_user
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('phase', 'aebs phase\n\n'),
            ('moving', 'moving\nstate\n'),
            ('asso', 'asso\nstate\n'),
            ('speed', 'ego speed\n[kmph]\n'),
        ])
        return


class CameraResetTimeline(Summary):
    def init(self, batch, view_name):
        data = RESET_TABLE
        self.title = 'Camera Reset event details'
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                reset_reason=row['ResetReason'],
                reset_cntr=row['ResetCounter'],
                comment=row['comment']
            ))

        self.columns.update([
            ('start', 'start [s]\n'),
            ('reset_reason', 'ResetReason\n'),
            ('reset_cntr', 'ResetCounter\n'),
            ('comment', 'Comment\n'),
        ])
        return

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'measurement')
        data = [header]
        for meas, resets in self.iteritems():
            basename = os.path.basename(meas)
            for reset in resets:
                row = [basename, reset['start'], reset['reset_reason'], reset['reset_cntr'], reset['comment']]
                data.append(row)
        return data

    def get_style(self):
        style = [
            ('GRID', (0, 0), (-1, -1), 0.025 * cm, colors.black),
            ('FONT', (0, 0), (-1, 0), '%s-Bold' % self.font_name, self.font_size),
            ('FONT', (0, 1), (-1, -1), self.font_name, self.font_size),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ]
        return style


class Flr25Summary(AebsSummary):
    title = "AEBS event details"
    explanation = """
  <b>Phase</b>: AEBS %s<br/>
  <b>Event Duration</b>: %s sec<br/>
  <b>Event Cause</b>: %s<br/>
  <b>Event Rating</b>: %s<br/>
  Event is triggered because <b>AEBS state</b> was active: warning (%d), partial (%d)
  or emergency (%d) braking.<br/> 
  <b>Comment:</b> %s.
  """\
    % ('%(phase)s', '%(duration).2f', '%(cause)s', '%(rating)s',
       Flr25Calc.WARNING, Flr25Calc.PARTIAL, Flr25Calc.EMERGENCY, '%(comment)s')

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
        ('view_driveract_aebsout@aebseval',
         Client('DriverAct_AebsOut_Plot', '640x700+0+0', 11, 12, cm)),
        ('view_kinematics_FLC25@aebseval',
         Client('Kinematics_Plot', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']

def addPageTemplates(doc):

    # Get Sizes and Positions for Frames on Page
    x, y, width, height = doc.getGeom()
    ext_x, ext_y, ext_width, ext_height = doc.getExtGeom()
    app_x, app_y, app_width, app_height = doc.getAppGeom()
    z_height, z_width = landscape(A3)  # Used for A3 frames, as doc template is set to A4 and not usable for A3 templates

    offset = 58  # Manual adapted margin offset

    z_x = offset
    z_y = offset
    z_width = z_width - 2 * offset
    z_height = z_height - 2 * offset

    _showBoundary = 0

    portrait_frames = [
        Frame(ext_x, y, ext_width, height, id='FullPage'),
    ]

    # Special Frames just for A3 Event Summary View
    landscape_frames = [
        Frame(z_x,
              z_y + 0.9 * z_width,
              z_height,
              0.1 * z_width,
              id='Title'),
        Frame(z_y,
              z_x + 0.7 * z_width,
              z_height,
              0.2 * z_width,
              id='Duartion'),
        Frame(z_y,
              z_x + 0.4 * z_width,
              0.2 * z_height,
              0.3 * z_width,
              id='VideoNav'),
        Frame(z_y,
              z_x,
              0.2 * z_height,
              0.4 * z_width,
              id='TrackNav'),
        Frame(z_y + 0.2 * z_height,
              z_x,
              0.266 * z_height,
              0.6 * z_width,
              id='EgoPlot'),
        Frame(z_y + 0.466 * z_height,
              z_x,
              0.266 * z_height,
              0.6 * z_width,
              id='TargetPlot'),
        Frame(z_y + 0.733 * z_height,
              z_x,
              0.266 * z_height,
              0.6 * z_width,
              id='VehiclePlot'),
    ]

    comparing_frames = [
        Frame(ext_y, x + 0.9 * width, ext_height, 0.1 * width, id='Title', showBoundary=_showBoundary),
        Frame(ext_y, x + 0.8 * width, 0.6 * ext_height, 0.1 * width, id='Duartion', showBoundary=_showBoundary),
        Frame(ext_y, x + 0.5 * width, 0.2 * ext_height, 0.3 * width, id='VideoNav', showBoundary=_showBoundary),
        Frame(ext_y, x, 0.2 * ext_height, 0.5 * width, id='TrackNav', showBoundary=_showBoundary),
        Frame(ext_y + 0.2 * ext_height, x, 0.4 * ext_height, 0.8 * width, id='EgoPlot', showBoundary=_showBoundary),
        Frame(ext_y + 0.6 * ext_height, x, 0.4 * ext_height, 0.9 * width, id='TargetPlot', showBoundary=_showBoundary),
        Frame(ext_y + 1.0 * ext_height, x, 0.4 * ext_height, 0.9 * width, id='VehiclePlot', showBoundary=_showBoundary),
    ]

    landscape_table_frames = [
        Frame(y, x, height, width, id='FullPage'),
    ]

    doc.addPageTemplates([
        PageTemplate(id='Portrait', frames=portrait_frames,
                     onPage=doc.onPortraitPage, pagesize=A4),
        PageTemplate(id='Landscape', frames=landscape_frames,
                     pagesize=landscape(A3)),
        PageTemplate(id='LandscapeTable', frames=landscape_table_frames,
                     onPage=doc.onLandscapePage, pagesize=landscape(A4)),
        PageTemplate(id='Comparing', frames=comparing_frames,
                     onPage=doc.onLandscapePage, pagesize=landscape(A4)),
    ])

    return

class CorruptMeasSummary(Summary):
    def init(self, batch, view_name):
        data = CORRUPT_MEAS_TABLE
        self.title = "Measurement summary"
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                meas_name=row['measurement']
            ))

        return

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'Measurement Name')
        data = [header]
        for meas, resets in self.iteritems():
            for reset in resets:
                row = [reset['meas_name']]
                data.append(row)
        return data

    def get_style(self):
        style = [
            ('GRID', (0, 0), (-1, -1), 0.025 * cm, colors.black),
            ('FONT', (0, 0), (-1, 0), '%s-Bold' % self.font_name, self.font_size),
            ('FONT', (0, 1), (-1, -1), self.font_name, self.font_size),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ]
        return style


if __name__ == '__main__':
    from reportgen.common.main import main

    main(os.path.abspath(__file__))
