# -*- dataeval: init -*-
"""

:Name: reportgen_kbendrun_can_tsr_daily

:Description:
    Generates the report for KBKPI .
    Can data and Postmarker(GT) are the input considered for evaluation.

"""

import os
from os.path import expanduser

import matplotlib

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from reportlab.platypus import Image, Spacer, PageBreak, NextPageTemplate, FrameBreak
from reportlab.lib.pagesizes import cm

from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph, italic, bold
from config.interval_header import cIntervalHeader

from aebs.par import aebs_classif
from reportgen.common.analyze import Analyze
from reportgen.common.summaries import EventSummary
from reportgen.common.clients import VideoNavigator, TableNavigator, Client, TrackNavigator, PlotNavigator
from reportgen.common.utils import vector2scalar

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

AEBS_TABLE = None
TRUE_POSITIVE = None
TP = []
TRUE_NEGATIVE = None
TN = []
FALSE_NEGATIVE = None
FN = []
FALSE_POSITIVE_Type_3 = None
FP_T3 = []
FALSE_POSITIVE_Type_2 = None
FP_T2 = []
FALSE_POSITIVE_Type_1 = None
FP_T1 = []
CAN_Signal_group = ""

navistar_can_modules = [
    ('view_nxtvideoeventgrabbernav_lanes-NO_LANES@evaltools',
     VideoNavigator('VideoNavigator', '300x300+0+0', 9, 12, cm)),
    ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
     VideoNavigator('VideoNavigator', '300x300+0+0', 9, 12, cm)),
    ('viewCompare_can_tsr_with_postmarker@tsreval',
     PlotNavigator('PlotNavigator', '640x300+0+0', 10, 6.5, cm)),
    ('view_conti_tsr_data-REPORT@tsreval',
     TableNavigator('view_postmarker_traffic_data', '640x300+0+0', 10, 5.5, cm)),
    ('view_postmarker_traffic_data-REPORT@tsreval',
     TableNavigator('view_postmarker_traffic_data', '640x300+0+0', 11, 5.5, cm)),
    ('view_tsr_can_signals@tsreval',
     TableNavigator('view_postmarker_traffic_data', '640x300+0+0', 11, 5.5, cm)),

]

ford_can_modules = [
    ('view_nxtvideoeventgrabbernav_lanes-NO_LANES@evaltools',
     VideoNavigator('VideoNavigator', '300x300+0+0', 9, 12, cm)),
    ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
     VideoNavigator('VideoNavigator', '300x300+0+0', 9, 12, cm)),
    ('viewCompare_prop_TSR_Alone_with_postmarker@tsreval',
     PlotNavigator('PlotNavigator', '640x300+0+0', 10, 6.5, cm)),
    ('view_conti_tsr_data-REPORT@tsreval',
     TableNavigator('view_postmarker_traffic_data', '640x300+0+0', 10, 5.5, cm)),
    ('view_postmarker_traffic_data-REPORT@tsreval',
     TableNavigator('view_postmarker_traffic_data', '640x300+0+0', 11, 5.5, cm)),
    ('view_prop_tsr_alone_signals@tsreval',
     PlotNavigator('PlotNavigator', '640x300+0+0', 11, 5.5, cm)),
]


