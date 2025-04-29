# -*- dataeval: init -*-

import os

import matplotlib

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph,\
    italic, bold
from pyutils.math import round2
from config.interval_header import cIntervalHeader

from reportgen.common.analyze import Analyze
from reportgen.common.summaries import EventSummary, PIC_DIR
from reportlab.lib.pagesizes import inch, cm, A4, A3, landscape
from reportgen.common.clients import Client, TrackNavigator, VideoNavigator
from reportgen.common.utils import vector2scalar
from reportlab.platypus import Image, Spacer, PageBreak, Table, NextPageTemplate, FrameBreak, BaseDocTemplate, PageTemplate, Frame

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

RSP_TABLE = None
Rsptestactive_Active_data = []
RspStep1Active_Active_data = []
RspStep2Active_Active_data = []
Nearly_Active_data = []
VrefFilter_active_data = []
AyFilt_active_data = []
AyCalc_active_data = []
AyLimLeft_active_data = []
AyLimRight_active_data = []
RSPAyOffset_data = []
RSPTestedLifted_data =[]
RSPLowMuSide_data = []
RSPVDCActive_data = []
RSPPlauError_data = []
RSPtUnstabA_data = []
RSPtUnstabB_data = []
RSPtUnstabC_data = []
RSPtUnstabD_data = []
RSPtUnstabE_data = []
RSPtUnstabF_data = []

