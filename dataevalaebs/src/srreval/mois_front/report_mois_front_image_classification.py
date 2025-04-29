# -*- dataeval: init -*-

import os

import matplotlib
import datetime

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

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

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), pth))

MOIS_TABLE = None
INFORMATION_WARNING = []
VDP_WARNING = []
COLLISION_WARNING = []
NA_STATUS = []
ERROR_STATE = []

class AebsAnalyze(Analyze):
    optdep = dict(
        srr_events ='analyze_mois_event-last_entries@srreval.mois_front',
        dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
        dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
        dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
        dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@mfc525eval.daytime',
    )

    query_files = {
        'srr_events': abspath('bsis_and_mois_event_data.sql'),
    }

    def init(self):
        self.view_name = ''
        self.EVENT_LINK = '%s @ %.2f sec | %s'
        return

    def analyze(self, story):  # overwritten function to individualize report for paebs
        doc = self.get_doc('dataeval.simple', pagesize=A4,
                           header="Strictly confidential")
        addPageTemplates(doc)
        doc.multiBuild(story)
        return

    def summaries(self, summaries, module_name=None):
        story = [ ]
        if module_name is not None:
            story.insert(1, self.module_plot(module_name))
            story.append(PageBreak())
        for summary in summaries:
            story.append(IndexedParagraph(summary.title, style='Heading1'))
            story.append(summary.get_table(link_pattern=self.EVENT_LINK,
                                           link_heading='Heading2')),
            story.extend(self.events(summary))
            story.append(NextPageTemplate('LandscapeTable'))
            story.append(PageBreak())
        return story

    def fill(self):
        self.view_name = self.batch.create_table_from_last_entries(
            start_date=self.start_date, end_date=self.end_date)

        story = intro(
            "MOIS Image Classification Report",
            """ """
        )

        story.extend(toc())
        story.append(PageBreak())
        story.append(Spacer(width=1 * cm, height=0.5 * cm))

        story.extend(self.overall_summary())
        summaries = [SRRWarningFrontSummary(self.batch, self.view_name)]
        story.extend(self.summaries(summaries))
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

            if self.optdep['srr_events'] in self.passed_optdep:
                srr_events_ei_ids = index_fill(self.modules.fill(self.optdep['srr_events']))
                header = cIntervalHeader.fromFileName(self.query_files['srr_events'])
                table = self.batch.get_table_dict(header, srr_events_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global MOIS_TABLE,INFORMATION_WARNING,VDP_WARNING,COLLISION_WARNING,NA_STATUS,ERROR_STATE
                MOIS_TABLE = table
                for id, value in enumerate(MOIS_TABLE):
                    if bool(MOIS_TABLE[id]['BSIS Event']) and MOIS_TABLE[id]['BSIS Event'][0] == u'Information Warning':
                        INFORMATION_WARNING.append(MOIS_TABLE[id])
                    elif bool(MOIS_TABLE[id]['BSIS Event']) and MOIS_TABLE[id]['BSIS Event'][0] == u'VDP Warning':
                        VDP_WARNING.append(MOIS_TABLE[id])
                    elif bool(MOIS_TABLE[id]['BSIS Event']) and MOIS_TABLE[id]['BSIS Event'][0] == u'Collision Warning':
                        COLLISION_WARNING.append(MOIS_TABLE[id])
                    elif bool(MOIS_TABLE[id]['BSIS Event']) and MOIS_TABLE[id]['BSIS Event'][0] == u'NA Status':
                        NA_STATUS.append(MOIS_TABLE[id])
                    elif bool(MOIS_TABLE[id]['BSIS Event']) and MOIS_TABLE[id]['BSIS Event'][0] == u'Error State':
                        ERROR_STATE.append(MOIS_TABLE[id])

                story += [Paragraph('Total MOIS Warnings : {}'.format(len(table)))]

                story.append(Table([('Event type', 'Event Count'),
                                    ('Information Warning', '%d' % (len(INFORMATION_WARNING))),
                                    ('VDP Warning', '%d' % (len(VDP_WARNING))),
                                    ('Collision Warning', '%d' % (len(COLLISION_WARNING))),
                                    ('NA Status', '%d' % (len(NA_STATUS))),
                                    ('Error State', '%d' % (len(ERROR_STATE)))
                                    ], style=grid_table_style))

            story.append(Spacer(width=1 * cm, height=0.5 * cm))
            return

        story = [IndexedParagraph('Overall summary', style='Heading1')]

        story += [IndexedParagraph('Cumulative results', style='Heading2')]
        index_fill = lambda fill: fill.all
        one_summary(story, self.start_date, self.end_date, index_fill)

        story += [PageBreak()]
        return story

    def events(self, summary):
        statuses = ['fillSLR25_Front@aebs.fill']
        statuses.extend(summary.statuses)
        groups = ['FLR25', 'moving', 'stopped']
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
                title = self.EVENT_LINK % (os.path.basename(meas), warning['start'],datetime.datetime.fromtimestamp(float(warning['start'])).strftime('%Y-%b-%d %H:%M:%S'))
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
                    if summary.modules.keys()[1] == module_name:
                        sync.seek(warning['start'] - 1)
                        manager.set_roi(warning['start'] - 1, warning['end'] - 1, color='y',
                                        pre_offset=5.0, post_offset=5.0)
                        story.append(client(sync, module_name))
                        story.append(FrameBreak())
                    elif summary.modules.keys()[2] == module_name:
                        sync.seek(warning['start'] + 1)
                        manager.set_roi(warning['start'] + 1, warning['end'] + 1, color='y',
                                        pre_offset=5.0, post_offset=5.0)
                        story.append(client(sync, module_name))
                        story.append(FrameBreak())
                    elif summary.modules.keys()[3] == module_name:
                        sync.seek(warning['start'] - 2)
                        manager.set_roi(warning['start'] - 2, warning['end'] - 2, color='y',
                                        pre_offset=5.0, post_offset=5.0)
                        story.append(client(sync, module_name))
                        story.append(FrameBreak())
                    elif summary.modules.keys()[4] == module_name:
                        sync.seek(warning['start'] + 2)
                        manager.set_roi(warning['start'] + 2, warning['end'] + 2, color='y',
                                        pre_offset=5.0, post_offset=5.0)
                        story.append(client(sync, module_name))
                        story.append(FrameBreak())
                    else:
                        sync.seek(warning['start'])
                        manager.set_roi(warning['start'], warning['end'], color='y',
                                        pre_offset=5.0, post_offset=5.0)
                        story.append(client(sync, module_name))
                        story.append(FrameBreak())

                if summary.modules:
                    story.pop(-1)  # remove last FrameBreak
            manager.close()
        return story


class SRRWarningFront(EventSummary):
    def init(self, batch, view_name):
        data = MOIS_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['BSIS Event']),
                LonDispMIORightSide=row['LonDispMIORightSide'],
                LatDispMIORightSide=row['LatDispMIORightSide'],
                LatDispMIOFront=row['LatDispMIOFront'],
                LonDispMIOFront=row['LonDispMIOFront'],
            ))

        self.modules.update([
            ('view_nxtvideoeventgrabbernav_lanes-FLR25_ROAD_ESTIMATION@evaltools',
             VideoNavigator('VideoNavigator', '500x450+0+0', 6.5, 8.5, cm)),
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '500x450+0+0', 6.5, 8.5, cm)),
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_CAN@evaltools',
             VideoNavigator('VideoNavigator', '500x450+0+0', 6.5, 8.5, cm)),
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_ABD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '500x450+0+0', 6.5, 8.5, cm)),
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_AOA_LANE@evaltools',
             VideoNavigator('VideoNavigator', '500x450+0+0', 6.5, 8.5, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '500x450+0+0', 6.5, 8.5, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('LatDispMIOFront', 'LatDispMIOFront'),
            ('LonDispMIOFront', 'LonDispMIOFront'),
            ('event', 'event type\n'),
        ])
        return


