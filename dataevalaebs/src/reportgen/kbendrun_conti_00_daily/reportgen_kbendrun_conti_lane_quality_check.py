# -*- dataeval: init -*-

import os
from collections import defaultdict
import matplotlib
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
from reportgen.common.summaries import Summary, EventSummary, PIC_DIR
from reportgen.common.clients import Client, TrackNavigator, VideoNavigator
from reportgen.common.utils import vector2scalar
from aebs.fill.calc_radar_aebs_phases import Calc as Flr25Calc
from flr25eval.FLR25_DTC_mapping import Get_DTC_Name
from flr25eval.FLR25_DTC_mapping import Get_DEM_event_ids

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

AEBS_TABLE = None
DTC_TABLE = None
RESET_TABLE = None

class AebsAnalyze(Analyze):
	optdep = dict(
		aebs_events='analyze_events_merged_FLR25-last_entries@aebseval',
		dtc_events = 'analyze_flr25_dtc_active_events-last_entries@flr25eval.faults',
		radar_reset_events = 'analyze_flr25_radar_reset_events-last_entries@flr25eval.faults',
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
		'aebs_events': abspath('../../aebseval/events_inttable.sql'),
		'dtc_events' : abspath('../../flr25eval/faults/flr25_active_dtc_inittable.sql'),
		'radar_reset_events' : abspath('../../flr25eval/faults/flr25_radar_reset_inittable.sql')
	}
	
	def fill(self):
		self.view_name = self.batch.create_table_from_last_entries(
			start_date=self.start_date, end_date=self.end_date)

		story = intro(
			"AEBS field test evaluation report",
			"""
			This is an automatically generated report, based on field tests with
			simultaneously measured forward-looking radar (FLR25) and camera (MFC525)
			sensors.<br/>
			<br/>
			The output signals of AEBS are analyzed and the
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
		dtc_summary = [DTCSummary(self.batch, self.view_name)]
		story.extend(self.aebs_event_classification(dtc_summary))
		summaries = [Flr25Summary(self.batch, self.view_name)]
		story.extend(self.summaries(summaries))
		story.extend(self.warnings(summaries))
		fault_summaries = [DTCTimeline(self.batch, self.view_name),  RadarResetTimeline(self.batch, self.view_name)]
		story.extend(self.faults(fault_summaries))
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
			# common remark
			story += [Paragraph(italic('Remark: Percentage values with "ca." are '
																 'rounded to nearest 5.'), fontsize=8),
								Spacer(width=1*cm, height=0.2*cm),]
			
			# Radar Reset event table
			if (self.optdep['radar_reset_events'] in self.passed_optdep):
				reset_ei_ids = index_fill(self.modules.fill(self.optdep['radar_reset_events']))
				header1 = cIntervalHeader.fromFileName(self.query_files['radar_reset_events'])
				reset_table_internal = self.batch.get_table_dict(header1, reset_ei_ids, sortby = [('measurement', True), ('start [s]', True)])
				global RESET_TABLE
				RESET_TABLE = reset_table_internal

			# DTC event table
			if (self.optdep['dtc_events'] in self.passed_optdep):
				dtc_ei_ids = index_fill(self.modules.fill(self.optdep['dtc_events']))
				header1 = cIntervalHeader.fromFileName(self.query_files['dtc_events'])
				dtc_table_internal = self.batch.get_table_dict(header1, dtc_ei_ids, sortby = [('measurement', True), ('start [s]', True)])
				global DTC_TABLE
				DTC_TABLE = dtc_table_internal

			# AEBS warning rate
			if (self.optdep['aebs_events'] in self.passed_optdep and
					self.optdep['count_vs_aebs_severity'] in self.passed_optdep):
				aebs_ei_ids = index_fill(self.modules.fill(self.optdep['aebs_events']))
				header = cIntervalHeader.fromFileName(self.query_files['aebs_events'])
				table = self.batch.get_table_dict(header, aebs_ei_ids, sortby=[('measurement', True), ('start [s]', True)])
				global AEBS_TABLE
				AEBS_TABLE = table
				
				aebs_count = index_fill(self.modules.fill(self.optdep['count_vs_aebs_severity']))
				
				tot_aebs = len(table)
				story += [Paragraph('Total number of AEBS events: %d' % tot_aebs)]
				if 'roadt_dist' in locals() and roadt_dist.total > 0.0:
					tot_rate = float(tot_aebs)/roadt_dist.total * 1000.0
					false_rate = float(aebs_count['1-False alarm'])/roadt_dist.total * 5000.0
					ques_rate = float(aebs_count['2-Questionable false alarm'])/roadt_dist.total * 400.0
					story += [Paragraph('AEBS warning rate - overall: <b>%.1f events / 1000 km</b>' % tot_rate),
										Paragraph('AEBS warning rate - 1-False alarm: <b>%.1f events / 5000 km</b>' % false_rate),
										Paragraph('AEBS warning rate - 2-Questionable false alarm: <b>%.1f events / 400 km</b>' % ques_rate),
										Spacer(width=1*cm, height=0.2*cm),]
				else:
					story += [Paragraph('AEBS warning rate: n/a'),
										Spacer(width=1*cm, height=0.2*cm),]
			else:
				story += [Paragraph('Total number of AEBS events: n/a'),
									Paragraph('AEBS warning rate: n/a'),
									Spacer(width=1*cm, height=0.2*cm),]
			
			# system performance
			m_plot = lambda m: self.module_plot(m,
				windgeom="250x200+0+0", width=60.0, height=60.0, unit=1.0, kind='%',
				overwrite_start_end=True, start_date=start_date, end_date=end_date)
			table_style = [
				('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
				('VALIGN', (0, 0), (-1, -1), 'TOP'),
			]
			story += [ Table([
				[m_plot("view_quantity_vs_systemstate_stats_flr25-pie_duration@aebseval.systemstate")],
			], style=table_style)]
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

	def aebs_event_classification(self, dtc_summary):
		story = [IndexedParagraph('AEBS event classification', style='Heading1'), NextPageTemplate('LandscapeTable'),]
		
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
		for summary in dtc_summary:
			story.append(IndexedParagraph(summary.title, style='Heading2'))
			story.append(summary.get_table(link_pattern=self.EVENT_LINK, link_heading='Heading2')),
			story.append(Spacer(width = 1 * cm, height = 0.5 * cm))

		story += [self.module_plot(
			"view_quantity_vs_radar_reset_stats-bar_count@flr25eval.faults",
			windgeom = "1000x300+0+0", width = 50.0, height = 50.0, unit = 1.0, kind = '%')]
		story += [Paragraph(italic('Remark: Whenever the ResetCounter signal is increased it will count as a Radar Reset'), fontsize = 8),
				Spacer(width = 1 * cm, height = 0.2 * cm), ]
		story += [PageBreak()]
		return story

	def faults(self, summaries, module_name=None):
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

	def events(self, summary):
		statuses = ['fillFLR25_AEB@aebs.fill']
		statuses.extend(summary.statuses)
		groups = ['FLR25', 'moving', 'stationary', 'stopped']
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

class AebsSummary(EventSummary):
	def init(self, batch, view_name):
		data = AEBS_TABLE
		
		for row in data:
			self.setdefault(row['fullmeas'], []).append(dict(
				start=row['start [s]'],
				end=row['start [s]']+row['duration [s]'],
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
			('view_nxtvideoeventgrabbernav_lanes-NO_LANES@evaltools',
			 VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
			('view_tracknav_lanes-FLC25_CAN@evaltools',
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


class RadarResetTimeline(Summary):
		def init(self, batch, view_name):
				data = RESET_TABLE
				self.title = 'Radar Reset event details'
				for row in data:
						self.setdefault(row['fullmeas'], []).append(dict(
										start = row['start [s]'],
										reset_reason = row['Cat2LastResetReason'],
										address = row['Address'],
										reset_cntr = row['ResetCounter'],
										rtrn_addr = row['Return Address'],
										comment = row['comment']
						))

				self.columns.update([
						('start', 'start [s]\n'),
						('reset_reason', 'Cat2LastResetReason\n'),
						('address', 'Address\n'),
						('reset_cntr', 'ResetCounter\n'),
						('rtrn_addr', 'Return Address\n'),
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
						row = [basename, reset['start'], reset['reset_reason'], reset['address'], reset['reset_cntr'], reset['rtrn_addr'], reset['comment']]
						data.append(row)
				return data
			
		def get_style(self):
    			style = [
				('GRID',   ( 0, 0), (-1, -1), 0.025*cm, colors.black),
				('FONT',   ( 0, 0), (-1,  0), '%s-Bold' % self.font_name, self.font_size),
				('FONT',   ( 0, 1), (-1, -1), self.font_name, self.font_size),
				('ALIGN',  ( 0, 1), (-1, -1), 'CENTER'),
				('VALIGN', ( 0, 1), (-1, -1), 'MIDDLE'),
    			]
    			return style

class DTCSummary(Summary):
		def init(self, batch, view_name):
				data = DTC_TABLE
				self.title = "DTC event summary"
				for row in data:
						self.setdefault(row['fullmeas'], []).append(dict(
										dtc_id = row['DTC ID'],
										dtc_counter = row['DTC counter'],
										active_dem_event_ids = row['DEM event ids'],
										dtc_comment = row['comment']
						))

				self.columns.update([
						('dtc_id', 'DTC ID\n'),
						('dtc_counter', 'DTC count\n'),
						('dtc_name', 'DTC name\n'),
						('active_dem_event_ids', 'DEM events\n'),
						('dtc_comment', 'Comment\n'),

				])
				return

		def get_data(self, link_pattern, link_heading):
				header = self.columns.values()
				data = [header]
				dtc_sum = {}
				dem_sum = {}
				comments_sum = {}
				for _, dtcs in self.iteritems():
					for dtc in dtcs:
						key = dtc['dtc_id']
						counter = str(int(dtc['dtc_counter']))
						dem = Get_DEM_event_ids(str(int(dtc['active_dem_event_ids'])))
						comment = dtc['dtc_comment']
						if not comments_sum.has_key(key):
							comments_sum[key] = comment
						else:
							if comment:
								if len(comments_sum[key].split(', -')) < 2:
									comments_sum[key] = comments_sum[key] + '\n' + comment
						if not dtc_sum.has_key(key):
							dtc_sum[key] = counter
						else:
							if counter not in dtc_sum[key]:
								dtc_sum[key] = dtc_sum[key] + ',' + counter
						if not dem_sum.has_key(key):
							dem_sum[key] = dem
						else:
							for id in dem.split(', '):
								if id not in dem_sum[key]:
									dem_sum[key] = dem_sum[key] + ', ' + id

				for k,v in dtc_sum.iteritems():
					if dem_sum[k]:
						if len(dem_sum[k].split(', ')) > 10:
							dem_sum[k] = '\n'.join(dem_sum[k][i:i+50] for i in range(0, len(dem_sum[k]), 50))
					data.append([hex(int(k)), len(v.split(',')), Get_DTC_Name(hex(int(k))), dem_sum[k], comments_sum[k]])
				return data
			
		def get_style(self):
    			style = [
				('GRID',   ( 0, 0), (-1, -1), 0.025*cm, colors.black),
				('FONT',   ( 0, 0), (-1,  0), '%s-Bold' % self.font_name, self.font_size),
				('FONT',   ( 0, 1), (-1, -1), self.font_name, self.font_size),
				('ALIGN',  ( 0, 1), (-1, -1), 'CENTER'),
				('VALIGN', ( 0, 1), (-1, -1), 'MIDDLE'),
    			]
    			return style


class DTCTimeline(Summary):
		def init(self, batch, view_name):
				data = DTC_TABLE
				self.title = 'DTC event details'
				for row in data:
						self.setdefault(row['fullmeas'], []).append(dict(
										dtc_id = row['DTC ID'],
										dtc_counter = row['DTC counter'],
										dtc_timestamp = row['DTC timestamp'],
										active_dem_event_ids = row['DEM event ids'],
										dtc_comment = row['comment']
						))

				self.columns.update([
						('dtc_id', 'DTC ID\n'),
						('dtc_counter', 'DTC counter\n'),
						('dtc_timestamp', 'DTC timestamp\n'),
						('dtc_name', 'DTC name\n'),
						('active_dem_event_ids', 'Active DEM event ids\n'),
						('dtc_comment', 'Comment\n'),
				])
				return

		def get_data(self, link_pattern, link_heading):
				header = self.columns.values()
				header.insert(0, 'measurement')
				data = [header]
				for meas, dtcs in self.iteritems():
					basename = os.path.basename(meas)
					for dtc in dtcs:
						dem_events = Get_DEM_event_ids(str(int(dtc['active_dem_event_ids'])))
						if len(dem_events.split(', ')) > 5:
							dem_events = '\n'.join(dem_events[i:i+25] for i in range(0, len(dem_events), 25))
						dtc_cmnt = dtc['dtc_comment']
						if dtc_cmnt:
							if len(dtc_cmnt) > 40:
								dtc_cmnt = '\n'.join(dtc_cmnt[i:i+40] for i in range(0, len(dtc_cmnt), 40))
						dtc_name = Get_DTC_Name(hex(int(dtc['dtc_id'])))
						row = [basename, hex(int(dtc['dtc_id'])), dtc['dtc_counter'], dtc['dtc_timestamp'], dtc_name, dem_events, dtc_cmnt]
						data.append(row)
				return data
			
		def get_style(self):
    			style = [
				('GRID',   ( 0, 0), (-1, -1), 0.025*cm, colors.black),
				('FONT',   ( 0, 0), (-1,  0), '%s-Bold' % self.font_name, self.font_size),
				('FONT',   ( 0, 1), (-1, -1), self.font_name, self.font_size),
				('ALIGN',  ( 0, 1), (-1, -1), 'CENTER'),
				('VALIGN', ( 0, 1), (-1, -1), 'MIDDLE'),
    			]
    			return style


class Flr25Summary(AebsSummary):
	title = "AEBS event details"
	explanation = """
	AEBS %s - event duration: %s sec, cause: %s, rating: %s<br/>
	Event is triggered because AEBS state was active: warning (%d), partial (%d)
	or emergency (%d) braking.
	"""\
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
		('view_kinematics_FLR25@aebseval',
		 Client('Kinematics_Plot', '640x700+0+0', 11, 12, cm)),
	]
	statuses = ['fillFLR25_AEB@aebs.fill']
	groups = ['FLR25_AEB']


if __name__ == '__main__':
	from reportgen.common.main import main
	main(os.path.abspath(__file__))
