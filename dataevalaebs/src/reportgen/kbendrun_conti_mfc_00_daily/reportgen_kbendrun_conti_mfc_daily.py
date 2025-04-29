# -*- dataeval: init -*-
import logging
import os

import matplotlib
import copy

import numpy as np

from reportgen.kbendrun_conti_00_daily.reportgen_kbendrun_conti_daily import RESET_TABLE
from sqlalchemy import true
import collections
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

dtcMappingFile_path = os.path.join(os.path.dirname(__file__),"config", "dtc_mapping.txt")

DETECTED_OBJS_TABLE = None
RESET_TABLE = None
DTC_TABLE = None
dtcMappningDict = {}
ACAL_YAW_STAT_TABLE = None
RADAR_RESET_TABLE = None
AEBS_TABLE = None
LANCE_CHANGE_TABLE = None
LANE_QUALITY_CHECK = None
LANE_C0_JUMP_CHECK = None
LDWS_TABLE = None
COMPARE_C0_TABLE = None
CONSTRUCTION_SITE_DATA = None
OBJ_JUMP_TABLE = None
SWITCHOVER_TABLE = None
LANE_BLOCKAGE_STATUS = None
CEM_STATES_TABLE = None
ESIGN_STATES_TABLE = None
ACTL_STATES_TABLE = None
ACCOBJ_TABLE = None
DISABLE_BLOCKAGE_TABLE = True
DROP_WORST_CASE = None
SENSOR_STATES_TABLE = None
CORRUPT_MEAS_TABLE = None


