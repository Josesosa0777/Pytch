# -*- dataeval: init -*-

import os

import matplotlib
from aebs.fill.calc_radar_aebs_phases import Calc as Flr25Calc
from aebs.par import paebs_classif
from config.interval_header import cIntervalHeader
from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph, italic, bold, grid_table_style
from measproc.batchsqlite import str_cell
from pyutils.math import round2
from reportgen.common.analyze import Analyze
from reportgen.common.clients import Client, TrackNavigator, VideoNavigator
from reportgen.common.summaries import EventSummary, PIC_DIR, Summary
from reportgen.common.utils import vector2scalar, vector2scalar2
from reportlab.lib import colors
from reportlab.lib.pagesizes import inch, cm, A4, A3, landscape
from reportlab.platypus import Image, Spacer, PageBreak, Table, NextPageTemplate, FrameBreak, BaseDocTemplate, PageTemplate, Frame
from reportlab.platypus import SimpleDocTemplate

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError


def abspath(pth): return os.path.abspath(
    os.path.join(os.path.dirname(__file__), pth))


PAEBS_TABLE = None
CORRUPT_MEAS_TABLE = None


class AebsAnalyze(Analyze):
    optdep = dict(
        paebs_events='analyze_events_paeb-last_entries@paebseval',
        count_vs_aebs_severity='view_count_vs_severity_stats_flr25-print_mergedcount@paebseval.classif',
        smess_faults='analyze_smess_faults-last_entries@flr20eval.faults',
        # TODO merge crash event script
        a087_faults='analyze_a087_faults-last_entries@flr20eval.faults',
        flc20_spec_statuses='analyze_issues-last_entries@mfc525eval.sensorstatus',
        dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
        dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
        dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
        corrupt_meas_event="analyze_events_to_find_corrupt_meas-last_entries@aebseval",
        # TODO Get signal for day time
        dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@mfc525eval.daytime',
        dur_vs_inlane_tr0='view_quantity_vs_inlane_flr20_tr0_stats-print_duration@trackeval.inlane',
        dur_vs_inlane_tr0_fused='view_quantity_vs_inlane_flr20_tr0_fused_stats-print_duration@trackeval.inlane',
        dist_vs_inlane_tr0='view_quantity_vs_inlane_flr20_tr0_stats-print_mileage@trackeval.inlane',
        dist_vs_inlane_tr0_fused='view_quantity_vs_inlane_flr20_tr0_fused_stats-print_mileage@trackeval.inlane',
    )

    query_files = {
        'paebs_events': abspath('../../paebseval/events_inttable.sql'),
        'corrupt_meas_event': abspath('../../aebseval/events_inttable_to_get_corrupt_meas.sql'),
    }

    def analyze(self, story):  # overwritten function to individualize report for paebs
        doc = self.get_doc('dataeval.simple', pagesize=A4,
                           header="Strictly confidential")
        addPageTemplates(doc)
        doc.multiBuild(story)
        return

    def explanation(self):
        story = [IndexedParagraph('Data Interpretation', style='Heading1')]

        story += [IndexedParagraph('Statistical Results', style='Heading2')]
        ptext = """The statistical values are valid in the indicated
      time period.<br/>
      The ratios are representing the distribution over time, unless
      explicitly stated otherwise."""
        story += [Paragraph(ptext)]

        story += [IndexedParagraph('PAEBS Event Classification',
                                   style='Heading2')]
        ptext = """Besides the automatic measurement evaluation, all PAEBS events
      are reviewed and rated manually.<br/>
      The two most important aspects are the severity and root cause."""
        story += [Paragraph(ptext)]
        story += [IndexedParagraph('PAEBS Event Severities', style='Heading3')]
        ptext = """Five pre-defined severity classes are used:<br/>
      <br/>
      <b>1 - False Alarm</b><br/>
      Driver has no idea, what the warning was given for, e.g. bridge,
      ghost objects etc.<br/>
      <br/>
      <b>2 - Questionable False Alarm</b><br/>
      Very unlikely to become a dangerous situation, but real obstacle is
      present, e.g. parking car, low speed situations.<br/>
      <br/>
      <b>3 - Questionable</b><br/>
      50% of the drivers would find the warning helpful, 50% would not.<br/>
      Driver keeps speed, only soft reaction, e.g. sharp turn, braking car.<br/>
      <br/>
      <b>4 - Questionable Justified Alarm</b><br/>
      Warning supposed to be helpful for the driver.<br/>
      Driver action was needed (pedal activation, steering), e.g. sharp turn,
      braking car.<br/>
      <br/>
      <b>5 - Justified Alarm</b><br/>
      Driver has to make emergency maneuver (evasive steering or emergency
      braking) to avoid a collision; it is obvious that a crash was likely.<br/>
      """
        story += [Paragraph(ptext)]

        story += [PageBreak()]

        story += [IndexedParagraph('PAEBS Event Causes', style='Heading3')]
        ptext = """A total of twelve causes for <b>PAEBS events</b> are defined, which in turn can be assigned to three <b><u>event groups</u></b>:<br/>
      <br/>
      <b><u>Group 1: Misclassifications</u></b></p><br/>
      <br/>
      <b>Misclassification: Ghost Object</b><br/>
      PAEBS reacts to a non-existing object due to e.g. improper radar
      reflection.<br/>
      <br/>
      <b>Misclassification: Surrounding</b><br/>
      PAEBS reacts to an existing but out-of-plane object, e.g. bridges, manhole.<br/>
      <br/>
      <b>Misclassification: Road Infrastructure</b><br/>
      PAEBS reacts to an exsiting in-plane object, that is part of static road infrastructure such as traffic signs, reflector posts, guardrails or planting.<br/>
      <br/>
      <b>Misclassification: Vehicle</b><br/>
      PAEBS reacts to a (part) of a vehicle or other regular road user that does not fall under the VRU category, e.g. tires.<br/>
      <br/>
      <b>Misclassification: Others</b><br/>
      PAEBS reacts on a not yet defined object.<br/>
      <br/>
      <b><u>Group 2: Wrong Environment Interpretation</u></b><br/>
      <br/>
      <b>Oncoming Traffic</b><br/>
      PAEBS reacts to oncoming traffic in an adjacent lane.<br/>
      <br/>
      <b>Out-Of-Path/On Sidewalk VRU</b><br/>
      PAEBS reacts on a VRU that is walking clearly outside of the ego path (e.g. on a sidewalk)<br/>.
      <br/>
      <b>Sharp Turning of Ego Vehicle</b><br/>
      PAEBS reacts to a potentially dangerous traffic situation in a direct extension of the ego vehicle's longitudinal axis, which, however, does not require intervention due to the ego vehicle's turning maneuver.<br/>
      <br/>
      <b><u>Group 3: Complex VRU Behaviour</u></b><br/>
      <br/>
      <b>Stopping/Turning VRU</b><br/>
      PAEBS reacts to VRUs that are not at risk in the specific traffic situation, but may temporarily appear to be at risk due to their difficult-to-predict movement sequences.<br/>
      <br/>
      <b><u>Group 4: Wrong Behaviour Detection</u></b><br/>
      <br/>
      <b>False Crossing VRU</b><br/>
      PAEBS incorrectly classifies a VRU as crossing and reacts on it although it is actually not crossing.<br/>
      <br/>
      <b><u>Group 5: Dangerous VRU Behaviour</u></b><br/>
      <br/>
      <b>Crossing VRU</b><br/>
      PAEBS classifies a VRU as crossing and reacts to it even if it might not be necessary from an objective point of view.<br/>
      <br/>
      <b>In-Path VRU</b><br/>
      PAEBS reacts on a VRU within the path of the ego vehicle.<br/>
      """
        story += [Paragraph(ptext)]

        story += [PageBreak()]

        story += [IndexedParagraph('Coordinate frames', style='Heading2')]
        ptext = """All values in this document are referenced to the conventional
      land vehicle frame according to ISO 8855, having its origin in the middle of the front bumper.
      The x axis is pointing forward, while the y axis is pointing to the left.
      The remaining directions fulfill the right-hand rule."""
        fig = Image(os.path.join(PIC_DIR, 'coord_sys_paebs.png'),
                    width=15.0*cm, height=5.8*cm)
        story += [Paragraph(ptext), Spacer(0, 0.5*cm), fig,
                  NextPageTemplate('LandscapeTable'), ]

        story += [PageBreak()]
        return story

    def fill(self):
        self.view_name = self.batch.create_table_from_last_entries(
            start_date=self.start_date, end_date=self.end_date)

        fig = Image(os.path.join(PIC_DIR, 'paebs_icon1.png'),
                    width=15.0*cm, height=12.5*cm)
        story = [Spacer(0, 1.0*cm), fig, Spacer(0, 1.0*cm)]

        story += intro(
            "PAEBS Field Test Evaluation Report",
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
        # Set Event Details Page size
        story.append(PageBreak())
        story.extend(toc())
        story.append(PageBreak())

        story.extend(self.overall_summary())
        story.extend(self.explanation())
        story.extend(self.paebs_event_classification())
        summaries = [PaebsSummary(self.batch, self.view_name)]
        story.extend(self.summaries(summaries))
        story.extend(self.warnings(summaries))
        flc25_corrupt_meas_summary = [CorruptMeasSummary(self.batch, self.view_name)]
        story.extend(self.flc25_corrupt_meas_summary(flc25_corrupt_meas_summary))
        #story.extend(self.faults())
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
                      Spacer(width=1*cm, height=0.2*cm), ]

            # driven distance and duration
            if (self.optdep['dur_vs_roadtype'] in self.passed_optdep and
                    self.optdep['dist_vs_roadtype'] in self.passed_optdep):
                roadt_dur = index_fill(self.modules.fill(
                    self.optdep['dur_vs_roadtype']))
                roadt_dist = index_fill(self.modules.fill(
                    self.optdep['dist_vs_roadtype']))

                # distance
                if roadt_dist.total > 0.0:
                    def calc_dist_perc(d): return int(
                        round2(d/roadt_dist.total*100.0, 5.0))
                    story += [Paragraph(
                        'Total mileage: %s (ca. %d%% city, %d%% rural, %d%% highway)' %
                        (bold('%.1f km' % roadt_dist.total),
                         calc_dist_perc(roadt_dist['city']),
                         calc_dist_perc(roadt_dist['rural']),
                         calc_dist_perc(roadt_dist['highway']))), ]
                else:
                    story += [Paragraph('Total mileage: %s' %
                                        bold('%.1f km' % roadt_dist.total))]
                # duration
                if roadt_dur.total > 0.25:
                    def calc_dist_perc(d): return int(
                        round2(d/roadt_dur.total*100.0, 5.0))
                    story += [Paragraph(
                        'Total duration: %s (ca. %d%% standstill, %d%% city, %d%% rural, %d%% highway)' %
                        (bold('%.1f hours' % roadt_dur.total),
                         calc_dist_perc(roadt_dur['ego stopped']),
                         calc_dist_perc(roadt_dur['city']),
                         calc_dist_perc(roadt_dur['rural']),
                         calc_dist_perc(roadt_dur['highway']))), ]
                else:
                    story += [Paragraph('Total duration: %s' %
                                        bold('%.1f hours' % roadt_dur.total))]
            else:
                self.logger.warning('Road type statistics not available')
                story += [Paragraph('Total duration: n/a'),
                          Paragraph('Total mileage: n/a'), ]
            # engine running
            if self.optdep['dur_vs_engine_onoff'] in self.passed_optdep:
                engine_dur = index_fill(self.modules.fill(
                    self.optdep['dur_vs_engine_onoff']))
                if 'roadt_dur' in locals():
                    # plau check for durations of different sources
                    # 2% tolerance
                    if roadt_dur.total > 0.25 and abs(1.0 - engine_dur.total/roadt_dur.total) > 0.02:
                        self.logger.error("Different duration results: %.1f h (engine state) "
                                          "vs. %.1f h (road type)" % (engine_dur.total, roadt_dur.total))
                # duration
                if engine_dur.total > 0.0:
                    story += [Paragraph(
                        'Total duration: %.1f hours (%.1f%% engine running, %.1f%% engine off)' %
                        (engine_dur.total, 100.0 * engine_dur['yes']/engine_dur.total, 100.0 * engine_dur['no']/engine_dur.total)), ]
                else:
                    story += [Paragraph('Total duration: %.1f hours' %
                                        engine_dur.total)]
            else:
                self.logger.warning('Engine state statistics not available')
                story += [Paragraph('Total duration: n/a'), ]
            # daytime
            if self.optdep['dur_vs_daytime'] in self.passed_optdep:
                daytime_dur = index_fill(
                    self.modules.fill(self.optdep['dur_vs_daytime']))
                if 'roadt_dur' in locals():
                    # plau check for durations of different sources
                    # 2% tolerance
                    if roadt_dur.total > 0.25 and abs(1.0 - daytime_dur.total/roadt_dur.total) > 0.02:
                        self.logger.error("Different duration results: %.1f h (daytime) "
                                          "vs. %.1f h (road type)" % (daytime_dur.total, roadt_dur.total))
                # duration
                if daytime_dur.total > 0.0:
                    def calc_dist_perc(d): return int(
                        round2(d/daytime_dur.total*100.0, 5.0))
                    story += [Paragraph(
                        'Total duration: %.1f hours (ca. %d%% day, %d%% night, %d%% dusk)' %
                        (daytime_dur.total,
                         calc_dist_perc(daytime_dur['day']),
                         calc_dist_perc(daytime_dur['night']),
                         calc_dist_perc(daytime_dur['dusk']))), ]
                else:
                    story += [Paragraph('Total duration: %.1f hours' %
                                        daytime_dur.total)]
            else:
                self.logger.warning('Daytime statistics not available')
                story += [Paragraph('Total duration: n/a'), ]
            # common remark
            story += [Paragraph(italic('Remark: Percentage values with "ca." are '
                                       'rounded to nearest 5.'), fontsize=8),
                      Spacer(width=1*cm, height=0.2*cm), ]

            # AEBS warning rate
            if (self.optdep['paebs_events'] in self.passed_optdep and
                    self.optdep['count_vs_aebs_severity'] in self.passed_optdep):
                paebs_ei_ids = index_fill(
                    self.modules.fill(self.optdep['paebs_events']))
                header = cIntervalHeader.fromFileName(
                    self.query_files['paebs_events'])
                table = self.batch.get_table_dict(header, paebs_ei_ids, sortby=[
                                                  ('measurement', True), ('start [s]', True)])
                global PAEBS_TABLE
                PAEBS_TABLE = table

                paebs_count = index_fill(self.modules.fill(
                    self.optdep['count_vs_aebs_severity']))
                WARNING_RATING_LABEL_CNT = 0

                for i in range(len(table)):
                    try:
                        if not table[i]['warning rating scale']:
                            WARNING_RATING_LABEL_CNT += 1
                    except Exception as e:
                        pass

                tot_paebs = len(table)
                story += [Paragraph('Total number of PAEBS events: %d' %
                                    tot_paebs)]

                story += [Paragraph('Total unlabeled events : %d' % WARNING_RATING_LABEL_CNT),
                          Spacer(width=1 * cm, height=0.2 * cm), ]


                if 'roadt_dist' in locals() and roadt_dist.total > 0.0:
                    tot_rate = float(tot_paebs)/roadt_dist.total * 1000.0
                    false_rate = float(
                        paebs_count['1-False alarm'])/roadt_dist.total * 1000.0
                    ques_rate = float(
                        paebs_count['2-Questionable false alarm'])/roadt_dist.total * 1000.0
                    story += [Paragraph('PAEBS warning rate - overall: <b>%.1f events / 1000 km</b>' % tot_rate),
                              Paragraph(
                                  'PAEBS warning rate - 1-False alarm: <b>%.1f events / 1000 km</b>' % false_rate),
                              Paragraph(
                                  'PAEBS warning rate - 2-Questionable false alarm: <b>%.1f events / 1000 km</b>' % ques_rate),
                              Spacer(width=1*cm, height=0.2*cm), ]
                else:
                    story += [Paragraph('PAEBS warning rate: n/a'),
                              Spacer(width=1*cm, height=0.2*cm), ]
            else:
                story += [Paragraph('Total number of PAEBS events: n/a'),
                          Paragraph('PAEBS warning rate: n/a'),
                          Spacer(width=1*cm, height=0.2*cm), ]

            # Detected VRUs
            num_vru = self.batch.query("""
                                Select COUNT(title) From 
                                entryintervals 
                                JOIN entries
                                on entryintervals.entryid == entries.id
                                where title = 'PAEBS VRU Detection'
                                """)
            story += [Paragraph('Total number of detected VRUs: <b>%d</b>' % num_vru[0])]
            
            if roadt_dist.total > 0.0:
                story += [Paragraph('Detected VRUs per km: <b>%.1f 1/km</b>' % (num_vru[0][0]/roadt_dist.total))]
            
            # Automated False Positive Rate
            afpr = self.batch.query("""
                                Select COUNT(title) From 
                                entryintervals 
                                JOIN entries
                                on entryintervals.entryid == entries.id
                                where title = 'PAEBS Automated False Positive'
                                """)
            if roadt_dist.total > 0.0:
                story += [Paragraph('Automated False Positive Rate per km: <b>%.1f 1/km</b>' % (afpr[0][0]/roadt_dist.total))]
             

            if (self.optdep['corrupt_meas_event'] in self.passed_optdep):
                corrupt_meas_ei_ids = index_fill(self.modules.fill(self.optdep['corrupt_meas_event']))
                header1 = cIntervalHeader.fromFileName(self.query_files['corrupt_meas_event'])
                corrupt_meas_table = self.batch.get_table_dict(header1, corrupt_meas_ei_ids,
                                                               sortby=[('measurement', True), ('start [s]', True)])
                global CORRUPT_MEAS_TABLE
                CORRUPT_MEAS_TABLE = corrupt_meas_table

            # system performance
            def m_plot(m): return self.module_plot(m,
                                                   windgeom="250x200+0+0", width=60.0, height=60.0, unit=1.0, kind='%',
                                                   overwrite_start_end=True, start_date=start_date, end_date=end_date)
            table_style = [
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]
            story += [Table([
                [m_plot("view_quantity_vs_systemstate_stats_flr25-pie_duration@paebseval.systemstate"),
                 ],
            ], style=table_style)]
            return

        story = [IndexedParagraph('Overall summary', style='Heading1')]

        story += [IndexedParagraph('Cumulative results', style='Heading2')]
        def index_fill(fill): return fill.all
        one_summary(story, self.start_date, self.end_date, index_fill)

        if 'datelist' in self.global_params:
            story += [IndexedParagraph('Latest results', style='Heading2')]
            def index_fill(fill): return fill.values()[-1]
            middatelist = self.global_params.get('datelist', "").split()
            one_summary(story, middatelist[-1], self.end_date, index_fill)

        story += [PageBreak()]
        return story

    def paebs_event_classification(self):
        story = [IndexedParagraph(
            'PAEBS event classification', style='Heading1')]

        def m_plot(m): return self.module_plot(m,
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
            "view_collision_probability_hist-probability@paebseval.classif",
            windgeom="500x300+0+0", width=60.0, height=60.0, unit=1.0, kind='%')]

        story += [PageBreak()]
        return story

    def faults(self):
        def index_fill(fill): return fill.all

        gt_kwargs = dict(
            sortby=[('measurement', True), ('start [s]', True)],
            cell_formatter=str_cell,
        )
        table_kwargs = dict(
            style=grid_table_style,
        )

        story = [IndexedParagraph('FLR25 faults ()', 'Heading2')]
        return story

    def flc25_corrupt_meas_summary(self, summaries, module_name=None):
        story = [
            IndexedParagraph('Corrupt Measurement Summary', style='Heading1'),
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
        statuses = ['fillFLC25_PAEBS_DEBUG@aebs.fill']
        statuses.extend(summary.statuses)
        groups = ['FLC25_PAEBS_DEBUG']
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
                title = self.EVENT_LINK % (
                    os.path.basename(meas), warning['start'])
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
                if summary.modules:
                    story.pop(-1)  # remove last FrameBreak
            manager.close()
        return story


class AebsSummary(EventSummary):
    def init(self, batch, view_name):
        data = PAEBS_TABLE

        for row in data:
            # Handle large comments
            comment_user = str(row['comment'])
            if len(comment_user) > 250:
                comment_user = comment_user[0:249] + '...[to be continued]...'
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]']+row['duration [s]'],
                duration=row['duration [s]'],
                phase=vector2scalar(row['cascade phase']),
                moving=vector2scalar2(row['moving state']),
                source=vector2scalar(row['source']),
                speed=row['ego speed [km/h]'],
                target_dx=row['dx along ego path [m]'],
                vx=row['vx_ref [km/h]'],
                prob=row['collision probability [%]'],
                rating=vector2scalar(row['warning rating scale']),
                cause=vector2scalar(row['warning cause']),
                comment=comment_user
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
            ('phase', 'paebs phase\n\n'),
            ('moving', 'moving\nstate\n'),
            ('source', 'source\n'),
            ('prob', 'coll. prob.\n[%]\n'),
            ('speed', 'ego speed\n[kmph]\n'),
        ])
        return