class AebsAnalyze(Analyze):
    optdep = dict(
        rsp_events="analyze_trailer_rsp_active-last_entries@trailereval",
        dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
        dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
        dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
        dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@mfc525eval.daytime',
    )

    query_files = {
        'aebs_events': abspath('../../aebseval/events_inttable.sql'),
        'rsp_events': abspath('../../trailereval/trailer_evaluation_inttable.sql'),
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

        story = intro("Trailer endurance report", """ """)


        story.extend(toc())
        # story.append(PageBreak())
        story.append(Spacer(width=1 * cm, height=0.5 * cm))
        story.extend(self.overall_summary())
        summaries = [
        RSPactiveSummary(self.batch, self.view_name),
                     RSPStep1Summary(self.batch, self.view_name),
                     RSPStep2Summary(self.batch, self.view_name),
                     NearlySummary(self.batch, self.view_name),
                     VrefFilterSummary(self.batch, self.view_name),
                     AyFiltSummary(self.batch, self.view_name),
                     AyCalcSummary(self.batch, self.view_name),
                     AyLimLeftSummary(self.batch, self.view_name),
                     AyLimRightSummary(self.batch, self.view_name),
                     # RSPAyOffsetSummary(self.batch, self.view_name),
                     RSPTestedLiftedSummary(self.batch, self.view_name),
                     RSPLowMuSideSummary(self.batch, self.view_name),
                     RSPVDCActiveSummary(self.batch, self.view_name),
                     RSPPlauErrorSummary(self.batch, self.view_name),
                     RSPtUnstabASummary(self.batch, self.view_name),
                     RSPtUnstabBSummary(self.batch, self.view_name),
                     RSPtUnstabCSummary(self.batch, self.view_name),
                     RSPtUnstabDSummary(self.batch, self.view_name),
                     RSPtUnstabESummary(self.batch, self.view_name),
                     RSPtUnstabFSummary(self.batch, self.view_name),
                     ]
        story.extend(self.summaries(summaries))
        # story.extend(self.warnings(summaries))
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
                global RSP_TABLE,Rsptestactive_Active_data,RspStep1Active_Active_data,RspStep2Active_Active_data,Nearly_Active_data,VrefFilter_active_data,\
                    AyFilt_active_data,AyCalc_active_data,AyLimLeft_active_data,AyLimRight_active_data,\
                    RSPAyOffset_data,RSPTestedLifted_data,RSPLowMuSide_data,\
                RSPVDCActive_data ,RSPPlauError_data ,RSPtUnstabA_data,RSPtUnstabB_data,RSPtUnstabC_data,RSPtUnstabD_data,RSPtUnstabE_data,RSPtUnstabF_data
                RSP_TABLE = table
                for id, value in enumerate(RSP_TABLE):
                    if bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'VrefFilter>2100AND(RSPStep1Enable=0ORRSPStep2=0)':
                        VrefFilter_active_data.append(RSP_TABLE[id])
                    if bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'ABS(AyFilt)>2500':
                        AyFilt_active_data.append(RSP_TABLE[id])
                    if bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'ABS(AyCalc)>2000':
                        AyCalc_active_data.append(RSP_TABLE[id])
                    if bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'delta(AyLimLeft)<>0':
                        AyLimLeft_active_data.append(RSP_TABLE[id])
                    if bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'delta(AyLimRight)<>0':
                        AyLimRight_active_data.append(RSP_TABLE[id])
                    if bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'delta(AyOffset)<>0':
                        RSPAyOffset_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'RSPTestedLifted=1':
                        RSPTestedLifted_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'RSPLowMuSide>0':
                        RSPLowMuSide_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'RSPVDCActive=1':
                        RSPVDCActive_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'RSPPlauError>0':
                        RSPPlauError_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'RSPtUnstabA>=0':
                        RSPtUnstabA_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'RSPtUnstabB>=0':
                        RSPtUnstabB_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'RSPtUnstabC>=0':
                        RSPtUnstabC_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'RSPtUnstabD>=0':
                        RSPtUnstabD_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'RSPtUnstabE>=0':
                        RSPtUnstabE_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'RSPtUnstabF>=0':
                        RSPtUnstabF_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'Rsptestactive=1':
                        Rsptestactive_Active_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'RspStep1Active=1':
                        RspStep1Active_Active_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'RspStep2Active=1':
                        RspStep2Active_Active_data.append(RSP_TABLE[id])
                    elif bool(RSP_TABLE[id]['GTATRL event']) and RSP_TABLE[id]['GTATRL event'][0] == u'NearlyRSP=1':
                        Nearly_Active_data.append(RSP_TABLE[id])


                story += [Paragraph('Total number of Rsptestactive=1 active events: %d' % len(Rsptestactive_Active_data))]
                story += [Paragraph('Total number of RspStep1Active=1 active events: %d' % len(RspStep1Active_Active_data))]
                story += [Paragraph('Total number of RspStep2Active=1 active events: %d' % len(RspStep2Active_Active_data))]
                story += [Paragraph('Total number of NearlyRSP=1 active events: %d' % len(Nearly_Active_data))]

                story += [Paragraph('Total number of VrefFilter>2100AND(RSPStep1Enable=0ORRSPStep2=0) active events: %d' % len(VrefFilter_active_data))]
                story += [Paragraph('Total number of ABS(AyFilt)>2500 active events: %d' % len(AyFilt_active_data))]
                story += [Paragraph('Total number of ABS(AyCalc)>2000 active events: %d' % len(AyCalc_active_data))]
                story += [Paragraph('Total number of delta(AyLimLeft)<>0 active events: %d' % len(AyLimLeft_active_data))]
                story += [Paragraph('Total number of delta(AyLimRight)<>0 active events: %d' % len(AyLimRight_active_data))]
                story += [Paragraph('Total number of delta(AyOffset)<>0 active events: %d' % len(RSPAyOffset_data))]
                story += [Paragraph('Total number of RSPTestedLifted=1 active events: %d' % len(RSPTestedLifted_data))]
                story += [Paragraph('Total number of RSPLowMuSide>0 active events: %d' % len(RSPLowMuSide_data))]
                story += [Paragraph('Total number of RSPVDCActive=1 active events: %d' % len(RSPVDCActive_data))]
                story += [Paragraph('Total number of RSPPlauError>0 active events: %d' % len(RSPPlauError_data))]

                story += [Paragraph('Total number of RSPtUnstabA>=0 active events: %d' % len(RSPtUnstabA_data))]
                story += [Paragraph('Total number of RSPtUnstabB>=0 active events: %d' % len(RSPtUnstabB_data))]
                story += [Paragraph('Total number of RSPtUnstabC>=0 active events: %d' % len(RSPtUnstabC_data))]
                story += [Paragraph('Total number of RSPtUnstabD>=0 active events: %d' % len(RSPtUnstabD_data))]
                story += [Paragraph('Total number of RSPtUnstabE>=0 active events: %d' % len(RSPtUnstabE_data))]
                story += [Paragraph('Total number of RSPtUnstabF>=0 active events: %d' % len(RSPtUnstabF_data))]


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
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))

        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class RSPactiveSummary(RsptestactiveSummary):
    title = "Rsptestactive=1 active event details"
    explanation = """Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSPTestActive_event_plot@trailereval',
         Client('RSP active', '640x700+0+0', 12, 12.3, cm)),
    ]


class RspStep1ActiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = RspStep1Active_Active_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))

        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class RSPStep1Summary(RspStep1ActiveSummary):
    title = "RspStep1Active=1  active event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSPStep1Aactive_event_plot@trailereval',
         Client('RSP active', '640x700+0+0', 12, 12.3, cm)),
    ]


class RspStep2ActiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = RspStep2Active_Active_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))

        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class RSPStep2Summary(RspStep2ActiveSummary):
    title = "RspStep2Active=1 active event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSPStep2Aactive_event_plot@trailereval',
         Client('RSP active', '640x700+0+0', 12, 12.3, cm)),
    ]


class NearlyactiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = Nearly_Active_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))

        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class NearlySummary(NearlyactiveSummary):
    title = "NearlyRSP=1 active event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_NearlyRSP_event_plot@trailereval',
         Client('RSP active', '640x700+0+0', 12, 12.3, cm)),
    ]


class VrefFilteractiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = VrefFilter_active_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))

        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class VrefFilterSummary(VrefFilteractiveSummary):
    title = "VrefFilter>2100 AND (RSPStep1Enable=0 OR RSPStep2=0) active event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_VrefFilter_event_plot@trailereval',
         Client('VrefFilter active', '640x700+0+0', 12, 12.3, cm)),
    ]


class AyFiltactiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = AyFilt_active_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
                AyFilt_max_value=row['AyFilt_max_value'],
            ))

        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('AyFilt_max_value', 'AyFilt\nmax_value'),
            ('event', 'event label\n'),
        ])
        return


class AyFiltSummary(AyFiltactiveSummary):
    title = "ABS(AyFilt)>2500 active event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_AyFilt_event_plot@trailereval',
         Client('AyFilt active', '640x700+0+0', 12, 12.3, cm)),
    ]


class AyCalcactiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = AyCalc_active_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
                AyCalc_max_value=row['AyCalc_max_value'],
            ))

        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('AyCalc_max_value', 'AyCalc\nmax_value'),
            ('event', 'event label\n'),
        ])
        return


class AyCalcSummary(AyCalcactiveSummary):
    title = "ABS(AyCalc)>2000 active event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_AyCalc_event_plot@trailereval',
         Client('AyCalc active', '640x700+0+0', 12, 12.3, cm)),
    ]


class AyLimLeftactiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = AyLimLeft_active_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
                AyLimLeft_max_value=row['AyLimLeft_max_value'],
            ))

        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('AyLimLeft_max_value', 'AyLimLeft\nmax_value'),
            ('event', 'event label\n'),
        ])
        return


class AyLimLeftSummary(AyLimLeftactiveSummary):
    title = "delta(AyLimLeft)<>0 active event details"
    explanation = """Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_AyLimLeft_event_plot@trailereval',
         Client('AyLimLeft active', '640x700+0+0', 12, 12.3, cm)),
    ]


