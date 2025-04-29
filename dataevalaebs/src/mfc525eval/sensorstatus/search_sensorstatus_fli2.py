# -*- dataeval: init -*-

from mfc525eval.sensorstatus import search_sensorstatus

class Search(search_sensorstatus.Search):
  sgs = [{
    "SensorStatus": ("FLI2_E8", "FLI2_CameraStatus"),
  }]
