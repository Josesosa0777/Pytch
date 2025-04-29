# -*- dataeval: init -*-
import os
import sys
from collections import OrderedDict

from reportlab.platypus import Spacer, PageBreak, Table, FrameBreak, Image,\
                               NextPageTemplate, Frame, PageTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, cm, landscape, A4
from reportlab.pdfbase.pdfmetrics import stringWidth

from interface.Interfaces import iAnalyze
from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, grid_table_style, Paragraph, Link,\
                          get_index_link, superscript

from docgen_bendix_warning import Client, Analyze as iAnalyze, Summary
from analyzeAEBSWarningsSimAndRoadTypes import conv_float, TableDict

class Analyze(iAnalyze):
  def init(self):
    self.view_name = ''
    self.EVENT_LINK = '%s'
    return

  def fill(self):
    batch = self.get_batch()
    self.view_name = batch.create_table_from_last_start()

    story = intro(
      "ECU performance evaluation report",
      """
      This is an automatically generated report, based on ECU processor load and
      cycle time.<br/>
      The results are summarized in the table below, followed by the detailed
      overview of the individual events.<br/>
      """
    )
    story.append(PageBreak())
    story.extend(toc())
    story.append(PageBreak())

    summaries = [
      ProcLoadSummary(batch, self.view_name),
    ]

    avg = PerformanceAvg(self.get_batch(), self.view_name)
    story.extend(self.summaries(summaries, avg))
    story.extend(self.warnings(summaries, avg))
    return story

  def analyze(self, story):
    doc = self.get_doc('dataeval.simple', pagesize=A4)
    addPageTemplates(doc)
    doc.multiBuild(story)
    return

  def summaries(self, summaries, avg):
    story = [
      IndexedParagraph('Processor load summary tables', style='Heading1'),
      Spacer(1.0*cm, 0.5*cm),
      avg.get_table(),
      NextPageTemplate('LandscapeTable'),
    ]
    for summary in summaries:
      story.append(PageBreak())
      story.append(IndexedParagraph(summary.title, style='Heading2'))
      story.append(summary.get_table(link_pattern=self.EVENT_LINK,
                                     link_heading='Heading2',
                                     avg=avg)),
    return story

  def warnings(self, summaries, avg):
    story = [
      PageBreak(),
    ]
    for summary in summaries:
      events = self.events(summary, avg)
      if events:
        story.append(IndexedParagraph(summary.title, style='Heading1'))
        story.extend(events)
        story.extend(self.events(summary, avg))
        story.append(NextPageTemplate('LandscapeTable'))
        story.append(PageBreak())
    return story

  def events(self, summary, avg):
    story = []
    for meas, stat in summary.iteritems():
      if not avg.differ(stat): continue

      # clone manager
      manager = self.clone_manager()
      manager.set_measurement(meas)
      manager.build(summary.modules, show_navigators=False)
      sync = manager.get_sync()

      # capture
      title = self.EVENT_LINK % os.path.basename(meas)
      story.extend([
        NextPageTemplate('Landscape'),
        PageBreak(),
        IndexedParagraph(title, style='Heading2'),
        FrameBreak(),
      ])
      for module_name, client in summary.modules.iteritems():
        # sys.stdout.write('%s:\t' % module_name)
        story.append( client(sync, module_name) )
      manager.close()
    return story


