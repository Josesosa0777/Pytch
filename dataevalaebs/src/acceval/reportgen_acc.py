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


class ACCAnalyze(Analyze):
	dep = {
		'acc_events': 'analyze_acc_dirk_events-last_entries@acceval',
		'acc_brakepedal_events': 'analyze_acc_brakepedal_override-last_entries@acceval',
		'acc_eco_drive_events': 'analyze_acc_eco_drive_events-last_entries@acceval',
		'acc_eval_overreaction_events': 'analyze_acc_eval_overreaction-last_entries@acceval',
		'acc_torque_request_events': 'analyze_acc_torque_request-last_entries@acceval',
		'acc_strong_brake_req_events': 'analyze_acc_strong_brake_req-last_entries@acceval',
		'acc_take_over_req_events': 'analyze_acc_take_over_req-last_entries@acceval',
	}
	optdep = dict(
		dur_vs_roadtype = 'view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
		dist_vs_roadtype = 'view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
		dur_vs_engine_onoff = 'view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
	)

	query_files = {
		'acc_events': abspath('../acceval/events_inttable_merged.sql'),
		# 'acc_brakepedal_events': abspath('../acceval/events_inttable.sql'),
	}

	def fill(self):
		self.view_name = self.batch.create_table_from_last_entries(
			start_date=self.start_date, end_date=self.end_date)

		# ACC events - TODO: restruct
		index_fill = lambda fill: fill.all
		# acc_ei_ids = index_fill(self.modules.fill(self.dep['acc_events']))
		acc_dirk = index_fill(self.modules.fill(self.dep['acc_events']))
		acc_brakepedal = index_fill(self.modules.fill(self.dep['acc_brakepedal_events']))
		acc_eco_drive = index_fill(self.modules.fill(self.dep['acc_eco_drive_events']))
		acc_eval_overreaction = index_fill(self.modules.fill(self.dep['acc_eval_overreaction_events']))
		acc_request_events = index_fill(self.modules.fill(self.dep['acc_torque_request_events']))
		acc_strong_brake = index_fill(self.modules.fill(self.dep['acc_strong_brake_req_events']))
		acc_take_over = index_fill(self.modules.fill(self.dep['acc_take_over_req_events']))

		header = cIntervalHeader.fromFileName(self.query_files['acc_events'])
		global ACC_TABLE
		# ACC_TABLE = self.batch.get_table_dict(header, acc_ei_ids, sortby=[('measurement', True), ('start [s]', True)])
		ACC_TABLE.append(
			self.batch.get_table_dict(header, acc_dirk, sortby=[('measurement', True), ('start [s]', True)]))
		ACC_TABLE.append(
			self.batch.get_table_dict(header, acc_brakepedal, sortby=[('measurement', True), ('start [s]', True)]))
		ACC_TABLE.append(
			self.batch.get_table_dict(header, acc_eco_drive, sortby=[('measurement', True), ('start [s]', True)]))
		ACC_TABLE.append(
			self.batch.get_table_dict(header, acc_eval_overreaction,
									  sortby=[('measurement', True), ('start [s]', True)]))
		ACC_TABLE.append(
			self.batch.get_table_dict(header, acc_request_events, sortby=[('measurement', True), ('start [s]', True)]))
		ACC_TABLE.append(
			self.batch.get_table_dict(header, acc_strong_brake, sortby=[('measurement', True), ('start [s]', True)]))
		ACC_TABLE.append(
			self.batch.get_table_dict(header, acc_take_over, sortby=[('measurement', True), ('start [s]', True)]))

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
		acc_summary = ACCEventSummary(self.batch, self.view_name)
		story.extend(self.overall_summary(acc_summary))
		# story.extend(self.overall_summary())
		# summaries = [Summary(self.batch, self.view_name), Summary2(self.batch, self.view_name),
		#              Summary3(self.batch, self.view_name)]
		summaries = [Summary(self.batch, self.view_name)]
		story.extend(self.summaries_acc(summaries))
		story.extend(self.warnings(summaries))
		return story


	def overall_summary(self, summary):
		def one_summary(story, start_date, end_date, index_fill):
			# analyzed period
			if start_date is not None and end_date is not None:
				from_to = '%s - %s' % (start_date, end_date)
			elif start_date is None and end_date is None:
				from_to = 'whole duration'
			elif start_date is None:
				from_to = 'until %s' % end_date
			else:  # end_date is None:
				from_to = 'from %s' % start_date
			story += [Paragraph('Analyzed time period: %s' % from_to),
			Spacer(width = 1 * cm, height = 0.2 * cm), ]

			# driven distance and duration
			if (self.optdep['dur_vs_roadtype'] in self.passed_optdep and self.optdep['dist_vs_roadtype'] in self.passed_optdep):
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
						calc_dist_perc(roadt_dist['highway']))), 
						]
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
						 calc_dist_perc(roadt_dur['highway']))),
						 ]
				else:
					story += [Paragraph('Road type statistics, Total duration: %s' % bold('%.1f hours' % roadt_dur.total))]
			else:
				self.logger.warning('Road type statistics not available')
				story += [Paragraph('Road type statistics, Total duration: n/a'), Paragraph('Total mileage: n/a'), ]
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
						'Engine state statistics, Total duration: %.1f hours (%.1f%% engine running, %.1f%% engine off)' %
						(engine_dur.total, 100.0 * engine_dur['yes'] / engine_dur.total,
						100.0 * engine_dur['no'] / engine_dur.total)), ]
				else:
					story += [Paragraph('Engine state statistics, Total duration: %.1f hours' % engine_dur.total)]
			else:
				self.logger.warning('Engine state statistics not available')
				story += [Paragraph('Engine state statistics, Total duration: n/a'), ]
			tot_acc = len(ACC_TABLE)
			story += [Paragraph('Total number of FCW events: %d' % tot_acc)]
			if 'roadt_dist' in locals() and roadt_dist.total > 0.0:
				tot_rate = float(tot_acc) / roadt_dist.total
				story += [Paragraph('Total number of ACC events: %d' % tot_rate)]
			# common remark
			story += [Paragraph(italic('Remark: Percentage values with "ca." are '
				'rounded to nearest 5.'), fontsize = 8),
				Spacer(width = 1 * cm, height = 0.2 * cm), ]
			return
		
		story = [IndexedParagraph('Overall summary', style = 'Heading1')]
		story += [IndexedParagraph('Cumulative results', style = 'Heading2')]
		index_fill = lambda fill: fill.all
		one_summary(story, self.start_date, self.end_date, index_fill)
		acc_events = summary.get_data(link_pattern=self.EVENT_LINK, link_heading='Heading2')
		issues = summary.get_type_data()
		for event in acc_events:
			name = event[0]
			value = int(event[1]) / len(ACC_TABLE)
			story += [Paragraph('%s: %.1f' % name, value)]

		if 'datelist' in self.global_params:
			story += [IndexedParagraph('Latest results', style = 'Heading2')]
			index_fill = lambda fill: fill.values()[-1]
			middatelist = self.global_params.get('datelist', "").split()
			one_summary(story, middatelist[-1], self.end_date, index_fill)
		story.append(IndexedParagraph(summary.title, style='Heading2'))
		story.append(summary.get_table(link_pattern=self.EVENT_LINK, link_heading='Heading2')),
		story.append(Spacer(width = 1 * cm, height = 0.5 * cm))
		story.append(NextPageTemplate('LandscapeTable'))
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
					type=vector2scalar(i['ACC issue type']),
					cause = vector2scalar(i['ACC event cause']),
					comment=i['comment']
				))

		self.modules.update([
			('view_videonav_lanes-FLC25_CAN@evaltools',
			 VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
			('view_tracknav_lanes-FLC25_CAN@evaltools',
			 TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
		])

		self.columns.update([
			('start', 'start\n[s]\n'),
			('end', 'end\n'),
			('duration', 'duration\n[s]\n'),
			('acc', 'acc event\n\n'),
			('type', 'acc issue\ntype\n'),
			('cause', 'acc event\ncause\n'),
			('comment', 'comment\n\n'),

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
						type = vector2scalar(i['ACC issue type']),
					))

			self.columns.update([
				('type', 'acc issue\ntype\n'),
				('acc_event', 'ACC event\n'),
				('acc_counter', 'ACC count\n'),
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
	title = " ACC Events Details"
	explanation = """
		   ACC Event: %s - Event Duration: %s sec, cause: %s
			""" \
				  % ('%(acc)s', '%(duration).2f', '%(cause)s')

	legend_pics = [
		(EventSummary.stat_im, 'stationary'),
		(EventSummary.mov_im, 'moving'),
		(EventSummary.acc_im, 'ACC track'),
	]

	extra_modules = [
		('view_flr25_acc_driveract_hmi-TESTER@acceval',
		 Client('view_flr25_acc_driveract_hmi', '640x700+0+0', 11, 12, cm)),
		('view_flr25_acc_kinematics_control-TESTER@acceval',
		 Client('view_flr25_acc_kinematics_control', '640x700+0+0', 11, 12, cm)),
	]

	statuses = ['fillFLR25_ACC@aebs.fill']
	groups = ['FLR25', 'moving', 'stationary', 'stopped']


	# def overall_summary(self):
	#     def events(self, summary):
	#         statuses = ['fillFLR25@aebs.fill']
	#         statuses.extend(summary.statuses)
	#         groups = ['FLR25', 'moving', 'stationary', 'stopped']
	#         groups.extend(summary.groups)
	#
	#         story = summary.get_tracknav_legend()
	#
	#         for meas, warnings in summary.iteritems():
	#             manager = self.clone_manager()
	#             manager.strong_time_check = False  # TODO: make default behavior with warning
	#             manager.set_measurement(meas)
	#             manager.build(summary.modules, status_names=statuses,
	#                           visible_group_names=groups, show_navigators=False)
	#             sync = manager.get_sync()
	#             for warning in warnings:
	#                 title = self.EVENT_LINK % (os.path.basename(meas), warning['start'])
	#                 story.extend([
	#                     NextPageTemplate(self.warningtemplate),
	#                     PageBreak(),
	#                     IndexedParagraph(title, style='Heading2'),
	#                     FrameBreak(),
	#                     Paragraph(summary.explanation % warning, style='Normal'),
	#                 ])
	#                 sync.seek(warning['start'])
	#                 manager.set_roi(warning['start'], warning['end'], color='y',
	#                                 pre_offset=5.0, post_offset=5.0)
	#                 for module_name, client in summary.modules.iteritems():
	#                     story.append(client(sync, module_name))
	#                     story.append(FrameBreak())
	#                 if summary.modules: story.pop(-1)  # remove last FrameBreak
	#             manager.close()
	#         return story


# class Summary2(ACCSummary):
#     title = " ACC Events Details"
#     explanation = """
#            ACC Event: %s - Event Duration: %s sec
#             """ \
#                   % ('%(acc)s', '%(duration).2f')
#
#     legend_pics = [
#         (EventSummary.stat_im, 'stationary'),
#         (EventSummary.mov_im, 'moving'),
#         (EventSummary.acc_im, 'ACC track'),
#     ]
#
#     extra_modules = [
#         ('view_acc_driver_input@acceval',
#          Client('view_acc_driver_input', '640x700+0+0', 11, 12, cm)),
#         ('view_acc_control@acceval',
#          Client('view_acc_control', '640x700+0+0', 11, 12, cm)),
#     ]
#
#     statuses = ['fillFLR25@aebs.fill']
#     groups = ['FLR25', 'moving', 'stationary', 'stopped']


# class Summary3(ACCSummary):
#     title = " ACC Events Details"
#     explanation = """
#            ACC Event: %s - Event Duration: %s sec
#             """ \
#                   % ('%(acc)s', '%(duration).2f')
#
#     legend_pics = [
#         (EventSummary.stat_im, 'stationary'),
#         (EventSummary.mov_im, 'moving'),
#         (EventSummary.acc_im, 'ACC track'),
#     ]
#
#     extra_modules = [
#         ('view_kinematics@acceval',
#          Client('view_kinematics', '640x700+0+0', 11, 12, cm)),
#         ('view_acc_states@acceval',
#          Client('view_acc_states', '640x700+0+0', 11, 12, cm)),
#     ]
#
#     statuses = ['fillFLR25@aebs.fill']
#     groups = ['FLR25', 'moving', 'stationary', 'stopped']