class AebsAnalyze(Analyze):
    optdep = dict(
        aebs_events='analyze_kb_kpi_events-last_entries@tsreval',
        weather_condition='view_quantity_vs_weatherconditions_stats-print_count@tsreval',
        time_condition='view_quantity_vs_timeconditions_stats-print_count@tsreval',
        count_vs_aebs_severity='view_count_vs_severity_stats_flr25-print_mergedcount@aebseval.classif',
        dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
        dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
        dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
    )

    query_files = {
        'aebs_events': abspath('../../tsreval/events_inttable_kpi.sql'),
    }
    # def init(self):
    #     if (self.optdep['aebs_events'] in self.passed_optdep):
    #         aebs_ei_ids = index_fill(self.modules.fill(optdep['aebs_events']))
    #         header = cIntervalHeader.fromFileName(query_files['aebs_events'])
    #         table = batch.get_table_dict(header, aebs_ei_ids,
    #                                           sortby=[('measurement', True), ('start [s]', True)])
    #
    #         CAN_Signal_group = table[0]['CAN_Signal_group'][0]

    def fill(self):
        self.view_name = self.batch.create_table_from_last_entries(
            start_date=self.start_date, end_date=self.end_date)

        story = intro(
            "CAN TSR field test evaluation report",
            """
                                This is an automatically generated report, based on field tests with
                                simultaneously measured camera (MFC525)	sensor.<br/>
                                <br/>
                                The output signals of CAN TSR are analyzed with ground truth data(Postmarker Tool) and the
                                relevant events are collected in this report.<br/>
                                Statistical results are presented first, followed by the detailed
                                overview of the individual events.<br/>
                                """
        )
        # Set Event Details Page size
        story += [Paragraph('Event details pagesize is: %s' % "A3-TSR")]

        # if (self.optdep['aebs_events'] in self.passed_optdep):
        #     index_fill = lambda fill: fill.values()[-1]
        #     aebs_ei_ids = index_fill(self.modules.fill(self.optdep['aebs_events']))
        #     header = cIntervalHeader.fromFileName(self.query_files['aebs_events'])
        #     table = self.batch.get_table_dict(header, aebs_ei_ids,
        #                                       sortby=[('measurement', True), ('start [s]', True)])
        #     global  CAN_Signal_group
        #     CAN_Signal_group = table[0]['CAN_Signal_group']

        story.append(PageBreak())
        story.extend(toc())
        story.append(PageBreak())

        story.extend(self.overall_summary())
        summaries = [TPSummary(self.batch, self.view_name),TNSummary(self.batch, self.view_name),
                     FNSummary(self.batch, self.view_name), FP3Summary(self.batch, self.view_name),
                     FP2Summary(self.batch, self.view_name), FP1Summary(self.batch, self.view_name)]
        story.extend(self.summaries(summaries))
        del story[-1]
        story.extend(self.warnings(summaries))
        return story

    def summaries(self, summaries, module_name=None):
        story = [
            IndexedParagraph('TSR summary tables', style='Heading1'),
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

    def warnings(self, summaries):
        story = []
        for summary in summaries:
            story.append(IndexedParagraph(summary.title, style='Heading1'))
            story.extend(self.events(summary))
            story.append(NextPageTemplate('LandscapeTable'))
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

            # driven distance and duration
            if (self.optdep['dur_vs_roadtype'] in self.passed_optdep and
                    self.optdep['dist_vs_roadtype'] in self.passed_optdep):
                roadt_dur = index_fill(self.modules.fill(self.optdep['dur_vs_roadtype']))
                roadt_dist = index_fill(self.modules.fill(self.optdep['dist_vs_roadtype']))

                # distance
                if roadt_dist.total > 0.0:
                    calc_dist_perc = lambda d: (100.0 * d / roadt_dist.total)
                    story += [Paragraph(
                        'Total mileage: %s (ca. %.1f%% city, %.1f%% rural, %.1f%% highway)' %
                        (bold('%.1f km' % roadt_dist.total),
                         calc_dist_perc(roadt_dist['city']),
                         calc_dist_perc(roadt_dist['rural']),
                         calc_dist_perc(roadt_dist['highway']))), ]
                else:
                    story += [Paragraph('Total mileage: %s' % bold('%.1f km' % roadt_dist.total))]
                # duration
                if roadt_dur.total > 0.25:
                    calc_dist_perc = lambda d: (100 * d / roadt_dur.total)
                    story += [Paragraph(
                        'Total duration: %s (ca. %.1f%% standstill, %.1f%% city, %.1f%% rural, %.1f%% highway)' %
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

            # Weather Condition Statistics
            if self.optdep['weather_condition'] in self.passed_optdep:
                weather_dur = index_fill(self.modules.fill(self.optdep['weather_condition']))
                if weather_dur.total > 0.0:
                    story += [Paragraph(
                        'Weather Condition: (%.1f%% Clear, %.1f%% Cloudy, %.1f%% Rain, %.1f%% Snow fall, %.1f%% Fog, %.1f%% Hail)' %
                        (100.0 * weather_dur['Clear'] / weather_dur.total,
                         100.0 * weather_dur['Cloudy'] / weather_dur.total,
                         100.0 * weather_dur['Rain'] / weather_dur.total,
                         100.0 * weather_dur['Snow fall'] / weather_dur.total,
                         100.0 * weather_dur['Fog'] / weather_dur.total,
                         100.0 * weather_dur['Hail'] / weather_dur.total,)), ]
                else:
                    story += [Paragraph(
                        'Weather Condition: (0.0% Clear, 0.0% Cloudy, 0.0% Rain, 0.0% Snow fall, 0.0% Fog, 0.0% Hail)')]
            else:
                self.logger.warning('Weather condition statistics not available')
                story += [Paragraph('Total duration: n/a'), ]

            # Time Condition Statistics
            if self.optdep['time_condition'] in self.passed_optdep:
                time_dur = index_fill(self.modules.fill(self.optdep['time_condition']))
                if time_dur.total > 0.0:
                    story += [Paragraph(
                        'Time Condition: (%.1f%% Day, %.1f%% Night, %.1f%% Twilight)' %
                        (100.0 * time_dur['Day'] / time_dur.total, 100.0 * time_dur['Night'] / time_dur.total,
                         100.0 * time_dur['Twilight'] / time_dur.total))]
                else:
                    story += [Paragraph('Time Condition: (0.0% Day, 0.0% Night, 0.0% Twilight)')]
            else:
                self.logger.warning('Time condition statistics not available')
                story += [Paragraph('Total duration: n/a'), ]

            # common remark
            story += [Paragraph(italic('Remark: Percentage values with "ca." are '
                                       'rounded to nearest 5.'), fontsize=8),
                      Spacer(width=1 * cm, height=0.2 * cm), ]

            # AEBS warning rate
            if (self.optdep['aebs_events'] in self.passed_optdep):
                aebs_ei_ids = index_fill(self.modules.fill(self.optdep['aebs_events']))
                header = cIntervalHeader.fromFileName(self.query_files['aebs_events'])
                table = self.batch.get_table_dict(header, aebs_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global AEBS_TABLE, CAN_Signal_group, TRUE_POSITIVE, TP, TN, TRUE_NEGATIVE, FALSE_NEGATIVE, FN, FALSE_POSITIVE_Type_2, FP_T2, FP_T3, FALSE_POSITIVE_Type_3, FALSE_POSITIVE_Type_1, FP_T1
                AEBS_TABLE = table
                CAN_Signal_group = table[0]['CAN_Signal_group'][0]
                for id, value in enumerate(AEBS_TABLE):
                    if bool(AEBS_TABLE[id]['Event']) and AEBS_TABLE[id]['Event'][0] == u'True Positive':
                        TP.append(AEBS_TABLE[id])
                        TRUE_POSITIVE = TP
                    elif bool(AEBS_TABLE[id]['Event']) and AEBS_TABLE[id]['Event'][0] == u'True Negative':
                        TN.append(AEBS_TABLE[id])
                        TRUE_NEGATIVE = TN
                    elif bool(AEBS_TABLE[id]['Event']) and AEBS_TABLE[id]['Event'][0] == u'False Negative':
                        FN.append(AEBS_TABLE[id])
                        FALSE_NEGATIVE = FN
                    elif bool(AEBS_TABLE[id]['Event']) and AEBS_TABLE[id]['Event'][0] == u'False Positive Type 3':
                        FP_T3.append(AEBS_TABLE[id])
                        FALSE_POSITIVE_Type_3 = FP_T3
                    elif bool(AEBS_TABLE[id]['Event']) and AEBS_TABLE[id]['Event'][0] == u'False Positive Type 2':
                        FP_T2.append(AEBS_TABLE[id])
                        FALSE_POSITIVE_Type_2 = FP_T2
                    elif bool(AEBS_TABLE[id]['Event']) and AEBS_TABLE[id]['Event'][0] == u'False Positive Type 1':
                        FP_T1.append(AEBS_TABLE[id])
                        FALSE_POSITIVE_Type_1 = FP_T1

            # tot_aebs = len(TP)+len(FP_T1)+len(FP_T2)+len(TN)
            # story += [Paragraph('Total number of TSR events: %d' % tot_aebs)]
            else:
                story += [Paragraph('Total number of TSR events: n/a'),
                          Paragraph('Total Traffic Sign events - overall: n/a'),
                          Spacer(width=1 * cm, height=0.2 * cm), ]

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

        if len(AEBS_TABLE) > 0:
            measurement_name = AEBS_TABLE[0]['measurement']
            # CAN_Signal_group = AEBS_TABLE[0]['CAN Signal group']
            tp_count = AEBS_TABLE[0]['CAN_TP']
            tn_count = AEBS_TABLE[0]['CAN_TN']
            fp_count = AEBS_TABLE[0]['CAN_FP']
            fp1_count = AEBS_TABLE[0]['CAN_FP1']
            fp2_count = AEBS_TABLE[0]['CAN_FP2']
            fp3_count = AEBS_TABLE[0]['CAN_FP3']
            fn_count = AEBS_TABLE[0]['CAN_FN']
            total_gt = AEBS_TABLE[0]['CAN_Total_GT']
            gt_existance_false = AEBS_TABLE[0]['CAN_GT_existance_false']
            gt_existance_true = AEBS_TABLE[0]['CAN_GT_existance_true']

            for idx, value in enumerate(AEBS_TABLE):
                if measurement_name != AEBS_TABLE[idx]['measurement']:
                    measurement_name = AEBS_TABLE[idx]['measurement']

                    if AEBS_TABLE[idx]['CAN_Total_GT'] is not None:
                        total_gt += AEBS_TABLE[idx]['CAN_Total_GT']
                    if AEBS_TABLE[idx]['CAN_GT_existance_false'] is not None:
                        gt_existance_false += AEBS_TABLE[idx]['CAN_GT_existance_false']
                    if AEBS_TABLE[idx]['CAN_GT_existance_true'] is not None:
                        gt_existance_true += AEBS_TABLE[idx]['CAN_GT_existance_true']

                    if AEBS_TABLE[idx]['CAN_FP1'] is not None:
                        fp1_count = fp1_count + AEBS_TABLE[idx]['CAN_FP1']
                    if AEBS_TABLE[idx]['CAN_FP2'] is not None:
                        fp2_count = fp2_count + AEBS_TABLE[idx]['CAN_FP2']
                    if AEBS_TABLE[idx]['CAN_FP3'] is not None:
                        fp3_count = fp3_count + AEBS_TABLE[idx]['CAN_FP3']

                    if AEBS_TABLE[idx]['CAN_TP'] is not None:
                        tp_count = tp_count + AEBS_TABLE[idx]['CAN_TP']
                        if AEBS_TABLE[idx]['CAN_TN'] is not None:
                            tn_count = tn_count + AEBS_TABLE[idx]['CAN_TN']
                            if AEBS_TABLE[idx]['CAN_FP'] is not None:
                                fp_count = fp_count + AEBS_TABLE[idx]['CAN_FP']
                                if AEBS_TABLE[idx]['CAN_FN'] is not None:
                                    fn_count = fn_count + AEBS_TABLE[idx]['CAN_FN']
            tot_aebs = tp_count + fp_count + tn_count
            story += [Paragraph(
                'Total Ground Truths : {} ( True Existance: {} , False Existance: {}  )'.format(total_gt,
                                                                                                gt_existance_true,
                                                                                                gt_existance_false)),
                Spacer(width=1 * cm, height=0.2 * cm),
                Paragraph('Total number of TSR events: %d ' % tot_aebs)]

            # common remark
            story += [
                Paragraph(italic('Remark: Total TSR events is sum of True Positive,False Positive and True Negative)'),
                          fontsize=8),
                Spacer(width=1 * cm, height=0.2 * cm), ]

            story += [Paragraph('Total True Positive: {}'.format(tp_count)),
                      Paragraph('Total True Negative: {}'.format(tn_count)),
                      Paragraph(
                          'Total False Positive: {} ( FP1: {} FP2: {} FP3: {})'.format(fp_count, fp1_count, fp2_count,
                                                                                       fp3_count)),
                      Paragraph('Total False Negative: {}'.format(fn_count))]

            ptext = """Confusion Matrix for {}\n""".format(AEBS_TABLE[0]['measurement'])
            meas_name = AEBS_TABLE[0]['measurement']
            confusion_matrix_path = os.path.splitext(AEBS_TABLE[0]['fullmeas'])[0] + ".png"
            if os.path.isfile(confusion_matrix_path):
                fig = Image(os.path.join(confusion_matrix_path), width=12.0 * cm, height=8 * cm)
                story += [Paragraph(ptext), Spacer(0, 0.5 * cm), fig]

            for idx, value in enumerate(AEBS_TABLE):
                if meas_name != AEBS_TABLE[idx]['measurement']:
                    ptext = """Confusion Matrix for {}\n""".format(AEBS_TABLE[idx]['measurement'])
                    confusion_matrix_path = os.path.splitext(AEBS_TABLE[idx]['fullmeas'])[0] + ".png"
                    meas_name = AEBS_TABLE[idx]['measurement']
                    if os.path.isfile(confusion_matrix_path):
                        fig = Image(os.path.join(confusion_matrix_path), width=12.0 * cm, height=8 * cm)
                        story += [Paragraph(ptext), Spacer(0, 0.5 * cm), fig]

            story += [PageBreak()]
        return story

    def events(self, summary):
        statuses = ['fillFLC25_TSR@aebs.fill']
        statuses.extend(summary.statuses)
        groups = ['FLC25', 'moving', 'stationary', 'stopped']
        groups.extend(summary.groups)

        story = []  # summary.get_tracknav_legend()

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
                    Paragraph(summary.explanation % warning, style='Normal'),
                    Paragraph(summary.can_signals % warning, style='Normal'),
                ])
                sync.seek(warning['start'])
                manager.set_roi(warning['start'], warning['end'], color='y',
                                pre_offset=5.0, post_offset=5.0)
                for module_name, client in summary.modules.iteritems():
                    if summary.modules.keys()[1] == module_name:
                        sync.seek(warning['start'] - 0.2)
                        manager.set_roi(warning['start'] - 0.2, warning['end'] - 0.2, color='y',
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


class TruePositive(EventSummary):
    def init(self, batch, view_name):
        data = TRUE_POSITIVE

        if data is not None:

            for row in data:
                if CAN_Signal_group == 'TSSDetectedValue':
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        phase=vector2scalar(row['Event']),
                        weather_condition=vector2scalar(row['WeatherCondition']),
                        time_condition=vector2scalar(row['TimeCondition']),
                        signclass=row['CAN Sign class ID'],
                        CAN_Signal_group=row['CAN_Signal_group'],

                        CAN_0='AutoHighLowBeamControl:',
                        CAN_1=',TSSCurrentRegion:',
                        CAN_2=',TSSDetectedStatus:',
                        CAN_3=',TSSDetectedUoM:',
                        CAN_4=',TSSDetectedValue:',
                        CAN_5=',TSSLifeTime:',
                        CAN_6=',TSSOverspeedAlert:',

                        CAN_0_value=row['CAN_AutoHighLowBeamControl'],
                        CAN_1_value=row['CAN_TSSCurrentRegion'],
                        CAN_2_value=row['CAN_TSSDetectedStatus'],
                        CAN_3_value=row['CAN_TSSDetectedUoM'],
                        CAN_4_value=row['CAN_TSSDetectedValue'],
                        CAN_5_value=row['CAN_TSSLifeTime'],
                        CAN_6_value=row['CAN_TSSOverspeedAlert'],

                        CAN_TP=row['CAN_TP'],
                        CAN_TN=row['CAN_TN'],
                        CAN_FP=row['CAN_FP'],
                        CAN_FN=row['CAN_FN'],

                        can_duration=row['can_duration'],
                        rating=vector2scalar(row['warning rating scale']),
                        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                    ))
                elif CAN_Signal_group == "TSR_SpeedLimit1_E8_sE8":
                    # for row in data:
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        phase=vector2scalar(row['Event']),
                        weather_condition=vector2scalar(row['WeatherCondition']),
                        time_condition=vector2scalar(row['TimeCondition']),
                        signclass=row['CAN Sign class ID'],
                        CAN_Signal_group=row['CAN_Signal_group'],

                        CAN_0="SpeedLimit1:",
                        CAN_1=", SpeedLimit1Supplementary:",
                        CAN_2=', SpeedLimit2:',
                        CAN_3=', SpeedLimitElectronic:',
                        CAN_4=', NoPassingRestriction:',
                        CAN_5=', CountryCode:',
                        CAN_6='',

                        CAN_0_value=row['TSR_SpeedLimit1_E8_sE8'],
                        CAN_1_value=row['TSR_SpeedLimit1Supplementary_E8_sE8'],
                        CAN_2_value=row['TSR_SpeedLimit2_E8_sE8'],
                        CAN_3_value=row['TSR_SpeedLimitElectronic_E8_sE8'],
                        CAN_4_value=row['TSR_NoPassingRestriction_E8_sE8'],
                        CAN_5_value=row['TSR_CountryCode_E8_sE8'],
                        CAN_6_value='',

                        CAN_TP=row['CAN_TP'],
                        CAN_TN=row['CAN_TN'],
                        CAN_FP=row['CAN_FP'],
                        CAN_FN=row['CAN_FN'],

                        can_duration=row['can_duration'],
                        rating=vector2scalar(row['warning rating scale']),
                        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                    ))

            # view_tsr_can_signals
            if CAN_Signal_group == 'TSSDetectedValue':
                self.modules.update(navistar_can_modules)
            elif CAN_Signal_group == "TSR_SpeedLimit1_E8_sE8":
                self.modules.update(ford_can_modules)

            self.columns.update([
                    ('start', 'Start\n[s]\n'),
                    ('phase', 'Event\n\n'),
                    ('signclass', 'SignID\n'),
                ])

        return