class AyLimRightactiveSummary(EventSummary):
    def init(self, batch, view_name):
        data = AyLimRight_active_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
                AyLimRight_max_value=row['AyLimRight_max_value'],
            ))

        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('AyLimRight_max_value', 'AyLimRight\nmax_value'),
            ('event', 'event label\n'),
        ])
        return


class AyLimRightSummary(AyLimRightactiveSummary):
    title = "delta(AyLimRight)<>0 active event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_AyLimRight_event_plot@trailereval',
         Client('AyLimRight active', '640x700+0+0', 12, 12.3, cm)),
    ]


class RSPAyOffset(EventSummary):
    def init(self, batch, view_name):
        data = RSPAyOffset_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class RSPAyOffsetSummary(RSPAyOffset):
    title = "delta(AyOffset)<>0 event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSP_Ayoffset_event_plot@trailereval',
         Client('RSP AyOffset', '640x700+0+0', 12, 12.3, cm)),
    ]


class RSPTestedLifted(EventSummary):
    def init(self, batch, view_name):
        data = RSPTestedLifted_data
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

class RSPTestedLiftedSummary(RSPTestedLifted):
    title = "RSPTestedLifted=1 event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSP_RSPTestedLifted_event_plot@trailereval',
         Client('RSP RSPTestedLifted', '640x700+0+0', 12, 12.3, cm)),
    ]


class RSPLowMuSide(EventSummary):
    def init(self, batch, view_name):
        data = RSPLowMuSide_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

class RSPLowMuSideSummary(RSPLowMuSide):
    title = "RSPLowMuSide>0 event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSP_RSPLowMuSide_event_plot@trailereval',
         Client('RSP RSPLowMuSide', '640x700+0+0', 12, 12.3, cm)),
    ]


