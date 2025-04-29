# -*- dataeval: init -*-

import os

import matplotlib
import datetime

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from reportlab.platypus import Image, Spacer, PageBreak, Table, NextPageTemplate, FrameBreak, PageTemplate, Frame
from reportlab.lib.pagesizes import cm, A4, landscape, A3
from reportlab.lib import colors
from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph, \
    italic, bold, grid_table_style, get_index_link, Link, dtc_table
from pyutils.math import round2
from config.interval_header import cIntervalHeader
from reportlab.pdfbase.pdfmetrics import stringWidth

from reportgen.common.analyze import Analyze
from reportgen.common.summaries import EventSummary, PIC_DIR, Summary
from reportgen.common.clients import Client, VideoNavigator, TrackNavigator, TableNavigator
from reportgen.common.utils import vector2scalar
from reportgen.common.utils import conv_float

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

dtcMappingFile_path = os.path.join(os.path.dirname(__file__), "config", "dtc_mapping.txt")

SYS_BITFIELD_TABLE = None
dtcMappningDict = {}
DTC_TABLE = None


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
        sys_bitfield_event='analyze_sys_bitfield_event-last_entries@mfc525eval.sys_bitfield',
        dtc_events='analyze_flc25_dtc_active_events-last_entries@mfc525eval.faults'
    )

    query_files = {
        'sys_bitfield_event': abspath('../../mfc525eval/sys_bitfield/sys_bitfield_event_inittable.sql'),
        'dtc_events': abspath('../../mfc525eval/faults/flc25_active_dtc_inittable.sql'),
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
            "Sys Bitfield Event Report",
            """
            This is evaluation report for Sys Bitfield events.
            """
        )
        story.append(PageBreak())
        story.extend(toc())
        story.append(PageBreak())

        story.extend(self.overall_summary())
        story.extend(self.explanation())
        summaries = [SysBitfieldEventSummary(self.batch, self.view_name)]
        story.extend(self.summaries(summaries))
        story.extend(self.warnings(summaries))
        # flc25_dtc_summary = [DTCSummary(self.batch, self.view_name)]
        # story.extend(self.flc25_dtc_summary(flc25_dtc_summary))
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

                # DTC event table
            if (self.optdep['dtc_events'] in self.passed_optdep):
                dtc_ei_ids = index_fill(self.modules.fill(self.optdep['dtc_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['dtc_events'])
                dtc_table_internal = self.batch.get_table_dict(header1, dtc_ei_ids,
                                                               sortby=[('measurement', True), ('start [s]', True)])
                global DTC_TABLE, dtcMappningDict
                DTC_TABLE = dtc_table_internal

                col_widths = [2 * cm, 12 * cm, 3 * cm]

                dtcMappingFile = open(dtcMappingFile_path, 'r')

                for line in dtcMappingFile:
                    dtc_id, dtc_name = line.strip().split('=')
                    dtcMappningDict[dtc_id.strip().lower()] = dtc_name.strip()

                story += [Paragraph('DTC Overview Table:')]

                story += [Spacer(width=1 * cm, height=0.2 * cm)]

                dtc_dictionary = {}

                dtc_list_in_hex = [hex(int(dtc_list['DTC in DEC'])) for dtc_list in dtc_table_internal]

                previoud_dtc_id = ""
                refined_dtc_list = []

                for key in dtc_list_in_hex:
                    if key != previoud_dtc_id:
                        if len(key) < 8:
                            key = (key).replace('x', 'x0')
                        refined_dtc_list.append(key)
                        previoud_dtc_id = key

                dtc_dictionary = {key: refined_dtc_list.count(key) for key in refined_dtc_list}

                story.append(
                    Table([('DTCs', 'DTC Name', 'No of Events')], colWidths=col_widths, style=grid_table_style,
                          vAlign='MIDDLE'))

                for dtc_name, dtc_value in dtc_dictionary.iteritems():
                    story.append(
                        Table([(dtc_name, dtcMappningDict.get(dtc_name, 'DTC_Mapping_ID_Missing'), '%d' % (dtc_value))],
                              colWidths=col_widths, style=grid_table_style,
                              vAlign='MIDDLE'))

                story += [Spacer(width=1 * cm, height=0.2 * cm)]

            if self.optdep['sys_bitfield_event'] in self.passed_optdep:
                lane_cutting_ei_ids = index_fill(self.modules.fill(self.optdep['sys_bitfield_event']))
                header = cIntervalHeader.fromFileName(self.query_files['sys_bitfield_event'])
                table = self.batch.get_table_dict(header, lane_cutting_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global SYS_BITFIELD_TABLE
                SYS_BITFIELD_TABLE = table

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

    def sys_bitfield_event_classification(self):
        story = [IndexedParagraph('Sys_Bitfield event Status', style='Heading1')]

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

    def flc25_dtc_summary(self, summaries, module_name=None):
        story = [
            IndexedParagraph('FLC25 DTC Summary', style='Heading1'),
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
        statuses = ['fillFLR25_AEB@aebs.fill']
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
            for id, warning in enumerate(warnings):
                if id <= 0:
                    try:
                        for dtc_key, dtc_value in warnings[1].iteritems():
                            warning[dtc_key] = dtc_value
                    except:
                        dtc_dict = {"dtc_key": 0, "dtc_value": 0, "dtc_id": 0, "dtc_id_in_hex": 0, "dtc_counter": 0,
                                    "dtc_timestamp": 0, "dtc_name": None}

                        for key, value in dtc_dict.iteritems():
                            warning[key] = value

                        # print dtc_key, dtc_value
                    try:
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
                    except:
                        pass
            manager.close()
        return story


class SysBitfieldEvent(EventSummary):

    def init(self, batch, view_name):
        data = SYS_BITFIELD_TABLE
        dtc_data = DTC_TABLE

        for row in data:
            comment_user = str(row['comment'])
            if len(comment_user) > 250:
                comment_user = comment_user[0:249] + '...[to be continued]...'
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['Sys_Bitfield event']),
                comment=comment_user
            ))

        for row in dtc_data:
            if hex(int(row['DTC in DEC'])) in dtcMappningDict:
                self.setdefault(row['fullmeas'], []).append(dict(
                    dtc_id=row['DTC in DEC'],
                    dtc_id_in_hex=hex(int(row['DTC in DEC'])),
                    dtc_counter=row['DTC counter'],
                    dtc_timestamp=row['DTC timestamp'],
                    dtc_name=dtcMappningDict[hex(int(row['DTC in DEC']))],
                    dtc_comment=row['comment']
                ))
            else:
                self.setdefault(row['fullmeas'], []).append(dict(
                    dtc_id=row['DTC in DEC'],
                    dtc_id_in_hex=hex(int(row['DTC in DEC'])),
                    dtc_counter=row['DTC counter'],
                    dtc_timestamp=row['DTC timestamp'],
                    dtc_name='DTC_Mapping_ID_Missing',
                    dtc_comment=row['comment']
                ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            # ('view_sys_bitfield_table_status@mfc525eval.sys_bitfield',
            #  TableNavigator('TableNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'sys_bitfield\n'),
        ])
        return

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'measurement')
        data = [header]
        for meas, warnings in self.iteritems():
            basename = os.path.basename(meas)
            for id, warning in enumerate(warnings):
                if id <= 0:
                    try:
                        row = [conv_float(warning[name]) for name in self.columns]
                        # create sub table for link
                        try:
                            if warning['event'] in ['Information Warning', 'VDP Warning', 'Collision Warning',
                                                    'NA Status',
                                                    'Error State']:
                                # http://xiix.wordpress.com/2008/03/12/a-reportlab-link-in-table-cell-workaround/
                                link = get_index_link(link_pattern % (basename, warning['start'],
                                                                      datetime.datetime.fromtimestamp(
                                                                          float(warning['start'])).strftime(
                                                                          '%Y-%b-%d %H:%M:%S')),
                                                      link_heading)
                                self.colWidths = stringWidth(self.keys()[0], self.font_name, self.font_size - 3)
                            else:
                                link = get_index_link(link_pattern % (basename, warning['start']), link_heading)
                        except:
                            link = get_index_link(link_pattern % (basename, warning['start']), link_heading)

                        row.insert(0, Table([[Paragraph(Link(link, basename),
                                                        fontSize=self.font_size,
                                                        fontName=self.font_name)]],
                                            colWidths=self.colWidths))
                        data.append(row)
                    except:
                        pass
        return data


class SysBitfieldEventSummary(SysBitfieldEvent):
    title = "Sys Bitfield Event Status"
    explanation = """
    	Start Time %s , Event Duration: %s sec, DTC in DEC: %s , DTC in HEX: %s,  DTC Counter: %s , DTC Timestamp: %s , DTC Name: %s
    	""" \
                  % ('%(start)s', '%(duration).2f', '%(dtc_id)s', '%(dtc_id_in_hex)s', '%(dtc_counter)s',
                     '%(dtc_timestamp)s', '%(dtc_name)s')

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
        ('view_sys_bitfield_status@mfc525eval.sys_bitfield',
         Client('sys_bitfield_plot_1', '740x700+0+0', 11, 12, cm)),
        ('view_bitfield_signal@mfc525eval.sys_bitfield',
         Client('sys_bitfield_plot_2', '740x700+0+0', 11, 12, cm)),
        ('view_actl_state@mfc525eval.laneeval',
         Client('ACTL States', '740x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLR25_AEB@aebs.fill']
    groups = ['FLR25_AEB']


class DTCSummary(Summary):
    def init(self, batch, view_name):
        data = DTC_TABLE
        self.title = "DTC event summary"
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                dtc_id=row['DTC in DEC'],
                dtc_id_in_hex=hex(int(row['DTC in DEC'])),
                dtc_counter=row['DTC counter'],
                dtc_timestamp=row['DTC timestamp'],
                dtc_comment=row['comment']
            ))

        self.columns.update([
            ('dtc_id', 'DTC in DEC\n'),
            ('dtc_id_in_hex', 'DTC in HEX\n'),
            ('dtc_counter', 'DTC Counter\n'),
            ('dtc_timestamp', 'DTC timestamp\n'),
            ('dtc_comment', 'Comment\n'),
        ])
        return

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'measurement')
        header.insert(5, 'dtc_name')
        data = [header]
        previous_dtc_id = ""
        for meas, resets in self.iteritems():
            basename = os.path.basename(meas)
            for reset in resets:
                if reset['dtc_id_in_hex'] != previous_dtc_id:
                    if len(reset['dtc_id_in_hex']) < 8:
                        reset['dtc_id_in_hex'] = (reset['dtc_id_in_hex']).replace('x', 'x0')
                    if reset['dtc_id_in_hex'] in dtcMappningDict:
                        row = [basename, reset['dtc_id'], reset['dtc_id_in_hex'], reset['dtc_counter'],
                               reset['dtc_timestamp'], dtcMappningDict[reset['dtc_id_in_hex']],
                               reset['dtc_comment']]
                        previous_dtc_id = reset['dtc_id_in_hex']
                        data.append(row)
                    else:
                        row = [basename, reset['dtc_id'], reset['dtc_id_in_hex'], reset['dtc_counter'],
                               reset['dtc_timestamp'], 'DTC_Mapping_ID_Missing',
                               reset['dtc_comment']]
                        previous_dtc_id = reset['dtc_id_in_hex']
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


