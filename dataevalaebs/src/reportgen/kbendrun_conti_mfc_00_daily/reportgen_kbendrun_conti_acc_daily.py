# -*- dataeval: init -*-

import os

import matplotlib
import copy
matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

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
from reportgen.common.summaries import EventSummary, PIC_DIR
from reportgen.common.clients import Client, TrackNavigator, VideoNavigator
from reportgen.common.utils import vector2scalar
from aebs.fill.calc_radar_aebs_phases import Calc as Flr25Calc

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

LANCE_CHANGE_TABLE = None
OBJ_JUMP_TABLE = None
SWITCHOVER_TABLE = None
ACCOBJ_TABLE = None
FUSDEG_TABLE = None

class AebsAnalyze(Analyze):
	optdep = dict(
		fusion_degradation='analyze_flc25_acc_obj_fusion_degradation-last_entries@mfc525eval.objecteval',
		lane_change_events='analyze_acc_object_lane_change-last_entries@mfc525eval.objecteval',
		dx_obj_jump_events='analyze_acc_obj_jumps_in_distance_x-last_entries@mfc525eval.objecteval',
		switchover_events='analyze_acc_object_track_switchovers-last_entries@mfc525eval.objecteval',
		accobjtracking_events='analyze_flc25_acc_unstable_obj_tracking-last_entries@mfc525eval.objecteval',
		count_vs_aebs_severity='view_count_vs_severity_stats_flr25-print_mergedcount@aebseval.classif',
		smess_faults='analyze_smess_faults-last_entries@flr20eval.faults',
		a087_faults='analyze_a087_faults-last_entries@flr20eval.faults', #TODO merge crash event script
		flc20_spec_statuses='analyze_issues-last_entries@mfc525eval.sensorstatus',
		dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
		dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
		dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
		dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@mfc525eval.daytime', #TODO Get signal for day time
		dur_vs_inlane_tr0='view_quantity_vs_inlane_flr20_tr0_stats-print_duration@trackeval.inlane',
		dur_vs_inlane_tr0_fused='view_quantity_vs_inlane_flr20_tr0_fused_stats-print_duration@trackeval.inlane',
		dist_vs_inlane_tr0='view_quantity_vs_inlane_flr20_tr0_stats-print_mileage@trackeval.inlane',
		dist_vs_inlane_tr0_fused='view_quantity_vs_inlane_flr20_tr0_fused_stats-print_mileage@trackeval.inlane',
	)
	
	query_files = {
		'lane_change_events': abspath('../../mfc525eval/objecteval/flc25_object_lane_change_inittable.sql'),
		'dx_obj_jump_events': abspath('../../mfc525eval/objecteval/flc25_obj_jumps_in_distance_x_inittable.sql'),
		'switchover_events': abspath('../../mfc525eval/objecteval/flc25_object_track_switchovers_inittable.sql'),
		'accobjtracking_events': abspath('../../mfc525eval/objecteval/flc25_acc_unstable_object_tracking_inittable.sql'),
		'fusion_degradation': abspath('../../mfc525eval/objecteval/flc25_obj_fusion_degradation_inittable.sql'),
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
		story.extend(self.aebs_event_classification())
		summaries = [ODSummary(self.batch, self.view_name), OJSummary(self.batch, self.view_name),
		 SWSummary(self.batch, self.view_name), AOSummary(self.batch, self.view_name), FusDegSummary(self.batch, self.view_name)]
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
			# engine running
			if self.optdep['dur_vs_engine_onoff'] in self.passed_optdep:
				engine_dur = index_fill(self.modules.fill(self.optdep['dur_vs_engine_onoff']))
				if 'roadt_dur' in locals():
					# plau check for durations of different sources
					if roadt_dur.total > 0.25 and abs(1.0 - engine_dur.total/roadt_dur.total) > 0.02:  # 2% tolerance
						self.logger.error("Different duration results: %.1f h (engine state) "
						"vs. %.1f h (road type)" % (engine_dur.total, roadt_dur.total))
				# duration
				if engine_dur.total > 0.0:
					story += [Paragraph(
						'Total duration: %.1f hours (%.1f%% engine running, %.1f%% engine off)'%
						(engine_dur.total, 100.0 * engine_dur['yes']/engine_dur.total, 100.0 * engine_dur['no']/engine_dur.total)),]
				else:
					story += [Paragraph('Total duration: %.1f hours' % engine_dur.total)]
			else:
				self.logger.warning('Engine state statistics not available')
				story += [Paragraph('Total duration: n/a'),]
			# daytime
			if self.optdep['dur_vs_daytime'] in self.passed_optdep:
				daytime_dur = index_fill(self.modules.fill(self.optdep['dur_vs_daytime']))
				if 'roadt_dur' in locals():
					# plau check for durations of different sources
					if roadt_dur.total > 0.25 and abs(1.0 - daytime_dur.total/roadt_dur.total) > 0.02:  # 2% tolerance
						self.logger.error("Different duration results: %.1f h (daytime) "
						"vs. %.1f h (road type)" % (daytime_dur.total, roadt_dur.total))
				# duration
				if daytime_dur.total > 0.0:
					calc_dist_perc = lambda d: int(round2(d/daytime_dur.total*100.0, 5.0))
					story += [Paragraph(
						'Total duration: %.1f hours (ca. %d%% day, %d%% night, %d%% dusk)'%
						(daytime_dur.total,
						 calc_dist_perc(daytime_dur['day']),
						 calc_dist_perc(daytime_dur['night']),
						 calc_dist_perc(daytime_dur['dusk']))),]
				else:
					story += [Paragraph('Total duration: %.1f hours' % daytime_dur.total)]
			else:
				self.logger.warning('Daytime statistics not available')
				story += [Paragraph('Total duration: n/a'),]
			# common remark
			story += [Paragraph(italic('Remark: Percentage values with "ca." are '
																 'rounded to nearest 5.'), fontsize=8),
								Spacer(width=1*cm, height=0.2*cm),]
			
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
					story += [Paragraph('In-lane obstacle presence: %.0f%% / %.0f%% (duration / mileage)' % (inlane_dur_perc, inlane_dist_perc)),
										Paragraph('Fused in-lane obstacle presence: %.0f%% / %.0f%% (duration / mileage)' % (inlane_fused_dur_perc, inlane_fused_dist_perc)),
										Spacer(width=1*cm, height=0.2*cm),]
				else:
					story += [Paragraph('In-lane obstacle presence: n/a'),
										Paragraph('Fused in-lane obstacle presence: n/a'),
										Spacer(width=1*cm, height=0.2*cm),]
			else:
				self.logger.warning('In-lane obstacle presence not available')
				story += [Paragraph('In-lane obstacle presence: n/a'),
									Paragraph('Fused in-lane obstacle presence: n/a'),
									Spacer(width=1*cm, height=0.2*cm),]
				
				# lane change table
			if self.optdep['lane_change_events'] in self.passed_optdep:
				lane_change_ei_ids = index_fill(self.modules.fill(self.optdep['lane_change_events']))
				header = cIntervalHeader.fromFileName(self.query_files['lane_change_events'])
				table = self.batch.get_table_dict(header, lane_change_ei_ids, sortby=[('measurement', True), ('start [s]', True)])
				global LANCE_CHANGE_TABLE
				LANCE_CHANGE_TABLE = table
				story += [Paragraph('Total number of lane change events: %d' % len(table))]

				# obj jump table
			if self.optdep['dx_obj_jump_events'] in self.passed_optdep:
				obj_jump_ei_ids = index_fill(self.modules.fill(self.optdep['dx_obj_jump_events']))
				header = cIntervalHeader.fromFileName(self.query_files['dx_obj_jump_events'])
				table = self.batch.get_table_dict(header, obj_jump_ei_ids, sortby=[('measurement', True), ('start [s]', True)])
				global OBJ_JUMP_TABLE
				OBJ_JUMP_TABLE = table
				story += [Paragraph('Total number of obj jump events: %d' % len(table))]

				# switchover table
			if self.optdep['switchover_events'] in self.passed_optdep:
				switchover_ei_ids = index_fill(self.modules.fill(self.optdep['switchover_events']))
				header = cIntervalHeader.fromFileName(self.query_files['switchover_events'])
				table = self.batch.get_table_dict(header, switchover_ei_ids, sortby=[('measurement', True), ('start [s]', True)])
				global SWITCHOVER_TABLE
				SWITCHOVER_TABLE = table
				story += [Paragraph('Total number of switchover events: %d' % len(table))]

				# accobjtracking table
			if self.optdep['accobjtracking_events'] in self.passed_optdep:
				accobjtrack_ei_ids = index_fill(self.modules.fill(self.optdep['accobjtracking_events']))
				header = cIntervalHeader.fromFileName(self.query_files['accobjtracking_events'])
				table = self.batch.get_table_dict(header, accobjtrack_ei_ids, sortby=[('measurement', True), ('start [s]', True)])
				global ACCOBJ_TABLE
				ACCOBJ_TABLE = table
				story += [Paragraph('Total number of stable acc object tracking events: %d' % len(table))]

					# fusion degradation table
			if self.optdep['fusion_degradation'] in self.passed_optdep:
				accobjtrack_ei_ids = index_fill(self.modules.fill(self.optdep['fusion_degradation']))
				header = cIntervalHeader.fromFileName(self.query_files['fusion_degradation'])
				table = self.batch.get_table_dict(header, accobjtrack_ei_ids, sortby=[('measurement', True), ('start [s]', True)])
				global FUSDEG_TABLE
				FUSDEG_TABLE = table
				story += [Paragraph('Total number of Fusion Degradation events: %d' % len(table))]
			
			# system performance
			m_plot = lambda m: self.module_plot(m,
				windgeom="250x200+0+0", width=60.0, height=60.0, unit=1.0, kind='%',
				overwrite_start_end=True, start_date=start_date, end_date=end_date)
			table_style = [
				('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
				('VALIGN', (0, 0), (-1, -1), 'TOP'),
			]
			story += [ Table([
				[m_plot("view_quantity_vs_systemstate_stats_flr25-pie_duration@aebseval.systemstate"),
				 m_plot("view_quantity_vs_sensorstatus_stats-pie_duration@mfc525eval.sensorstatus")],
			], style=table_style) ]

			story.append(Spacer(width = 1 * cm, height = 0.5 * cm))

			story += [ Table([
				[m_plot("view_quantity_vs_left_lane_quality_stats-pie_duration@mfc525eval.laneeval"),
				 m_plot("view_quantity_vs_right_lane_quality_stats-pie_duration@mfc525eval.laneeval")],
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

	def aebs_event_classification(self):
		story = [IndexedParagraph('AEBS event classification', style='Heading1')]
		
		m_plot = lambda m: self.module_plot(m,
			windgeom="500x300+0+0", width=60.0, height=60.0, unit=1.0, kind='%')
		table_style = [
			('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
			('VALIGN', (0, 0), (-1, -1), 'TOP'),
		]
		story += [ Table([
			[m_plot("view_count_vs_phase_stats_flr25-bar_mergedcount@aebseval.classif"),
			 m_plot("view_count_vs_movstate_stats_flr25-bar_mergedcount@aebseval.classif")],
			[m_plot("view_count_vs_severity_stats_flr25-bar_mergedcount@aebseval.classif"),
			 m_plot("view_count_vs_cause_maingroup_stats_flr25-bar_mergedcount@aebseval.classif")],
		], style=table_style) ]
		
		story += [PageBreak()]
		return story

	def events(self, summary):
		statuses = ['fillFLC25_AOA_ACC@aebs.fill']
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
					modules_in_event.update({'view_lane_change_data_FLC25-TRACK_%03d@mfc525eval.objecteval' %int(warning['objectid']):
											Client('FLC25 internal track', '640x700+0+0', 11, 12, cm)})
				elif type(summary) in [FusDegSummary]:
					modules_in_event.update({'view_fusion_degradation_data_FLC25-TRACK_%03d@mfc525eval.objecteval' %int(warning['objectid']):
											Client('FLC25 internal track', '640x700+0+0', 11, 12, cm)})
				elif type(summary) in [SWSummary]:
					modules_in_event.update({'view_lane_change_data_FLC25-TRACK_%03d@mfc525eval.objecteval' %int(warning['initialid']):
											Client('FLC25 internal track', '640x700+0+0', 11, 12, cm)})
					modules_in_event.update({'view_lane_change_data_FLC25-TRACK_%03d@mfc525eval.objecteval' %int(warning['changedid']):
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
					modules_in_warnings.update({'view_lane_change_data_FLC25-TRACK_%03d@mfc525eval.objecteval' %int(warning['objectid']):
											Client('FLC25 internal track', '640x700+0+0', 11, 12, cm)})
				elif type(summary) in [SWSummary]:
					modules_in_warnings.update({'view_lane_change_data_FLC25-TRACK_%03d@mfc525eval.objecteval' %int(warning['initialid']):
											Client('FLC25 internal track', '640x700+0+0', 11, 12, cm)})
					modules_in_warnings.update({'view_lane_change_data_FLC25-TRACK_%03d@mfc525eval.objecteval' %int(warning['changedid']):
											Client('FLC25 internal track', '640x700+0+0', 11, 12, cm)})
				for module_name, client in modules_in_warnings.iteritems():
					story.append( client(sync, module_name) )
					story.append( FrameBreak() )
				if summary.modules: story.pop(-1)  # remove last FrameBreak
			manager.close()
		return story


class LaneChangeSummary(EventSummary):
	def init(self, batch, view_name):
		data = LANCE_CHANGE_TABLE
		
		for row in data:
			self.setdefault(row['fullmeas'], []).append(dict(
				start=row['start [s]'],
				end=row['start [s]']+row['duration [s]'],
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


class ObjJumpSummary(EventSummary):
	def init(self, batch, view_name):
		data = OBJ_JUMP_TABLE
		
		for row in data:
			self.setdefault(row['fullmeas'], []).append(dict(
				start=row['start [s]'],
				end=row['start [s]']+row['duration [s]'],
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
				end=row['start [s]']+row['duration [s]'],
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
				end=row['start [s]']+row['duration [s]'],
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


class FusDegradationSummary(EventSummary):
	def init(self, batch, view_name):
		data = FUSDEG_TABLE
		
		for row in data:
			self.setdefault(row['fullmeas'], []).append(dict(
				start=row['start [s]'],
				end=row['start [s]']+row['duration [s]'],
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


class FusDegSummary(FusDegradationSummary):
	title = "Fusion degradation event"
	explanation = """
	After stable fusion detection the object detection degraded %s 
	"""\
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
		 Client('Ego Velocity', '640x700+0+0', 11, 12, cm))
	]
	statuses = ['fillFLC25_AOA_ACC@aebs.fill']
	groups = ['FLC25_AOA_ACC']



class AOSummary(ACCObjSummary):
	title = "ACC object stable tracking event"
	explanation = """
	ACC object was tracking an object in a stable manner, when it changed obj id <br/>
	and than continued to once again select the original object id, Changed object ID: %s 
	"""\
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
	statuses = ['fillFLC25_AOA_ACC@aebs.fill']
	groups = ['FLC25_AOA_ACC']


class ODSummary(LaneChangeSummary):
	title = "Lane Change event details"
	explanation = """
	Object ID %s - Lane changed from: %s Lane changed to: %s<br/>
	dx distance to object: %s
	"""\
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
	statuses = ['fillFLC25_AOA_ACC@aebs.fill']
	groups = ['FLC25_AOA_ACC']


class OJSummary(ObjJumpSummary):
	title = "ObjJump Events"
	explanation = """
	Object ID %s - Delta distance X: %s dx distance: %s<br/>
				 - Delta distance Y: %s dy distance: %s
	"""\
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
	statuses = ['fillFLC25_AOA_ACC@aebs.fill']
	groups = ['FLC25_AOA_ACC']


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
		statuses = ['fillFLC25_AOA_ACC@aebs.fill']
		groups = ['FLC25_AOA_ACC']


if __name__ == '__main__':
	from reportgen.common.main import main
	main(os.path.abspath(__file__))
