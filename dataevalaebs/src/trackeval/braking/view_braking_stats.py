# -*- dataeval: init -*-

"""
Plot statistics about target braking behavior.
"""

import numpy as np

from interface import iView
from datavis.MatplotlibNavigator import MatplotlibNavigator
from measparser.signalproc import histogram2d
from search_braking import AX_THRESHOLD

AX_AXLIM = (-7.0, 2.0)  # axis limits for ax (acceleration)

def quantity_join(quanamegroup, quaname):
  query_part = """(
    SELECT qu.entry_intervalid, qu.value
    FROM quantities qu
    JOIN quanames qn ON qn.id = qu.nameid
    JOIN quanamegroups qg ON qg.id = qn.groupid
    WHERE qg.name = '%(quanamegroup)s'
      AND qn.name = '%(quaname)s'
  )""" % dict(quanamegroup=quanamegroup, quaname=quaname)
  return query_part

class View(iView):
  def check(self):
    table_name = self.batch.create_table_from_last_entries(
      start_date=self.start_date, end_date=self.end_date)
    query = """
      SELECT ei.end_time-ei.start_time AS dura,
             %(speed)s.value,
             %(axmin)s.value, %(axmax)s.value,
             %(axavg)s.value, %(axstd)s.value
      FROM entryintervals ei
      JOIN %(entries)s en ON en.id = ei.entryid
      JOIN modules mo ON mo.id = en.moduleid
      LEFT JOIN %(s_speed)s AS %(speed)s ON %(speed)s.entry_intervalid = ei.id
      LEFT JOIN %(s_axmin)s AS %(axmin)s ON %(axmin)s.entry_intervalid = ei.id
      LEFT JOIN %(s_axmax)s AS %(axmax)s ON %(axmax)s.entry_intervalid = ei.id
      LEFT JOIN %(s_axavg)s AS %(axavg)s ON %(axavg)s.entry_intervalid = ei.id
      LEFT JOIN %(s_axstd)s AS %(axstd)s ON %(axstd)s.entry_intervalid = ei.id
      WHERE mo.class = '%(moduleclass)s' AND
            dura > 1.0 AND
            %(axavg)s.value < %(axthreshold)f
      ORDER BY %(axmax)s.value - %(axmin)s.value DESC
    """ % dict(
      entries=table_name,
      moduleclass="dataevalaebs.search_braking_vehicle.Search",
      speed="speed", s_speed=quantity_join("ego vehicle", "speed"),
      axmin="axmin", s_axmin=quantity_join("target", "ax min"),
      axmax="axmax", s_axmax=quantity_join("target", "ax max"),
      axavg="axavg", s_axavg=quantity_join("target", "ax avg"),
      axstd="axstd", s_axstd=quantity_join("target", "ax std"),
      axthreshold=AX_THRESHOLD,
    )
    res = self.batch.query(query)
    header = ("dura", "speed", "axmin", "axmax", "axavg", "axstd")
    assert res, "incomplete information in database"
    assert len(res[0]) == len(header), "invalid header"
    return res, header
  
  def view(self, res, header):
    i = {v: k for k, v in enumerate(header)}  # {"dura":0, "speed":1, ...}
    
    mn = MatplotlibNavigator()
    self.sync.addStaticClient(mn)
    # Braking duration histogram
    ax = mn.fig.add_subplot(1,2,1, title="Braking duration histogram")
    ax.set_xlabel("duration [s]"); ax.set_ylabel("#occurrences")
    ax.hist([row[i["dura"]] for row in res], bins=20)
    # Mean acceleration histogram
    ax = mn.fig.add_subplot(1,2,2, title="Mean acceleration histogram")
    ax.set_xlim(AX_AXLIM)
    ax.set_xlabel("mean accel. [m/s^2]"); ax.set_ylabel("#occurrences")
    ax.hist([row[i["axavg"]] for row in res], bins=20)
    
    mn = MatplotlibNavigator()
    self.sync.addStaticClient(mn)
    # Acceleration limits vs. duration
    ax = mn.fig.add_subplot(1,2,1, title="Acceleration limits vs. duration")
    ax.set_xlim(AX_AXLIM)
    ax.set_xlabel("accel. min-max [m/s^2]"); ax.set_ylabel("duration [s]")
    for row in res:
      dura = row[i["dura"]]
      ax.plot((row[i["axmin"]], row[i["axmax"]]), (dura, dura), 'b-')
      ax.plot(row[i["axavg"]], dura, 'r.')
    # Acceleration distribution vs. duration
    ax = mn.fig.add_subplot(1,2,2, title="Acceleration distribution vs. duration")
    ax.set_xlim(AX_AXLIM)
    ax.set_xlabel("accel. +/- 3std [m/s^2]"); ax.set_ylabel("duration [s]")
    for row in res:
      dura = row[i["dura"]]; avg = row[i["axavg"]]; std = row[i["axstd"]]
      ax.plot((avg-3*std, avg+3*std), (dura, dura), 'b-')
      ax.plot(avg, dura, 'r.')
    
    mn = MatplotlibNavigator()
    self.sync.addStaticClient(mn)
    # Mean acceleration vs. standard deviation
    ax = mn.fig.add_subplot(1,2,1, title="Mean acceleration vs. standard deviation")
    ax.set_xlim(AX_AXLIM)
    ax.set_xlabel("mean accel. [m/s^2]"); ax.set_ylabel("std accel. [m/s^2]")
    for row in res:
      ax.plot(row[i["axavg"]], row[i["axstd"]], 'r.')
    # Acceleration duration vs. standard deviation
    ax = mn.fig.add_subplot(1,2,2, title="Acceleration duration vs. standard deviation")
    ax.set_xlabel("duration [s]"); ax.set_ylabel("std accel. [m/s^2]")
    for row in res:
      ax.plot(row[i["dura"]], row[i["axstd"]], 'r.')
    
    mn = MatplotlibNavigator()
    self.sync.addStaticClient(mn)
    # Mean acceleration vs. duration
    ax = mn.fig.add_subplot(1,1,1, title="Mean acceleration vs. duration")
    ax.set_xlim(AX_AXLIM);
    ax.set_xlabel("mean accel. [m/s^2]"); ax.set_ylabel("duration [s]")
    avgs = [row[i["axavg"]] for row in res]
    duras = [row[i["dura"]] for row in res]
    avg_bins = np.arange(AX_AXLIM[0], AX_AXLIM[1]+0.1, 0.5)
    dura_bins = np.arange(0.0, max(duras)+0.1, 0.5)
    H, xedges, yedges = histogram2d(avgs, duras,
      bins=(avg_bins, dura_bins), toplotframe=True)
    extent = (xedges[0], xedges[-1], yedges[0], yedges[-1])
    im = ax.imshow(H, extent=extent, cmap='OrRd')
    mn.fig.colorbar(im)
    return