class TrueNegative(EventSummary):
    def init(self, batch, view_name):
        data = TRUE_NEGATIVE

        if data is not None:
            CAN_Signal_group = data[0]['CAN_Signal_group'][0]
            if CAN_Signal_group == 'TSSDetectedValue':
                for row in data:
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        phase=vector2scalar(row['Event']),
                        weather_condition=vector2scalar(row['WeatherCondition']),
                        time_condition=vector2scalar(row['TimeCondition']),
                        signclass=row['CAN Sign class ID'],
                        CAN_Signal_group=row['CAN_Signal_group'],

                        CAN_0='AutoHighLowBeamControl:',
                        CAN_1=',TSSCurrentRegion:',
                        CAN_2=',TSSDetectedStatus:',
                        CAN_3=',TSSDetectedUoM:',
                        CAN_4=',TSSDetectedValue:',
                        CAN_5=',TSSLifeTime:',
                        CAN_6=',TSSOverspeedAlert:',

                        CAN_0_value=row['CAN_AutoHighLowBeamControl'],
                        CAN_1_value=row['CAN_TSSCurrentRegion'],
                        CAN_2_value=row['CAN_TSSDetectedStatus'],
                        CAN_3_value=row['CAN_TSSDetectedUoM'],
                        CAN_4_value=row['CAN_TSSDetectedValue'],
                        CAN_5_value=row['CAN_TSSLifeTime'],
                        CAN_6_value=row['CAN_TSSOverspeedAlert'],

                        CAN_TP=row['CAN_TP'],
                        CAN_TN=row['CAN_TN'],
                        CAN_FP=row['CAN_FP'],
                        CAN_FN=row['CAN_FN'],

                        can_duration=row['can_duration'],
                        rating=vector2scalar(row['warning rating scale']),
                        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                    ))
            elif CAN_Signal_group == "TSR_SpeedLimit1_E8_sE8":
                for row in data:
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        phase=vector2scalar(row['Event']),
                        weather_condition=vector2scalar(row['WeatherCondition']),
                        time_condition=vector2scalar(row['TimeCondition']),
                        signclass=row['CAN Sign class ID'],
                        CAN_Signal_group=row['CAN_Signal_group'],

                        CAN_0="SpeedLimit1:",
                        CAN_1=", SpeedLimit1Supplementary:",
                        CAN_2=', SpeedLimit2:',
                        CAN_3=', SpeedLimitElectronic:',
                        CAN_4=', NoPassingRestriction:',
                        CAN_5=', CountryCode:',
                        CAN_6='',

                        CAN_0_value=row['TSR_SpeedLimit1_E8_sE8'],
                        CAN_1_value=row['TSR_SpeedLimit1Supplementary_E8_sE8'],
                        CAN_2_value=row['TSR_SpeedLimit2_E8_sE8'],
                        CAN_3_value=row['TSR_SpeedLimitElectronic_E8_sE8'],
                        CAN_4_value=row['TSR_NoPassingRestriction_E8_sE8'],
                        CAN_5_value=row['TSR_CountryCode_E8_sE8'],
                        CAN_6_value='',

                        can_duration=row['can_duration'],
                        rating=vector2scalar(row['warning rating scale']),
                        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                    ))

            # view_tsr_can_signals
            if CAN_Signal_group == 'TSSDetectedValue':
                self.modules.update(navistar_can_modules)
            elif CAN_Signal_group == "TSR_SpeedLimit1_E8_sE8":
                self.modules.update(ford_can_modules)

            self.columns.update([
                ('start', 'Start\n[s]\n'),
                ('phase', 'Event\n\n'),

                ('signclass', 'SignID\n'),
            ])
        return


