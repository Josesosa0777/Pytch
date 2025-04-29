# -*- dataeval: init -*-
import os
import csv

import matplotlib
import copy
from primitives.egomotion import EgoMotion
from reportgen.kbendrun_conti_00_daily.reportgen_kbendrun_conti_daily import RESET_TABLE
matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from reportlab.lib import colors
from reportlab.platypus import Image, Spacer, PageBreak, Table, NextPageTemplate, FrameBreak
from reportlab.lib.pagesizes import cm
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.lib.pagesizes import A4, A3, landscape

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

USECASE_EVAL_TABLE = None
RESET_TABLE = None
AEBS_TABLE = None

query_files = {
	'expectedDistances': abspath('../../mfc525eval/objecteval/expectedDistances.csv'),
}
title = "AEBS event details"
reader = csv.DictReader(open(query_files['expectedDistances']),delimiter = ';')
global dictExpectedWarnings
dictExpectedWarnings = {}
for row in reader:
	key = row.pop('velocity_kmh')
	dictExpectedWarnings[key] = row

class AebsAnalyze(Analyze):
	optdep = dict(
		aebs_usecase_eval='analyze_flc25_aebs_usecase_eval-last_entries@mfc525eval.objecteval',
	)

	query_files = {
		'aebs_usecase_eval': abspath('../../mfc525eval/objecteval/flc25_aebs_usecase_eval_inittable.sql'),
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
		story += [Paragraph('Event details pagesize is: %s' % "AEBS-Usecase")]
		story.append(PageBreak())
		story.extend(toc())
		story.append(PageBreak())
		story += [NextPageTemplate('LandscapeTable')]
		story.extend(self.overall_summary())

		summaries = [Flr25Summary(self.batch, self.view_name)]
		story.extend(self.summaries(summaries))
		story.extend(self.warnings(summaries))

		fault_summaries = [DataMiningTimeline(self.batch, self.view_name)]
		story.extend(self.faults(fault_summaries))
		return story

	def overall_summary(self):
		def one_summary(story, start_date, end_date, index_fill):
			if start_date != end_date and start_date == '2000-01-01' and end_date == '2050-01-01':
				start_date, end_date = self.batch.get_measdate()
			# Radar Reset event table
			if (self.optdep['aebs_usecase_eval'] in self.passed_optdep):
				reset_ei_ids = index_fill(self.modules.fill(self.optdep['aebs_usecase_eval']))
				header1 = cIntervalHeader.fromFileName(self.query_files['aebs_usecase_eval'])
				camera_table_internal = self.batch.get_table_dict(header1, reset_ei_ids, sortby = [('measurement', True), ('start [s]', True)])
				global USECASE_EVAL_TABLE
				USECASE_EVAL_TABLE = camera_table_internal

			# AEBS warning rate
			if (self.optdep['aebs_usecase_eval'] in self.passed_optdep):
				aebs_ei_ids = index_fill(self.modules.fill(self.optdep['aebs_usecase_eval']))
				header = cIntervalHeader.fromFileName(self.query_files['aebs_usecase_eval'])
				table = self.batch.get_table_dict(header, aebs_ei_ids, sortby=[('measurement', True), ('start [s]', True)])
				global AEBS_TABLE
				AEBS_TABLE = table

			story.append(Spacer(width = 1 * cm, height = 0.5 * cm))
		
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
						IndexedParagraph('AEBS overview', style='Heading1'),
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

	# def warnings(self, summaries):
	# 		story = []
	# 		for summary in summaries:
	# 			story.append(IndexedParagraph(summary.title, style='Heading1'))
	# 			story.extend(self.events(summary))
	# 			story.append(NextPageTemplate('LandscapeTable'))
	# 			story.append(PageBreak())
	# 		return story

	def events(self, summary):
		statuses = ['fillFLR20@aebs.fill']
		statuses.extend(summary.statuses)
		groups = ['FLR20', 'moving', 'stationary']
		groups.extend(summary.groups)

		story = summary.get_tracknav_legend()

		for meas, warnings in summary.iteritems():
			manager = self.clone_manager()
			manager.strong_time_check = False  # TODO: make default behavior with warning
			manager.set_measurement(meas)
			modules_in_event = copy.deepcopy(summary.modules)
			manager.build(modules_in_event, status_names=statuses,
										visible_group_names=groups, show_navigators=False)
			sync = manager.get_sync()
			for warning in warnings:
				warning['target_vx_at_warning'] = warning['ego_vx_at_warning']+warning['aebs_obj_vx_at_warning']*3.6
				warning['Diff_vel_ego_target']= warning['ego_vx_at_warning'] - warning['target_vx_at_warning']
				warning['exp_warn_dx'] = float(dictExpectedWarnings[str(int(warning['Diff_vel_ego_target']))]['d_warn_m'])
				warning['exp_pb_dx'] = float(dictExpectedWarnings[str(int(warning['Diff_vel_ego_target']))]['d_pb_m'])
				warning['exp_eb_dx'] = float(dictExpectedWarnings[str(int(warning['Diff_vel_ego_target']))]['d_eb_m'])
				warning['exp_dx_secure'] = float(dictExpectedWarnings[str(int(warning['Diff_vel_ego_target']))]['dx_secure_m'])
				if (warning['dx_stopping']<998)&(warning['ego_vx_stopping']<0.5): 
					warning['evaluated_dx_stopping']=warning['dx_stopping']	
				else:
					warning['evaluated_dx_stopping']=999	

				title = self.EVENT_LINK % (os.path.basename(meas), warning['start'])
				story.extend([
					NextPageTemplate(self.warningtemplate),
					PageBreak(),
					IndexedParagraph(title, style='Heading2'),
					FrameBreak(),
					Paragraph(summary.explanation % warning, style='Normal'),
				])
				sync.seek(warning['start'])
				manager.set_roi(max(warning['t_warning']-15,warning['start']), warning['end'], color='w',
												pre_offset=0, post_offset=0)
				for module_name, client in summary.modules.iteritems():
					story.append( client(sync, module_name) )
					story.append( FrameBreak() )
				if summary.modules: story.pop(-1)  # remove last FrameBreak
			manager.close()
		return story


class DataMiningTimeline(Summary):
		def init(self, batch, view_name):
				data = USECASE_EVAL_TABLE
				self.title = 'AEBS UseCase details'
				for row in data:
						self.setdefault(row['fullmeas'], []).append(dict(
										ego_vx_at_warning = row['ego_vx_at_warning'],
										aebs_obj_vx_at_warning = row['aebs_obj_vx_at_warning'],
										dx_warning = row['dx_warning'],
										dx_braking = row['dx_braking'],
										dx_emergency = row['dx_emergency'],
										t_warning = row['t_warning'],
										dx_stopping = row['dx_stopping'],
										ego_vx_stopping = row['ego_vx_stopping'],
										comment = row['comment']
						))

				# add here title for table (needs to match with content below)
				self.columns.update([
						('ego_vx_at_warning', 'ego_vx\nkm/h'),
						('aebs_obj_vx_at_warning', 'target_vx\nkm/h'),
						('dx_warning', 'actual\ndx_warning\nm'),
						('exp_dx_warning', 'expected\ndx_warning\nm'),
						('dx_braking', 'actual\ndx_pb\nm'),
						('exp_dx_braking', 'expected\ndx_pb\nm'),
						('dx_emergency', 'actual\ndx_eb\nm'),
						('exp_dx_emergency', 'expected\ndx_eb\nm'),
						('evaluated_dx_stopping', 'actual\ndx_stop\nm'),
						('comment', 'Verdict\n'),
				])
				return

		def get_data(self, link_pattern, link_heading):
				header = self.columns.values()
				header.insert(0, 'measurement')
				data = [header]
				for meas, events in self.iteritems():
					basename = os.path.basename(meas)
					for event in events:
						myEvent ={}
						myEvent['target_vx_at_warning'] = event['ego_vx_at_warning']+event['aebs_obj_vx_at_warning']*3.6
						myEvent['Diff_vel_ego_target']= event['ego_vx_at_warning'] - myEvent['target_vx_at_warning']
						myEvent['exp_warn_dx'] = float(dictExpectedWarnings[str(int(myEvent['Diff_vel_ego_target']))]['d_warn_m'])
						myEvent['exp_pb_dx'] = float(dictExpectedWarnings[str(int(myEvent['Diff_vel_ego_target']))]['d_pb_m'])
						myEvent['exp_eb_dx'] = float(dictExpectedWarnings[str(int(myEvent['Diff_vel_ego_target']))]['d_eb_m'])
						myEvent['exp_dx_secure'] = float(dictExpectedWarnings[str(int(myEvent['Diff_vel_ego_target']))]['dx_secure_m'])
						if (event['dx_stopping']<998)&(event['ego_vx_stopping']<0.5): 
							myEvent['evaluated_dx_stopping']=event['dx_stopping']	
						else:
							myEvent['evaluated_dx_stopping']=999

						# add here content for table (needs to match with titles)
						row = [basename,
						round(event['ego_vx_at_warning'],1), 
						round(myEvent['target_vx_at_warning'],1), 
						round(event['dx_warning'],1), 
						round(myEvent['exp_warn_dx'],1),
						round(event['dx_braking'],1), 
						round(myEvent['exp_pb_dx'],1),
						round(event['dx_emergency'],1), 
						round(myEvent['exp_eb_dx'],1),
						round(myEvent['evaluated_dx_stopping'],1),
						event['comment']]
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

class AebsSummary(EventSummary):
	def init(self, batch, view_name):
		data = AEBS_TABLE
		
		for row in data:
			self.setdefault(row['fullmeas'], []).append(dict(
				start=row['start [s]'],
				end=row['start [s]']+row['duration [s]'],
				duration=row['duration [s]'],
				ego_vx_at_warning=row['ego_vx_at_warning'],
				aebs_obj_vx_at_warning=row['aebs_obj_vx_at_warning'],
				dx_warning=row['dx_warning'],
				dx_braking=row['dx_braking'],
				dx_emergency=row['dx_emergency'],		
				t_warning = row['t_warning'],
				dx_stopping = row['dx_stopping'],
				ego_vx_stopping = row['ego_vx_stopping']
				#exp_warn = row['exp_warn'] 
			))

		self.modules.update([
		])

		self.columns.update([
			('start', 'start\n[s]\n'),
			('duration', 'duration\n[s]\n'),
			('ego_vx_at_warning','ego_vx_at_warning\n'),
			('aebs_obj_vx_at_warning','aebs_obj_vx_at_warning\n'),
			('dx_warning','dx_warning\n'),
			('dx_braking','dx_braking\n'),
			('dx_emergency','dx_emergency\n'),
			('t_warning','t_warning\n'),
		])
		return

class Flr25Summary(AebsSummary):
	explanation = """
	Ego velocity: %s km/h, target velocity: %s km/h,  <br/>
	Warning at %s m (Exp: %s m), Partial Brake at %s m (Exp: %s m), Emergency Brake at %s m (Exp: %s m), Stopping Distance: %s m (Exp: %s m) 
	"""\
	% ('%(ego_vx_at_warning).0f','%(target_vx_at_warning).0f','%(dx_warning).2f','%(exp_warn_dx).2f','%(dx_braking).2f','%(exp_pb_dx).2f','%(dx_emergency).2f','%(exp_eb_dx).2f','%(evaluated_dx_stopping).2f','%(exp_dx_secure).2f')

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
			('view_aebs_usecase@mfc525eval.objecteval',
		 	Client('AEBS_usecase_plot', '1283x700+0+0', 22, 12, cm)),
	]
	statuses = ['fillFLC25_AOA_AEBS@aebs.fill']
	groups = ['FLC25_AOA_AEBS']