class AebsAnalyze(Analyze):
    optdep = dict(
        aebs_events='analyze_events_merged_FLR25-last_entries@aebseval',
        dtc_events = 'analyze_flc25_dtc_active_events-last_entries@mfc525eval.faults',
        lane_quality_check="analyze_flc25_lane_quality_check-last_entries@mfc525eval.laneeval",
        lane_quality_worst_drop="analyze_flc25_lane_quality_drop_worst-last_entries@mfc525eval.laneeval",
        lane_blockage_status="analyze_flc25_lane_blockage_detection-last_entries@mfc525eval.laneeval",
        sensor_states="analyze_flc25_sensor_states-last_entries@mfc525eval.laneeval",
        cem_status="analyze_flc25_cem_states_detection-last_entries@mfc525eval.laneeval",
        actl_status="analyze_actl_events-last_entries@mfc525eval.laneeval",
        eSign_Status="analyze_flc25_eSignStatus-last_entries@mfc525eval.laneeval",
        lane_c0_jump="analyze_flc25_lane_c0_jump-last_entries@mfc525eval.laneeval",
        ldws_events="analyze_flc25_ldws_events-last_entries@mfc525eval.laneeval",
        compare_c0_flc25vsmfc525="analyze_flc25_compare_c0-last_entries@mfc525eval.laneeval",
        construction_site_event="analyze_flc25_construction_site_event-last_entries@mfc525eval.laneeval",
        corrupt_meas_event="analyze_events_to_find_corrupt_meas-last_entries@aebseval",
        num_of_used_objects_detected_events='analyze_flc25_num_of_objects_detected-last_entries@mfc525eval.objecteval',
        camera_reset_events='analyze_flc25_camera_reset_events-last_entries@mfc525eval.faults',
        acal_yaw_statistics='analyze_flc25_acal_yaw_statistics-last_entries@mfc525eval.laneeval',
        radar_reset_events='analyze_flr25_radar_reset_events-last_entries@flr25eval.faults',
        lane_change_events='analyze_flc25_object_lane_change-last_entries@mfc525eval.objecteval',
        dx_obj_jump_events='analyze_flc25_obj_jumps_in_distance_x-last_entries@mfc525eval.objecteval',
        switchover_events='analyze_flc25_object_track_switchovers-last_entries@mfc525eval.objecteval',
        accobjtracking_events='analyze_flc25_acc_unstable_obj_tracking-last_entries@mfc525eval.objecteval',
        count_vs_aebs_severity='view_count_vs_severity_stats_flr25-print_mergedcount@aebseval.classif',
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
        'aebs_events': abspath('../../aebseval/events_inttable.sql'),
        'dtc_events': abspath('../../mfc525eval/faults/flc25_active_dtc_inittable.sql'),
        'lane_c0_jump': abspath('../../mfc525eval/laneeval/flc25_LD_eval_inttable.sql'),
        'lane_blockage_status': abspath('../../mfc525eval/laneeval/flc25_LD_eval_inttable.sql'),
        'cem_status': abspath("../../mfc525eval/laneeval/flc25_CEM_State_inttable.sql"),
        'actl_status': abspath("../../mfc525eval/laneeval/ACTL_event_inittable.sql"),
        'eSign_Status': abspath("../../mfc525eval/laneeval/flc25_eSignStatus_inttable.sql"),
        'sensor_states': abspath('../../mfc525eval/laneeval/flc25_sensor_states_inttable.sql'),
        'ldws_events': abspath('../../mfc525eval/laneeval/flc25_LD_eval_inttable.sql'),
        'compare_c0_flc25vsmfc525': abspath('../../mfc525eval/laneeval/flc25_LD_eval_inttable.sql'),
        'lane_quality_check': abspath('../../mfc525eval/laneeval/flc25_LD_eval_inttable.sql'),
        'lane_quality_worst_drop': abspath('../../mfc525eval/laneeval/flc25_LD_eval_inttable.sql'),
        'lane_change_events': abspath('../../mfc525eval/objecteval/flc25_object_lane_change_inittable.sql'),
        'dx_obj_jump_events': abspath('../../mfc525eval/objecteval/flc25_obj_jumps_in_distance_x_inittable.sql'),
        'switchover_events': abspath('../../mfc525eval/objecteval/flc25_object_track_switchovers_inittable.sql'),
        'accobjtracking_events': abspath(
            '../../mfc525eval/objecteval/flc25_acc_unstable_object_tracking_inittable.sql'),
        'camera_reset_events': abspath('../../mfc525eval/faults/flc25_camera_reset_inittable.sql'),
        'acal_yaw_statistics': abspath('../../mfc525eval/laneeval/flc25_acal_yaw_statistics_inittable.sql'),
        'radar_reset_events': abspath('../../flr25eval/faults/flr25_radar_reset_inittable.sql'),
        'num_of_used_objects_detected_events': abspath('../../mfc525eval/objecteval/flc25_num_of_detected_objs_inittable.sql'),
        'construction_site_event': abspath('../../mfc525eval/laneeval/flc25_construction_site_inttable.sql'),
        'corrupt_meas_event': abspath('../../aebseval/events_inttable_to_get_corrupt_meas.sql'),
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
        acal_yaw_stat = [ACAlYawStat(self.batch, self.view_name)]
        story.extend(self.flr25_acal_yaw_stat(acal_yaw_stat))
        story.extend(self.explanation())
        summaries = [LQSummary(self.batch, self.view_name), LJSummary(self.batch, self.view_name),
                     LBSummary(self.batch, self.view_name),
                     LDSummary(self.batch, self.view_name), CompareC0FLCvsMFC525Summary(self.batch, self.view_name),
                     LQWSummary(self.batch, self.view_name),
                     CEMSummary(self.batch, self.view_name), ESIGNSummary(self.batch, self.view_name),
                     SENSORSummary(self.batch, self.view_name), ACTLSummary(self.batch, self.view_name),
					 ConstructionSiteSummary(self.batch, self.view_name)
                     ]
        story.extend(self.summaries(summaries))
        story.extend(self.warnings(summaries))

        fault_summaries = [CameraResetTimeline(self.batch, self.view_name)]
        flr25_fault = [RadarResetTimeline(self.batch, self.view_name)]
        flc25_dtc_summary = [DTCSummary(self.batch, self.view_name)]
        flc25_corrupt_meas_summary = [CorruptMeasSummary(self.batch, self.view_name)]

        story.extend(self.faults(fault_summaries))
        story.extend(self.flr25_faults(flr25_fault))
        story.extend(self.flc25_dtc_summary(flc25_dtc_summary))
        story.extend(self.flc25_corrupt_meas_summary(flc25_corrupt_meas_summary))
        return story

    def cal_acal_stat(self, table):
        # Stat calculation per meas in a day
        # Day=yaw_table_internal[0]['measurement'].split("_")[-2]
        yaw_stat_per_meas = {}
        if len(table) == 0:
            return {'Stat':{},'Summarization':{}}
        print("Meas wise table:")
        for val in table:
            print (val)
            Day = val['fullmeas'].split("\\")[-2]
            if not yaw_stat_per_meas.has_key(Day):
                yaw_stat_per_meas[Day] = {'Count': [], 'Sum': [], 'Mean': [], 'Std': [], 'Min': [], 'Max': [],'Violation':[],'comment':val['comment']}
            yaw_stat_per_meas[Day]['Count'].append(val['Count'])
            yaw_stat_per_meas[Day]['Sum'].append(val['Mean']*val['Count'])
            yaw_stat_per_meas[Day]['Mean'].append(val['Mean'])
            yaw_stat_per_meas[Day]['Std'].append(val['Std'] * val['Count'])   # Std * count -------for one meas-----will make list of this cal
            yaw_stat_per_meas[Day]['Min'].append(val['Min'])
            yaw_stat_per_meas[Day]['Max'].append(val['Max'])
            yaw_stat_per_meas[Day]['Violation'].append(val['Violation'])

        # Stat calculation per day
        yaw_stat_per_day = {}
        yaw_stat_compaign = {'Count': [], 'Sum': [], 'Mean': [], 'Std': [], 'Min': [], 'Max': [],'Violation':[]}

        for day_val,sample in zip(yaw_stat_per_meas.keys(),yaw_stat_per_meas.values()):

            yaw_stat_per_day[day_val] = {'Count': [], 'Sum': [], 'Mean': [], 'Std': [], 'Min': [], 'Max': [],'Violation':[],'comment':sample['comment']}

            yaw_stat_per_day[day_val]['Count'] = int(np.sum(sample['Count']))
            yaw_stat_compaign['Count'].append(yaw_stat_per_day[day_val]['Count'])

            yaw_stat_per_day[day_val]['Sum'] = np.sum(sample['Sum'])
            yaw_stat_compaign['Sum'].append(yaw_stat_per_day[day_val]['Sum'])

            yaw_stat_per_day[day_val]['Mean'] = (yaw_stat_per_day[day_val]['Sum'] / yaw_stat_per_day[day_val]['Count'])
            yaw_stat_compaign['Mean'].append(yaw_stat_per_day[day_val]['Mean'])

            yaw_stat_per_day[day_val]['Std'] = np.sum(sample['Std']) / yaw_stat_per_day[day_val]['Count']
            yaw_stat_compaign['Std'].append(yaw_stat_per_day[day_val]['Std'] * yaw_stat_per_day[day_val]['Count'])

            yaw_stat_per_day[day_val]['Min'] = np.min(sample['Min'])
            yaw_stat_compaign['Min'].append(yaw_stat_per_day[day_val]['Min'])

            yaw_stat_per_day[day_val]['Max'] = np.max(sample['Max'])
            yaw_stat_compaign['Max'].append(yaw_stat_per_day[day_val]['Max'])

            yaw_stat_per_day[day_val]['Violation'] = np.sum(sample['Violation'])
            yaw_stat_compaign['Violation'].append(yaw_stat_per_day[day_val]['Violation'])

            yaw_stat_per_day[day_val]['Diff'] = yaw_stat_per_day[day_val]['Max']-yaw_stat_per_day[day_val]['Min']

            yaw_stat_compaign['comment']=yaw_stat_per_day[day_val]['comment']

        print(yaw_stat_compaign)
        # Stat calculation per Measurement campaigns
        total_cnt = int(np.sum(yaw_stat_compaign['Count']))
        mean = np.around((np.sum(yaw_stat_compaign['Sum']) / total_cnt)*57.3248,3)
        std = np.around((np.sum(yaw_stat_compaign['Std'])/ total_cnt)*57.3248,3)
        min_val = np.around(np.min(yaw_stat_compaign['Min'])*57.3248,3)
        max_val = np.around(np.max(yaw_stat_compaign['Max'])*57.3248,3)
        violation = np.around(np.sum(yaw_stat_compaign['Violation']))
        diff=max_val-min_val

        #COnverting Radian value into degree formula is rad val * 180/pi
        yaw_stat = {'Count': total_cnt, 'Mean': mean, 'Std': std, 'Min': min_val, 'Max': max_val,'Violation':violation,'Diff': diff,'Comment':yaw_stat_compaign['comment']}
        stat_table={}

        stat_table['Stat']=collections.OrderedDict(sorted(yaw_stat_per_day.items()))
        stat_table['Summarization']=yaw_stat
        print("Stat:",stat_table['Stat'])
        print("Summary:", stat_table['Summarization'])

        # logging.Logger.info('Day Stat: ',stat_table['Stat'])
        # logging.Logger.info('Summary Stat: ', stat_table['Summarization'])

        return stat_table
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

            # Radar Reset event table
            if (self.optdep['radar_reset_events'] in self.passed_optdep):
                reset_ei_ids = index_fill(self.modules.fill(self.optdep['radar_reset_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['radar_reset_events'])
                radar_table_internal = self.batch.get_table_dict(header1, reset_ei_ids,
                                                                 sortby=[('measurement', True),
                                                                         ('start [s]', True)])
                global RADAR_RESET_TABLE
                RADAR_RESET_TABLE = radar_table_internal

            # Camera Reset event table
            if (self.optdep['camera_reset_events'] in self.passed_optdep):
                reset_ei_ids = index_fill(self.modules.fill(self.optdep['camera_reset_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['camera_reset_events'])
                camera_table_internal = self.batch.get_table_dict(header1, reset_ei_ids,
                                                                  sortby=[('measurement', True), ('start [s]', True)])
                global RESET_TABLE
                RESET_TABLE = camera_table_internal

            if (self.optdep['num_of_used_objects_detected_events'] in self.passed_optdep):
                num_of_obj_ei_ids = index_fill(self.modules.fill(self.optdep['num_of_used_objects_detected_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['num_of_used_objects_detected_events'])
                detected_objects_table_internal = self.batch.get_table_dict(header1, num_of_obj_ei_ids,
                                                                            sortby=[('measurement', True),
                                                                                    ('start [s]', True)])
                global DETECTED_OBJS_TABLE
                DETECTED_OBJS_TABLE = detected_objects_table_internal

            # lane change table
            if self.optdep['lane_change_events'] in self.passed_optdep:
                lane_change_ei_ids = index_fill(self.modules.fill(self.optdep['lane_change_events']))
                header = cIntervalHeader.fromFileName(self.query_files['lane_change_events'])
                table = self.batch.get_table_dict(header, lane_change_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global LANCE_CHANGE_TABLE
                LANCE_CHANGE_TABLE = table
                story += [Paragraph('Total number of lane change events: %d' % len(table))]

            if self.optdep['lane_quality_check'] in self.passed_optdep:
                lane_quality_ei_ids = index_fill(self.modules.fill(self.optdep['lane_quality_check']))
                header = cIntervalHeader.fromFileName(self.query_files['lane_quality_check'])
                table = self.batch.get_table_dict(header, lane_quality_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global LANE_QUALITY_CHECK
                LANE_QUALITY_CHECK = table
                story += [Paragraph('Total number of lane quality drop events: %d' % len(table))]

            if self.optdep['lane_quality_worst_drop'] in self.passed_optdep:
                lane_quality_ei_ids = index_fill(self.modules.fill(self.optdep['lane_quality_worst_drop']))
                header = cIntervalHeader.fromFileName(self.query_files['lane_quality_worst_drop'])
                table = self.batch.get_table_dict(header, lane_quality_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global DROP_WORST_CASE
                DROP_WORST_CASE = table
                story += [Paragraph('Total number of lane worst quality drop events: %d' % len(table))]

            if self.optdep['lane_blockage_status'] in self.passed_optdep:
                lane_blockage_ei_ids = index_fill(self.modules.fill(self.optdep['lane_blockage_status']))
                header = cIntervalHeader.fromFileName(self.query_files['lane_blockage_status'])
                table = self.batch.get_table_dict(header, lane_blockage_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                event_count = 0
                global LANE_BLOCKAGE_STATUS
                global DISABLE_BLOCKAGE_TABLE
                LANE_BLOCKAGE_STATUS = table
                for i in range(len(table)):
                    if table[i]['FLC25 Blockage state'][0] == u'CB_NO_BLOCKAGE':
                        continue
                    else:
                        DISABLE_BLOCKAGE_TABLE = False
                        event_count = event_count + 1
                if DISABLE_BLOCKAGE_TABLE:
                    story += [Paragraph('Total blockage states : 0')]
                else:
                    story += [Paragraph('Total blockage states : %d' % event_count)]

            if self.optdep['cem_status'] in self.passed_optdep:
                cem_state_ei_ids = index_fill(self.modules.fill(self.optdep['cem_status']))
                header = cIntervalHeader.fromFileName(self.query_files['cem_status'])
                table = self.batch.get_table_dict(header, cem_state_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                event_count = 0
                global CEM_STATES_TABLE
                CEM_STATES_TABLE = table

                story += [Paragraph('Total CEM states : %d' % len(table))]
            # ACAL YAW STAT table
            if (self.optdep['acal_yaw_statistics'] in self.passed_optdep):
                yaw_ei_ids = index_fill(self.modules.fill(self.optdep['acal_yaw_statistics']))
                header1 = cIntervalHeader.fromFileName(self.query_files['acal_yaw_statistics'])
                yaw_table_internal = self.batch.get_table_dict(header1, yaw_ei_ids,
                                                               sortby=[('measurement', True), ('start [s]', True)])
                global ACAL_YAW_STAT_TABLE
                # ACAL_YAW_STAT_TABLE = yaw_table_internal
                ACAL_YAW_STAT_TABLE= self.cal_acal_stat(yaw_table_internal)

            if self.optdep['eSign_Status'] in self.passed_optdep:
                esign_state_ei_ids = index_fill(self.modules.fill(self.optdep['eSign_Status']))
                header = cIntervalHeader.fromFileName(self.query_files['eSign_Status'])
                table = self.batch.get_table_dict(header, esign_state_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])

                global ESIGN_STATES_TABLE
                ESIGN_STATES_TABLE = table
                tpf_cnt = 0
                ld_cnt = 0
                for id, value in enumerate(ESIGN_STATES_TABLE):
                    if value['FLC25 eSign Status'][0] == u'TPF AL_SIG_STATE_INIT' or value['FLC25 eSign Status'][
                        0] == u'TPF AL_SIG_STATE_INVALID':
                        ESIGN_STATES_TABLE[id]['eSignHeader Source'] = 'TPF'
                        tpf_cnt += 1
                    elif value['FLC25 eSign Status'][0] == u'LD AL_SIG_STATE_INIT' or value['FLC25 eSign Status'][
                        0] == u'LD AL_SIG_STATE_INVALID':
                        ESIGN_STATES_TABLE[id]['eSignHeader Source'] = 'LD'
                        ld_cnt += 1

                story += [
                    Paragraph("Total eSignStatus : {} ( TPF : {} , LD : {} ) ".format(len(table), tpf_cnt, ld_cnt))]

            if self.optdep['actl_status'] in self.passed_optdep:
                cem_state_ei_ids = index_fill(self.modules.fill(self.optdep['actl_status']))
                header = cIntervalHeader.fromFileName(self.query_files['actl_status'])
                table = self.batch.get_table_dict(header, cem_state_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                event_count = 0
                global ACTL_STATES_TABLE
                ACTL_STATES_TABLE = table

                story += [Paragraph('Total ACTL states : %d' % len(table))]

            if self.optdep['sensor_states'] in self.passed_optdep:
                sensor_state_ei_ids = index_fill(self.modules.fill(self.optdep['sensor_states']))
                header = cIntervalHeader.fromFileName(self.query_files['sensor_states'])
                table = self.batch.get_table_dict(header, sensor_state_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                event_count = 0
                global SENSOR_STATES_TABLE
                SENSOR_STATES_TABLE = table

                story += [Paragraph('Total Sensor degraded states : %d' % len(table))]
                # Sensor remark
                story += [
                    Paragraph(italic('Remark: Only Radar degradation events  > 60ms are considered (See DI6662789)'),
                              fontsize=8),
                    Spacer(width=1 * cm, height=0.2 * cm), ]

            if self.optdep['compare_c0_flc25vsmfc525'] in self.passed_optdep:
                compare_c0_ei_ids = index_fill(self.modules.fill(self.optdep['compare_c0_flc25vsmfc525']))
                header = cIntervalHeader.fromFileName(self.query_files['compare_c0_flc25vsmfc525'])
                table = self.batch.get_table_dict(header, compare_c0_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global COMPARE_C0_TABLE
                COMPARE_C0_TABLE = table
                story += [Paragraph('Total compare_c0_flc25vsmfc525 : %d' % len(table))]

            if self.optdep['construction_site_event'] in self.passed_optdep:
                construction_site_ei_ids = index_fill(self.modules.fill(self.optdep['construction_site_event']))
                header = cIntervalHeader.fromFileName(self.query_files['construction_site_event'])
                table = self.batch.get_table_dict(header, construction_site_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global CONSTRUCTION_SITE_DATA
                CONSTRUCTION_SITE_DATA = table
                story += [Paragraph('Total Construction Site Events : %d' % len(table))]

            if self.optdep['ldws_events'] in self.passed_optdep:
                ldws_events_ei_ids = index_fill(self.modules.fill(self.optdep['ldws_events']))
                header = cIntervalHeader.fromFileName(self.query_files['ldws_events'])
                table = self.batch.get_table_dict(header, ldws_events_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global LDWS_TABLE
                LDWS_TABLE = table
                story += [Paragraph('Total ldws_events : %d' % len(table))]

            if self.optdep['lane_c0_jump'] in self.passed_optdep:
                lane_quality_ei_ids = index_fill(self.modules.fill(self.optdep['lane_c0_jump']))
                header = cIntervalHeader.fromFileName(self.query_files['lane_c0_jump'])
                table = self.batch.get_table_dict(header, lane_quality_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global LANE_C0_JUMP_CHECK
                LANE_C0_JUMP_CHECK = table
                story += [Paragraph('Total number of lane c0 jump (Tare Stripe) events: %d' % len(table))]

            # obj jump table
            if self.optdep['dx_obj_jump_events'] in self.passed_optdep:
                obj_jump_ei_ids = index_fill(self.modules.fill(self.optdep['dx_obj_jump_events']))
                header = cIntervalHeader.fromFileName(self.query_files['dx_obj_jump_events'])
                table = self.batch.get_table_dict(header, obj_jump_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global OBJ_JUMP_TABLE
                OBJ_JUMP_TABLE = table
                story += [Paragraph('Total number of obj jump events: %d' % len(table))]

            # switchover table
            if self.optdep['switchover_events'] in self.passed_optdep:
                switchover_ei_ids = index_fill(self.modules.fill(self.optdep['switchover_events']))
                header = cIntervalHeader.fromFileName(self.query_files['switchover_events'])
                table = self.batch.get_table_dict(header, switchover_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global SWITCHOVER_TABLE
                SWITCHOVER_TABLE = table
                story += [Paragraph('Total number of switchover events: %d' % len(table))]

            # accobjtracking table
            if self.optdep['accobjtracking_events'] in self.passed_optdep:
                accobjtrack_ei_ids = index_fill(self.modules.fill(self.optdep['accobjtracking_events']))
                header = cIntervalHeader.fromFileName(self.query_files['accobjtracking_events'])
                table = self.batch.get_table_dict(header, accobjtrack_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global ACCOBJ_TABLE
                ACCOBJ_TABLE = table
                story += [Paragraph('Total number of stable acc object tracking events: %d' % len(table))]

            # AEBS warning rate
            if (self.optdep['aebs_events'] in self.passed_optdep and
                    self.optdep['count_vs_aebs_severity'] in self.passed_optdep):
                aebs_ei_ids = index_fill(self.modules.fill(self.optdep['aebs_events']))
                header = cIntervalHeader.fromFileName(self.query_files['aebs_events'])
                table = self.batch.get_table_dict(header, aebs_ei_ids,
                                                  sortby=[('measurement', True), ('start [s]', True)])
                global AEBS_TABLE
                AEBS_TABLE = table

                aebs_count = index_fill(self.modules.fill(self.optdep['count_vs_aebs_severity']))

                tot_aebs = len(table)
                story += [Paragraph('Total number of AEBS events: %d' % tot_aebs)]
                if 'roadt_dist' in locals() and roadt_dist.total > 0.0:
                    tot_rate = float(tot_aebs) / roadt_dist.total * 1000.0
                    false_rate = float(aebs_count['1-False alarm']) / roadt_dist.total * 1000.0
                    ques_rate = float(aebs_count['2-Questionable false alarm']) / roadt_dist.total * 1000.0
                    story += [Paragraph('AEBS warning rate - overall: <b>%.1f events / 1000 km</b>' % tot_rate),
                              Paragraph('AEBS warning rate - 1-False alarm: <b>%.1f events / 1000 km</b>' % false_rate),
                              Paragraph(
                                  'AEBS warning rate - 2-Questionable false alarm: <b>%.1f events / 1000 km</b>' % ques_rate),
                              Spacer(width=1 * cm, height=0.2 * cm), ]
                else:
                    story += [Paragraph('AEBS warning rate: n/a'),
                              Spacer(width=1 * cm, height=0.2 * cm), ]
            else:
                story += [Paragraph('Total number of AEBS events: n/a'),
                          Paragraph('AEBS warning rate: n/a'),
                          Spacer(width=1 * cm, height=0.2 * cm), ]

                # DTC event table
            if (self.optdep['dtc_events'] in self.passed_optdep):
                dtc_ei_ids = index_fill(self.modules.fill(self.optdep['dtc_events']))
                header1 = cIntervalHeader.fromFileName(self.query_files['dtc_events'])
                dtc_table_internal = self.batch.get_table_dict(header1, dtc_ei_ids,
                                                               sortby=[('measurement', True), ('start [s]', True)])
                global DTC_TABLE,dtcMappningDict
                DTC_TABLE = dtc_table_internal

                story += [Paragraph('DTC Overview Table:')]

                dtc_dictionary = {}

                dtc_list_in_hex = [hex(int(dtc_list['DTC in DEC'])) for dtc_list in dtc_table_internal]

                previoud_dtc_id = ""
                refined_dtc_list = []

                for key in dtc_list_in_hex:
                    if key != previoud_dtc_id:
                        if len(key)<8:
                            key = (key).replace('x', 'x0')
                        refined_dtc_list.append(key)
                        previoud_dtc_id = key

                dtc_dictionary = {key: refined_dtc_list.count(key) for key in refined_dtc_list}

                story.append(Table([('DTCs', 'No of Events')], colWidths=4 * cm,style=grid_table_style,vAlign='MIDDLE'))

                for dtc_name, dtc_value in dtc_dictionary.iteritems():
                    story.append(Table([(dtc_name, '%d' % (dtc_value))], colWidths=4 * cm,style=grid_table_style,vAlign='MIDDLE'))

                dtcMappingFile = open(dtcMappingFile_path, 'r')

                for line in dtcMappingFile:
                    dtc_id, dtc_name = line.strip().split('=')
                    dtcMappningDict[dtc_id.strip().lower()] = dtc_name.strip()

            if (self.optdep['corrupt_meas_event'] in self.passed_optdep):
                corrupt_meas_ei_ids = index_fill(self.modules.fill(self.optdep['corrupt_meas_event']))
                header1 = cIntervalHeader.fromFileName(self.query_files['corrupt_meas_event'])
                corrupt_meas_table = self.batch.get_table_dict(header1, corrupt_meas_ei_ids,
                                                               sortby=[('measurement', True), ('start [s]', True)])
                global CORRUPT_MEAS_TABLE
                CORRUPT_MEAS_TABLE = corrupt_meas_table

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

    def faults(self, summaries, module_name=None):
        story = [
            IndexedParagraph('FLC25 faults', style='Heading1'),
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

    def flr25_faults(self, summaries, module_name=None):
        story = [
            IndexedParagraph('FLR25 faults', style='Heading1'),
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

    def flr25_acal_yaw_stat(self, summaries, module_name=None):
        story = [
            IndexedParagraph('ACAL YAW Statistics', style='Heading1'),
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
            for warning in warnings:
                if type(summary) in [ODSummary, OJSummary]:
                    modules_in_event.update(
                        {'view_lane_change_data_FLC25-TRACK_%03d@mfc525eval.objecteval' % int(warning['objectid']):
                             Client('FLC25 internal track', '640x700+0+0', 11, 12, cm)})
                elif type(summary) in [SWSummary]:
                    modules_in_event.update(
                        {'view_lane_change_data_FLC25-TRACK_%03d@mfc525eval.objecteval' % int(warning['initialid']):
                             Client('FLC25 internal track', '640x700+0+0', 11, 12, cm)})
                    modules_in_event.update(
                        {'view_lane_change_data_FLC25-TRACK_%03d@mfc525eval.objecteval' % int(warning['changedid']):
                             Client('FLC25 internal track', '640x700+0+0', 11, 12, cm)})
                else:
                    break
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
                if type(summary) in [ODSummary, OJSummary]:
                    modules_in_warnings.update(
                        {'view_lane_change_data_FLC25-TRACK_%03d@mfc525eval.objecteval' % int(warning['objectid']):
                             Client('FLC25 internal track', '640x700+0+0', 11, 12, cm)})
                elif type(summary) in [SWSummary]:
                    modules_in_warnings.update(
                        {'view_lane_change_data_FLC25-TRACK_%03d@mfc525eval.objecteval' % int(warning['initialid']):
                             Client('FLC25 internal track', '640x700+0+0', 11, 12, cm)})
                    modules_in_warnings.update(
                        {'view_lane_change_data_FLC25-TRACK_%03d@mfc525eval.objecteval' % int(warning['changedid']):
                             Client('FLC25 internal track', '640x700+0+0', 11, 12, cm)})
                for module_name, client in modules_in_warnings.iteritems():
                    story.append(client(sync, module_name))
                    story.append(FrameBreak())
                if summary.modules: story.pop(-1)  # remove last FrameBreak
            manager.close()
        return story


class AebsSummary(EventSummary):
    def init(self, batch, view_name):
        data = AEBS_TABLE

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
            ('view_nxtvideoeventgrabbernav_lanes-FLC25_LD_LANE@evaltools',
             VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
            ('view_tracknav_lanes-FLC25_LD_LANE@evaltools',
             TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
        ])

        self.columns.update([
            ('start', 'start\n[s]\n'),
            ('duration', 'duration\n[s]\n'),
            ('phase', 'aebs phase\n\n'),
            ('moving', 'moving\nstate\n'),
            ('asso', 'asso\nstate\n'),
            ('speed', 'ego speed\n[kmph]\n'),
        ])
        return


class LaneChangeSummary(EventSummary):
    def init(self, batch, view_name):
        data = LANCE_CHANGE_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                objectid=row['Object Info(current_id)'],
                from_lane=row['Object lane Changed From(previous_lane)'],
                to_lane=row['Object lane Changed to(current_lane)'],
                distance=row['Object Distance X']
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
            ('objectid', 'object id'),
            ('from_lane', 'lane changed\nfrom'),
            ('to_lane', 'lane changed\nto'),
            ('distance', 'dx\n[m]\n')
        ])
        return


class LaneQualitySummary(EventSummary):
    def init(self, batch, view_name):
        data = LANE_QUALITY_CHECK

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                speed=row['ego speed [km/h]'],
                event=vector2scalar(row['FLC25 event']),
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
            ('event', 'lane quality\n'),
            # ('speed', 'ego speed\n[kmph]\n'),
        ])
        return


class LaneQualityWorstSummary(EventSummary):
    def init(self, batch, view_name):
        data = DROP_WORST_CASE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                speed=row['ego speed [km/h]'],
                event=vector2scalar(row['FLC25 event']),
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
            ('event', 'lane quality\ndrop\n'),
        ])
        return


class CEMStatusSummary(EventSummary):
    def init(self, batch, view_name):
        data = CEM_STATES_TABLE
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['FLC25 CEM state']),
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
            ('event', 'CEM state\n'),
        ])
        return


class ESIGNStatusSummary(EventSummary):
    def init(self, batch, view_name):
        data = ESIGN_STATES_TABLE
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                Source=row['eSignHeader Source'],
                event=vector2scalar(row['FLC25 eSign Status']),
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
            ('Source', 'eSignHeader Source\n'),
            ('event', 'eSign status\n'),
        ])
        return


class ACTLStatusSummary(EventSummary):
    def init(self, batch, view_name):
        data = ACTL_STATES_TABLE
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['ACTL event']),
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
            ('event', 'ACTL state\n'),
        ])
        return


class SensorStatesSummary(EventSummary):
    def init(self, batch, view_name):
        data = SENSOR_STATES_TABLE
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['FLC25 Sensor state']),
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
            ('event', 'Sensor state\n'),
        ])
        return


class LaneBlockageSummary(EventSummary):
    def init(self, batch, view_name):
        if not DISABLE_BLOCKAGE_TABLE:
            data = LANE_BLOCKAGE_STATUS
            for row in data:
                if vector2scalar(row['FLC25 Blockage state']) != 'CB_NO_BLOCKAGE':
                    self.setdefault(row['fullmeas'], []).append(dict(
                        start=row['start [s]'],
                        end=row['start [s]'] + row['duration [s]'],
                        duration=row['duration [s]'],
                        event=vector2scalar(row['FLC25 Blockage state']),
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
                ('event', 'blockage state\n'),
            ])
            return


class LdwsSummary(EventSummary):
    def init(self, batch, view_name):
        data = LDWS_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['FLC25 event']),
                status=vector2scalar(row['LDWS system status']),
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
            ('event', 'ldws event\n'),
            # ('status', 'ldws\nsystem\nstatus'),
        ])
        return


class CompareC0FLCvsMFC525(EventSummary):
    def init(self, batch, view_name):
        data = COMPARE_C0_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['FLC25 event']),
                status=vector2scalar(row['LDWS system status']),
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
            ('event', 'ldws event\n'),
        ])
        return


class ConstructionSiteEvent(EventSummary):

    def init(self, batch, view_name):
        data = CONSTRUCTION_SITE_DATA

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                speed=row['frontAxleSpeed [km/h]'],
                event=vector2scalar(row['ConstructionSiteAvailable']),
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
            ('speed', 'frontAxleSpeed [km/h]'),
            ('event', 'constructionSiteEvent\n'),
        ])
        return


class LaneC0JumpSummary(EventSummary):
    def init(self, batch, view_name):
        data = LANE_C0_JUMP_CHECK

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                event=vector2scalar(row['FLC25 event']),
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
            ('event', 'c0 jump events\n'),
        ])
        return


