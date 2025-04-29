# -*- dataeval: init -*-

import os

import matplotlib

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

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
from reportgen.common.summaries import EventSummary, PIC_DIR
from reportgen.common.clients import Client, TrackNavigator, VideoNavigator
from reportgen.common.utils import vector2scalar
from aebs.fill.calc_radar_aebs_phases import Calc as Flr25Calc

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

PAEBS_TABLE = None


class AebsAnalyze(Analyze):
    optdep = dict(
        paebs_events='analyze_events_paeb-last_entries@paebseval',
        count_vs_aebs_severity='view_count_vs_severity_stats_flr25-print_mergedcount@paebseval.classif',
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
        'paebs_events': abspath('../../paebseval/events_inttable.sql'),
    }

    def fill(self):
        self.view_name = self.batch.create_table_from_last_entries(
            start_date=self.start_date, end_date=self.end_date)

        story = intro(
            "PAEBS field test evaluation report",
            """
      This is an automatically generated report, based on field tests with
      simultaneously measured forward-looking radar (FLR25) and camera (MFC525)
      sensors.<br/>
      <br/>
      The output signals of PAEBS are analyzed and the
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
        story.extend(self.faults())
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
                    story += [Paragraph('In-lane obstacle presence: %.0f%% / %.0f%% (duration / mileage)' % (
                    inlane_dur_perc, inlane_dist_perc)),
                              Paragraph('Fused in-lane obstacle presence: %.0f%% / %.0f%% (duration / mileage)' % (
                              inlane_fused_dur_perc, inlane_fused_dist_perc)),
                              Spacer(width=1 * cm, height=0.2 * cm), ]
                else:
                    story += [Paragraph('In-lane obstacle presence: n/a'),
                              Paragraph('Fused in-lane obstacle presence: n/a'),
                              Spacer(width=1 * cm, height=0.2 * cm), ]
            else:
                self.logger.warning('In-lane obstacle presence not available')
                story += [Paragraph('In-lane obstacle presence: n/a'),
                          Paragraph('Fused in-lane obstacle presence: n/a'),
                          Spacer(width=1 * cm, height=0.2 * cm), ]

            # AEBS warning rate
            if (self.optdep['paebs_events'] in self.passed_optdep and
                    self.optdep['count_vs_aebs_severity'] in self.passed_optdep):
                paebs_ei_ids = index_fill(self.modules.fill(self.optdep['paebs_events']))
                header = cIntervalHeader.fromFileName(self.query_files['paebs_events'])
                table = self.batch.get_table_dict(header, paebs_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global PAEBS_TABLE
                PAEBS_TABLE = table

                paebs_count = index_fill(self.modules.fill(self.optdep['count_vs_aebs_severity']))

                tot_paebs = len(table)
                story += [Paragraph('Total number of PAEBS events: %d' % tot_paebs)]
                if 'roadt_dist' in locals() and roadt_dist.total > 0.0:
                    tot_rate = float(tot_paebs) / roadt_dist.total * 1000.0
                    false_rate = float(paebs_count['1-False alarm']) / roadt_dist.total * 5000.0
                    ques_rate = float(paebs_count['2-Questionable false alarm']) / roadt_dist.total * 400.0
                    story += [Paragraph('PAEBS warning rate - overall: <b>%.1f events / 1000 km</b>' % tot_rate),
                              Paragraph(
                                  'PAEBS warning rate - 1-False alarm: <b>%.1f events / 5000 km</b>' % false_rate),
                              Paragraph(
                                  'PAEBS warning rate - 2-Questionable false alarm: <b>%.1f events / 400 km</b>' % ques_rate),
                              Spacer(width=1 * cm, height=0.2 * cm), ]
                else:
                    story += [Paragraph('PAEBS warning rate: n/a'),
                              Spacer(width=1 * cm, height=0.2 * cm), ]
            else:
                story += [Paragraph('Total number of PAEBS events: n/a'),
                          Paragraph('PAEBS warning rate: n/a'),
                          Spacer(width=1 * cm, height=0.2 * cm), ]

            # system performance
            m_plot = lambda m: self.module_plot(m,
                                                windgeom="250x200+0+0", width=60.0, height=60.0, unit=1.0, kind='%',
                                                overwrite_start_end=True, start_date=start_date, end_date=end_date)
            table_style = [
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]
            story += [Table([
                [m_plot("view_quantity_vs_systemstate_stats_flr25-pie_duration@paebseval.systemstate"),
                 m_plot("view_quantity_vs_sensorstatus_stats-pie_duration@mfc525eval.sensorstatus")],
            ], style=table_style)]
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
        story = [IndexedParagraph('PAEBS event classification', style='Heading1')]

        m_plot = lambda m: self.module_plot(m,
                                            windgeom="500x300+0+0", width=60.0, height=60.0, unit=1.0, kind='%')
        table_style = [
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]
        story += [Table([
            [m_plot("view_count_vs_phase_stats_flr25-bar_mergedcount@paebseval.classif"),
             m_plot("view_count_vs_movstate_stats_flr25-bar_mergedcount@paebseval.classif")],
            [m_plot("view_count_vs_severity_stats_flr25-bar_mergedcount@paebseval.classif"),
             m_plot("view_count_vs_cause_maingroup_stats_flr25-bar_mergedcount@paebseval.classif")],
        ], style=table_style)]
        story += [self.module_plot(
            "view_quantity_vs_smess_fault_stats-bar_duration@flr20eval.faults",
            windgeom="1000x300+0+0", width=50.0, height=50.0, unit=1.0, kind='%')]

        story += [PageBreak()]
        return story

    def faults(self):
        index_fill = lambda fill: fill.all

        gt_kwargs = dict(
            sortby=[('measurement', True), ('start [s]', True)],
            cell_formatter=str_cell,
        )
        table_kwargs = dict(
            style=grid_table_style,
        )

        story = [IndexedParagraph('FLR25 faults ()', 'Heading2')]
        # ----------------------------------------------------------------
        if self.optdep['smess_faults'] in self.passed_optdep:
            header = cIntervalHeader.fromFileName(abspath('../../flr20eval/faults/smess_faults_inttable.sql'))
            ids = index_fill(self.modules.fill(self.optdep['smess_faults']))
            table = self.batch.get_table(header, ids, **gt_kwargs)
            table_chunk = [row[1:-1] for row in table]
            story += [NonEmptyTableWithHeader(table_chunk, **table_kwargs),
                      Spacer(width=1 * cm, height=0.2 * cm), ]
        else:
            self.logger.warning('FLR25 faults () not available')
            story += [Paragraph('Information not available'),
                      Spacer(width=1 * cm, height=0.2 * cm), ]

        story += [IndexedParagraph('FLR25 faults (A087)', 'Heading2')]
        # -------------------------------------------------------------
        if self.optdep['a087_faults'] in self.passed_optdep:
            header = cIntervalHeader.fromFileName(abspath('../../flr20eval/faults/a087_faults_inttable.sql'))
            ids = index_fill(self.modules.fill(self.optdep['a087_faults']))
            table = self.batch.get_table(header, ids, **gt_kwargs)
            table_chunk = [row[1:-1] for row in table]
            story += [NonEmptyTableWithHeader(table_chunk, **table_kwargs),
                      Spacer(width=1 * cm, height=0.2 * cm), ]
        else:
            self.logger.warning('FLR21 faults (A087) not available')
            story += [Paragraph('Information not available'),
                      Spacer(width=1 * cm, height=0.2 * cm), ]

        story += [IndexedParagraph('FLC25 sensor statuses (without Fully Operational)', 'Heading2')]
        # -----------------------------------------------------------------------
        if self.optdep['flc20_spec_statuses'] in self.passed_optdep:
            header = cIntervalHeader.fromFileName(abspath('../../mfc525eval/sensorstatus/status_inttable.sql'))
            ids = index_fill(self.modules.fill(self.optdep['flc20_spec_statuses']))
            table = self.batch.get_table(header, ids, **gt_kwargs)
            table_chunk = [row[1:-1] for row in table]
            story += [NonEmptyTableWithHeader(table_chunk, **table_kwargs),
                      Spacer(width=1 * cm, height=0.2 * cm), ]
        else:
            self.logger.warning('FLC25 special sensor statuses not available')
            story += [Paragraph('Information not available'),
                      Spacer(width=1 * cm, height=0.2 * cm), ]
        return story

    def events(self, summary):
        statuses = []
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


class AebsSummary(EventSummary):
    def init(self, batch, view_name):
        data = PAEBS_TABLE

        for row in data:
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
            ))

        self.modules.update([
            ('view_nxtvideonav_lanes-FLC25_CAN@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('phase', 'paebs phase\n\n'),
            ('moving', 'moving\nstate\n'),
            ('asso', 'asso\nstate\n'),
            ('speed', 'ego speed\n[kmph]\n'),
        ])
        return


class Flr25Summary(AebsSummary):
    title = "PAEBS event details"
    explanation = """
  PAEBS %s - event duration: %s sec, cause: %s, rating: %s<br/>
  Event is triggered because PAEBS state was active: warning (%d), partial (%d)
  or emergency (%d) braking.
  """ \
                  % ('%(phase)s', '%(duration).2f', '%(cause)s', '%(rating)s',
                     Flr25Calc.WARNING, Flr25Calc.PARTIAL, Flr25Calc.EMERGENCY)

    EventSummary.stat_im = Image(os.path.join(PIC_DIR, 'flr25_stationary_legend.png'),
                                 width=0.5 * cm, height=0.5 * cm)
    EventSummary.mov_im = Image(os.path.join(PIC_DIR, 'flr25_moving_legend.png'),
                                width=0.5 * cm, height=0.5 * cm)

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.aeb_im, 'PAEB track'),
    ]

    extra_modules = [
        ('view_driveract_paebsout@paebseval',
         Client('DriverAct_AebsOut_Plot', '640x700+0+0', 11, 12, cm)),
    ]


if __name__ == '__main__':
    from reportgen.common.main import main

    main(os.path.abspath(__file__))