class SRRWarningFrontSummary(SRRWarningFront):
    title = "SRR Warning Front event details"
    explanation = """ SRR Warning Front Active event: %s, Event Duration: %s, LatDispMIOFront: %s, LonDispMIOFront: %s""" % ('%(event)s', '%(duration)s',
                                                                        '%(LatDispMIOFront)s', '%(LonDispMIOFront)s')
    extra_modules = [
        ('view_BSIS_MOIS@srreval',
         Client('BSIS/MOIS Plot', '1500x1050+0+0', 13, 12, cm)),
    ]

    statuses = ['fillSLR25_Front@aebs.fill']
    groups = ['SLR25_Front']

def addPageTemplates(doc):
    # Get Sizes and Positions for Frames on Page
    x, y, width, height = doc.getGeom()
    ext_x, ext_y, ext_width, ext_height = doc.getExtGeom()

    _showBoundary = 0

    portrait_frames = [
        Frame(ext_x, y, ext_width, height, id='FullPage'),
    ]

    # Special Frames just for A3 Event Summary View
    landscape_frames = [
        Frame(ext_y, x +1.55* width, ext_height, 0.1 * width, id='Title'),
        Frame(ext_y, x + 1.48 * width, ext_height, 0.1 * width, id='Duartion'),

        Frame(ext_y, x * 5.3, 0.25 * ext_height, 0.8 * width, id='VideoNav'),
        Frame(ext_y, x * 1.8, 0.25 * ext_height, 0.8 * width, id='VideoNav'),

        Frame(ext_y * 15, x * 5.4, 0.25 * ext_height, 0.8 * width, id='VideoNav'),
        Frame(ext_y * 15, x * 1.8, 0.25 * ext_height, 0.8 * width, id='VideoNav'),

        Frame(ext_y * 35 , x * 5.3, 0.25 * ext_height, 0.8 * width, id='VideoNav'),

        Frame(ext_y * 35 , x * 1.8, 0.25 * ext_height, 0.8 * width, id='TrackNav'),

        Frame(ext_y * 55, x * 5.3, 0.4 * ext_height, 0.8 * width, id='TargetPlot'),
    ]

    comparing_frames = [
        Frame(ext_y, x +1.55* width, ext_height, 0.1 * width, id='Title', showBoundary=_showBoundary),
        Frame(ext_y, x + 1.48 * width, 0.6 * ext_height, 0.1 * width, id='Duartion', showBoundary=_showBoundary),

        Frame(ext_y , x * 5.3, 0.25 * ext_height, 0.8 * width, id='VideoNav', showBoundary=_showBoundary),
        Frame(ext_y , x * 1.8, 0.25 * ext_height, 0.8 * width, id='VideoNav', showBoundary=_showBoundary),

        Frame(ext_y * 15, x * 5.4, 0.25 * ext_height, 0.8 * width, id='VideoNav', showBoundary=_showBoundary),
        Frame(ext_y * 15, x * 1.8, 0.25 * ext_height, 0.8 * width, id='VideoNav', showBoundary=_showBoundary),

        Frame(ext_y * 35 , x * 5.3, 0.25 * ext_height, 0.8 * width, id='VideoNav', showBoundary=_showBoundary),

        Frame(ext_y * 35, x *1.8 , 0.25 * ext_height, 0.8 * width, id='TrackNav', showBoundary=_showBoundary),

        Frame(ext_y * 55, x * 5.3,0.4*ext_height, 0.9*width, id='TargetPlot', showBoundary=_showBoundary),
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
