# -*- dataeval: init -*-

import os
import matplotlib

from reportgen.common.clients import Client, VideoNavigator, TrackNavigator
from reportgen.common.summaries import EventSummary
from reportgen_ldwsendrun_short_customer import LdwsShortAnalyze
from reportlab.platypus import Spacer
from reportlab.platypus.flowables import PageBreak
from datalab.tygra import IndexedParagraph
from reportlab.platypus.doctemplate import NextPageTemplate

matplotlib.rcParams['savefig.dpi'] = 72  # to avoid MemoryError
from reportlab.lib.pagesizes import cm


abspath = lambda pth: os.path.abspath(os.path.join(os.path.dirname(__file__), pth))


class LdwsAnalyze(LdwsShortAnalyze):

  def fill(self, **kwargs):
    story = super(LdwsAnalyze, self).fill(**kwargs)
    summaries = [Flr20Summary(self.table, self.batch, self.view_name)]
    story.extend(self.warnings(summaries))

    return story


class LdwsSummary(EventSummary):
  def __init__(self, table, batch, view_name):
    """
    This constructor is here to get 'table', the init function will be called by the super().__init__() in Summary.
    :param table:
      database dict created in 'LdwsShortAnalyze.overall_summary()'
    :param batch:
      required by Summary
    :param view_name:
      required by Summary
    """
    self.table = table
    EventSummary.__init__(self, batch, view_name)

  def init(self, batch, view_name):

    self.modules.update([
      ('view_videonav_lanes-FLC20@evaltools',
       VideoNavigator('VideoNavigator', '320x240+0+0', 5.3, 4.0, cm)),
      ('view_tracknav_lanes-FLC20@evaltools',
       TrackNavigator('TrackNavigator', '320x454+0+0', 5.3, 7.53, cm)),
    ])

    for row in self.table:
      self.setdefault(row['fullmeas'], []).append(dict(
        start=float(row['start [s]']),
        end=float(row['start [s]']) + float(row['duration [s]']),
        duration=float(row['duration [s]']),
        side=row['side'],
        maneuver=row['maneuver'],
      ))

    return


class Flr20Summary(LdwsSummary):
  title = "LDWS event details"
  explanation = """
  LDWS warning - event duration: %s sec, side: %s, maneuver: %s<br/>
  Event is triggered because LDWS state was active: warning (5).
  """\
  % ('%(duration).2f', '%(side)s', '%(maneuver)s')

  extra_modules = [
    ('view_driveract_ldwsout@ldwseval',
     Client('DriverAct_LdwsOut_Plot', '640x700+0+0', 11, 12, cm)),
    ('view_kinematics@ldwseval',
     Client('Kinematics_Plot', '640x700+0+0', 11, 12, cm)),
  ]

  def get_tracknav_legend(self):
    """
    This document does not need a legend, override method of EventSummary
    :return:
      An emtpy list for the story
    """
    return []

if __name__ == '__main__':
  from reportgen.common.main import main
  main(os.path.abspath(__file__))
