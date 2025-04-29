# -*- dataeval: init -*-

import os

import matplotlib
from collections import OrderedDict
matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from reportlab.platypus import PageBreak, Table
from reportlab.lib.pagesizes import cm

from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph
from config.interval_header import cIntervalHeader

from reportgen.common.analyze import Analyze
from reportgen.common.clients import TrackNavigator, VideoNavigator

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

class ReportGenExample(Analyze):
  def fill(self):
    ###
    ### create title page
    ###
    story = intro(
      "Lorem Ipsum Title",
      """
      Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy
      eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam
      voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet
      clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit
      amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam
      nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
      sed diam voluptua. At vero eos et accusam et justo duo dolores et ea
      rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem
      ipsum dolor sit amet.
      """
    )
    story += [PageBreak()]
    
    ###
    ### insert table of contents
    ###
    story += toc()
    story += [PageBreak()]
    
    ###
    ### create a table with the list of events
    ###
    ei_ids, intval_header = self._get_table_def("aebseval.search_events.Search")
    # get query results in a table in a dictionary form
    table_data_dict = self.batch.get_table_dict(intval_header, ei_ids,
      sortby=[('measurement', True), ('start [s]', True)])
    # re-create the table only with a subset of the columns
    needed_cols = ['entry', 'measurement', 'start [s]', 'duration [s]']
    table_data = [[row[j] for j in needed_cols] for row in table_data_dict]
    table_data.insert(0, needed_cols)  # add header
    # add table to the document
    story += [IndexedParagraph("First Heading", style='Heading1')]
    story += [Table(table_data)]
    story += [PageBreak()]

    ###
    ### insert one detailed page for each event
    ###
    story += [IndexedParagraph("Second Heading", style='Heading1')]
    # define view modules to be run for each event
    modules = OrderedDict([
      ('view_videonav_lanes-FLC20@evaltools',
       VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
      ('view_tracknav_lanes-FLC20@evaltools',
       TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
    ])
    # create detail pages
    for row in table_data_dict:
      story += self._get_detailed_page(row, modules)
    return story
  
  def _get_table_def(self, search_class):
    # create an sql 'view' with the last entries only
    entries_view = self.batch.create_table_from_last_entries(
      start_date=self.start_date, end_date=self.end_date)
    # filter for the given entries (i.e. construct the rows)
    ei_ids = self.batch.query("""
      SELECT ei.id FROM entryintervals AS ei
      JOIN %(entries)s AS en ON en.id = ei.entryid
      JOIN modules AS mo ON mo.id = en.moduleid
      WHERE mo.class = "%(mo_class)s"
    """ % dict(
      entries=entries_view,
      mo_class=search_class,
    ))
    ei_ids = [ei_id for ei_id, in ei_ids]
    # query given attributes for each event (i.e. construct the columns)
    intval_header = cIntervalHeader.fromString("""
      --$entry
      --!TITLE
      --$fullmeas
      --!FULLMEAS
      --$measurement
      --!MEAS
      --$start [s]
      --!STARTTIME
      --$end [s]
      --!ENDTIME
      --$duration [s]
      --!DURATION
      --$comment
      --!COMMENT
    """)
    return ei_ids, intval_header

  def _get_detailed_page(self, row, modules):
    # set up the framework for the actual event
    manager = self.clone_manager()
    manager.strong_time_check = False
    manager.set_measurement(row['fullmeas'])
    statuses = ['fillFLR20@aebs.fill']
    groups = ['FLR20', 'moving', 'stationary']
    manager.build(modules, status_names=statuses,
                  visible_group_names=groups, show_navigators=False)
    sync = manager.get_sync()
    sync.seek(row['start [s]'])
    manager.set_roi(row['start [s]'], row['end [s]'], color='y',
                    pre_offset=5.0, post_offset=5.0)
    
    # add content to the document
    story = []
    story += [IndexedParagraph("Sub-Heading", style='Heading2')]
    story += [Paragraph("Some explanation goes here.")]
    for module_name, client in modules.iteritems():
      story += [client(sync, module_name)]
    story += [PageBreak()]
    
    # restore framework
    manager.close()
    
    # return content
    return story

if __name__ == '__main__':
  from reportgen.common.main import main
  main(os.path.abspath(__file__))
