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

LDWS_AVAILABILITY_CHECK = None
LANE_KEEP_ALIVE_DATA = None
LeftLaneNotAvailable = 0.0
RightLaneNotAvailable = 0.0
TotalLeftLaneNotAvailable=0.0
TotalRightLaneNotAvailable=0.0
Total_Duration = 0.0
meas_dict={}

class AebsAnalyze(Analyze):
    optdep = dict(

        # ldws_availability_check="analyze_ldws_availability_check-last_entries@ldwseval.laneeval",
        ldws_availability_check="analyze_ld_marking_id-last_entries@ldwseval.laneeval",
        ld_keep_alive="analyze_ld_keep_alive-last_entries@ldwseval.laneeval",
        dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
        dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
        dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
        dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@mfc525eval.daytime',
    )

    query_files = {
        # 'ldws_availability_check': abspath('../../mfc525eval/laneeval/flc25_LD_eval_inttable.sql'),
        'ldws_availability_check': abspath('../../ldwseval/laneeval/flc25_LDKPI_eval.sql'),
        'ld_keep_alive': abspath('../../ldwseval/laneeval/flc25_ld_keep_alive.sql'),

    }

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
        # summaries = [LDWSAvailability(self.batch, self.view_name)]
        summaries = [LaneMarkingID(self.batch, self.view_name),LaneKeepAliveEvents(self.batch, self.view_name)]#
        story.extend(self.summaries(summaries))
        story.extend(self.warnings(summaries))

        return story

    def ld_table(self, story,summaries, module_name=None):
        if module_name is not None:
            story.insert(1, self.module_plot(module_name))
            story.append(PageBreak())
        for summary in summaries:
            story.append(IndexedParagraph(summary.title, style='Heading2'))
            story.append(summary.get_table(link_pattern=self.EVENT_LINK,
                                           link_heading='Heading2')),
            # story.append(PageBreak())
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
            global Total_Duration
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
                Total_Duration = round(roadt_dur.total,1)*3600 #Converting hrs to sec
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
            # LDWS availability check
            if self.optdep['ld_keep_alive'] in self.passed_optdep:
                lane_change_ei_ids = index_fill(self.modules.fill(self.optdep['ld_keep_alive']))
                header = cIntervalHeader.fromFileName(self.query_files['ld_keep_alive'])
                table = self.batch.get_table_dict(header, lane_change_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])

                global LANE_KEEP_ALIVE_DATA
                LANE_KEEP_ALIVE_DATA=table

                story += [Paragraph('Total KeepAlive events: %.1f' % len(LANE_KEEP_ALIVE_DATA)),
                          Spacer(width=1 * cm, height=0.2 * cm), ]

            # LDWS availability check
            if self.optdep['ldws_availability_check'] in self.passed_optdep:
                lane_change_ei_ids = index_fill(self.modules.fill(self.optdep['ldws_availability_check']))
                header = cIntervalHeader.fromFileName(self.query_files['ldws_availability_check'])
                table = self.batch.get_table_dict(header, lane_change_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])

                global LDWS_AVAILABILITY_CHECK, LeftLaneNotAvailable, RightLaneNotAvailable ,TotalLeftLaneNotAvailable,TotalRightLaneNotAvailable

                LDWS_AVAILABILITY_CHECK = table
                TotalLeftLaneNotAvailable = 0.0
                TotalRightLaneNotAvailable = 0.0
                for value in table:
                    if value['ldws availability'][0] == u'LeftLaneNotAvailable' and value['duration [s]'] > 2.0:
                        LeftLaneNotAvailable = LeftLaneNotAvailable + 1.0
                    elif value['ldws availability'][0] == u'RightLaneNotAvailable' and value['duration [s]'] > 2.0:
                        RightLaneNotAvailable = RightLaneNotAvailable + 1.0
                    if value['ldws availability'][0] == u'LeftLaneNotAvailable':
                        TotalLeftLaneNotAvailable = TotalLeftLaneNotAvailable + value['duration [s]']
                    elif value['ldws availability'][0] == u'RightLaneNotAvailable':
                        TotalRightLaneNotAvailable = TotalRightLaneNotAvailable + value['duration [s]']

                story += [Paragraph('Total LeftLaneNotAvailable events: %.1f' % LeftLaneNotAvailable)]
                story += [Paragraph('Total RightLaneNotAvailable events: %.1f' % RightLaneNotAvailable),
                          Spacer(width=1 * cm, height=0.2 * cm),]

                #print("Total dur: {}".format(Total_Duration))
                story += [Paragraph('LeftLaneNotAvailable events: %.2f%% ' % ((TotalLeftLaneNotAvailable/Total_Duration) * 100))]
                story += [Paragraph('RightLaneNotAvailable events: %.2f%%  ' % ((TotalRightLaneNotAvailable/Total_Duration) * 100))]
                story += [Paragraph(italic('Remark: Duration < 2.0 is also included in percentage calculation' ), fontsize=8),
                          Spacer(width=1 * cm, height=0.2 * cm), ]

                # for data in table:
                #     if not meas_dict.has_key(data['measurement']):
                #         temp_dict={}
                #         temp_dict["Available"]=0.0
                #         temp_dict["Not_Available"] = 0.0
                #         temp_dict["Available_rate"] = 0.0
                #         temp_dict["Not_Available_rate"] = 0.0
                #         meas_dict[data['measurement']]=temp_dict
                #
                #
                # for data in table:
                #     if bool(data['lane_not_available_count']):
                #         meas_dict[data['measurement']]["Not_Available"] = meas_dict[data['measurement']]["Not_Available"] + data['lane_not_available_count']
                #     elif bool(data['lane_available_count']):
                #         meas_dict[data['measurement']]["Available"] = meas_dict[data['measurement']]["Available"] + data['lane_available_count']
                #
                # for meas,meas_data in zip(meas_dict.keys(),meas_dict.values()):
                #
                #     if meas_data["Not_Available"] != 0 and meas_data["Available"] != 0:
                #         #if (meas_data["Not_Available"] / meas_data["Available"] * 100) > 0.0:
                #         meas_data["Available_rate"]= round(100 - meas_data["Not_Available"] / meas_data["Available"] * 100,1)
                #         meas_data["Not_Available_rate"]=round(meas_data["Not_Available"] / meas_data["Available"] * 100,1)
                #         # else:
                #         #     meas_data["Not_Available_rate"] = round(meas_data["Not_Available"] / meas_data["Available"] * 100,1)

            return

        story = [IndexedParagraph('Overall summary', style='Heading1')]

        story += [IndexedParagraph('Cumulative results', style='Heading2')]
        index_fill = lambda fill: fill.all
        one_summary(story, self.start_date, self.end_date, index_fill)
        # ld_summary_table = [LDKPISummaryTable(self.batch, self.view_name)]
        # self.ld_table(story,ld_summary_table)

        if 'datelist' in self.global_params:
            story += [IndexedParagraph('Latest results', style='Heading2')]
            index_fill = lambda fill: fill.values()[-1]
            middatelist = self.global_params.get('datelist', "").split()
            one_summary(story, middatelist[-1], self.end_date, index_fill)

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

