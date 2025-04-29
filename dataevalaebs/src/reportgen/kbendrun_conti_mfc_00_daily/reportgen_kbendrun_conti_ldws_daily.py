# -*- dataeval: init -*-

import os

import matplotlib
import copy
from reportgen.kbendrun_conti_00_daily.reportgen_kbendrun_conti_daily import RESET_TABLE
matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from reportlab.lib import colors
from reportlab.platypus import Image, Spacer, PageBreak, Table, NextPageTemplate, FrameBreak
from reportlab.lib.pagesizes import cm

from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph, NonEmptyTableWithHeader,\
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

LD_EVENTS_TABLE = None
LD_DROPOUTS_TABLE = None

class AebsAnalyze(Analyze):
    optdep = dict(
        lane_change_events='analyze_flc25_LD_avail_during_lane_change-last_entries@mfc525eval.laneeval',
        LD_dropouts_highway='analyze_flc25_LD_dropouts-last_entries@mfc525eval.laneeval',
        dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
        dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
    )
    
    query_files = {
        'lane_change_events': abspath('../../mfc525eval/laneeval/flc25_LD_eval_inttable.sql'),
        'LD_dropouts_highway': abspath('../../mfc525eval/laneeval/flc25_LD_eval_inttable.sql')
    }
    
    def fill(self):
        self.view_name = self.batch.create_table_from_last_entries(
            start_date=self.start_date, end_date=self.end_date)

        pagesize = 'A3'

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

        story += [Paragraph('Event details pagesize is: %s' % pagesize)]
        story.append(PageBreak())
        story.extend(toc())
        story.append(PageBreak())

        story.extend(self.overall_summary())
        story.extend(self.explanation())
        summaries = [LaneDetectionSummary(self.batch, self.view_name), LDDropOutHWSummary(self.batch, self.view_name)]
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
                                Spacer(width=1*cm, height=0.2*cm),]
            
            # driven distance and duration
            if (self.optdep['dur_vs_roadtype'] in self.passed_optdep and 
                    self.optdep['dist_vs_roadtype'] in self.passed_optdep):
                roadt_dur = index_fill(self.modules.fill(self.optdep['dur_vs_roadtype']))
                roadt_dist = index_fill(self.modules.fill(self.optdep['dist_vs_roadtype']))
                
                # distance
                if roadt_dist.total > 0.0:
                    calc_dist_perc = lambda d: int(round2(d/roadt_dist.total*100.0, 5.0))
                    story += [Paragraph(
                        'Total mileage: %s (ca. %d%% city, %d%% rural, %d%% highway)'%
                        (bold('%.1f km' % roadt_dist.total),
                         calc_dist_perc(roadt_dist['city']),
                         calc_dist_perc(roadt_dist['rural']),
                         calc_dist_perc(roadt_dist['highway']))),]
                else:
                    story += [Paragraph('Total mileage: %s' % bold('%.1f km' % roadt_dist.total))]
                # duration
                if roadt_dur.total > 0.25:
                    calc_dist_perc = lambda d: int(round2(d/roadt_dur.total*100.0, 5.0))
                    story += [Paragraph(
                        'Total duration: %s (ca. %d%% standstill, %d%% city, %d%% rural, %d%% highway)'%
                        (bold('%.1f hours' % roadt_dur.total),
                         calc_dist_perc(roadt_dur['ego stopped']),
                         calc_dist_perc(roadt_dur['city']),
                         calc_dist_perc(roadt_dur['rural']),
                         calc_dist_perc(roadt_dur['highway']))),]
                else:
                    story += [Paragraph('Total duration: %s' % bold('%.1f hours' % roadt_dur.total))]
            else:
                self.logger.warning('Road type statistics not available')
                story += [Paragraph('Total duration: n/a'),
                                    Paragraph('Total mileage: n/a'),]			
                
            if (self.optdep['lane_change_events'] in self.passed_optdep):
                reset_ei_ids = index_fill(self.modules.fill(self.optdep['lane_change_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['lane_change_events'])
                camera_table_internal = self.batch.get_table_dict(header1, reset_ei_ids, sortby = [('measurement', True), ('start [s]', True)])
                global LD_EVENTS_TABLE
                LD_EVENTS_TABLE = camera_table_internal

            if (self.optdep['LD_dropouts_highway'] in self.passed_optdep):
                reset_ei_ids = index_fill(self.modules.fill(self.optdep['LD_dropouts_highway']))
                header1 = cIntervalHeader.fromFileName(self.query_files['LD_dropouts_highway'])
                camera_table_internal = self.batch.get_table_dict(header1, reset_ei_ids, sortby = [('measurement', True), ('start [s]', True)])
                global LD_DROPOUTS_TABLE
                LD_DROPOUTS_TABLE = camera_table_internal
            
            # system performance
            m_plot = lambda m: self.module_plot(m,
                windgeom="250x200+0+0", width=60.0, height=60.0, unit=1.0, kind='%',
                overwrite_start_end=True, start_date=start_date, end_date=end_date)
            table_style = [
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]

            story.append(Spacer(width = 1 * cm, height = 0.5 * cm))

            story += [ Table([
                [m_plot("view_quantity_vs_left_lane_quality_stats-pie_duration@mfc525eval.laneeval"),
                 m_plot("view_quantity_vs_right_lane_quality_stats-pie_duration@mfc525eval.laneeval")],
            ], style=table_style) ]

            story += [ Table([
                [m_plot("view_quantity_vs_flc25_ldws_state_stat-pie_duration@mfc525eval.laneeval"),
                 m_plot("view_quantity_vs_flc20_ldws_state_stat-pie_duration@mfc525eval.laneeval")],
            ], style=table_style) ]

            story += [ Table([
                [m_plot("view_quantity_vs_ldws_warnings-bar_count@mfc525eval.laneeval")],
            ], style=table_style) ]


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
        statuses = ['fillFLR20@aebs.fill']
        statuses.extend(summary.statuses)
        groups = ['FLR20', 'moving', 'stationary']
        groups.extend(summary.groups)
    
        story = []
    
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
              story.append( client(sync, module_name) )
              story.append( FrameBreak() )
            if summary.modules: story.pop(-1)  # remove last FrameBreak
          manager.close()
        return story



class LaneDetectionSummary(EventSummary):
    def init(self, batch, view_name):
        data = LD_EVENTS_TABLE
        
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]']+row['duration [s]'],
                duration=row['duration [s]'],
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '700x700+0+0', 12, 12, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
        ])
        return