class ProcLoadSummary(Summary):
  title = 'Processor load'
  query = """
        FROM %s en
        JOIN modules ON
             modules.id = en.moduleid

        JOIN measurements ON
             measurements.id = en.measurementid

        JOIN entryintervals ON
             entryintervals.entryid = en.id

        JOIN quantities load_min ON
                        load_min.entry_intervalid = entryintervals.id
        JOIN quanames load_min_names ON
                      load_min_names.id = load_min.nameid
        JOIN quanamegroups load_min_namegroups ON
                           load_min_namegroups.id = load_min_names.groupid

        JOIN quantities load_max ON
                        load_max.entry_intervalid = entryintervals.id
        JOIN quanames load_max_names ON
                      load_max_names.id = load_max.nameid
        JOIN quanamegroups load_max_namegroups ON
                           load_max_namegroups.id = load_max_names.groupid

        JOIN quantities load_avg ON
                        load_avg.entry_intervalid = entryintervals.id
        JOIN quanames load_avg_names ON
                      load_avg_names.id = load_avg.nameid
        JOIN quanamegroups load_avg_namegroups ON
                           load_avg_namegroups.id = load_avg_names.groupid

        JOIN quantities cycle_min ON
                        cycle_min.entry_intervalid = entryintervals.id
        JOIN quanames cycle_min_names ON
                      cycle_min_names.id = cycle_min.nameid
        JOIN quanamegroups cycle_min_namegroups ON
                           cycle_min_namegroups.id = cycle_min_names.groupid

        JOIN quantities cycle_max ON
                        cycle_max.entry_intervalid = entryintervals.id
        JOIN quanames cycle_max_names ON
                      cycle_max_names.id = cycle_max.nameid
        JOIN quanamegroups cycle_max_namegroups ON
                           cycle_max_namegroups.id = cycle_max_names.groupid

        JOIN quantities cycle_avg ON
                        cycle_avg.entry_intervalid = entryintervals.id
        JOIN quanames cycle_avg_names ON
                      cycle_avg_names.id = cycle_avg.nameid
        JOIN quanamegroups cycle_avg_namegroups ON
                           cycle_avg_namegroups.id = cycle_avg_names.groupid

      WHERE modules.class = :class_name
        AND load_min_namegroups.name = :ecu_group
        AND load_min_names.name = :load_min
        AND load_max_namegroups.name = :ecu_group
        AND load_max_names.name = :load_max
        AND load_avg_namegroups.name = :ecu_group
        AND load_avg_names.name = :load_avg
        AND cycle_min_namegroups.name = :ecu_group
        AND cycle_min_names.name = :cycle_min
        AND cycle_max_namegroups.name = :ecu_group
        AND cycle_max_names.name = :cycle_max
        AND cycle_avg_namegroups.name = :ecu_group
        AND cycle_avg_names.name = :cycle_avg

      ORDER BY measurements.basename
  """

  query_filters = dict(
      class_name='dataevalaebs.search_ecu_performance.Search',
      ecu_group='ecu performance',
      load_min='processor load min',
      load_max='processor load max',
      load_avg='processor load avg',
      cycle_min='cycle time min',
      cycle_max='cycle time max',
      cycle_avg='cycle time avg',
  )

  def init(self, batch, view_name):
    data = batch.query(("""
      SELECT IFNULL(measurements.local, measurements.origin),
             load_min.value*100, load_max.value*100, load_avg.value*100,
             cycle_min.value*1000, cycle_max.value*1000, cycle_avg.value*1000
      """ + self.query)% view_name, **self.query_filters)

    for meas, load_min, load_max, load_avg, cycle_min, cycle_max, cycle_avg\
     in data:
      self[meas] = dict(
        load_min=load_min, load_max=load_max, load_avg=load_avg,
        cycle_min=cycle_min, cycle_max=cycle_max, cycle_avg=cycle_avg,
      )

    self.modules.update([
      ('view_proc_load',
       Client('MatplotlibNavigator', '544x595+0+0', 9.35, 10.2, cm)),
      ('view_cycle_time',
       Client('MatplotlibNavigator', '544x595+0+0', 9.35, 10.2, cm)),
      ('view_no_tracks_per_proc_load',
       Client('MatplotlibNavigator', '544x595+0+0', 9.35, 10.2, cm)),
    ])

    self.columns.update([
      ('load_min', 'min'), ('load_max', 'max'), ('load_avg', 'avg'),
      ('cycle_min', 'min'), ('cycle_max', 'max'), ('cycle_avg', 'avg'),
    ])
    return

  def get_data(self, link_pattern, link_heading, avg=None):
    data = [
      ['measurement', 'processor load [%]', '', '', 'cycle time [ms]', '', ''],
    ]
    header = self.columns.values()
    header.insert(0, '')
    data.append(header)
    for meas, stat in self.iteritems():
      basename = os.path.basename(meas)
      row = [conv_float(stat[name]) for name in self.columns]
      if avg.differ(stat):
        # create sub table for link
        # http://xiix.wordpress.com/2008/03/12/a-reportlab-link-in-table-cell-workaround/
        link = get_index_link(link_pattern % basename, link_heading)
        head = Link(link, basename)
      else:
        head = basename
      row.insert(0, Table([[Paragraph(head,
                                      fontSize=self.font_size,
                                      fontName=self.font_name)]],
                          colWidths=self.colWidths))
      data.append(row)
    return data

  def get_style(self):
    style = [
      ('SPAN',   ( 0, 0), ( 0,  1)),
      ('SPAN',   ( 1, 0), ( 3,  0)),
      ('SPAN',   ( 4, 0), ( 6,  0)),
      ('GRID',   ( 0, 0), (-1, -1), 0.025*cm, colors.black),
      ('FONT',   ( 0, 0), (-1,  0), '%s-Bold' % self.font_name, self.font_size),
      ('FONT',   ( 0, 1), (-1, -1), self.font_name, self.font_size),
      ('ALIGN',  ( 0, 1), (-1, -1), 'CENTER'),
      ('VALIGN', ( 0, 1), (-1, -1), 'MIDDLE'),
    ]
    return style


