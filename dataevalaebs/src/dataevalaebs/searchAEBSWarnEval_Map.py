from collections import OrderedDict

import numpy

import interface
import measproc
from measparser.signalgroup import SignalGroupError, SignalGroup

DefParam = interface.NullParam

visuSignalGroups = OrderedDict([
  ('vbox', {
    "Longitude": ("VBOX_2", "Longitude"),
    "Latitude":  ("VBOX_1", "Latitude"),
  },),
  ('maus', {
    "Longitude": ("GPS_Maus_1", "Longitude"),
    "Latitude":  ("GPS_Maus_1", "Latitude"),
  },),
])

multimSignalGroups = [
  {
    "Multimedia_1": ("Multimedia", "Multimedia_1"),
  },
]

class cSearch(interface.iSearch):
  def check(self):
    Source = self.get_source('main')
    multimGroup = SignalGroup.from_first_valid(multimSignalGroups, Source,
                                               StrictTime=True, TimeMonGapIdx=5)
    
    visuGroup = SignalGroup.from_named_signalgroups(visuSignalGroups, Source)
    if visuGroup.winner == 'vbox':
      normalize = 60.0
    elif visuGroup.winner == 'maus':
      normalize = 100.0
    else:
      raise SignalGroupError('No visuSignalGroups selection')

    time, lon = visuGroup.get_signal('Longitude')
    lat = visuGroup.get_value('Latitude', ScaleTime=time)
    lon = numpy.abs(lon) / normalize
    lat = numpy.abs(lat) / normalize
    if numpy.any(lon > 180.0) or numpy.any(lat > 90.0):
      raise SignalGroupError("Invalid GPS coordinates")
    return time, lon, lat, multimGroup
  
  def fill(self, time, lon, lat, multimGroup):
    return time, lon, lat, multimGroup
  
  def search(self, param, time, lon, lat, multimGroup):
    Source = self.get_source('main')
    Batch = self.get_batch()
    
    workspaceMap = measproc.DinWorkSpace('AEBS_MapData')
    mm = multimGroup.get_value('Multimedia_1', ScaleTime=time)
    workspaceMap.add(Time=time, Latitude=lat, Longitude=lon, Multimedia_1=mm)
    Batch.add_entry(workspaceMap, self.NONE)
    return

