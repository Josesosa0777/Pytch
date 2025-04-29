# -*- dataeval: init -*-

import os

import matplotlib

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph,\
    italic, bold, grid_table_style
from pyutils.math import round2
from config.interval_header import cIntervalHeader
from reportgen.common.utils import conv_float
from datalab.tygra import grid_table_style, get_index_link, Link, Paragraph

from reportgen.common.analyze import Analyze
from reportgen.common.summaries import EventSummary, PIC_DIR, TableDict
from reportlab.lib.pagesizes import inch, cm, A4, A3, landscape
from reportgen.common.clients import Client, TrackNavigator, VideoNavigator
from reportgen.common.utils import vector2scalar
from reportlab.platypus import Image, Spacer, PageBreak, Table, NextPageTemplate, FrameBreak, BaseDocTemplate, PageTemplate, Frame

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

RSP_TABLE = None
Rsptestactive_Active_data = []
RspStep1Active_Active_data = []
RspStep2Active_Active_data = []
RSPTestedLifted_data =[]
RSPVDCActive_data = []


class AebsAnalyze(Analyze):
    optdep = dict(
        rsp_events="analyze_trailer_rsp_eval-last_entries@trailereval.rsp_eval",
        dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
        dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
        dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
        dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@mfc525eval.daytime',
    )

    query_files = {
        'aebs_events': abspath('../../aebseval/events_inttable.sql'),
        'rsp_events': abspath('../../trailereval/rsp_eval/rsp_eval_inttable.sql'),
    }

    def init(self):
        self.view_name = ''
        self.EVENT_LINK = '%s @ %.4f sec'
        return

    def analyze(self, story):  # overwritten function to individualize report for paebs
        doc = self.get_doc('dataeval.simple', pagesize=A4,
                           header="Strictly confidential")
        addPageTemplates(doc)
        doc.multiBuild(story)
        return

    def fill(self):
        self.view_name = self.batch.create_table_from_last_entries(
            start_date=self.start_date, end_date=self.end_date)

        story = intro("Trailer endurance report", """ """)

        story.extend(toc())
        story.append(PageBreak())
        story.append(Spacer(width=1 * cm, height=0.5 * cm))
        story.extend(self.overall_summary())
        summaries = [RSPactiveSummary(self.batch, self.view_name),
                     RSPStep1Summary(self.batch, self.view_name),RSPStep2Summary(self.batch, self.view_name),
                     RSPTestedLiftedSummary(self.batch, self.view_name),RSPVDCActiveSummary(self.batch, self.view_name)]
        story.extend(self.summaries(summaries))
        return story

    def summaries(self, summaries, module_name=None):
        story = [
            # IndexedParagraph('Warning summary tables', style='Heading1'),
            # NextPageTemplate('LandscapeTable'),
        ]
        if module_name is not None:
            story.insert(1, self.module_plot(module_name))
            story.append(PageBreak())
        for summary in summaries:
            story.append(IndexedParagraph(summary.title, style='Heading1'))
            story.append(summary.get_table(link_pattern=self.EVENT_LINK,
                                           link_heading='Heading2')),
            # story.append(PageBreak())
            # story = []
            # for summary in summaries:
            # story.append(IndexedParagraph(summary.title, style='Heading1'))
            story.extend(self.events(summary))
            story.append(NextPageTemplate('LandscapeTable'))
            # story.append(PageBreak())
            # return story
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

            if self.optdep['rsp_events'] in self.passed_optdep:
                wl_active_ei_ids = index_fill(self.modules.fill(self.optdep['rsp_events']))
                header = cIntervalHeader.fromFileName(self.query_files['rsp_events'])
                table = self.batch.get_table_dict(header, wl_active_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global RSP_TABLE,Rsptestactive_Active_data,RspStep1Active_Active_data,RspStep2Active_Active_data,RSPTestedLifted_data,RSPVDCActive_data
                RSP_TABLE = table
                for id, value in enumerate(RSP_TABLE):
                    if bool(RSP_TABLE[id]['RSP event']) and RSP_TABLE[id]['RSP event'][0] == u'RSPTestedLifted=1':
                        RSPTestedLifted_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['RSP event']) and RSP_TABLE[id]['RSP event'][0] == u'RSPVDCActive=1':
                        RSPVDCActive_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['RSP event']) and RSP_TABLE[id]['RSP event'][0] == u'Rsptestactive=1':
                        Rsptestactive_Active_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['RSP event']) and RSP_TABLE[id]['RSP event'][0] == u'RspStep1Active=1':
                        RspStep1Active_Active_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['RSP event']) and RSP_TABLE[id]['RSP event'][0] == u'RspStep2Active=1':
                        RspStep2Active_Active_data.append(RSP_TABLE[id])

                story.append(Table([('Trigger type', 'Active Event Count'),('Rsptestactive=1', '%d' % (len(Rsptestactive_Active_data))),
                                    ('RspStep1Active=1', '%d' % (len(RspStep1Active_Active_data))),
                                    ('RspStep2Active=1', '%d' % (len(RspStep2Active_Active_data))),
                                    ('RSPTestedLifted=1', '%d' % (len(RSPTestedLifted_data))),
                                    ('RSPVDCActive=1', '%d' % (len(RSPVDCActive_data)))], style=grid_table_style))

            story.append(Spacer(width=1 * cm, height=0.5 * cm))

            return

        story = [IndexedParagraph('Overall summary', style='Heading1')]

        story += [IndexedParagraph('Cumulative results', style='Heading2')]
        index_fill = lambda fill: fill.all
        one_summary(story, self.start_date, self.end_date, index_fill)

        story += [PageBreak()]
        return story

    def events(self, summary):
        statuses = []
        statuses.extend(summary.statuses)
        groups = []
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
                    story.append(client(sync, module_name))
                    story.append(FrameBreak())
                if summary.modules: story.pop(-1)  # remove last FrameBreak
            manager.close()
        return story


class RsptestactiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = Rsptestactive_Active_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=round(row['start [s]'], 4),
                end=round(row['start [s]'] + row['duration [s]'], 4),
                duration=round(row['duration [s]'],4),
                event=vector2scalar(row['RSP event']),
            ))

        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

    def get_table(self, link_pattern, link_heading, **kwargs):
        data = self.get_data(link_pattern, link_heading, **kwargs)
        style = self.get_style()
        colWidths = [self.colWidths]
        colWidths.extend(None for e in self.columns)
        table = Table(data, style=style, colWidths=colWidths)
        return table

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'measurement')
        data = [header]
        for meas, warnings in self.iteritems():
            basename = os.path.basename(meas)
            for warning in warnings:
                row = [conv_float(warning[name], format_spec="%.4f") for name in self.columns]
                # create sub table for link
                # http://xiix.wordpress.com/2008/03/12/a-reportlab-link-in-table-cell-workaround/
                link = get_index_link(link_pattern % (basename, warning['start']),
                                      link_heading)
                row.insert(0, Table([[Paragraph(Link(link, basename),
                                                fontSize=self.font_size,
                                                fontName=self.font_name)]],
                                    colWidths=self.colWidths))
                data.append(row)
        return data

class RSPactiveSummary(RsptestactiveSummary):
    title = "Rsptestactive=1 active event details"
    explanation = """Event: %s, Start Time: %s, End Time: %s, Event Duration: %s """ % ('%(event)s','%(start)s','%(end)s', '%(duration)s')

    extra_modules = [
        ('View_rsp_plot@trailereval.rsp_eval',
         Client('RSP Plot', '640x700+0+0', 11, 12, cm)),
        ('View_rsp_eval@trailereval.rsp_eval',
         Client('RSP Plot', '640x700+0+0', 11, 12, cm)),
    ]