class FalseNegative(EventSummary):
    def init(self, batch, view_name):
        data = FALSE_NEGATIVE

        if data is not None:
            CAN_Signal_group = data[0]['CAN_Signal_group'][0]
            if CAN_Signal_group == 'TSSDetectedValue':
                for row in data:
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        phase=vector2scalar(row['Event']),
                        weather_condition=vector2scalar(row['WeatherCondition']),
                        time_condition=vector2scalar(row['TimeCondition']),
                        signclass=row['CAN Sign class ID'],
                        CAN_Signal_group=row['CAN_Signal_group'],

                        CAN_0='AutoHighLowBeamControl:',
                        CAN_1=',TSSCurrentRegion:',
                        CAN_2=',TSSDetectedStatus:',
                        CAN_3=',TSSDetectedUoM:',
                        CAN_4=',TSSDetectedValue:',
                        CAN_5=',TSSLifeTime:',
                        CAN_6=',TSSOverspeedAlert:',

                        CAN_0_value=row['CAN_AutoHighLowBeamControl'],
                        CAN_1_value=row['CAN_TSSCurrentRegion'],
                        CAN_2_value=row['CAN_TSSDetectedStatus'],
                        CAN_3_value=row['CAN_TSSDetectedUoM'],
                        CAN_4_value=row['CAN_TSSDetectedValue'],
                        CAN_5_value=row['CAN_TSSLifeTime'],
                        CAN_6_value=row['CAN_TSSOverspeedAlert'],

                        CAN_TP=row['CAN_TP'],
                        CAN_TN=row['CAN_TN'],
                        CAN_FP=row['CAN_FP'],
                        CAN_FN=row['CAN_FN'],

                        can_duration=row['can_duration'],
                        rating=vector2scalar(row['warning rating scale']),
                        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                    ))
            elif CAN_Signal_group == "TSR_SpeedLimit1_E8_sE8":
                for row in data:
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        phase=vector2scalar(row['Event']),
                        weather_condition=vector2scalar(row['WeatherCondition']),
                        time_condition=vector2scalar(row['TimeCondition']),
                        signclass=row['CAN Sign class ID'],
                        CAN_Signal_group=row['CAN_Signal_group'],

                        CAN_0="SpeedLimit1:",
                        CAN_1=", SpeedLimit1Supplementary:",
                        CAN_2=', SpeedLimit2:',
                        CAN_3=', SpeedLimitElectronic:',
                        CAN_4=', NoPassingRestriction:',
                        CAN_5=', CountryCode:',
                        CAN_6='',

                        CAN_0_value=row['TSR_SpeedLimit1_E8_sE8'],
                        CAN_1_value=row['TSR_SpeedLimit1Supplementary_E8_sE8'],
                        CAN_2_value=row['TSR_SpeedLimit2_E8_sE8'],
                        CAN_3_value=row['TSR_SpeedLimitElectronic_E8_sE8'],
                        CAN_4_value=row['TSR_NoPassingRestriction_E8_sE8'],
                        CAN_5_value=row['TSR_CountryCode_E8_sE8'],
                        CAN_6_value='',

                        CAN_TP=row['CAN_TP'],
                        CAN_TN=row['CAN_TN'],
                        CAN_FP=row['CAN_FP'],
                        CAN_FN=row['CAN_FN'],

                        can_duration=row['can_duration'],
                        rating=vector2scalar(row['warning rating scale']),
                        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                    ))

            # view_tsr_can_signals
            if CAN_Signal_group == 'TSSDetectedValue':
                self.modules.update(navistar_can_modules)
            elif CAN_Signal_group == "TSR_SpeedLimit1_E8_sE8":
                self.modules.update(ford_can_modules)

            self.columns.update([
                ('start', 'Start\n[s]\n'),
                ('phase', 'Event\n\n'),

                ('signclass', 'SignID\n'),
            ])
        return


