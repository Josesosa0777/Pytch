# -*- dataeval: init -*-

import os

import matplotlib

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from reportlab.platypus import Image, Spacer, PageBreak, NextPageTemplate, FrameBreak
from reportlab.lib.pagesizes import cm

from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph, italic, bold
from pyutils.math import round2
from config.interval_header import cIntervalHeader

from aebs.par import aebs_classif
from reportgen.common.analyze import Analyze
from reportgen.common.summaries import EventSummary
from reportgen.common.clients import VideoNavigator, TableNavigator, Client
from reportgen.common.utils import vector2scalar

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

AEBS_TABLE = None


class AebsAnalyze(Analyze):
	optdep = dict(
		aebs_events='analyze_kpi_events_resim-last_entries@tsreval',
		count_vs_aebs_severity='view_count_vs_severity_stats_flr25-print_mergedcount@aebseval.classif',
		dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
		dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
		dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
	)

	query_files = {
		'aebs_events': abspath('../../tsreval/events_inttable_kpi_resim.sql'),
	}

	def fill(self):
		self.view_name = self.batch.create_table_from_last_entries(
			start_date=self.start_date, end_date=self.end_date)

		story = intro(
			"Conti TSR RESIM field test evaluation report",
			"""
			This is an automatically generated report, based on field tests with
			simultaneously measured camera (MFC525)	sensor.<br/>
			<br/>
			The output signals of Conti TSR are analyzed with ground truth data(Postmarker Tool) and the
			relevant events are collected in this report.<br/>
			Statistical results are presented first, followed by the detailed
			overview of the individual events.<br/>
			"""
		)
		# Set Event Details Page size
		story += [Paragraph('Event details pagesize is: %s' % "A3-TSR")]

		story.append(PageBreak())
		story.extend(toc())
		story.append(PageBreak())

		story.extend(self.overall_summary())
		summaries = [TSRSummary(self.batch, self.view_name)]
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
			# story.append(IndexedParagraph(summary.title, style='Heading1'))
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
				global AEBS_TABLE
				AEBS_TABLE = table

				tot_aebs = len(table)
				story += [Paragraph('Total number of TSR events: %d' % tot_aebs)]
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
			story += [Paragraph('Total True Positive: {}'.format(AEBS_TABLE[0]['TP'])),
					  Paragraph('Total False Positive: {}'.format(AEBS_TABLE[0]['FP'])),
					  Paragraph('Total False Negative: {}'.format(AEBS_TABLE[0]['FN']))]

			ptext = """Confusion Matrix\n"""
			confusion_matrix_path = os.path.splitext(AEBS_TABLE[0]['fullmeas'])[0] + ".png"
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
		data = AEBS_TABLE

		for row in data:
			self.setdefault(row['fullmeas'], []).append(dict(
				start=row['start [s]'],
				end=row['start [s]'] + row['duration [s]'],
				duration=row['duration [s]'],
				phase=vector2scalar(row['Event']),
				signclass=row['Sign class ID'],
				TP=row['TP'],
				FP=row['FP'],
				FN=row['FN'],
				conti_uid=row['conti_uid'],
				rating=vector2scalar(row['warning rating scale']),
				cause=aebs_classif.label2maingroup.get(vector2scalar(row['warning cause'])),
			))
		# view_tsr_can_signals
		self.modules.update([
			('view_nxtvideoeventgrabbernav_lanes-NO_LANES@evaltools',
			 VideoNavigator('VideoNavigator', '700x700+0+0', 12, 12, cm)),
			# ('view_tracknav_lanes-NO_LANES@evaltools',
			#  TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
			('view_postmarker_traffic_data-REPORT@tsreval',
			 TableNavigator('view_postmarker_traffic_data', '640x300+0+0', 11, 5.5, cm)),
			('view_conti_tsr_data-REPORT@tsreval',
			 TableNavigator('view_postmarker_traffic_data', '640x300+0+0', 11, 5.5, cm)),
		])

		self.columns.update([
			('start', 'Start\n[s]\n'),
			('phase', 'Event\n\n'),
			('conti_uid', 'Conti UID\n\n'),
			('signclass', 'SignID\n'),
		])
		return


class TSRSummary(AebsSummary):
	title = "TSR event details"
	explanation = """Event: %s, Event time: %s, Conti UID: %s""" % ('%(phase)s', '%(start)s', '%(conti_uid)s')

	statuses = ['fillFLC25_TSR@aebs.fill']
	groups = ['FLC25_TSR']


if __name__ == '__main__':
	from reportgen.common.main import main

	main(os.path.abspath(__file__))