class PaebsSummary(AebsSummary):

    paebs_debug_ped_cross_im = Image(os.path.join(PIC_DIR, 'flc25_paebs_debug_ped_crossing_legend.png'),
                                     width=0.5 * cm, height=0.5 * cm)
    paebs_debug_ped_not_cross_im = Image(os.path.join(PIC_DIR, 'flc25_paebs_debug_ped_not_crossing_legend.png'),
                                         width=0.5 * cm, height=0.5 * cm)
    paebs_debug_bic_cross_im = Image(os.path.join(PIC_DIR, 'flc25_paebs_debug_bic_crossing_legend.png'),
                                     width=0.5 * cm, height=0.5 * cm)
    paebs_debug_bic_not_cross_im = Image(os.path.join(PIC_DIR, 'flc25_paebs_debug_bic_not_crossing_legend.png'),
                                         width=0.5 * cm, height=0.5 * cm)

    title = "PAEBS event details"
    explanation = """
  <b>Phase</b>: PAEBS %s<br/>
  <b>Event Duration</b>: %s sec<br/>
  <b>Event Cause</b>: %s<br/>
  <b>Event Rating</b>: %s<br/>
  Event is triggered because <b>PAEBS state</b> was active: warning (%d), partial (%d)
  or emergency (%d) braking.<br/> 
  <b>Comment:</b> %s.
  """\
    % ('%(phase)s', '%(duration).2f', '%(cause)s', '%(rating)s',
       Flr25Calc.WARNING, Flr25Calc.PARTIAL, Flr25Calc.EMERGENCY, '%(comment)s')

    legend_pics = [
        (paebs_debug_ped_not_cross_im, 'pedestrian not crossing'),
        (paebs_debug_ped_cross_im, 'pedestrian crossing'),
        (paebs_debug_bic_not_cross_im, 'bicyclist not crossing'),
        (paebs_debug_bic_cross_im, 'bicyclist crossing'),
    ]

    extra_modules = [
        ('view_paebs_object_data-w/oCascadePrediction@paebseval.debug',
         Client('Object_Plot', '640x700+0+0', 11, 12, cm)),
        ('view_paebs_debug_data@paebseval.debug',
            Client('Debug_Plot', '640x700+0+0', 11, 12, cm)),
        ('view_driver_and_vehicle_paebsout@paebseval',
            Client('Driver&Vehicle_PaebsOut_Plot', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_PAEBS_DEBUG@aebs.fill']
    groups = ['FLC25_PAEBS_DEBUG']

    def get_tracknav_legend(self):
        story = [
            Paragraph('Legend of the birdeye view picture', style='Heading3'),
            Paragraph('Meaning of the PAEBS debug object shapes:',
                      style='Normal'),
            Table([pic for pic in self.legend_pics], hAlign='LEFT'),
            Spacer(width=1*cm, height=0.2*cm),
            Paragraph('Meaning of the shape type:', style='Normal'),
            Table([
                ["diamond", 'pedestrian'],
                ["circle", 'bicyclist']
            ], hAlign='LEFT'),
            Spacer(width=1*cm, height=0.2*cm),
            Paragraph('Meaning of the colors and filling:', style='Normal'),
            Table([['empty', 'not crossing'],
                   ['filled', 'crossing']],
                  style=[('TEXTCOLOR', (0, 0), (0,  0), colors.blue),
                         ('TEXTCOLOR', (0, 1), (0,  1), colors.red)],
                  hAlign='LEFT'),
            Spacer(width=1*cm, height=0.2*cm),
            Paragraph(r'Meaning of the object label: {track}({lat}|{long})',
                      style='Normal'),
            Table([
                ['track', 'Name of the track.'],
                ['lat', 'Lateral distance from the ego vehicle. Left is positive'],
                ['long', 'Longitudinal distance from the ego vehicle.'],
            ], hAlign='LEFT'),
            Spacer(width=1*cm, height=0.2*cm),
        ]
        return story


def addPageTemplates(doc):

    # Get Sizes and Positions for Frames on Page
    x, y, width, height = doc.getGeom()
    ext_x, ext_y, ext_width, ext_height = doc.getExtGeom()
    app_x, app_y, app_width, app_height = doc.getAppGeom()
    z_height, z_width = landscape(A3)  # Used for A3 frames, as doc template is set to A4 and not usable for A3 templates

    offset = 58  # Manual adapted margin offset

    z_x = offset
    z_y = offset
    z_width = z_width - 2 * offset
    z_height = z_height - 2 * offset

    _showBoundary = 0

    portrait_frames = [
        Frame(ext_x, y, ext_width, height, id='FullPage'),
    ]

    # Special Frames just for A3 Event Summary View
    landscape_frames = [
        Frame(z_x,
              z_y + 0.9 * z_width,
              z_height,
              0.1 * z_width,
              id='Title'),
        Frame(z_y,
              z_x + 0.7 * z_width,
              z_height,
              0.2 * z_width,
              id='Duartion'),
        Frame(z_y,
              z_x + 0.4 * z_width,
              0.2 * z_height,
              0.3 * z_width,
              id='VideoNav'),
        Frame(z_y,
              z_x,
              0.2 * z_height,
              0.4 * z_width,
              id='TrackNav'),
        Frame(z_y + 0.2 * z_height,
              z_x,
              0.266 * z_height,
              0.6 * z_width,
              id='EgoPlot'),
        Frame(z_y + 0.466 * z_height,
              z_x,
              0.266 * z_height,
              0.6 * z_width,
              id='TargetPlot'),
        Frame(z_y + 0.733 * z_height,
              z_x,
              0.266 * z_height,
              0.6 * z_width,
              id='VehiclePlot'),
    ]

    comparing_frames = [
        Frame(ext_y, x + 0.9 * width, ext_height, 0.1 * width, id='Title', showBoundary=_showBoundary),
        Frame(ext_y, x + 0.8 * width, 0.6 * ext_height, 0.1 * width, id='Duartion', showBoundary=_showBoundary),
        Frame(ext_y, x + 0.5 * width, 0.2 * ext_height, 0.3 * width, id='VideoNav', showBoundary=_showBoundary),
        Frame(ext_y, x, 0.2 * ext_height, 0.5 * width, id='TrackNav', showBoundary=_showBoundary),
        Frame(ext_y + 0.2 * ext_height, x, 0.4 * ext_height, 0.8 * width, id='EgoPlot', showBoundary=_showBoundary),
        Frame(ext_y + 0.6 * ext_height, x, 0.4 * ext_height, 0.9 * width, id='TargetPlot', showBoundary=_showBoundary),
        Frame(ext_y + 1.0 * ext_height, x, 0.4 * ext_height, 0.9 * width, id='VehiclePlot', showBoundary=_showBoundary),
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

class CorruptMeasSummary(Summary):
    def init(self, batch, view_name):
        data = CORRUPT_MEAS_TABLE
        self.title = "Measurement summary"
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                meas_name=row['measurement']
            ))

        return

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'Measurement Name')
        data = [header]
        for meas, resets in self.iteritems():
            for reset in resets:
                row = [reset['meas_name']]
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