class FalsePositiveType3(EventSummary):
    def init(self, batch, view_name):
        data = FALSE_POSITIVE_Type_3

        if data is not None:
            CAN_Signal_group = data[0]['CAN_Signal_group'][0]
            if CAN_Signal_group == 'TSSDetectedValue':
                for row in data:
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        phase=vector2scalar(row['Event']),
                        weather_condition=vector2scalar(row['WeatherCondition']),
                        time_condition=vector2scalar(row['TimeCondition']),
                        signclass=row['CAN Sign class ID'],
                        CAN_Signal_group=row['CAN_Signal_group'],

                        CAN_0='AutoHighLowBeamControl:',
                        CAN_1=',TSSCurrentRegion:',
                        CAN_2=',TSSDetectedStatus:',
                        CAN_3=',TSSDetectedUoM:',
                        CAN_4=',TSSDetectedValue:',
                        CAN_5=',TSSLifeTime:',
                        CAN_6=',TSSOverspeedAlert:',

                        CAN_0_value=row['CAN_AutoHighLowBeamControl'],
                        CAN_1_value=row['CAN_TSSCurrentRegion'],
                        CAN_2_value=row['CAN_TSSDetectedStatus'],
                        CAN_3_value=row['CAN_TSSDetectedUoM'],
                        CAN_4_value=row['CAN_TSSDetectedValue'],
                        CAN_5_value=row['CAN_TSSLifeTime'],
                        CAN_6_value=row['CAN_TSSOverspeedAlert'],

                        CAN_TP=row['CAN_TP'],
                        CAN_TN=row['CAN_TN'],
                        CAN_FP=row['CAN_FP'],
                        CAN_FN=row['CAN_FN'],

                        can_duration=row['can_duration'],
                        rating=vector2scalar(row['warning rating scale']),
                        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                    ))
            elif CAN_Signal_group == "TSR_SpeedLimit1_E8_sE8":
                for row in data:
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        phase=vector2scalar(row['Event']),
                        weather_condition=vector2scalar(row['WeatherCondition']),
                        time_condition=vector2scalar(row['TimeCondition']),
                        signclass=row['CAN Sign class ID'],
                        CAN_Signal_group=row['CAN_Signal_group'],

                        CAN_0="SpeedLimit1:",
                        CAN_1=", SpeedLimit1Supplementary:",
                        CAN_2=', SpeedLimit2:',
                        CAN_3=', SpeedLimitElectronic:',
                        CAN_4=', NoPassingRestriction:',
                        CAN_5=', CountryCode:',
                        CAN_6='',

                        CAN_0_value=row['TSR_SpeedLimit1_E8_sE8'],
                        CAN_1_value=row['TSR_SpeedLimit1Supplementary_E8_sE8'],
                        CAN_2_value=row['TSR_SpeedLimit2_E8_sE8'],
                        CAN_3_value=row['TSR_SpeedLimitElectronic_E8_sE8'],
                        CAN_4_value=row['TSR_NoPassingRestriction_E8_sE8'],
                        CAN_5_value=row['TSR_CountryCode_E8_sE8'],
                        CAN_6_value='',

                        CAN_TP=row['CAN_TP'],
                        CAN_TN=row['CAN_TN'],
                        CAN_FP=row['CAN_FP'],
                        CAN_FN=row['CAN_FN'],

                        can_duration=row['can_duration'],
                        rating=vector2scalar(row['warning rating scale']),
                        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                    ))

            # view_tsr_can_signals
            if CAN_Signal_group == 'TSSDetectedValue':
                self.modules.update(navistar_can_modules)
            elif CAN_Signal_group == "TSR_SpeedLimit1_E8_sE8":
                self.modules.update(ford_can_modules)

            self.columns.update([
                ('start', 'Start\n[s]\n'),
                ('phase', 'Event\n\n'),

                ('signclass', 'SignID\n'),
            ])
        return


