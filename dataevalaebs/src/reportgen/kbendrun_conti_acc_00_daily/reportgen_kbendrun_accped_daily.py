# -*- dataeval: init -*-

import os

import matplotlib
from collections import defaultdict
# matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from reportlab.lib import colors
from reportlab.platypus import Spacer, PageBreak, Table, NextPageTemplate, FrameBreak
from reportlab.lib.pagesizes import cm

from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph, NonEmptyTableWithHeader, \
		italic, bold, grid_table_style
from pyutils.math import round2
from config.interval_header import cIntervalHeader

from aebs.par import aebs_classif
from reportgen.common.analyze import Analyze
from reportgen.common.summaries import EventSummary, Summary
from reportgen.common.clients import Client, TrackNavigator, VideoNavigator
from reportgen.common.utils import vector2scalar
from aebs.fill.calc_flr20_aebs_phases import Calc as Flr20Calc

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

ACC_TABLE = []
percentage_vehicle_in_accped_speed_range = 0

class ACCAnalyze(Analyze):
	dep = {
		'acc_events': 'analyze_accped_stop_resim-last_entries@accpedresim',

	}
	optdep = dict(
		vehicle_in_speeed_range = 'analyze_accped_vehicle_speed_range-last_entries@accpedresim',
		dur_vs_roadtype = 'view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
		dist_vs_roadtype = 'view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
		dur_vs_engine_onoff = 'view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
		dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@flc20eval.daytime',
	)

	query_files = {
		'acc_events': abspath('../../accpedresim/events_inttable.sql'),
		'vehicle_in_speeed_range': abspath('../../accpedresim/accped_speed_range_inttable.sql'),
		# 'acc_brakepedal_events': abspath('../acceval/events_inttable.sql'),
	}

	def fill(self):
		self.view_name = self.batch.create_table_from_last_entries(
			start_date=self.start_date, end_date=self.end_date)

		# ACC events - TODO: restruct
		index_fill = lambda fill: fill.all
		acc_dirk = index_fill(self.modules.fill(self.dep['acc_events']))
		header = cIntervalHeader.fromFileName(self.query_files['acc_events'])

		# vehicle_in_speeed_range = index_fill(self.modules.fill(self.optdep['vehicle_in_speeed_range']))
		# vehicle_in_speeed_range_header = cIntervalHeader.fromFileName(self.query_files['vehicle_in_speeed_range'])
		# vehicle_in_speed_range_data = self.batch.get_table_dict(vehicle_in_speeed_range_header, vehicle_in_speeed_range, sortby=[('measurement', True), ('start [s]', True)])
		# global percentage_vehicle_in_accped_speed_range
		# try:
		# 	percentage_vehicle_in_accped_speed_range = vehicle_in_speed_range_data[1]
		# except:
		# 	pass

		global ACC_TABLE
		# ACC_TABLE = self.batch.get_table_dict(header, acc_ei_ids, sortby=[('measurement', True), ('start [s]', True)])
		ACC_TABLE.append(
			self.batch.get_table_dict(header, acc_dirk, sortby=[('measurement', True), ('start [s]', True)]))

		story = intro(
			"ACC field test evaluation report",
			"""
			This is an automatically generated report, based on field tests with
			simultaneously measured forward-looking radar (FLR25).<br/>
			<br/>
			The output signals of ACC are analyzed and the
			relevant events are collected in this report.<br/>
			Results are presented in table format first, followed by the detailed
			overview of the individual events.<br/>
			"""
		)
		story.append(PageBreak())
		story.extend(toc())
		story.append(PageBreak())
		# acc_summary = ACCEventSummary(self.batch, self.view_name)
		# story.extend(self.overall_summary(acc_summary))
		story.extend(self.overall_summary())
		# story.extend(self.explanation())
		# story.extend(self.aebs_event_classification())
		# summaries = [Summary(self.batch, self.view_name), Summary2(self.batch, self.view_name),
		#              Summary3(self.batch, self.view_name)]
		summaries = [Summary(self.batch, self.view_name)]
		story.extend(self.summaries_acc(summaries))
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
						'Road type statistics, Total duration: %s (ca. %d%% standstill, %d%% city, %d%% rural, %d%% highway)' %
						(bold('%.1f hours' % roadt_dur.total),
						calc_dist_perc(roadt_dur['ego stopped']),
						calc_dist_perc(roadt_dur['city']),
						calc_dist_perc(roadt_dur['rural']),
						calc_dist_perc(roadt_dur['highway']))), ]
				else:
					story += [Paragraph('Road type statistics, Total duration: %s' % bold('%.2f hours' % roadt_dur.total))]
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
						self.logger.error("Different duration results: %.2f h (engine state) "
										  "vs. %.2f h (road type)" % (engine_dur.total, roadt_dur.total))
				# duration
				if engine_dur.total > 0.0:
					story += [Paragraph(
						'Engine state statistics, Total duration: %.2f hours (%.1f%% engine running, %.1f%% engine off)' %
						(engine_dur.total, 100.0 * engine_dur['yes'] / engine_dur.total, 100.0 * engine_dur['no'] / engine_dur.total)), ]
				else:
					story += [Paragraph('Engine state statistics, Total duration: %.2f hours' % engine_dur.total)]
			else:
				self.logger.warning('Engine state statistics not available')
				story += [Paragraph('Total duration: n/a'), ]
			# daytime
			if self.optdep['dur_vs_daytime'] in self.passed_optdep:
				daytime_dur = index_fill(self.modules.fill(self.optdep['dur_vs_daytime']))
				if 'roadt_dur' in locals():
					# plau check for durations of different sources
					if roadt_dur.total > 0.25 and abs(1.0 - daytime_dur.total / roadt_dur.total) > 0.02:  # 2% tolerance
						self.logger.error("Different duration results: %.2f h (daytime) "
										  "vs. %.2f h (road type)" % (daytime_dur.total, roadt_dur.total))
				# duration
				if daytime_dur.total > 0.0:
					calc_dist_perc = lambda d: int(round2(d / daytime_dur.total * 100.0, 5.0))
					story += [Paragraph(
						'Daytime statistics, Total duration: %.2f hours (ca. %d%% day, %d%% night, %d%% dusk)' %
						(daytime_dur.total,
						calc_dist_perc(daytime_dur['day']),
						calc_dist_perc(daytime_dur['night']),
						calc_dist_perc(daytime_dur['dusk']))), ]
				else:
					story += [Paragraph('Daytime statistics, Total duration: %.2f hours' % daytime_dur.total)]
			else:
				self.logger.warning('Daytime statistics not available')
				story += [Paragraph('Total duration: n/a'), ]
			# Vehicle speed range percentage
			if (self.optdep['vehicle_in_speeed_range'] in self.passed_optdep):
				percentage_vehicle_in_accped_speed_range = 0
				vehicle_in_speeed_range = index_fill(self.modules.fill(self.optdep['vehicle_in_speeed_range']))
				vehicle_in_speeed_range_header = cIntervalHeader.fromFileName(self.query_files['vehicle_in_speeed_range'])
				vehicle_in_speed_range_data = self.batch.get_table_dict(vehicle_in_speeed_range_header, vehicle_in_speeed_range, sortby=[('measurement', True), ('start [s]', True)])
				try:
					percentage_vehicle_in_accped_speed_range = vehicle_in_speed_range_data[0]['vehicle_in_accped_speed_range'] * 100
				except:
					pass
				story += [Paragraph('Vehicle in ACC PED STOP speed range: %s' % bold('%d%%' % percentage_vehicle_in_accped_speed_range))]

			# common remark
			story += [Paragraph(italic('Remark: Percentage values with "ca." are '
									   'rounded to nearest 5.'), fontsize=8),
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
			[m_plot("view_count_vs_phase_stats-bar_mergedcount@aebseval.classif"),
				m_plot("view_count_vs_movstate_stats-bar_mergedcount@aebseval.classif")],
			[m_plot("view_count_vs_severity_stats-bar_mergedcount@aebseval.classif"),
				m_plot("view_count_vs_cause_maingroup_stats-bar_mergedcount@aebseval.classif")],
		], style=table_style)]
		story += [self.module_plot(
			"view_quantity_vs_smess_fault_stats-bar_duration@flr20eval.faults",
			windgeom="1000x300+0+0", width=50.0, height=50.0, unit=1.0, kind='%')]

		story += [PageBreak()]
		return story

	def summaries_acc(self, summaries, module_name=None):
		story = [
			IndexedParagraph('ACC Event summary tables', style='Heading1'),
			NextPageTemplate('LandscapeTable'),
		]
		if module_name is not None:
			story.insert(1, self.module_plot(module_name))
			story.append(PageBreak())
		for summary in summaries:
			story.append(NextPageTemplate('LandscapeTable'))
			story.append(IndexedParagraph(summary.title, style='Heading2'))
			story.append(summary.get_table(link_pattern=self.EVENT_LINK,
				link_heading='Heading2')),
			story.append(PageBreak())
		return story

	def events(self, summary):
		statuses = ['fillFLR25_ACC_PED@aebs.fill']
		groups = ['FLR25_ACC_PED']
		statuses.extend(summary.statuses)
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