class PerformanceAvg(TableDict):
  def __init__(self, batch, view_name):
    TableDict.__init__(self)
    data = batch.query(("""
      SELECT AVG(load_min.value)*100, AVG(load_max.value)*100,
             AVG(load_avg.value)*100,

             AVG(cycle_min.value)*1000, AVG(cycle_max.value)*1000,
             AVG(cycle_avg.value)*1000
      """ + ProcLoadSummary.query)% view_name, **ProcLoadSummary.query_filters)
    keys = 'load_min', 'load_max', 'load_avg',\
            'cycle_min', 'cycle_max', 'cycle_avg'
    data, = data
    self.update(zip(keys, data))
    return

  def get_data(self):
    data = [
      ['processor load [%]', '', '', 'cycle time [ms]', '', ''],
      ['min', 'max', 'avg',          'min', 'max', 'avg']
    ]
    data.append([conv_float(v) for v in self.values()])
    return data

  def get_style(self):
    style = [
      ('SPAN',   ( 0, 0), ( 2,  0)),
      ('SPAN',   ( 3, 0), ( 5,  0)),
      ('GRID',   ( 0, 0), (-1, -1), 0.025*cm, colors.black),
      ('ALIGN',  ( 0, 0), (-1, -1), 'CENTER'),
      ('VALIGN', ( 0, 0), (-1, -1), 'MIDDLE'),
    ]
    return style

  def differ(self, other):
    if other['load_max'] > 95: return True
    for key, value in self.iteritems():
      margin = 0.2 * value
      other_value = other[key]
      if other_value < value - margin or other_value > value + margin:
        return True
    return False

def addPageTemplates(doc):
  x, y, width, height = doc.getGeom()
  ext_x, ext_y, ext_width, ext_height = doc.getExtGeom()
  app_x, app_y, app_width, app_height = doc.getAppGeom()

  portrait_frames = [
    Frame(ext_x, y, ext_width, height, id='FullPage'),
  ]
  landscape_frames = [
    Frame(ext_y,                  x + 0.9*width,      ext_height, 0.1*width, id='Title'),
    Frame(ext_y,                  x + 0.8*width,      ext_height, 0.1*width, id='Duartion'),
    Frame(ext_y,                  x,              1./3*ext_height, 0.8*width, id='ProcLoad'),
    Frame(ext_y + 1./3*ext_height, x,             1./3*ext_height, 0.8*width, id='CycleTime'),
    Frame(ext_y + 2./3*ext_height, x,             1./3*ext_height, 0.8*width, id='TargetPlot'),
  ]
  landscape_table_frames = [
    Frame(y, x, height, width, id='FullPage'),
  ]

  doc.addPageTemplates([
    PageTemplate(id='Portrait', frames=portrait_frames,
                 onPage=doc.onPortraitPage, pagesize=A4),
    PageTemplate(id='Landscape', frames=landscape_frames,
                 onPage=doc.onLandscapePage, pagesize=landscape(A4)),
    PageTemplate(id='LandscapeTable', frames=landscape_table_frames,
                 onPage=doc.onLandscapePage, pagesize=landscape(A4)),
  ])
  return