class FalsePositiveType2(EventSummary):
    def init(self, batch, view_name):
        data = FALSE_POSITIVE_Type_2

        if data is not None:
            CAN_Signal_group = data[0]['CAN_Signal_group'][0]
            if CAN_Signal_group == 'TSSDetectedValue':
                for row in data:
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        phase=vector2scalar(row['Event']),
                        weather_condition=vector2scalar(row['WeatherCondition']),
                        time_condition=vector2scalar(row['TimeCondition']),
                        signclass=row['CAN Sign class ID'],
                        CAN_Signal_group=row['CAN_Signal_group'],

                        CAN_0='AutoHighLowBeamControl:',
                        CAN_1=',TSSCurrentRegion:',
                        CAN_2=',TSSDetectedStatus:',
                        CAN_3=',TSSDetectedUoM:',
                        CAN_4=',TSSDetectedValue:',
                        CAN_5=',TSSLifeTime:',
                        CAN_6=',TSSOverspeedAlert:',

                        CAN_0_value=row['CAN_AutoHighLowBeamControl'],
                        CAN_1_value=row['CAN_TSSCurrentRegion'],
                        CAN_2_value=row['CAN_TSSDetectedStatus'],
                        CAN_3_value=row['CAN_TSSDetectedUoM'],
                        CAN_4_value=row['CAN_TSSDetectedValue'],
                        CAN_5_value=row['CAN_TSSLifeTime'],
                        CAN_6_value=row['CAN_TSSOverspeedAlert'],

                        CAN_TP=row['CAN_TP'],
                        CAN_TN=row['CAN_TN'],
                        CAN_FP=row['CAN_FP'],
                        CAN_FN=row['CAN_FN'],

                        can_duration=row['can_duration'],
                        rating=vector2scalar(row['warning rating scale']),
                        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                    ))
            elif CAN_Signal_group == "TSR_SpeedLimit1_E8_sE8":
                for row in data:
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        phase=vector2scalar(row['Event']),
                        weather_condition=vector2scalar(row['WeatherCondition']),
                        time_condition=vector2scalar(row['TimeCondition']),
                        signclass=row['CAN Sign class ID'],
                        CAN_Signal_group=row['CAN_Signal_group'],

                        CAN_0="SpeedLimit1:",
                        CAN_1=", SpeedLimit1Supplementary:",
                        CAN_2=', SpeedLimit2:',
                        CAN_3=', SpeedLimitElectronic:',
                        CAN_4=', NoPassingRestriction:',
                        CAN_5=', CountryCode:',
                        CAN_6='',

                        CAN_0_value=row['TSR_SpeedLimit1_E8_sE8'],
                        CAN_1_value=row['TSR_SpeedLimit1Supplementary_E8_sE8'],
                        CAN_2_value=row['TSR_SpeedLimit2_E8_sE8'],
                        CAN_3_value=row['TSR_SpeedLimitElectronic_E8_sE8'],
                        CAN_4_value=row['TSR_NoPassingRestriction_E8_sE8'],
                        CAN_5_value=row['TSR_CountryCode_E8_sE8'],
                        CAN_6_value='',

                        CAN_TP=row['CAN_TP'],
                        CAN_TN=row['CAN_TN'],
                        CAN_FP=row['CAN_FP'],
                        CAN_FN=row['CAN_FN'],

                        can_duration=row['can_duration'],
                        rating=vector2scalar(row['warning rating scale']),
                        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                    ))

            # view_tsr_can_signals
            if CAN_Signal_group == 'TSSDetectedValue':
                self.modules.update(navistar_can_modules)
            elif CAN_Signal_group == "TSR_SpeedLimit1_E8_sE8":
                self.modules.update(ford_can_modules)

            self.columns.update([
                ('start', 'Start\n[s]\n'),
                ('phase', 'Event\n\n'),

                ('signclass', 'SignID\n'),
            ])
        return