class RspStep1ActiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = RspStep1Active_Active_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=round(row['start [s]'], 4),
                end=round(row['start [s]'] + row['duration [s]'], 4),
                duration=round(row['duration [s]'], 4),
                event=vector2scalar(row['RSP event']),
            ))

        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

    def get_table(self, link_pattern, link_heading, **kwargs):
        data = self.get_data(link_pattern, link_heading, **kwargs)
        style = self.get_style()
        colWidths = [self.colWidths]
        colWidths.extend(None for e in self.columns)
        table = Table(data, style=style, colWidths=colWidths)
        return table

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'measurement')
        data = [header]
        for meas, warnings in self.iteritems():
            basename = os.path.basename(meas)
            for warning in warnings:
                row = [conv_float(warning[name], format_spec="%.4f") for name in self.columns]
                # create sub table for link
                # http://xiix.wordpress.com/2008/03/12/a-reportlab-link-in-table-cell-workaround/
                link = get_index_link(link_pattern % (basename, warning['start']),
                                      link_heading)
                row.insert(0, Table([[Paragraph(Link(link, basename),
                                                fontSize=self.font_size,
                                                fontName=self.font_name)]],
                                    colWidths=self.colWidths))
                data.append(row)
        return data



class RSPStep1Summary(RspStep1ActiveSummary):
    title = "RspStep1Active=1  active event details"
    explanation = """Event: %s, Start Time: %s, End Time: %s, Event Duration: %s """ % ('%(event)s','%(start)s','%(end)s', '%(duration)s')

    extra_modules = [
        ('View_rsp_plot@trailereval.rsp_eval',
         Client('RSP Plot', '640x700+0+0', 11, 12, cm)),
        ('View_rsp_eval@trailereval.rsp_eval',
         Client('RSP Plot', '640x700+0+0', 11, 12, cm)),
    ]


class RspStep2ActiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = RspStep2Active_Active_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=round(row['start [s]'], 4),
                end=round(row['start [s]'] + row['duration [s]'], 4),
                duration=round(row['duration [s]'], 4),
                event=vector2scalar(row['RSP event']),
            ))

        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

    def get_table(self, link_pattern, link_heading, **kwargs):
        data = self.get_data(link_pattern, link_heading, **kwargs)
        style = self.get_style()
        colWidths = [self.colWidths]
        colWidths.extend(None for e in self.columns)
        table = Table(data, style=style, colWidths=colWidths)
        return table

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'measurement')
        data = [header]
        for meas, warnings in self.iteritems():
            basename = os.path.basename(meas)
            for warning in warnings:
                row = [conv_float(warning[name], format_spec="%.4f") for name in self.columns]
                # create sub table for link
                # http://xiix.wordpress.com/2008/03/12/a-reportlab-link-in-table-cell-workaround/
                link = get_index_link(link_pattern % (basename, warning['start']),
                                      link_heading)
                row.insert(0, Table([[Paragraph(Link(link, basename),
                                                fontSize=self.font_size,
                                                fontName=self.font_name)]],
                                    colWidths=self.colWidths))
                data.append(row)
        return data


class RSPStep2Summary(RspStep2ActiveSummary):
    title = "RspStep2Active=1 active event details"
    explanation = """Event: %s, Start Time: %s, End Time: %s, Event Duration: %s """ % ('%(event)s','%(start)s','%(end)s', '%(duration)s')

    extra_modules = [
        ('View_rsp_plot@trailereval.rsp_eval',
         Client('RSP Plot', '640x700+0+0', 11, 12, cm)),
        ('View_rsp_eval@trailereval.rsp_eval',
         Client('RSP Plot', '640x700+0+0', 11, 12, cm)),
    ]