class ACCSummary(EventSummary):
	def init(self, batch, view_name):
		data = ACC_TABLE
		valid_data = [valid for valid in data if valid != []]
		for row in valid_data:
			for i in row:
				self.setdefault(i['fullmeas'], []).append(dict(
					start=i['start [s]'],
					end=i['start [s]'] + i['duration [s]'],
					duration=i['duration [s]'],
					acc=vector2scalar(i['ACC event']),
					# type=vector2scalar(i['ACC issue type']),
					# cause = "None",
					# comment=i['comment']
				))

		self.modules.update([
			('view_nxtvideoeventgrabbernav_lanes-NO_LANES@evaltools',
			 VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
			('view_tracknav_lanes-NO_LANES_ACC_PED_VEW@evaltools',
			 TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
		])

		self.columns.update([
			('start', 'start\n[s]\n'),
			('end', 'end\n'),
			('duration', 'duration\n[s]\n'),
			('acc', 'ACC event\n\n'),
		])
		return


class ACCEventSummary(Summary):
		def init(self, batch, view_name):
			data = ACC_TABLE
			self.title = "ACC event summary"
			valid_data = [valid for valid in data if valid != []]
			for row in valid_data:
				for i in row:
					self.setdefault(i['fullmeas'], []).append(dict(
						acc_event = vector2scalar(i['ACC event']),
						# type = vector2scalar(i['ACC issue type']),
					))

			self.columns.update([
				# ('type', 'acc issue\ntype\n'),
				('acc_event', 'ACC event\n'),
				# ('acc_counter', 'ACC count\n'),
			])
			return

		def get_data(self, link_pattern, link_heading):
				header = self.columns.values()
				data = [header]
				acc_sum = defaultdict(int)
				for _, acc_events in self.iteritems():
					for acc in acc_events:
						acc_sum[acc['acc_event']] += 1
				for k,v in acc_sum.iteritems():
					data.append([k, v])
				return data

		def get_type_data(self):
			data = []
			acc_sum = defaultdict(int)
			for _, acc_events in self.iteritems():
				for acc in acc_events:
					acc_sum[acc['type']] += 1
			for k,v in acc_sum.iteritems():
				data.append([k, v])
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


class Summary(ACCSummary):
	title = " ACC PED Events Details"
	explanation = """
		   ACC PED Event: %s - Event Duration: %s sec
			""" \
				  % ('%(acc)s', '%(duration).2f')

	legend_pics = [
		(EventSummary.stat_im, 'stationary'),
		(EventSummary.mov_im, 'moving'),
		(EventSummary.acc_im, 'ACC track'),
	]

	extra_modules = [
		('view_accped_stop_resim@accpedresim',
		 Client('Vehicle Speed and Accelerator Pedal Position', '640x700+0+0', 11, 12, cm)),
		# ('view_flr25_acc_kinematics_control-TESTER@acceval',
		#  Client('view_flr25_acc_kinematics_control', '640x700+0+0', 11, 12, cm)),
	]

	statuses = ['fillFLR25_ACC_PED@aebs.fill']
	groups = ['FLR25_ACC_PED']
