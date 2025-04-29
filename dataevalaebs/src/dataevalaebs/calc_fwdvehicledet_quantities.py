# -*- dataeval: init -*-

import numpy as np

import interface
from measparser.signalgroup import SignalGroupError

class AC100(object):
  """
  AC100-specific parameters and functions.
  """
  permaname = 'AC100'
  productname = "FLR20"
  objind_labelgroup = 'AC100 track'

init_params = {
  "FLR20": dict(sensor='AC100'),
}


querystr = """
  SELECT DISTINCT COALESCE(stableint.dxfirst, 0.0) dx_stable,
                  3.6*wholelife.egospeed egospeed_kph,
                  3.6*COALESCE(stableint.speedred, 0.0) speedred_kph,
                  3.6*wholelife.vx_ vx_kph
  FROM (
    SELECT me.basename measname,
           ei.start_time starttime,
           ei.end_time endtime,
           la2.name objind,
           qu1.value dxfirst,
           qu2.value vx_,
           qu3.value egospeed
    FROM entryintervals ei
    JOIN entries en         ON en.id = ei.entryid
    JOIN measurements me    ON me.id = en.measurementid
    JOIN modules mo         ON mo.id = en.moduleid
    JOIN interval2label il1 ON il1.entry_intervalid = ei.id
    JOIN labels la1         ON la1.id = il1.labelid
    JOIN labelgroups lg1    ON lg1.id = la1.groupid
    JOIN interval2label il2 ON il2.entry_intervalid = ei.id
    JOIN labels la2         ON la2.id = il2.labelid
    JOIN labelgroups lg2    ON lg2.id = la2.groupid
    JOIN quantities qu1     ON qu1.entry_intervalid = ei.id
    JOIN quanames qn1       ON qn1.id = qu1.nameid
    JOIN quanamegroups qg1  ON qg1.id = qn1.groupid
    JOIN quantities qu2     ON qu2.entry_intervalid = ei.id
    JOIN quanames qn2       ON qn2.id = qu2.nameid
    JOIN quanamegroups qg2  ON qg2.id = qn2.groupid
    JOIN quantities qu3     ON qu3.entry_intervalid = ei.id
    JOIN quanames qn3       ON qn3.id = qu3.nameid
    JOIN quanamegroups qg3  ON qg3.id = qn3.groupid
    WHERE qg1.name = "target" AND
          qn1.name = "dx start" AND
          qg2.name = "target" AND
          qn2.name = "vx" AND
          qg3.name = "ego vehicle" AND
          qn3.name = "speed" AND
          lg1.name = "standard" AND
          la1.name = "valid" AND
          lg2.name = :objind_labelgroup AND
          en.title = "AEBS use case - Forward vehicle detection (whole life)" AND
          mo.class = "dataevalaebs.search_fwdvehicledet.Search" AND
          mo.param = "sensor='" || :sensor || "'"
  ) wholelife
  LEFT JOIN (
    SELECT me.basename measname,
           ei.start_time starttime,
           ei.end_time endtime,
           la2.name objind,
           qu1.value dxfirst,
           qu2.value speedred
    FROM entryintervals ei
    JOIN entries en         ON en.id = ei.entryid
    JOIN measurements me    ON me.id = en.measurementid
    JOIN modules mo         ON mo.id = en.moduleid
    JOIN interval2label il1 ON il1.entry_intervalid = ei.id
    JOIN labels la1         ON la1.id = il1.labelid
    JOIN labelgroups lg1    ON lg1.id = la1.groupid
    JOIN interval2label il2 ON il2.entry_intervalid = ei.id
    JOIN labels la2         ON la2.id = il2.labelid
    JOIN labelgroups lg2    ON lg2.id = la2.groupid
    JOIN quantities qu1     ON qu1.entry_intervalid = ei.id
    JOIN quanames qn1       ON qn1.id = qu1.nameid
    JOIN quanamegroups qg1  ON qg1.id = qn1.groupid
    JOIN quantities qu2     ON qu2.entry_intervalid = ei.id
    JOIN quanames qn2       ON qn2.id = qu2.nameid
    JOIN quanamegroups qg2  ON qg2.id = qn2.groupid
    WHERE qg1.name = "target" AND
          qn1.name = "dx start" AND
          qg2.name = "AEBS" AND
          qn2.name = "speed reduction" AND
          lg1.name = "standard" AND
          la1.name = "valid" AND
          lg2.name = :objind_labelgroup AND
          en.title = "AEBS use case - Forward vehicle detection (stable period)" AND
          mo.class = "dataevalaebs.search_fwdvehicledet.Search" AND
          mo.param = "sensor='" || :sensor || "'"
  ) stableint ON stableint.measname = wholelife.measname AND
                 stableint.objind = wholelife.objind AND
                 stableint.starttime BETWEEN wholelife.starttime AND
                                             wholelife.endtime AND
                 stableint.endtime   BETWEEN wholelife.starttime AND
                                             wholelife.endtime
  ORDER BY wholelife.measname
"""

class Calc(interface.iCalc):
  def init(self, sensor):
    assert sensor in globals(), "parameter class for %s not defined" % sensor
    self.sensor = globals()[sensor]
    return

  def check(self):
    batch = self.get_batch()
    queryparams = {
      'objind_labelgroup': self.sensor.objind_labelgroup,
      'sensor':            self.sensor.permaname,
    }
    queryres = batch.query(querystr, **queryparams)
    if not queryres:
      raise SignalGroupError("incomplete information in database")
    return queryres

  def fill(self, queryres):
    detdata = np.array(queryres)
    detdatadict = {
      'dx_stable':    detdata[:,0],
      'egospeed_kph': detdata[:,1],
      'speedred_kph': detdata[:,2],
      'vx_kph':       detdata[:,3],
    }
    return detdatadict

class ViewBase(Calc, interface.iView):
  def check(self):
    return

  def fill(self):
    return

  def run(self, *args):
    return self.view(*args)