class RSPTestedLifted(EventSummary):
    def init(self, batch, view_name):
        data = RSPTestedLifted_data
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=round(row['start [s]'], 4),
                end=round(row['start [s]'] + row['duration [s]'], 4),
                duration=round(row['duration [s]'], 4),
                event=vector2scalar(row['RSP event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

    def get_table(self, link_pattern, link_heading, **kwargs):
        data = self.get_data(link_pattern, link_heading, **kwargs)
        style = self.get_style()
        colWidths = [self.colWidths]
        colWidths.extend(None for e in self.columns)
        table = Table(data, style=style, colWidths=colWidths)
        return table

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'measurement')
        data = [header]
        for meas, warnings in self.iteritems():
            basename = os.path.basename(meas)
            for warning in warnings:
                row = [conv_float(warning[name], format_spec="%.4f") for name in self.columns]
                # create sub table for link
                # http://xiix.wordpress.com/2008/03/12/a-reportlab-link-in-table-cell-workaround/
                link = get_index_link(link_pattern % (basename, warning['start']),
                                      link_heading)
                row.insert(0, Table([[Paragraph(Link(link, basename),
                                                fontSize=self.font_size,
                                                fontName=self.font_name)]],
                                    colWidths=self.colWidths))
                data.append(row)
        return data


class RSPTestedLiftedSummary(RSPTestedLifted):
    title = "RSPTestedLifted=1 event details"
    explanation = """Event: %s, Start Time: %s, End Time: %s, Event Duration: %s """ % ('%(event)s','%(start)s','%(end)s', '%(duration)s')

    extra_modules = [
        ('View_rsp_plot@trailereval.rsp_eval',
         Client('RSP Plot', '640x700+0+0', 11, 12, cm)),
        ('View_rsp_eval@trailereval.rsp_eval',
         Client('RSP Plot', '640x700+0+0', 11, 12, cm)),
    ]

class RSPVDCActive(EventSummary):
    def init(self, batch, view_name):
        data = RSPVDCActive_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=round(row['start [s]'],4),
                end=round(row['start [s]'] + row['duration [s]'],4),
                duration=round(row['duration [s]'], 4),
                event=vector2scalar(row['RSP event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

    def get_table(self, link_pattern, link_heading, **kwargs):
        data = self.get_data(link_pattern, link_heading, **kwargs)
        style = self.get_style()
        colWidths = [self.colWidths]
        colWidths.extend(None for e in self.columns)
        table = Table(data, style=style, colWidths=colWidths)
        return table

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'measurement')
        data = [header]
        for meas, warnings in self.iteritems():
            basename = os.path.basename(meas)
            for warning in warnings:
                row = [conv_float(warning[name], format_spec="%.4f") for name in self.columns]
                # create sub table for link
                # http://xiix.wordpress.com/2008/03/12/a-reportlab-link-in-table-cell-workaround/
                link = get_index_link(link_pattern % (basename, warning['start']),
                                      link_heading)
                row.insert(0, Table([[Paragraph(Link(link, basename),
                                                fontSize=self.font_size,
                                                fontName=self.font_name)]],
                                    colWidths=self.colWidths))
                data.append(row)
        return data


class RSPVDCActiveSummary(RSPVDCActive):
    title = "RSPVDCActive=1 event details"
    explanation = """Event: %s, Start Time: %s, End Time: %s Event Duration: %s """ % ('%(event)s','%(start)s','%(end)s', '%(duration)s')

    extra_modules = [
        ('View_rsp_plot@trailereval.rsp_eval',
         Client('RSP Plot', '640x700+0+0', 11, 12,cm)),
        ('View_rsp_eval@trailereval.rsp_eval',
         Client('RSP Plot', '640x700+0+0', 11, 12,cm)),
    ]

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
        Frame(ext_y, x + 1 * width, ext_height, 0.1 * width, id='Title'),
        Frame(ext_y, x + 0.9 * width, ext_height, 0.1 * width, id='Duartion'),
        Frame(ext_y * 6.5, x * 1.5, 0.4 * ext_height, 0.8 * width, id='EgoPlot'),
        Frame(ext_y * 36, x * 1.5, 0.4 * ext_height, 0.8 * width, id='VehiclePlot'),
    ]

    comparing_frames = [
        Frame(ext_y, x + 1 * width, ext_height, 0.1 * width, id='Title', showBoundary=_showBoundary),
        Frame(ext_y, x + 0.9 * width, 0.6 * ext_height, 0.1 * width, id='Duartion', showBoundary=_showBoundary),
        Frame(ext_y * 6.5, x * 1.5, 0.4 * ext_height, 0.8 * width, id='EgoPlot', showBoundary=_showBoundary),
        Frame(ext_y * 36, x * 1.5, 0.4 * ext_height, 0.9 * width, id='TargetPlot', showBoundary=_showBoundary),
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
