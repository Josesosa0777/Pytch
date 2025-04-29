# -*- dataeval: init -*-

import numpy as np

import interface
from primitives.trajectory import Path

HEADING_DIFF_TIME = 0.1

def ddiff(arr, d):
  """diff with `d` steps."""
  if arr.size < 1:
    return np.empty_like(arr)
  arr2 = np.roll(arr, -d)
  arr2[-d:] = arr[-1]
  return arr2 - arr

class Calc(interface.iCalc):
  def check(self):
    sgs = [{
      "latitude":  ("VBOX_1", "Latitude"),
      "longitude": ("VBOX_2", "Longitude"),
    }]
    group = self.get_source().selectSignalGroup(sgs)
    return group
  
  def fill(self, group):
    time, latitude = group.get_signal('latitude')
    if time.size < 1:
      return Path(time, np.empty(0), np.empty(0), np.empty(0))
    _, longitude = group.get_signal('longitude', ScaleTime=time, Order='valid')
    longitude = longitude.data
    # convert to Path
    lat_rad = np.deg2rad(latitude/60.0)
    lon_rad = np.deg2rad(longitude/60.0)
    dx = lat_rad * 6371000.0
    dy = lon_rad * 6371000.0 * np.cos(lat_rad)  # TODO: check why not *(-1)
    dx -= dx[0]
    dy -= dy[0]
    d = int(round(HEADING_DIFF_TIME / np.mean(np.diff(time))))
    psi = np.arctan2(ddiff(dy, d), ddiff(dx, d))  # ddiff for smoothing
    path = Path(time, dx, dy, psi)
    return path