class LDWSAvailabiitySummary(EventSummary):
    def init(self, batch, view_name):
        data = LDWS_AVAILABILITY_CHECK
        for row in data:
            if bool(row['ldws availability']) and (row['duration [s]'] > 3.0):
                self.setdefault(row['fullmeas'], []).append(dict(
                    start=row['start [s]'],
                    end=row['start [s]'] + row['duration [s]'],
                    duration=row['duration [s]'],
                    event=vector2scalar(row['ldws availability']),
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
            ('event', 'ldws availability status\n'),
        ])
        return


class LaneMarkingIDSummary(EventSummary):
    def init(self, batch, view_name):
        data = LDWS_AVAILABILITY_CHECK
        for row in data:
            if bool(row['ldws availability']) and (row['duration [s]'] > 2.0):
                self.setdefault(row['fullmeas'], []).append(dict(
                    start=row['start [s]'],
                    end=row['start [s]'] + row['duration [s]'],
                    duration=row['duration [s]'],
                    event=vector2scalar(row['ldws availability']),
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
            ('event', 'ldws availability status\n'),
        ])
        return
class LaneKeepAliveSummary(EventSummary):
    def init(self, batch, view_name):
        data = LANE_KEEP_ALIVE_DATA
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                    start=row['start [s]'],
                    end=row['start [s]'] + row['duration [s]'],
                    duration=row['duration [s]'],
                    event=vector2scalar(row['FLC25 keep alive']),
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
            ('event', 'Keep alive status\n'),
        ])
        return

class LaneKeepAliveEvents(LaneKeepAliveSummary):
    title = "LD Keep Alive Event "
    explanation = """LD Keep alive Status: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_ld_keep_alive@ldwseval.laneeval',
         Client('ld_keep_alive', '640x700+0+0', 11, 12, cm)),
        ('view_ldw_state_lk_state@ldwseval.laneeval',
         Client('ldw_state', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class LDWSAvailability(LDWSAvailabiitySummary):
    title = "LDWS Availability Check"
    explanation = """LDWS Availability: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_ldws_availability_check@mfc525eval.laneeval',
         Client('Sensor States', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class LaneMarkingID(LaneMarkingIDSummary):
    title = "Lane Marking ID"
    explanation = """Lane Marking ID: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_ldws_availability_check@ldwseval.laneeval',
         Client('ldws_availability', '640x700+0+0', 11, 12, cm)),
        ('View_road_edge_signals@ldwseval.laneeval',
         Client('Road_edge', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']

class LDKPISummaryTable(Summary):
    def init(self, batch, view_name):
        self.title = 'LDWS Availability Check Summary Table'
        for meas,meas_data in zip(meas_dict.keys(),meas_dict.values()):
            if meas_data["Available_rate"] != 0.0 and meas_data["Not_Available_rate"] != 0.0:
                self.setdefault(meas,[]).append(dict(
                    Available=meas_data["Available_rate"],
                    Not_Available=meas_data["Not_Available_rate"],
                ))

        self.columns.update([

            ('Available', 'Available [%]\n'),
            ('Not_Available', 'Not_Available [%]\n'),

        ])
        return

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'Measurement')
        data = [header]
        for meas, meas_data in zip(meas_dict.keys(), meas_dict.values()):
            # basename = os.path.basename(meas)
            if meas_data["Available_rate"] != 0.0 and meas_data["Not_Available_rate"] != 0.0:
                row=[meas,meas_data["Available_rate"],meas_data["Not_Available_rate"]]
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