def addPageTemplates(doc):
	print ("Called the overwritten pagetemplate")
	x, y, width, height = doc.getGeom()
	ext_x, ext_y, ext_width, ext_height = doc.getGeom()

	_showBoundary = 0

	portrait_frames = [
		Frame(ext_x, y, ext_width, height, id='FullPage')
	]

	landscape_frames = [
		Frame(ext_y, x + 0.9 * width, ext_height, 0.1 * width, id='Title'),
		Frame(ext_y, x + 0.8 * width, ext_height, 0.1 * width, id='Duartion'),
		Frame(ext_y, x + 0.5 * width, 0.2 * ext_height, 0.3 * width, id='VideoNav'),
		#Frame(ext_y, x, 0.2 * ext_height, 0.5 * width, id='TrackNav'),
		Frame(ext_y, x, 1*ext_height, 0.8*width, id='EgoPlot'),
		Frame(ext_y + 0.6 * ext_height, x, 0.4 * ext_height, 0.8 * width, id='TargetPlot'),
		Frame(ext_y + 1 * ext_height, x, 0.4 * ext_height, 0.8 * width, id='VehiclePlot'),
	]

	landscape_table_frames = [
		Frame(y, x, height, width, id='FullPage'),
	]

	doc.addPageTemplates([
		PageTemplate(id='Portrait', frames=portrait_frames, onPage=doc.onPortraitPage, pagesize=A4),
		PageTemplate(id='Landscape', frames=landscape_frames, onPage=doc.onLandscapePage, pagesize=landscape(A4)),
		PageTemplate(id='LandscapeTable', frames=landscape_table_frames, onPage=doc.onLandscapePage, pagesize=landscape(A4)),
		])

	return

if __name__ == '__main__':
	from reportgen.common.main import main
	main(os.path.abspath(__file__))
