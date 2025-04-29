# -*- dataeval: init -*-

import os
from os.path import expanduser
from collections import defaultdict
import matplotlib
import json
import logging
from collections import OrderedDict

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
from reportgen.common.summaries import Summary, EventSummary, PIC_DIR
from reportgen.common.clients import Client, TrackNavigator, VideoNavigator
from reportgen.common.utils import vector2scalar, vector2scalar2
from aebs.fill.calc_radar_aebs_phases import Calc as Flr25Calc

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

PAEBS_TABLE = None
DTC_TABLE = None
RESET_TABLE = None


class AebsAnalyze(Analyze):
    optdep = dict(
        paebs_events_resim='analyze_paebs_resim_events-last_entries@paebseval.resim',
        aebs_events='analyze_events_merged_FLR25-last_entries@aebseval',
        dtc_events='analyze_flr25_dtc_active_events-last_entries@flr25eval.faults',
        radar_reset_events='analyze_flr25_radar_reset_events-last_entries@flr25eval.faults',
        count_vs_aebs_severity='view_count_vs_severity_stats_flr25-print_mergedcount@aebseval.classif',
        count_vs_paebs_resim_event_severity='view_count_vs_severity_stats_flr25_paebs_resim_event-print_mergedcount@paebseval.classif',
        count_vs_paebs_meas_event_severity='view_count_vs_severity_stats_flr25_paebs_meas_event-print_mergedcount@paebseval.classif',
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
        'paebs_events_resim': abspath('../../paebseval/resim/delta_paebs_resim_events_inttable.sql'),
    }

    def fill(self):
        self.view_name = self.batch.create_table_from_last_entries(
            start_date=self.start_date, end_date=self.end_date)

        story = intro(
            "PAEBS field test evaluation report",
            """
            This is an automatically generated report, based on field tests with
            simultaneously measured forward-looking radar (FLR25) with a camera from baolong.<br/>
            <br/>
            The output signals of PAEBS from resimulation compared to the original measurement are analyzed 
            and the relevant events are colllected in this report.<br/>
            """
        )
        story.append(PageBreak())
        story.extend(toc())
        story.append(PageBreak())

        story.extend(self.overall_summary())
        story.extend(self.explanation())
        summaries = [Flr25Summary(self.batch, self.view_name)]
        story.extend(self.summaries(summaries))
        story.extend(self.warnings(summaries))
        resim_param = [ResimParameters(self.batch, self.view_name, self.global_params['json'])]
        story.extend(self.resim_parameters(resim_param))
        return story

    def summaries(self, summaries, module_name=None):
        story = [
            IndexedParagraph('Warning summary tables', style='Heading1'),
            NextPageTemplate('LandscapeTable'),
        ]
        # common remark
        story += [Paragraph(italic('Remark:'), fontsize=8)]
        story += [Paragraph(italic(
            '1. Positive event start time difference indicates resimulation event occurs after measurement event.'),
            fontsize=8)]
        story += [Paragraph(italic(
            '2. An event consider as "Common Event" if time difference between start & end time is less than or equal to threshold(i.e. 4)'),
            fontsize=8),
            Spacer(width=1 * cm, height=0.2 * cm), ]

        if module_name is not None:
            story.insert(1, self.module_plot(module_name))
            story.append(PageBreak())
        for summary in summaries:
            story.append(IndexedParagraph(summary.title, style='Heading2'))
            story.append(summary.get_table(link_pattern=self.EVENT_LINK,
                                           link_heading='Heading2')),
            story.append(PageBreak())
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

            # Calculate total mileage from resim output csv
            try:
                if (self.optdep['paebs_events_resim'] in self.passed_optdep):
                    paebs_ei_ids = index_fill(self.modules.fill(self.optdep['paebs_events_resim']))
                    header = cIntervalHeader.fromFileName(self.query_files['paebs_events_resim'])
                    table = self.batch.get_table_dict(header, paebs_ei_ids,
                                                      sortby=[('measurement', True), ('start [s]', True)])
                    total_mileage = table[0]['total mileage [km]']
            except:
                total_mileage = 0.0

            # driven distance and duration
            if (self.optdep['dur_vs_roadtype'] in self.passed_optdep and
                    self.optdep['dist_vs_roadtype'] in self.passed_optdep):
                roadt_dur = index_fill(self.modules.fill(self.optdep['dur_vs_roadtype']))
                roadt_dist = index_fill(self.modules.fill(self.optdep['dist_vs_roadtype']))

                # distance
                if roadt_dist.total > 0.0 or total_mileage > 0.0:
                    if total_mileage:
                        calc_dist_perc = lambda d: int(round2(d / total_mileage * 100.0, 5.0))
                        story += [Paragraph(
                            'Total mileage: %s (ca. %d%% city, %d%% rural, %d%% highway)' %
                            (bold('%.1f km' % total_mileage),
                             calc_dist_perc(roadt_dist['city']),
                             calc_dist_perc(roadt_dist['rural']),
                             calc_dist_perc(roadt_dist['highway']))), ]
                    else:
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
            # common remark
            story += [Paragraph(italic('Remark: Percentage values with "ca." are '
                                       'rounded to nearest 5.'), fontsize=8),
                      Spacer(width=1 * cm, height=0.2 * cm), ]

            tot_resim = 0
            tot_paebs = 0
            if (self.optdep['paebs_events_resim'] in self.passed_optdep and
                    self.optdep['count_vs_paebs_resim_event_severity'] in self.passed_optdep and
                    self.optdep['count_vs_paebs_meas_event_severity'] in self.passed_optdep):
                paebs_ei_ids = index_fill(self.modules.fill(self.optdep['paebs_events_resim']))
                header = cIntervalHeader.fromFileName(self.query_files['paebs_events_resim'])
                table = self.batch.get_table_dict(header, paebs_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global PAEBS_TABLE
                PAEBS_TABLE = table

                paebs_count = index_fill(self.modules.fill(self.optdep['count_vs_paebs_meas_event_severity']))
                paebs_resim_count = index_fill(self.modules.fill(self.optdep['count_vs_paebs_resim_event_severity']))

                # tot_paebs = len(table)
                for i, event_data in enumerate(table):
                    if "Resimulation\n Event" in event_data['event source']:
                        tot_resim = tot_resim + 1
                    elif "Measurement\n Event" in event_data['event source']:
                        tot_paebs = tot_paebs + 1
                    elif "Common\n Event" in event_data['event source']:
                        tot_resim = tot_resim + 1
                        tot_paebs = tot_paebs + 1

                # PAEBS endurance details
                story += [Paragraph('Total number of PAEBS events: %d' % tot_paebs)]
                if total_mileage:
                    if 'roadt_dist' in locals() and total_mileage > 0.0:
                        tot_rate = float(tot_paebs) / total_mileage * 1000.0
                        false_rate = float(paebs_count['1-False alarm']) / total_mileage * 5000.0
                        ques_rate = float(paebs_count['2-Questionable false alarm']) / total_mileage * 400.0
                        story += [Paragraph('PAEBS warning rate - overall: <b>%.1f events / 1000 km</b>' % tot_rate),
                                  Paragraph(
                                      'PAEBS warning rate - 1-False alarm: <b>%.1f events / 5000 km</b>' % false_rate),
                                  Paragraph(
                                      'PAEBS warning rate - 2-Questionable false alarm: <b>%.1f events / 400 km</b>' % ques_rate),
                                  Spacer(width=1 * cm, height=0.8 * cm), ]
                    else:
                        story += [Paragraph('PAEBS warning rate: n/a'),
                                  Spacer(width=1 * cm, height=0.8 * cm), ]
                else:
                    if 'roadt_dist' in locals() and roadt_dist.total > 0.0:
                        tot_rate = float(tot_paebs) / roadt_dist.total * 1000.0
                        false_rate = float(paebs_count['1-False alarm']) / roadt_dist.total * 5000.0
                        ques_rate = float(paebs_count['2-Questionable false alarm']) / roadt_dist.total * 400.0
                        story += [Paragraph('PAEBS warning rate - overall: <b>%.1f events / 1000 km</b>' % tot_rate),
                                  Paragraph(
                                      'PAEBS warning rate - 1-False alarm: <b>%.1f events / 5000 km</b>' % false_rate),
                                  Paragraph(
                                      'PAEBS warning rate - 2-Questionable false alarm: <b>%.1f events / 400 km</b>' % ques_rate),
                                  Spacer(width=1 * cm, height=0.8 * cm), ]
                    else:
                        story += [Paragraph('AEBS warning rate: n/a'),
                                  Spacer(width=1 * cm, height=0.8 * cm), ]

                #     Resimulation cumulative result
                # AEBS endurance details
                story += [Paragraph('Total number of PAEBS resim events: %d' % tot_resim)]
                if total_mileage:
                    if 'roadt_dist' in locals() and total_mileage > 0.0:
                        tot_rate = float(tot_resim) / total_mileage * 1000.0
                        false_rate = float(paebs_resim_count['1-False_alarm']) / total_mileage * 5000.0
                        ques_rate = float(paebs_resim_count['2-Questionable_false_alarm']) / total_mileage * 400.0
                        story += [
                            Paragraph('PAEBS resim warning rate - overall: <b>%.1f events / 1000 km</b>' % tot_rate),
                            Paragraph(
                                'PAEBS resim warning rate - 1-False alarm: <b>%.1f events / 5000 km</b>' % false_rate),
                            Paragraph(
                                'PAEBS resim warning rate - 2-Questionable false alarm: <b>%.1f events / 400 km</b>' % ques_rate),
                            Spacer(width=1 * cm, height=0.2 * cm), ]
                    else:
                        story += [Paragraph('PAEBS resim warning rate: n/a'),
                                  Spacer(width=1 * cm, height=0.2 * cm), ]
                else:
                    if 'roadt_dist' in locals() and roadt_dist.total > 0.0:
                        tot_rate = float(tot_resim) / roadt_dist.total * 1000.0
                        false_rate = float(paebs_resim_count['1-False_alarm']) / roadt_dist.total * 5000.0
                        ques_rate = float(paebs_resim_count['2-Questionable_false_alarm']) / roadt_dist.total * 400.0
                        story += [
                            Paragraph('PAEBS resim warning rate - overall: <b>%.1f events / 1000 km</b>' % tot_rate),
                            Paragraph(
                                'PAEBS resim warning rate - 1-False alarm: <b>%.1f events / 5000 km</b>' % false_rate),
                            Paragraph(
                                'PAEBS resim warning rate - 2-Questionable false alarm: <b>%.1f events / 400 km</b>' % ques_rate),
                            Spacer(width=1 * cm, height=0.2 * cm), ]
                    else:
                        story += [Paragraph('PAEBS resim warning rate: n/a'),
                                  Spacer(width=1 * cm, height=0.2 * cm), ]
            else:
                if not tot_paebs:
                    story += [Paragraph('Total number of PAEBS events: n/a'),
                              Paragraph('PAEBS warning rate: n/a'),
                              Spacer(width=1 * cm, height=0.2 * cm), ]

                if not tot_resim:
                    story += [Paragraph('Total number of PAEBS resim events: n/a'),
                              Paragraph('PAEBS resim warning rate: n/a'),
                              Spacer(width=1 * cm, height=0.2 * cm), ]

            # system performance
            # m_plot = lambda m: self.module_plot(m,
            #                                     windgeom="250x200+0+0", width=60.0, height=60.0, unit=1.0, kind='%',
            #                                     overwrite_start_end=True, start_date=start_date, end_date=end_date)
            # table_style = [
            #     ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            #     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            # ]
            # story += [Table([
            #     [m_plot("view_quantity_vs_systemstate_stats_flr25-pie_duration@aebseval.systemstate")],
            # ], style=table_style)]
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

    def aebs_event_classification(self, dtc_summary):
        story = [IndexedParagraph('PAEBS event classification', style='Heading1')]

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
        for summary in dtc_summary:
            story.append(IndexedParagraph(summary.title, style='Heading2'))
            story.append(summary.get_table(link_pattern=self.EVENT_LINK, link_heading='Heading2')),
            story.append(Spacer(width=1 * cm, height=0.5 * cm))

        story += [self.module_plot(
            "view_quantity_vs_radar_reset_stats-bar_count@flr25eval.faults",
            windgeom="1000x300+0+0", width=50.0, height=50.0, unit=1.0, kind='%')]
        story += [
            Paragraph(italic('Remark: Whenever the ResetCounter signal is increased it will count as a Radar Reset'),
                      fontsize=8),
            Spacer(width=1 * cm, height=0.2 * cm), ]
        story += [PageBreak()]
        return story

    def faults(self, summaries, module_name=None):
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

    def resim_parameters(self, summaries, module_name=None):
        story = [
            IndexedParagraph('Resimulation Parameters', style='Heading1'),
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
        # statuses = ['fillFLC25_PAEBS_AOAOUTPUT@aebs.fill']
        statuses = ['fillFLC25_PAEBS_AOAOUTPUT_RESIM@aebs.fill']
        # statuses = ['fillFLC25_PAEBS_AOAOUTPUT@aebs.fill', 'fillFLC25_PAEBS_AOAOUTPUT_RESIM@aebs.fill']
        statuses.extend(summary.statuses)
        groups = ['FLC25_PAEBS_DEBUG']
        groups = ['FLC25_PAEBS_AOAOUTPUT_STAT', 'FLC25_PAEBS_AOAOUTPUT_MOV', 'FLC25_PAEBS_AOAOUTPUT_STAT_RESIM',
                  'FLC25_PAEBS_AOAOUTPUT_MOV_RESIM']
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


class AebsSummary(EventSummary):
    def init(self, batch, view_name):
        data = PAEBS_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                phase=vector2scalar(row['cascade phase']),
                event=vector2scalar(row['event']),
                moving=vector2scalar2(row['moving state']),
                asso=vector2scalar(row['asso state']),
                event_source=vector2scalar(row['event source']),
                speed=row['ego speed [km/h]'],
                event_start_time_diff=row['event start time diff'],
                target_dx=row['dx [m]'],
                meas_rating=vector2scalar(row['measurement warning rating scale']),
                resim_rating=vector2scalar(row['resimulation warning rating scale']),
                cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_CAN@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_CAN@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('phase', 'measurement\npaebs\nevent\n\n'),
            ('event', 'resim\npaebs\nevent\n\n'),
            # ('moving', 'moving\nstate\n'),
            # ('asso', 'asso\nstate\n'),
            ('speed', 'ego\nspeed\n[kmph]\n'),
            ('event_source', 'event\nsource\n'),
            ('event_start_time_diff', 'event\nstart time\ndifference')
            # ('type', 'type\n'),
        ])

        return


