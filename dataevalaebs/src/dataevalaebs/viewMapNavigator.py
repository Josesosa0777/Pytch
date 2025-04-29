import datavis
import interface
import numpy

signal_groups = [{"Longitude": ("VBOX_2", "Longitude"),
                  "Latitude": ("VBOX_1", "Latitude")},
                 {"Longitude": ("GPS_Maus_1", "Longitude"),
                  "Latitude": ("GPS_Maus_1", "Latitude")}]

class cParameter(interface.iParameter):
  def __init__(self, zoom):
    self.zoom = zoom
    self.genKeys()
    return

# instantiation of module parameters
AUTO_ZOOM = cParameter(None)
ZOOM_LEVEL_07 = cParameter(7)
ZOOM_LEVEL_08 = cParameter(8)
ZOOM_LEVEL_09 = cParameter(9)
ZOOM_LEVEL_10 = cParameter(10)
ZOOM_LEVEL_11 = cParameter(11)
ZOOM_LEVEL_12 = cParameter(12)
ZOOM_LEVEL_13 = cParameter(13)
ZOOM_LEVEL_14 = cParameter(14)
ZOOM_LEVEL_15 = cParameter(15)
ZOOM_LEVEL_16 = cParameter(16)

class cView(interface.iView):
  def check(self):
    group = interface.Source.selectSignalGroup(signal_groups)
    return group
  
  def fill(self, group):
    return group
  
  def view(self, param, group):
    mapman = self.get_mapman()
    Client = datavis.MapNavigator(mapman)
    interface.Sync.addClient(Client)
    GPS_time, longitude = interface.Source.getSignalFromSignalGroup(group, "Longitude")
    latitude = interface.Source.getSignalFromSignalGroup(group, "Latitude", ScaleTime=GPS_time)[1]
    # GPS signals have to be converted to degrees and normalized
    if interface.Source.getShortDeviceName(group['Longitude'][0]) == 'VBOX_2':
      normalize = 60.0
    elif interface.Source.getShortDeviceName(group['Longitude'][0]) == 'GPS_Maus_1':
      normalize = 100.0
    longitude = numpy.abs(-longitude) / normalize
    latitude = numpy.abs(latitude) / normalize
    mask = numpy.logical_and(latitude != 0.0, longitude != 0.0)
    longitude = longitude[mask]
    latitude = latitude[mask]
    GPS_time = GPS_time[mask]
    Client.set_time(GPS_time)
    Client.set_route(longitude, latitude, param.zoom)
    return