class ObjJumpSummary(EventSummary):
    def init(self, batch, view_name):
        data = OBJ_JUMP_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                objectid=row['Object ID'],
                delta_distx=row['Delta DistanceX'],
                distancex=row['Object DistanceX'],
                delta_disty=row['Delta DistanceY'],
                distancey=row['Object DistanceY']
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
            ('objectid', 'object id'),
            ('delta_distx', 'delta\njump distx'),
            ('distancex', 'dx\n[m]'),
            ('delta_disty', 'delta\njump disty'),
            ('distancey', 'dy\n[m]')
        ])
        return


class SwitchOverSummary(EventSummary):
    def init(self, batch, view_name):
        data = SWITCHOVER_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                initialid=row['SwitchOver From'][0],
                changedid=row['SwitchOver To'][0]
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
            ('initialid', 'SwitchOver\nfrom\n'),
            ('changedid', 'SwitchOver\nto\n'),
        ])
        return


class ACCObjSummary(EventSummary):
    def init(self, batch, view_name):
        data = ACCOBJ_TABLE

        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                end=row['start [s]'] + row['duration [s]'],
                duration=row['duration [s]'],
                objectid=row['Object ID']
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
            ('objectid', 'Changed\nObject ID\n'),
        ])
        return


class CameraResetTimeline(Summary):
    def init(self, batch, view_name):
        data = RESET_TABLE
        self.title = 'Camera Reset event details'
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                reset_reason=row['ResetReason'],
                reset_cntr=row['ResetCounter'],
                comment=row['comment']
            ))

        self.columns.update([
            ('start', 'start [s]\n'),
            ('reset_reason', 'ResetReason\n'),
            ('reset_cntr', 'ResetCounter\n'),
            ('comment', 'Comment\n'),
        ])
        return

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'measurement')
        data = [header]
        for meas, resets in self.iteritems():
            basename = os.path.basename(meas)
            for reset in resets:
                row = [basename, reset['start'], reset['reset_reason'], reset['reset_cntr'], reset['comment']]
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


