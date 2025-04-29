import sys

import interface
import aebs.proc
import measproc
from aebs.proc.filters import delShorttimeObject, delLongrangeObjects

DefParam = interface.NullParam

class cHarmGhostLRR3_egolane(interface.iSearch):
  minlivetime = 1
  """:type: float
  Minimum livetime of LRR3_ATs0_Object_id in seconds"""
  rect_width_half = 8
  """:type: float
  maximum offset of assosiated IBEO object in positive/negative y-direction
  to LRR3_ATS0 object [m]"""
  delta_v_half = 2
  """:type: float
  maximum difference of assosiated IBEO object speed to LRR3_ATS0 object
  [m/s]"""
  v_ego_min = 10
  """:type: float
  minimum speed of ego vehicle based on LRR3_data [m/s]"""
  rect_depth_half = 4
  """:type: float
  maximum offset of assosiated IBEO object in positive/negative x-direction
  to LRR3_ATS0 object [m]"""
  maxrange = 80
  """:type: float
  maximal distance of LRR3_ATS0 object to ego vehicle [m]"""
  kritvalue = 0.5
  """:type:
  minimum hit_ratio over LRR3_ATS0 object livetime for IBEO referenced
  object
  (Counted as hitted if IBEO reference object in given rectangle around
  LRR3_ATS0 object)"""

  dep = 'fillLRR3_ATS@aebs.fill', 'fillIBEO@aebs.fill'
  SignalGroups = [{'vxvRef': ('MRR1plus', 'evi.General_T20.vxvRef')}]
  def check(self):
    Source = self.get_source('main')
    Group = Source.selectSignalGroup(self.SignalGroups)
    return Group

  def fill(self, Group):
    # viewFUSoverlayLRR3_AC100_ESR is dropped from MKS
    from assosiate import assosiate

    Title = "HarmGhostLRR3egolane"
    CommentNames = ['minlivetime', 'rect_width_half', 'delta_v_half',
                    'v_ego_min', 'rect_depth_half', 'maxrange', 'kritvalue']
    Comment = ','.join(['%s=%s' %(Name, getattr(self, Name))
                        for Name in CommentNames])
    Source = self.get_source('main')
    Modules = self.get_modules()

    data = {}
    for Name in self.dep:
      scaletime, data[Name] = Modules.fill(Name)

    time_v_ego, v = Source.getSignalFromSignalGroup(Group, 'vxvRef',
                                                    ScaleTime=scaletime)

    compared_Sensor = self.dep[0]
    if self.minlivetime > 0:
      delShorttimeObject(scaletime,[data[compared_Sensor][0]], self.minlivetime)

    if self.maxrange > 0:
      delLongrangeObjects([data[compared_Sensor][0]], self.maxrange)

    start_index_id = 0
    actual_id = 0
    stop_index_id = 0
    last_id = 0
    found_sth = False
    intervallist = measproc.cIntervalList(scaletime)
    offset_list = []
    for i in xrange(1,len(scaletime)):
      last_id = actual_id
      actual_id = data[compared_Sensor][0]["id"][i]
      stop_index_id = i
      if actual_id != 0 and last_id == 0:
        start_index_id = i
      livetime = scaletime[stop_index_id] - scaletime[start_index_id]
      if actual_id != last_id and last_id != 0 and self.minlivetime < livetime:
        referenced_data = assosiate([data[compared_Sensor][0]],
                                    data["fillIBEO@aebs.fill"],
                                    "IBEO",
                                    scaletime = scaletime,
                                    delta_v_half = self.delta_v_half,
                                    rectangle_width_half = self.rect_width_half,
                                    rectangle_depth_half = self.rect_depth_half,
                                    start_index = start_index_id,
                                    stop_index = stop_index_id)[0]
        idx = len(referenced_data[0]["hit_ratio"])-1
        hit_ratio = float(referenced_data[0]["hit_ratio"][idx])
        if hit_ratio < self.kritvalue and v[i] > self.v_ego_min:
          found_sth=True
          intervallist.add(start_index_id,stop_index_id)

          idx = len(referenced_data[0]["average_delta_x"])-1
          average_delta_x = float(referenced_data[0]["average_delta_x"][idx])

          idx = len(referenced_data[0]["average_delta_y"])-1
          average_delta_y = float(referenced_data[0]["average_delta_y"][idx])

          offset_string = "\nhit_ratio:\t" + str(hit_ratio)\
                        + "\n      average_delta_x:\t"\
                        + str(average_delta_x)\
                        + "\n      average_delta_y:\t"\
                        + str(average_delta_y) + "\n"
          offset_list.append(((start_index_id,stop_index_id),offset_string))

          print >> sys.stderr, "\n\nstarttime: "\
                             + str(scaletime[start_index_id])\
                             + " stoptime: "\
                             + str(scaletime[stop_index_id])
          print >> sys.stderr, offset_string

        start_index_id = i
    Report = measproc.cIntervalListReport(intervallist, Title=Title)
    for x in xrange(len(offset_list)):
      Report.IntervalAttrs[offset_list[x][0]]['Comment'] = offset_list[x][1]
    Report.ReportAttrs['Comment'] = Comment
    return Report

  def search(self, Param, Report):
    Batch = self.get_batch()
    Batch.add_entry(Report, self.NONE)
    return