class RadarResetTimeline(Summary):
    def init(self, batch, view_name):
        data = RESET_TABLE
        self.title = 'Radar Reset event details'
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                reset_reason=row['Cat2LastResetReason'],
                address=row['Address'],
                reset_cntr=row['ResetCounter'],
                comment=row['comment']
            ))

        self.columns.update([
            ('start', 'start [s]\n'),
            ('reset_reason', 'Cat2LastResetReason\n'),
            ('address', 'Address\n'),
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
                row = [basename, reset['start'], reset['reset_reason'], reset['address'], reset['reset_cntr'],
                       reset['comment']]
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


class DTCSummary(Summary):
    def init(self, batch, view_name):
        data = DTC_TABLE
        self.title = "DTC event summary"
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                dtc_id=row['DTC ID'],
                dtc_counter=row['DTC counter'],
            ))

        self.columns.update([
            ('dtc_id', 'DTC ID\n'),
            ('dtc_counter', 'DTC count\n'),
        ])
        return

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        data = [header]
        dtc_sum = defaultdict(int)
        for _, dtcs in self.iteritems():
            for dtc in dtcs:
                dtc_sum[dtc['dtc_id']] += 1
        for k, v in dtc_sum.iteritems():
            data.append([hex(int(k)), v])
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


class ResimParameters(Summary):

    def __init__(self, batch, view_name, json_path):
        """
        Overwritten from base class to take the path to the user provided .json file into account.
        Init method is called with third input argument.
        Otherwise, identical to the constructor of the base class.
        :param batch:
        :param view_name:
        :param json_path: Path to user provided .json file.
        """
        OrderedDict.__init__(self)
        self.columns = OrderedDict()
        self.modules = OrderedDict()
        self.init(batch, view_name, json_path)
        self.colWidths = self.get_colwidth()

    def init(self, batch, view_name, json_path):

        # Save inputted argument values
        self.title = 'Parameters List'
        self.JsonPath = json_path

        return

    def get_data(self, link_pattern, link_heading):
        """
        Method reads the name-value pairs of the PAEBS parameter that are available in the
        user provided .json file and in the temporary .json which contains the measurement parameter setting
        in return.
        These data are passed as columns to table of the summary object.

        :param link_pattern:
        :param link_heading:
        :return:
        """
        # Prepare Table Data
        logger = logging.getLogger('')
        header = self.columns.values()
        header.insert(0, 'Parameter Name')
        header.insert(1, 'Parameter Value')
        header.insert(2, 'Measurement Value')
        data = [header]

        try:
            # Read Measurement Param Signal File (.json)
            home_user_path = expanduser("~")
            measurement_json_path = (home_user_path + r'\measurement_valid_signals.json')
            with open(measurement_json_path) as measurement_json_file:
                measurement_signal_values = json.load(measurement_json_file)

            if not bool(measurement_signal_values):
                logger.error('Measurement data is not available in "{}" '
                             'due to missing signal.'.format(measurement_json_path))

            # Parse User provided .json-File
            status_json_read = False
            try:
                jsonPath = self.JsonPath
                with open(jsonPath) as param_json_file:
                    try:
                        resim_parameters = json.load(param_json_file)
                        status_json_read = True
                    except AttributeError as exc:
                        logger.warning("Content of parameter .json file is not parsable!")
                    except TypeError as exc:
                        logger.warning("Content of parameter .json file is not parsable!")
            except IOError as exc:
                logger.warning("Provided parameter .json file is not existing!")
            finally:
                if not status_json_read:
                    resim_parameters = {}

            # Check and compare measurement param setting with user provided param setting
            for key, val in resim_parameters.iteritems():
                data.append([str(key)])
                for param, value in val.iteritems():
                    if measurement_signal_values.has_key(param):
                        data.append([str(param), str(value), str(measurement_signal_values[param])])
                    else:
                        data.append([str(param), str(value), str('-')])
        except:
            logger.error("No entry present in measurement parameter signal database (.json)")

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
    title = "PAEBS event details"
    explanation = """
	PAEBS event: %s & PAEBS resim event: %s - event duration: %s sec, Event source: %s, Rating: %s<br/>
	Resimulation Event Rating: %s. Event is triggered because PAEBS state was active: warning (%d), partial (%d)
	or emergency (%d) braking.
	""" \
                  % (
                      '%(phase)s', '%(event)s', '%(duration).2f', '%(event_source)s', '%(meas_rating)s',
                      '%(resim_rating)s',
                      Flr25Calc.WARNING, Flr25Calc.PARTIAL, Flr25Calc.EMERGENCY)

    EventSummary.stat_im = Image(os.path.join(PIC_DIR, 'flr25_stationary_legend.png'),
                                 width=0.5 * cm, height=0.5 * cm)
    EventSummary.mov_im = Image(os.path.join(PIC_DIR, 'flc25_moving_legend.png'),
                                width=0.5 * cm, height=0.5 * cm)
    EventSummary.aebs_resim_im = Image(os.path.join(PIC_DIR, 'flc25_stationary_legend.png'),
                                       width=0.5 * cm, height=0.5 * cm)
    EventSummary.paebs_resim_im = Image(os.path.join(PIC_DIR, 'flr25_stationary.png'),
                                        width=0.5 * cm, height=0.5 * cm)
    EventSummary.get_tracknav_legend
    legend_pics = [
        (EventSummary.stat_im, 'PAEB resim'),
        (EventSummary.mov_im, 'PAEB track'),
        (EventSummary.aebs_resim_im, 'PAEB stationary'),
        (EventSummary.paebs_resim_im, 'PAEB resim stationary'),
    ]
    extra_modules = [
        ('view_paebs_debug_resim_data@paebseval.resim',
         Client('paebs debug', '640x700+0+0', 11, 12, cm)),
        ('view_paebs_object_resim_data@paebseval.resim',
         Client('paebs object', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_PAEBS_DEBUG@aebs.fill']
    groups = ['FLC25_PAEBS_DEBUG']


if __name__ == '__main__':
    from reportgen.common.main import main

    main(os.path.abspath(__file__))