class RadarResetTimeline(Summary):
    def init(self, batch, view_name):
        data = RADAR_RESET_TABLE
        self.title = 'Radar Reset event details'
        for row in data:
            row['Address'] = hex(int(row['Address']))
            self.setdefault(row['fullmeas'], []).append(dict(
                start=row['start [s]'],
                reset_reason=row['Cat2LastResetReason'],
                address=row['Address'],
                reset_cntr=row['ResetCounter'],
                comment=row['comment']
            ))

        self.columns.update([
            ('start', 'start [s]\n'),
            ('reset_reason', 'Cat2LastResetReason\n'),
            ('address', 'Address\n'),
            ('reset_cntr', 'ResetCounter\n'),
            ('comment', 'Comment\n'),
        ])
        return

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'measurement')
        data = [header]
        for meas, resets in self.iteritems():
            basename = os.path.basename(meas)
            for reset in resets:
                row = [basename, reset['start'], reset['reset_reason'], reset['address'], reset['reset_cntr'],
                       reset['comment']]
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


class NumOfUsedObjects(Summary):
    def init(self, batch, view_name):
        data = DETECTED_OBJS_TABLE
        self.title = 'iNumOfUsedObjects'
        for row in data:
            self.setdefault(row['fullmeas'], []).append(dict(
                numOfUsedObjs=row['NumOfDetectedObjects']
            ))

        self.columns.update([
            ('numOfUsedObjs', 'iNumOfUsedObjects\n'),
        ])
        return

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'measurement')
        data = [header]
        for meas, numOfUsedObjs in self.iteritems():
            basename = os.path.basename(meas)
            for obj in numOfUsedObjs:
                row = [basename, obj]
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


