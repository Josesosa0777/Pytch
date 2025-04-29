import os

import interface
from measparser.signalgroup import SignalGroupError
from collections import OrderedDict

DefParam = interface.NullParam

VOTES_EXPLAINED = OrderedDict([('bridge', 
                                ('Bridges', 
                                 'Bridges')),
                               ('tunnel', 
                                ('Tunnels', 
                                 'Tunnels')),
                               ('fw-red-with-sdf', 
                                ('FW red. with SDF', 
                                 'False warning reduction with SDF')),
                               ('scam-unavailable', 
                                ('No camera available', 
                                 'No KB-Cam Advanced was available')),
                               ('infrastructure', 
                                ('Infrastructure', 
                                 'Infrastructure element on path (typically city)')),
                               ('parking_car', 
                                ('Parking car', 
                                 'Parking car on path (typically city)')),
                               ('road_exit', 
                                ('Road exit', 
                                 'Road exit (obstacle is on the left of the ego path)')),
                               ('high_curvature', 
                                ('High curvature turn', 
                                 'Low speed high curvature turns (highway entry/exit, roundabout)')),
                               ('traffic_island', 
                                ('Traffic island', 
                                 'Traffic island')),
                               ('approaching_curve', 
                                ('Approaching curve', 
                                 'Approaching a curve with sidepoles or guardrail (mostly rural)')),
                               ('straight_road', 
                                ('Straight road', 
                                 'Straight road where some roadside elements appear on path (most likely because of corrective steering)')),
                               ('construction_site', 
                                ('Construction site', 
                                 'Construction site')),
                               ('braking_fw_vehicle', 
                                ('Braking forward vehicle', 
                                 'A vehicle is braking in front of the ego-vehicle'))])

TITLE_SEP = '-'

def iterTitles(ReportTags, TitleHead, **TitleTags):
  Tags = {}
  for Tag in ReportTags:
    Value = TitleTags.get(Tag, ReportTags[Tag])
    Tags[Tag] = Value
  for Sensor in Tags['Sensors']:
    for Road in Tags['Roads']:
      for Test in Tags['Tests']:
        Title = TitleHead, Sensor, Road, Test
        yield TITLE_SEP.join(Title)


class cAnalyze(interface.iAnalyze):
  ReportTags = {'Roads':   ('city', 'rural', 'highway'),
                'Sensors': ('CVR2', 'CVR3', 'AC100'),
                'Tests':   ('Mitigation10', 'Mitigation20', 'KBAEBS', 
                            'Avoidance', 'KBASFAvoidance', 'CVR3Warning',
                            'LRR3Warning', 'AC100Warning')}
  Votes = VOTES_EXPLAINED.keys()
  Sensors = ('CVR2', 'CVR3')
  Tests = ('KBASFAvoidance', 'CVR3Warning')
  TitleHead = 'AEBS-activity'

  def check(self):
    """
    :ReturnType: set
    :Return: measproc.cFileReport entries which title is 
    AEBS-activity-[CVR2|CVR3]-[city|rural|highway]-[Mitigation10|KBASFAvoidance]
    """
    Batch = self.get_batch()
    Group = set()
    for Title in iterTitles(self.ReportTags, self.TitleHead, Sensors=self.Sensors, Tests=self.Tests):
      Titles = Batch.filter(type="measproc.cFileReport", title=Title)
      Group.update(Titles)
    
    if not Group:
      raise SignalGroupError('No report with required title')
    return Group

  def fill(self, Group):
    Batch = self.get_batch()
    Reports = []
    Entries = set()
    for Entry in Group:
      Report = Batch.wake_entry(Entry)
      if Report.ReportAttrs['NoIntervals']:
        Reports.append(Report)
        Entries.add(Entry)
    return Entries, Reports 
    

  def analyze(self, Param, Entries, Reports):
    for Report in Reports:
      Report.addVotes(self.Votes)
      Report.save()
      
    BatchNav = self.get_batchnav()
    BatchNav.BatchFrame.addEntries(Entries)
    BatchNav.CheckMeasExist = False
    pass