class FalsePositiveType1(EventSummary):
    def init(self, batch, view_name):
        data = FALSE_POSITIVE_Type_1

        if data is not None:
            CAN_Signal_group = data[0]['CAN_Signal_group'][0]
            if CAN_Signal_group == 'TSSDetectedValue':
                for row in data:
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        phase=vector2scalar(row['Event']),
                        weather_condition=vector2scalar(row['WeatherCondition']),
                        time_condition=vector2scalar(row['TimeCondition']),
                        signclass=row['CAN Sign class ID'],
                        CAN_Signal_group=row['CAN_Signal_group'],

                        CAN_0='AutoHighLowBeamControl:',
                        CAN_1=',TSSCurrentRegion:',
                        CAN_2=',TSSDetectedStatus:',
                        CAN_3=',TSSDetectedUoM:',
                        CAN_4=',TSSDetectedValue:',
                        CAN_5=',TSSLifeTime:',
                        CAN_6=',TSSOverspeedAlert:',

                        CAN_0_value=row['CAN_AutoHighLowBeamControl'],
                        CAN_1_value=row['CAN_TSSCurrentRegion'],
                        CAN_2_value=row['CAN_TSSDetectedStatus'],
                        CAN_3_value=row['CAN_TSSDetectedUoM'],
                        CAN_4_value=row['CAN_TSSDetectedValue'],
                        CAN_5_value=row['CAN_TSSLifeTime'],
                        CAN_6_value=row['CAN_TSSOverspeedAlert'],

                        CAN_TP=row['CAN_TP'],
                        CAN_TN=row['CAN_TN'],
                        CAN_FP=row['CAN_FP'],
                        CAN_FN=row['CAN_FN'],

                        can_duration=row['can_duration'],
                        rating=vector2scalar(row['warning rating scale']),
                        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                    ))
            elif CAN_Signal_group == "TSR_SpeedLimit1_E8_sE8":
                for row in data:
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        phase=vector2scalar(row['Event']),
                        weather_condition=vector2scalar(row['WeatherCondition']),
                        time_condition=vector2scalar(row['TimeCondition']),
                        signclass=row['CAN Sign class ID'],
                        CAN_Signal_group=row['CAN_Signal_group'],

                        CAN_0="SpeedLimit1:",
                        CAN_1=", SpeedLimit1Supplementary:",
                        CAN_2=', SpeedLimit2:',
                        CAN_3=', SpeedLimitElectronic:',
                        CAN_4=', NoPassingRestriction:',
                        CAN_5=', CountryCode:',
                        CAN_6='',

                        CAN_0_value=row['TSR_SpeedLimit1_E8_sE8'],
                        CAN_1_value=row['TSR_SpeedLimit1Supplementary_E8_sE8'],
                        CAN_2_value=row['TSR_SpeedLimit2_E8_sE8'],
                        CAN_3_value=row['TSR_SpeedLimitElectronic_E8_sE8'],
                        CAN_4_value=row['TSR_NoPassingRestriction_E8_sE8'],
                        CAN_5_value=row['TSR_CountryCode_E8_sE8'],
                        CAN_6_value='',

                        CAN_TP=row['CAN_TP'],
                        CAN_TN=row['CAN_TN'],
                        CAN_FP=row['CAN_FP'],
                        CAN_FN=row['CAN_FN'],

                        can_duration=row['can_duration'],
                        rating=vector2scalar(row['warning rating scale']),
                        cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
                    ))

            # view_tsr_can_signals
            if CAN_Signal_group == 'TSSDetectedValue':
                self.modules.update(navistar_can_modules)
            elif CAN_Signal_group == "TSR_SpeedLimit1_E8_sE8":
                self.modules.update(ford_can_modules)

            self.columns.update([
                ('start', 'Start\n[s]\n'),
                ('phase', 'Event\n\n'),

                ('signclass', 'SignID\n'),
            ])
        return


