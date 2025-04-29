# -*- dataeval: init -*-

import os
import sys
import glob
import logging

import measparser
import datavis
import interface

init_params = {
    "DefParam" : dict(video_suffix=""),
    "VideoSuffix_m0" : dict(video_suffix="_m0"),
}

SignalGroups = [
  {'VidTime': ('Multimedia', 'Multimedia_1')},
  {'VidTime': ('Multimedia', 'Multimedia')},
  {'VidTime': ('Multimedia', 'Pro9000')},
  {'VidTime': ('Multimedia', 'LifeCam')},
]

AccelGroups = [{'Accel': ('ECU',        'evi.General_TC.axvRef')},
               {'Accel': ('MRR1plus',   'evi.General_TC.axvRef')},
               {'Accel': ('RadarFC',   'evi.General_TC.axvRef')}]

Optionals = [{'ego_speed': ('ECU',      'evi.General_T20.vxvRef'),                 
              'ego_acc':   ('ECU',      'evi.General_T20.axvRef'),},
             {'ego_speed': ('MRR1plus', 'evi.General_T20.vxvRef'),
              'ego acc':   ('MRR1plus', 'evi.General_T20.axvRef'),},
             {'ego_speed': ('RadarFC', 'evi.General_T20.vxvRef'),
              'ego_acc':   ('RadarFC', 'evi.General_T20.axvRef'),},]

class cView(interface.iView):
  def init(self, video_suffix):
    self.VideoSuffix = video_suffix
    return
    
  def check(self):
    Name, Ext = os.path.splitext(interface.Source.FileName)
    AviFile = getVideoName(Name + self.VideoSuffix + Ext)
    Group = interface.Source.selectSignalGroup(SignalGroups, 
                                               StrictTime=interface.StrictlyGrowingTimeCheck, 
                                               TimeMonGapIdx=5)
    return AviFile, Group

  def fill(self, AviFile, Group):
    return AviFile, Group

  def view(self, AviFile, Group):
    VN = datavis.cVideoNavigator(AviFile, self.vidcalibs)
    TimeVidTime, VidTime = interface.Source.getSignalFromSignalGroup(Group, 'VidTime')
    interface.Sync.addClient(VN, (TimeVidTime, VidTime))
    VN.setDisplayTime(TimeVidTime, VidTime)

    VN.setLegend(interface.ShapeLegends)
    VN.addGroups(interface.Groups)
    for Status in interface.Objects.get_selected_by_parent(interface.iFill):
      ScaleTime_, Objects = interface.Objects.fill(Status)
      VN.setObjects(ScaleTime_, Objects)  
    
    try:
      AccelGroup = interface.Source.selectSignalGroup(AccelGroups)
    except measparser.signalgroup.SignalGroupError:
      print >> sys.stderr, 'Warning: cabin movement compensation unavailable'
    else:
      Time, Accel = interface.Source.getSignalFromSignalGroup(AccelGroup, 'Accel')
      AccelComp = Accel / 50.0  # empirical value
      VN.setAccelComp(Time, AccelComp)
    
    try:
      OptGroup = interface.Source.selectSignalGroup(Optionals)
    except measparser.signalgroup.SignalGroupError:
      pass
    else:
      for Name in OptGroup:
        Time, Value = interface.Source.getSignalFromSignalGroup(OptGroup, Name)
        Unit = interface.Source.getPhysicalUnitFromSignalGroup(OptGroup, Name)
        VN.setSignal(Name, Time, Value, Unit)
    return

def getVideoName(MeasFile):
  # pre-defined list of alternative folders for video files
  alternative_dirs = [
    ("DAS/EnduranceRun", "DAS/ConvertedMeas"),
    ("DAS/Customer", "DAS/ConvertedMeas"),
    ("measurement", "measurement_conv"),
  ]
  # normalize paths
  meas_file = os.path.normpath(MeasFile)
  alternative_dirs = [(os.path.normpath(k), os.path.normpath(v))
                      for (k, v) in alternative_dirs]
  # create "reversed" list (to check both 1->2 and 2->1 replacement)
  alternative_dirs_reversed = [(v,k) for (k,v) in alternative_dirs]
  # put complete list of alternative folders together; start with the original
  alternative_dirs = [("", "")] + alternative_dirs + alternative_dirs_reversed
  # try to find the video file...
  for orig_dir, alternative_dir in alternative_dirs:
    if orig_dir not in meas_file:
      continue
    meas_file_mod = meas_file.replace(orig_dir, alternative_dir)
    try:
      Name = getVideoNameInSameDir(meas_file_mod)
      return Name
    except AssertionError:
      continue
  raise AssertionError('Video file not found for `%s`' % MeasFile)

def getVideoNameInSameDir(MeasFile):
  supp_exts = '.flv', '.avi'
  Base, Ext_ = os.path.splitext(MeasFile)
  for Ext in supp_exts:
    Name = Base + Ext
    if os.path.exists(Name):
      break
  else:
    Names = []
    for Ext in supp_exts:
      Names += glob.glob('%s*%s%s' % (Base, os.extsep, Ext))
      if Names:
        break
    else:
      raise AssertionError('Video file not found for `%s`' % MeasFile)
    Name = Names[0]
    logger = logging.getLogger()
    logger.warning('Alternative video file selected: %s' % Name)
  return Name
