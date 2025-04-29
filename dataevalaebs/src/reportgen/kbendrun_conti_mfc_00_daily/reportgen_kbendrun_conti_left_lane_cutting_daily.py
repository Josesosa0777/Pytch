# -*- dataeval: init -*-

import os

import matplotlib

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from reportlab.platypus import Image, Spacer, PageBreak, Table, NextPageTemplate, FrameBreak, PageTemplate, Frame
from reportlab.lib.pagesizes import cm, A4, landscape

from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph, \
    italic, bold
from pyutils.math import round2
from config.interval_header import cIntervalHeader

from reportgen.common.analyze import Analyze
from reportgen.common.summaries import EventSummary, PIC_DIR
from reportgen.common.clients import Client, VideoNavigator
from reportgen.common.utils import vector2scalar

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

LANE_CUTTING_ANALYSIS = None
Left_lane_departure = []


class AebsAnalyze(Analyze):
    optdep = dict(
        dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
        dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
        dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
        dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@mfc525eval.daytime',
        # TODO Get signal for day time
        dur_vs_inlane_tr0='view_quantity_vs_inlane_flr20_tr0_stats-print_duration@trackeval.inlane',
        dur_vs_inlane_tr0_fused='view_quantity_vs_inlane_flr20_tr0_fused_stats-print_duration@trackeval.inlane',
        dist_vs_inlane_tr0='view_quantity_vs_inlane_flr20_tr0_stats-print_mileage@trackeval.inlane',
        dist_vs_inlane_tr0_fused='view_quantity_vs_inlane_flr20_tr0_fused_stats-print_mileage@trackeval.inlane',
        lane_cutting_analysis="analyze_flc25_lane_cutting_analysis-last_entries@mfc525eval.laneeval",
    )

    query_files = {
        'lane_cutting_event': abspath('../../mfc525eval/laneeval/flc25_construction_site_inttable.sql'),
    }

    def analyze(self, story):  # overwritten function to individualize report for paebs
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
        summaries = [LaneDepartureWarningEventSummary(self.batch, self.view_name)]

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

            if self.optdep['lane_cutting_analysis'] in self.passed_optdep:
                lane_cutting_ei_ids = index_fill(self.modules.fill(self.optdep['lane_cutting_analysis']))
                header = cIntervalHeader.fromFileName(self.query_files['lane_cutting_event'])
                table = self.batch.get_table_dict(header, lane_cutting_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global LANE_CUTTING_ANALYSIS, Left_lane_departure
                LANE_CUTTING_ANALYSIS = table
                for id, value in enumerate(LANE_CUTTING_ANALYSIS):
                    if LANE_CUTTING_ANALYSIS[id]['LaneDepartureWarning'][0] == u'LeftLaneDepartureWarning':
                        Left_lane_departure.append(LANE_CUTTING_ANALYSIS[id])
                story += [Paragraph('Total LaneDepartureWarning Events : %d' % len(Left_lane_departure))]

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

            story += [Table([
                [m_plot("view_quantity_vs_left_lane_quality_stats-pie_duration@mfc525eval.laneeval"),
                 m_plot("view_quantity_vs_right_lane_quality_stats-pie_duration@mfc525eval.laneeval")],
            ], style=table_style)]

            story += [Table([
                [m_plot("view_quantity_vs_flc25_ldws_state_stat-pie_duration@mfc525eval.laneeval"),
                 m_plot("view_quantity_vs_flc20_ldws_state_stat-pie_duration@mfc525eval.laneeval")],
            ], style=table_style)]

            story += [Table([
                [m_plot("view_blockage_status-pie_duration@mfc525eval.laneeval")],
            ], style=table_style)]

            story += [Table([
                [m_plot("view_quantity_vs_ldws_warnings-bar_count@mfc525eval.laneeval")],
            ], style=table_style)]

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
                    if summary.modules.keys()[0] == module_name:
                        sync.seek(warning['start'] + 0.5)
                        manager.set_roi(warning['start'] + 0.5, warning['end'] + 0.5, color='y',
                                        pre_offset=5.0, post_offset=5.0)
                        story.append(client(sync, module_name))
                        story.append(FrameBreak())
                    elif summary.modules.keys()[1] == module_name:
                        sync.seek(warning['end'] + 0.5)
                        manager.set_roi(warning['start'] + 0.5, warning['end'] + 0.5, color='y',
                                        pre_offset=5.0, post_offset=5.0)
                        story.append(client(sync, module_name))
                        story.append(FrameBreak())
                    else:
                        sync.seek(warning['start'])
                        manager.set_roi(warning['start'], warning['end'], color='y',
                                        pre_offset=5.0, post_offset=5.0)
                        story.append(client(sync, module_name))
                        story.append(FrameBreak())
                if summary.modules: story.pop(-1)  # remove last FrameBreak
            manager.close()
        return story


class LaneDepartureWarningEvent(EventSummary):

    def init(self, batch, view_name):
        data = Left_lane_departure

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['LaneDepartureWarning']),
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_CAN@evaltools',
             VideoNavigator('VideoNavigator', '400x300+0+0', 6.5, 8.5, cm)),
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_ABD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '400x300+0+0', 6.5, 8.5, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'LaneDepartureWarning\n'),
        ])
        return


