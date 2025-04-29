# -*- dataeval: init -*-

import os
import matplotlib
from measproc.batchsqlite import str_cell

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError

from reportlab.platypus import Spacer, PageBreak
from reportlab.lib.pagesizes import cm

from datalab.story import toc, intro
from datalab.tygra import IndexedParagraph, Paragraph, italic, Table
from pyutils.math import round2
from config.interval_header import cIntervalHeader
from reportgen.common.analyze import Analyze

abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))

LDWS_TABLE = None


class LdwsShortAnalyze(Analyze):
  optdep = {
    # TODO change analyze_events_merged
    'ldws_events': 'analyze_events-last_entries@ldwseval',
    'dur_vs_roadtype': 'view_quantity_vs_roadtype_stats-print_duration@egoeval.roadtypes',
    'dist_vs_roadtype': 'view_quantity_vs_roadtype_stats-print_mileage@egoeval.roadtypes',
    'dur_vs_inlane_tr0': 'view_quantity_vs_inlane_flr20_tr0_stats-print_duration@trackeval.inlane',
  }
  
  query_files = {
    'ldws_events': abspath('../../ldwseval/events_inttable.sql'),
  }
  
  def __init__(self, *args, **kwargs):
    super(LdwsShortAnalyze, self).__init__(*args, **kwargs)
    self.table = None  # For extended report generation, LdwsAnalayze needs the database dict
  
  def fill(self, **kwargs):
    self.view_name = self.batch.create_table_from_last_entries(
      start_date=self.start_date, end_date=self.end_date)

    story = intro(
      "LDWS field test evaluation report",
      """
      This is an automatically generated report, based on field tests with
      forward-looking camera (FLC20)
      sensor.<br/>
      <br/>
      The output signals of LDWS are analyzed and the
      relevant events are collected in this report.<br/>
      Statistical results are presented first, followed by the detailed
      overview of the individual events.<br/>
      """
    )
    story.append(PageBreak())

    story.extend(self.overall_summary())

    return story

  def overall_summary(self):
    def one_summary(story, start_date, end_date, index_fill):
      # analyzed period - TODO: determine from measurement dates if not specified
      if start_date is not None and end_date is not None:
        from_to = '%s - %s' % (start_date, end_date)
      elif start_date is None and end_date is None:
        from_to = 'whole duration'
      elif start_date is None:
        from_to = 'until %s' % end_date
      else:  # end_date is None:
        from_to = 'from %s' % start_date
      story += [IndexedParagraph('Basic Statistics', style='Heading2')]
      story += [Paragraph('Analyzed time period: %s' % from_to),
                Spacer(width=1*cm, height=0.2*cm),]
      
      # driven distance and duration
      if (self.optdep['dur_vs_roadtype'] in self.passed_optdep and 
          self.optdep['dist_vs_roadtype'] in self.passed_optdep):
        roadt_dur = index_fill(self.modules.fill(self.optdep['dur_vs_roadtype']))
        roadt_dist = index_fill(self.modules.fill(self.optdep['dist_vs_roadtype']))
        
        story += [
          Paragraph('Total duration of measurements: %.1f hours' % roadt_dur.total)]
        
        if roadt_dist.total > 0.0:
          calc_dist_perc = lambda d: int(round2(d/roadt_dist.total*100.0, 5.0))
          story += [Paragraph(
            'Total mileage: <b>%.1f km</b> (ca. %d%% city, %d%% rural, %d%% highway)'%
            (roadt_dist.total,
             calc_dist_perc(roadt_dist['city']),
             calc_dist_perc(roadt_dist['rural']),
             calc_dist_perc(roadt_dist['highway']))),
            Paragraph(italic('Remark: Road type distribution is over distance. '
                             'Percentage values are '
                             'rounded to nearest 5.'), fontsize=8),
            Spacer(width=1*cm, height=0.2*cm),]
        else:
          story += [Paragraph('Total mileage: <b>%.1f km</b>' % roadt_dist.total),
                    Spacer(width=1*cm, height=0.2*cm),]
      else:
        self.logger.warning('Road type statistics not available')
        story += [Paragraph('Total duration of measurements: n/a'),
                  Paragraph('Total mileage: n/a'),
                  Spacer(width=1*cm, height=0.2*cm),]
      
      # LDWS warning rate
      if self.optdep['ldws_events'] in self.passed_optdep:
        ldws_ei_ids = index_fill(self.modules.fill(self.optdep['ldws_events']))
        header = cIntervalHeader.fromFileName(self.query_files['ldws_events'])
        table = self.batch.get_table_dict(header, ldws_ei_ids, sortby=[('measurement', True), ('start [s]', True)],
                                          cell_formatter=str_cell)
        self.table = table

        tot_ldws = len(table)
        story += [IndexedParagraph('LDWS Events', style='Heading2')]
        story += [Paragraph('Total number of LDWS events: %d' % tot_ldws)]
        if 'roadt_dist' in locals() and roadt_dist.total > 0.0:
          tot_rate = float(tot_ldws)/roadt_dist.total * 1000.0
          story += [Paragraph('LDWS warning rate: <b>%.1f events / 1000 km</b>' % tot_rate),
                    Spacer(width=1*cm, height=0.2*cm),]

          # Collect data for table
          lw = 0  # left warning
          rw = 0  # right warning
          lwlc = 0  # left with lane change
          rwlc = 0  # right with lane change
          for row in table:
            if row['side'] == 'left':
              lw += 1
            elif row['side'] == 'right':
              rw += 1
            if row['maneuver'] == 'left lane change':
              lwlc += 1
            elif row['maneuver'] == 'right lane change':
              rwlc += 1

          l_p = "{:.1f}%".format(100.0 * lw / tot_ldws) if lw > 0 and tot_ldws > 0 else "-"  # percentage
          lwnlc_p = "{:.1f}%".format(100.0 * (lw - lwlc) / lw) if lw > 0 else "-"  # percentage
          lwlc_p = "{:.1f}%".format(100.0 * lwlc / lw) if lw > 0 else "-"  # percentage
          r_p = "{:.1f}%".format(100.0 * rw / tot_ldws) if rw > 0 and tot_ldws > 0 else "-"  # percentage
          rwnlc_p = "{:.1f}%".format(100.0 * (rw - rwlc) / rw) if rw > 0 else "-"  # percentage
          rwlc_p = "{:.1f}%".format(100.0 * rwlc / rw) if rw > 0 else "-"  # percentage

          data = [['LDWS warning at left side', str(lw), l_p],
                  ['Without a lane change', str(lw - lwlc), lwnlc_p],
                  ['With a lane change', str(lwlc), lwlc_p],
                  ['LDWS warning at right side', str(rw), r_p],
                  ['Without a lane change', str(rw - rwlc), rwnlc_p],
                  ['With a lane change', str(rwlc), rwlc_p]]

          table_styles = []
          table_styles += [('GRID', (0, 0), (-1, -1), 0.25, (0.0, 0.0, 0.0))]
          table_styles += [('BOX', (0, 0), (-1, 2), 1, (0.0, 0.0, 0.0))]
          table_styles += [('BOX', (0, 3), (-1, -1), 1, (0.0, 0.0, 0.0))]
          table_styles += [('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]
          table_styles += [('ALIGN', (1, 0), (-1, -1), 'CENTER')]
          text_style = dict()
          text_style['bold'] = True
          table_styles += [('TEXT_STYLE', (0, 0), (-1, 0), text_style)]
          table_styles += [('TEXT_STYLE', (0, 3), (-1, 3), text_style)]
          col_widths = [200, 50, 50]
          story += [Table(data, style=table_styles, colWidths=col_widths)]
        else:
          story += [Paragraph('LDWS warning rate: n/a'),
                    Spacer(width=1*cm, height=0.2*cm),]
      else:
        story += [Paragraph('Total number of LDWS events: n/a'),
                  Paragraph('LDWS warning rate: n/a'),
                  Spacer(width=1*cm, height=0.2*cm),]

      # system performance
      firs_pie = self.module_plot(
        "view_quantity_vs_systemstate_maingroup_stats-pie_duration@ldwseval.systemstate",
        windgeom="250x200+0+0", width=60.0, height=60.0, unit=1.0, kind='%',
        overwrite_start_end=True, start_date=start_date, end_date=end_date)
      second_pie = self.module_plot(
        "view_quantity_vs_sensorstatus_maingroup_stats-pie_duration@flc20eval.sensorstatus",
        windgeom="250x200+0+0", width=60.0, height=60.0, unit=1.0, kind='%',
        overwrite_start_end=True, start_date=start_date, end_date=end_date)
      story += [IndexedParagraph('System Availability', style='Heading2')]
      story += [Table([[firs_pie, second_pie]])]
      # story += [PageBreak()]  Removed this page break - there is a blank legend page
      story += [Spacer(width=1*cm, height=2*cm)]
      return

    story = []
    story += [IndexedParagraph('Cumulative Results', style='Heading1')]
    index_fill = lambda fill: fill.all
    one_summary(story, self.start_date, self.end_date, index_fill)
    # comment to test redmine
    if 'summarycomment' in self.global_params:
      story += [Spacer(width=1*cm, height=0.2*cm),
                Paragraph("""
                  No false LDWS warnings are detected without objects.<br/>
                  Most of the warnings are caused by traffic situation with the risk of collision.<br/>
                  The overall system availability is very high while the warning rate is very low - <b>LDWS behaves as expected</b>.<br/>
                  See details in the following chapters.
                  """),
                Spacer(width=1*cm, height=0.2*cm),]
    
    if 'datelist' in self.global_params:
      story += [IndexedParagraph('Latest results', style='Heading1')]
      index_fill = lambda fill: fill.values()[-1]
      middatelist = self.global_params.get('datelist', "").split()
      one_summary(story, middatelist[-1], self.end_date, index_fill)

    return story


if __name__ == '__main__':
  from reportgen.common.main import main
  main(os.path.abspath(__file__))