class AOSummary(ACCObjSummary):
    title = "ACC object stable tracking event"
    explanation = """
	ACC object was tracking an object in a stable manner, when it changed obj id <br/>
	and than continued to once again select the original object id, Changed object ID: %s 
	""" \
                  % ('%(objectid)s')
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
        ('view_ego_velocity@mfc525eval.objecteval',
         Client('Ego Velocity', '640x700+0+0', 11, 12, cm)),
        ('view_aoa_acc_obj_data_FLC25@mfc525eval.objecteval',
         Client('Ego Velocity', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class ODSummary(LaneChangeSummary):
    title = "Lane Change event details"
    explanation = """
	Object ID %s - Lane changed from: %s Lane changed to: %s<br/>
	dx distance to object: %s
	""" \
                  % ('%(objectid)s', '%(from_lane)s', '%(to_lane)s', '%(distance)s')
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
        ('view_ego_velocity@mfc525eval.objecteval',
         Client('Ego Velocity', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class OJSummary(ObjJumpSummary):
    title = "ObjJump Events"
    explanation = """
	Object ID %s - Delta distance X: %s dx distance: %s<br/>
				 - Delta distance Y: %s dy distance: %s
	""" \
                  % ('%(objectid)s', '%(delta_distx)s', '%(distancex)s', '%(delta_disty)s', '%(distancey)s')
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
        ('view_ego_velocity@mfc525eval.objecteval',
         Client('Ego Velocity', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class LQSummary(LaneQualitySummary):
    title = "Lane Quality Drop."
    explanation = """Lane Quality: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_lane_quality_check@mfc525eval.laneeval',
         Client('Lane Quality Check', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class LQWSummary(LaneQualityWorstSummary):
    title = "Lane Quality Worst Drop"
    explanation = """Lane Worst Quality Drop: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_lane_quality_check@mfc525eval.laneeval',
         Client('Lane Quality Check', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class CEMSummary(CEMStatusSummary):
    title = "CEM States"
    explanation = """CEM States: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_cem_state@mfc525eval.laneeval',
         Client('CEM States', '640x700+0+0', 11, 12, cm)),
        ('view_actl_state@mfc525eval.laneeval',
         Client('ACTL States', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class ESIGNSummary(ESIGNStatusSummary):
    title = "eSignHeader Status"
    explanation = """eSignHeader Status: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_eSigStatus@mfc525eval.laneeval',
         Client('eSign Status', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class ACTLSummary(ACTLStatusSummary):
    title = "ACTL States"
    explanation = """ACTL States: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_actl_state@mfc525eval.laneeval',
         Client('ACTL States', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class SENSORSummary(SensorStatesSummary):
    title = "Sensor States"
    explanation = """Sensor State: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_sensor_state@mfc525eval.laneeval',
         Client('Sensor States', '640x700+0+0', 11, 12, cm)),
        ('view_actl_state@mfc525eval.laneeval',
         Client('ACTL States', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class LBSummary(LaneBlockageSummary):
    title = "Blockage Status"
    explanation = """Blockage State: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_flc25_camera_blockagestatus@mfc525eval.laneeval',
         Client('Blockage Status', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class LDSummary(LdwsSummary):
    title = "LDWS event status"
    explanation = """LDWS event: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_ldws_events@mfc525eval.laneeval',
         Client('LDWS Events', '640x700+0+0', 11, 12, cm)),
        ('view_ldws_events_c0_plots@mfc525eval.laneeval',
         Client('C0 Plot', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class CompareC0FLCvsMFC525Summary(CompareC0FLCvsMFC525):
    title = "CompareC0FLCvsMFC525 event status"
    explanation = """FLCvsMFC525 Compare C0 event: %s,  Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_compare_left_c0_events@mfc525eval.laneeval',
         Client('Compare Left C0 FLC25vsMFC525', '640x700+0+0', 11, 12, cm)),
        ('view_compare_right_c0_events@mfc525eval.laneeval',
         Client('Compare Right C0 FLC25vsMFC525', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class ConstructionSiteSummary(ConstructionSiteEvent):
    title = "Construction site event status"
    explanation = """Construction site event: %s,  Event Duration: %s""" % ('%(event)s', '%(duration)s')

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
        ('view_flc25_construction_site_event@mfc525eval.laneeval',
         Client('Construction Site Event', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class LJSummary(LaneC0JumpSummary):
    title = "Lane C0 Jump (Tare Stripe)."
    explanation = """Lane c0 jump event: %s, Event Duration: %s""" % ('%(event)s', '%(duration)s')
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
        ('view_lane_c0_jump@mfc525eval.laneeval',
         Client('Lane C0 Jump', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class SWSummary(SwitchOverSummary):
    title = "Object switch over event"
    explanation = """Initial object ID %s - Changed object ID: %s""" % ('%(initialid)s', '%(changedid)s')
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
        ('view_ego_velocity@mfc525eval.objecteval',
         Client('Ego Velocity', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


class Flr25Summary(AebsSummary):
    title = "AEBS event details"
    explanation = """
	AEBS %s - event duration: %s sec, cause: %s, rating: %s<br/>
	Event is triggered because AEBS state was active: warning (%d), partial (%d)
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
        (EventSummary.aeb_im, 'AEB track'),
    ]
    extra_modules = [
        ('view_driveract_aebsout@aebseval',
         Client('DriverAct_AebsOut_Plot', '640x700+0+0', 11, 12, cm)),
        ('view_kinematics_FLC25@aebseval',
         Client('Kinematics_Plot', '640x700+0+0', 11, 12, cm)),
    ]
    statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
    groups = ['FLC25_AOA_AEBS']


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
                        row = [basename, reset['dtc_id'], reset['dtc_id_in_hex'], reset['dtc_counter'], reset['dtc_timestamp'],dtcMappningDict[reset['dtc_id_in_hex']],
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

class ACAlYawStat(Summary):
    def init(self, batch, view_name):
        table = ACAL_YAW_STAT_TABLE
        self.title = "ACAL-Yaw-Statistics"
        stat_data=table['Stat']
        Summay_data = table['Summarization']
        for day,data in zip(stat_data.keys(),stat_data.values()):

            self.setdefault(day, []).append(dict(
                count=data['Count'],
                mean=np.around(data['Mean']*57.3248,3),
                std=np.around(data['Std']*57.3248,3),
                min=np.around(data['Min']*57.3248,3),
                max=np.around(data['Max']*57.3248,3),
                diff=np.around(data['Diff']*57.3248,3),
                Violation=int(data['Violation']),
                comment=data['comment']
            ))
        if len(Summay_data)!=0:
            self.setdefault('Summary', []).append(dict(
                count=Summay_data['Count'],
                mean=Summay_data['Mean'],
                std=Summay_data['Std'],
                min=Summay_data['Min'],
                max=Summay_data['Max'],
                diff=Summay_data['Diff'],
                Violation=int(Summay_data['Violation']),
                comment=Summay_data['Comment']
            ))

        self.columns.update([
            ('count', 'Count\n'),
            ('mean', 'Mean in deg\n'),
            ('std', 'Std in deg\n'),
            ('min', 'Min in deg\n'),
            ('max', 'Max in deg\n'),
            ('diff', 'Delta\n'),
            ('Violation', 'Violations\n'),
            ('comment', 'Comment\n'),
        ])
        return

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'Day')
        data = [header]
        for meas, resets in self.iteritems():
            basename = os.path.basename(meas)
            for reset in resets:
                row = [basename, reset['count'], reset['mean'], reset['std'], reset['min'],reset['max'],reset['diff'],reset['Violation'],
                       reset['comment']]
                data.append(row)
        return data

    def get_style(self):
        style = [
            ('GRID', (0, 0), (-1, -1), 0.009 * cm, colors.black),
            ('FONT', (0, 0), (-1, 0), '%s-Bold' % self.font_name, 5),
            ('FONT', (0, 1), (-1, -1), self.font_name, 5),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ]
        return style


if __name__ == '__main__':
    from reportgen.common.main import main

    main(os.path.abspath(__file__))