class LaneDepartureWarningEventSummary(LaneDepartureWarningEvent):
    title = "Lane Departure Warning Event Status"
    explanation = """Lane Departure Warning Event: %s,[IMG1: 500ms after warning starts, IMG2: 500ms after warning ends]
     Start Time: %s, End Time: %s, Event Duration: %s""" % ('%(event)s', '%(start)s', '%(end)s', '%(duration)s')

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
        ('view_flc25_lane_cutting_events@mfc525eval.laneeval',
         Client('Lane Departure Warning Event', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


def addPageTemplates(doc):
    # Get Sizes and Positions for Frames on Page
    x, y, width, height = doc.getGeom()
    ext_x, ext_y, ext_width, ext_height = doc.getExtGeom()

    _showBoundary = 0

    portrait_frames = [
        Frame(ext_x, y, ext_width, height, id='FullPage'),
    ]

    landscape_frames = [
        Frame(ext_y, x + 1.0 * width, ext_height, 0.1 * width, id='Title'),
        Frame(ext_y, x + 0.95 * width, ext_height, 0.1 * width, id='Duartion'),
        Frame(ext_y, x, 0.25 * ext_height, 0.8 * width, id='VideoNav'),
        Frame(ext_y * 17, x, 0.25 * ext_height, 0.8 * width, id='VideoNav'),
        Frame(ext_y * 35, x, 0.4 * ext_height, 0.8 * width, id='TargetPlot'),
    ]

    comparing_frames = [
        Frame(ext_y, x + 1.0 * width, ext_height, 0.1 * width, id='Title', showBoundary=_showBoundary),
        Frame(ext_y, x + 0.95 * width, 0.6 * ext_height, 0.1 * width, id='Duartion', showBoundary=_showBoundary),
        Frame(ext_y, x, 0.25 * ext_height, 0.8 * width, id='VideoNav', showBoundary=_showBoundary),
        Frame(ext_y * 17, x, 0.25 * ext_height, 0.8 * width, id='VideoNav', showBoundary=_showBoundary),
        Frame(ext_y * 35, x, 0.4 * ext_height, 0.9 * width, id='TargetPlot', showBoundary=_showBoundary),
    ]

    landscape_table_frames = [
        Frame(y, x, height, width, id='FullPage'),
    ]

    doc.addPageTemplates([
        PageTemplate(id='Portrait', frames=portrait_frames,
                     onPage=doc.onPortraitPage, pagesize=A4),
        PageTemplate(id='Landscape', frames=landscape_frames,
                     pagesize=landscape(A4)),
        PageTemplate(id='LandscapeTable', frames=landscape_table_frames,
                     onPage=doc.onLandscapePage, pagesize=landscape(A4)),
        PageTemplate(id='Comparing', frames=comparing_frames,
                     onPage=doc.onLandscapePage, pagesize=landscape(A4)),
    ])

    return


if __name__ == '__main__':
    from reportgen.common.main import main

    main(os.path.abspath(__file__))