def addPageTemplates(doc):
    # Get Sizes and Positions for Frames on Page
    x, y, width, height = doc.getGeom()
    ext_x, ext_y, ext_width, ext_height = doc.getExtGeom()

    _showBoundary = 0

    portrait_frames = [
        Frame(ext_x, y, ext_width, height, id='FullPage'),
    ]

    landscape_frames = [
        Frame(ext_y, x + 1.55 * width, ext_height, 0.1 * width, id='Title'),
        Frame(ext_y, x + 1.48 * width, ext_height, 0.1 * width, id='Duartion'),
        Frame(ext_y, x + 0.6 * width, 0.2 * ext_height, 0.3 * width, id='VideoNav'),
        Frame(ext_y * 20, x + 0.4 * width, 0.25 * ext_height, 0.8 * width, id='EgoPlot'),
        Frame(ext_y * 38, x + 0.4 * width, 0.4 * ext_height, 0.8 * width, id='TargetPlot'),
        Frame(ext_y * 61, x + 0.4 * width, 0.4 * ext_height, 0.8 * width, id='VehiclePlot'),
    ]

    comparing_frames = [
        Frame(ext_y, x + 1.55 * width, ext_height, 0.1 * width, id='Title', showBoundary=_showBoundary),
        Frame(ext_y, x + 1.48 * width, 0.6 * ext_height, 0.1 * width, id='Duartion', showBoundary=_showBoundary),
        Frame(ext_y, x + 0.6 * width, 0.2 * ext_height, 0.3 * width, id='VideoNav', showBoundary=_showBoundary),
        Frame(ext_y + 0.4 * ext_height, x + 0.4 * width, 0.4 * ext_height, 0.8 * width, id='EgoPlot',
              showBoundary=_showBoundary),
        Frame(ext_y + 0.8 * ext_height, x + 0.4 * width, 0.4 * ext_height, 0.9 * width, id='TargetPlot',
              showBoundary=_showBoundary),
        Frame(ext_y + 1.2 * ext_height, x + 0.4 * width, 0.4 * ext_height, 0.9 * width, id='VehiclePlot',
              showBoundary=_showBoundary),
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


if __name__ == '__main__':
    from reportgen.common.main import main

    main(os.path.abspath(__file__))
