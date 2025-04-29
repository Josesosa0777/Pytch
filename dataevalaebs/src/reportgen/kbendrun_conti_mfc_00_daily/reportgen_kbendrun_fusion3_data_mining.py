# -*- dataeval: init -*-
import os

import matplotlib
import copy
from reportgen.kbendrun_conti_00_daily.reportgen_kbendrun_conti_daily import RESET_TABLE
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
from reportgen.common.summaries import EventSummary, Summary, PIC_DIR
from reportgen.common.clients import Client, TrackNavigator, VideoNavigator
from reportgen.common.utils import vector2scalar
from aebs.fill.calc_radar_aebs_phases import Calc as Flr25Calc

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

RESET_TABLE = None

class AebsAnalyze(Analyze):
	optdep = dict(
		data_mining_events='analyze_fdf_f3p0_fda_low_speed-last_entries@mfc525eval.datamining',
		dur_vs_roadtype='view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
		dist_vs_roadtype='view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
		dur_vs_engine_onoff='view_quantity_vs_onoff_stats-print_duration@egoeval.enginestate',
		dur_vs_daytime='view_quantity_vs_daytime_stats-print_duration@mfc525eval.daytime',
	)

	query_files = {
		'data_mining_events': abspath('../../mfc525eval/datamining/data_mining.sql'),
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
		fault_summaries = [DataMiningTimeline(self.batch, self.view_name)]
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
				
			# Radar Reset event table
			if (self.optdep['data_mining_events'] in self.passed_optdep):
				reset_ei_ids = index_fill(self.modules.fill(self.optdep['data_mining_events']))
				header1 = cIntervalHeader.fromFileName(self.query_files['data_mining_events'])
				camera_table_internal = self.batch.get_table_dict(header1, reset_ei_ids, sortby = [('measurement', True), ('start [s]', True)])
				global RESET_TABLE
				RESET_TABLE = camera_table_internal

			
			story.append(Spacer(width = 1 * cm, height = 0.5 * cm))
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

	def events(self, summary):
		statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
		statuses.extend(summary.statuses)
		groups = ['FLC25', 'moving', 'stationary', 'stopped']
		groups.extend(summary.groups)

		story = summary.get_tracknav_legend()

		
		return story


class DataMiningTimeline(Summary):
		def init(self, batch, view_name):
				data = RESET_TABLE
				self.title = 'Data mining details'
				for row in data:
						self.setdefault(row['fullmeas'], []).append(dict(
										start = row['start [s]'],
										comment = row['comment']
						))

				self.columns.update([
						('start', 'start [s]\n'),
						('comment', 'Comment\n'),
				])
				return

		def get_data(self, link_pattern, link_heading):
				header = self.columns.values()
				header.insert(0, 'measurement')
				data = [header]
				for meas, events in self.iteritems():
					basename = os.path.basename(meas)
					for event in events:
						row = [basename, event['start'], event['comment']]
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


if __name__ == '__main__':
	from reportgen.common.main import main
	main(os.path.abspath(__file__))