class TPSummary(TruePositive):
    title = "TSR True Positive event details"
    explanation = """Event: %s, Event time: %s,Can Duration: %s sec, Weather Condition: %s, Time: %s""" % (        '%(phase)s', '%(start)s', '%(can_duration).2f', '%(weather_condition)s', '%(time_condition)s')

    can_signals = """%s %s %s %s %s %s %s %s %s %s %s %s %s %s""" % \
                  ('%(CAN_0)s', '%(CAN_0_value)s',
                   '%(CAN_1)s', '%(CAN_1_value)s',
                   '%(CAN_2)s', '%(CAN_2_value)s',
                   '%(CAN_3)s', '%(CAN_3_value)s',
                   '%(CAN_4)s', '%(CAN_4_value)s',
                   '%(CAN_5)s', '%(CAN_5_value)s',
                   '%(CAN_6)s', '%(CAN_6_value)s',
                   )

    statuses = ['fillFLC25_TSR@aebs.fill']
    groups = ['FLC25_TSR']


class TNSummary(TrueNegative):
    title = "TSR True Negative event details"
    explanation = """Event: %s, Event time: %s,   Weather Condition: %s, Time: %s""" % (
        '%(phase)s', '%(start)s', '%(weather_condition)s', '%(time_condition)s')

    can_signals = """%s %s %s %s %s %s %s %s %s %s %s %s %s %s""" % \
                  ('%(CAN_0)s', '%(CAN_0_value)s',
                   '%(CAN_1)s', '%(CAN_1_value)s',
                   '%(CAN_2)s', '%(CAN_2_value)s',
                   '%(CAN_3)s', '%(CAN_3_value)s',
                   '%(CAN_4)s', '%(CAN_4_value)s',
                   '%(CAN_5)s', '%(CAN_5_value)s',
                   '%(CAN_6)s', '%(CAN_6_value)s',
                   )
    statuses = ['fillFLC25_TSR@aebs.fill']
    groups = ['FLC25_TSR']


class FNSummary(FalseNegative):
    title = "TSR False Negative event details"
    explanation = """Event: %s, Event time: %s,   Weather Condition: %s, Time: %s""" % (
        '%(phase)s', '%(start)s', '%(weather_condition)s', '%(time_condition)s')

    can_signals = """%s %s %s %s %s %s %s %s %s %s %s %s %s %s""" % \
                  ('%(CAN_0)s', '%(CAN_0_value)s',
                   '%(CAN_1)s', '%(CAN_1_value)s',
                   '%(CAN_2)s', '%(CAN_2_value)s',
                   '%(CAN_3)s', '%(CAN_3_value)s',
                   '%(CAN_4)s', '%(CAN_4_value)s',
                   '%(CAN_5)s', '%(CAN_5_value)s',
                   '%(CAN_6)s', '%(CAN_6_value)s',
                   )

    statuses = ['fillFLC25_TSR@aebs.fill']
    groups = ['FLC25_TSR']


class FP3Summary(FalsePositiveType3):
    title = "TSR False Positive Type 3 event details"
    explanation = """Event: %s, Event time: %s, Can Duration: %s sec, Weather Condition: %s, Time: %s""" % (
        '%(phase)s', '%(start)s', '%(can_duration).2f', '%(weather_condition)s', '%(time_condition)s')

    can_signals = """%s %s %s %s %s %s %s %s %s %s %s %s %s %s""" % \
                  ('%(CAN_0)s', '%(CAN_0_value)s',
                   '%(CAN_1)s', '%(CAN_1_value)s',
                   '%(CAN_2)s', '%(CAN_2_value)s',
                   '%(CAN_3)s', '%(CAN_3_value)s',
                   '%(CAN_4)s', '%(CAN_4_value)s',
                   '%(CAN_5)s', '%(CAN_5_value)s',
                   '%(CAN_6)s', '%(CAN_6_value)s',
                   )

    statuses = ['fillFLC25_TSR@aebs.fill']
    groups = ['FLC25_TSR']


class FP2Summary(FalsePositiveType2):
    title = "TSR False Positive Type 2 event details"
    explanation = """Event: %s, Event time: %s, Can Duration: %s sec, Weather Condition: %s, Time: %s""" % (
        '%(phase)s', '%(start)s', '%(can_duration).2f', '%(weather_condition)s', '%(time_condition)s')

    can_signals = """%s %s %s %s %s %s %s %s %s %s %s %s %s %s""" % \
                  ('%(CAN_0)s', '%(CAN_0_value)s',
                   '%(CAN_1)s', '%(CAN_1_value)s',
                   '%(CAN_2)s', '%(CAN_2_value)s',
                   '%(CAN_3)s', '%(CAN_3_value)s',
                   '%(CAN_4)s', '%(CAN_4_value)s',
                   '%(CAN_5)s', '%(CAN_5_value)s',
                   '%(CAN_6)s', '%(CAN_6_value)s',
                   )

    statuses = ['fillFLC25_TSR@aebs.fill']
    groups = ['FLC25_TSR']


class FP1Summary(FalsePositiveType1):
    title = "TSR False Positive Type 1 event details"
    explanation = """Event: %s, Event time: %s,Can Duration: %s sec, Weather Condition: %s, Time: %s""" % (
        '%(phase)s', '%(start)s', '%(can_duration).2f', '%(weather_condition)s', '%(time_condition)s')

    can_signals = """%s %s %s %s %s %s %s %s %s %s %s %s %s %s""" % \
    ('%(CAN_0)s','%(CAN_0_value)s',
     '%(CAN_1)s','%(CAN_1_value)s',
     '%(CAN_2)s','%(CAN_2_value)s',
     '%(CAN_3)s','%(CAN_3_value)s',
     '%(CAN_4)s','%(CAN_4_value)s',
     '%(CAN_5)s','%(CAN_5_value)s',
     '%(CAN_6)s','%(CAN_6_value)s',
     )

    statuses = ['fillFLC25_TSR@aebs.fill']
    groups = ['FLC25_TSR']


if __name__ == '__main__':
    from reportgen.common.main import main

    main(os.path.abspath(__file__))