class RSPVDCActive(EventSummary):
    def init(self, batch, view_name):
        data = RSPVDCActive_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class RSPVDCActiveSummary(RSPVDCActive):
    title = "RSPVDCActive=1 event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSP_RSPVDCActive_event_plot@trailereval',
         Client('RSP RSPVDCActive', '640x700+0+0', 12, 12.3, cm)),
    ]


class RSPPlauError(EventSummary):
    def init(self, batch, view_name):
        data = RSPPlauError_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class RSPPlauErrorSummary(RSPPlauError):
    title = "RSPPlauError>0 event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSP_RSPPlauError_event_plot@trailereval',
         Client('RSP RSPLowMuSide', '640x700+0+0', 12, 12.3, cm)),
    ]


class RSPtUnstabA(EventSummary):
    def init(self, batch, view_name):
        data = RSPtUnstabA_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class RSPtUnstabASummary(RSPtUnstabA):
    title = "RSPtUnstabA>=0 event details"
    explanation = """Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSP_RSPPtUnstabA_event_plot@trailereval',
         Client('RSP RSPtUnstab', '640x700+0+0', 12, 12.3, cm)),
    ]


class RSPtUnstabB(EventSummary):
    def init(self, batch, view_name):
        data = RSPtUnstabB_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class RSPtUnstabBSummary(RSPtUnstabB):
    title = "RSPtUnstabB>=0 event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSP_RSPPtUnstabB_event_plot@trailereval',
         Client('RSP RSPtUnstab', '640x700+0+0', 12, 12.3, cm)),
    ]


class RSPtUnstabC(EventSummary):
    def init(self, batch, view_name):
        data = RSPtUnstabC_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class RSPtUnstabCSummary(RSPtUnstabC):
    title = "RSPtUnstabC>=0 event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSP_RSPPtUnstabC_event_plot@trailereval',
         Client('RSP RSPtUnstab', '640x700+0+0', 12, 12.3, cm)),
    ]


class RSPtUnstabD(EventSummary):
    def init(self, batch, view_name):
        data = RSPtUnstabD_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return

class RSPtUnstabDSummary(RSPtUnstabD):
    title = "RSPtUnstabC>=0 event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSP_RSPPtUnstabD_event_plot@trailereval',
         Client('RSP RSPtUnstab', '640x700+0+0', 12, 12.3, cm)),
    ]


class RSPtUnstabE(EventSummary):
    def init(self, batch, view_name):
        data = RSPtUnstabE_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class RSPtUnstabESummary(RSPtUnstabE):
    title = "RSPtUnstabE>=0 event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSP_RSPPtUnstabE_event_plot@trailereval',
         Client('RSP RSPtUnstab', '640x700+0+0', 12, 12.3, cm)),
    ]


class RSPtUnstabF(EventSummary):
    def init(self, batch, view_name):
        data = RSPtUnstabF_data

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['GTATRL event']),
            ))
        self.modules.update([])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('end', 'end\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('event', 'event label\n'),
        ])
        return


class RSPtUnstabFSummary(RSPtUnstabF):
    title = "RSPtUnstabF>=0 event details"
    explanation = """ Event: %s, Event Duration: %s """ % ('%(event)s', '%(duration)s')

    extra_modules = [
        ('View_RSP_signals@trailereval',
         Client('RSP Test', '640x700+0+0', 18, 12.3, cm)),
        ('view_trailer_RSP_RSPPtUnstabF_event_plot@trailereval',
         Client('RSP RSPtUnstab', '640x700+0+0', 12, 12.3, cm)),
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
        Frame(ext_y * 6.5, x *1.5, 0.4 * ext_height, 0.8 * width,id='EgoPlot'),
        Frame(ext_y * 36, x *1.5, 0.4 * ext_height, 0.8 * width, id='VehiclePlot'),
    ]

    comparing_frames = [
        Frame(ext_y, x + 1 * width, ext_height, 0.1 * width, id='Title', showBoundary=_showBoundary),
        Frame(ext_y, x + 0.9 * width, 0.6 * ext_height, 0.1 * width, id='Duartion', showBoundary=_showBoundary),
        Frame(ext_y * 6.5, x * 1.5 , 0.4 * ext_height, 0.8 * width, id='EgoPlot', showBoundary=_showBoundary),
        Frame(ext_y * 36, x *1.5, 0.4*ext_height, 0.9*width, id='TargetPlot', showBoundary=_showBoundary),
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