class LDDropOutHWSummary(EventSummary):
    def init(self, batch, view_name):
        data = LD_DROPOUTS_TABLE
        
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]']+row['duration [s]'],
                duration=row['duration [s]'],
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4, cm))
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
        ])
        return


class LDEventSummary(LaneDetectionSummary):
    title = "Lane Change event"
    explanation = """
    Ego lane change event on highway speed > 60 km/h
    """
    EventSummary.stat_im = Image(os.path.join(PIC_DIR, 'flr25_stationary_legend.png'),
        width=0.5 * cm, height=0.5 * cm)
    EventSummary.mov_im = Image(os.path.join(PIC_DIR, 'flr25_moving_legend.png'),
        width=0.5 * cm, height=0.5 * cm)

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.aeb_im, 'AEB track'),
    ]


class LDDropoutsSummary(LDDropOutHWSummary):
    title = "LD DropOut"
    explanation = """
    LD dropouts on highway, speed > 60 km/h
    """
    EventSummary.stat_im = Image(os.path.join(PIC_DIR, 'flr25_stationary_legend.png'),
        width=0.5 * cm, height=0.5 * cm)
    EventSummary.mov_im = Image(os.path.join(PIC_DIR, 'flr25_moving_legend.png'),
        width=0.5 * cm, height=0.5 * cm)

    legend_pics = [
        (EventSummary.stat_im, 'stationary'),
        (EventSummary.mov_im, 'moving'),
        (EventSummary.aeb_im, 'AEB track'),
    ]


if __name__ == '__main__':
    from reportgen.common.main import main
    main(os.path.abspath(__file__))
