# -*- dataeval: init -*-

import numpy as np

import interface
from measproc.IntervalList import intervalsToMask

class cFill(interface.iObjectFill):
  dep = 'calc_conti_srr520'

  def check(self):
    tracks = self.modules.fill(self.dep)
    return tracks

  types ={
      0: "Point",
      1: "Car",
      2: "Truck",
      3: "Pedestrian",
      4: "PedMicroDoppler",
      5: "Motorcycle",
      6: "Bicycle",
      7: "BicMicroDoppler",
      8: "Wide",
      9: "Unclassified",

  }

  def fill(self, tracks):
    objects = []
    for id, track in tracks.iteritems():
      # create object
      o = {}
      o["id"] = np.where(track.valid, id, -1)
      o["valid"] = track.valid
      o["class"] = track.obj_class
      #o["valid"] = np.ones(o["id"].shape)
      idlist = [_id if _id != -1 else "" for _id in o["id"]]
      typelist = [self.types[obj_type] if obj_type != -1 else "" for obj_type in o["class"]]
      o["label"] = np.array(["{} (Track_{})".format(*tuple) for tuple in zip(typelist, idlist)])
      o["dx"] = track.x
      o["dy"] = track.y
      o["vx"] = track.speed_x
      o["vy"] = track.speed_y

      # o["type"] = np.where(~track.valid, self.get_grouptype('NONE_TYPE'), self.get_grouptype('CONTI_SRR520'))
      if id < 6:
          o["type"] = np.where(~track.valid, self.get_grouptype('CONTI_SRR520_radar_1'), self.get_grouptype('CONTI_SRR520_radar_1'))
      else:
          o["type"] = np.where(~track.valid, self.get_grouptype('CONTI_SRR520_radar_2'), self.get_grouptype('CONTI_SRR520_radar_2'))

      objects.append(o)
    return tracks.time, objects

if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r'C:\KBData\TAevalData\DAF__2018-04-25\DAF__2018-04-25_09-20-38.mat'
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    srr520 = manager_modules.calc('fillContiSRR520@ta.fill', manager)
    dummy_id, dummy_target = srr520.iteritems().next()
    print dummy_id
    print dummy_target.x
    print dummy_target.y