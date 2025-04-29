# -*- dataeval: init -*-

"""
XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
"""

import os
import csv

import numpy as np

from interface import iView
from datavis.MatplotlibNavigator import MatplotlibNavigator
from datavis.PlotNavigator import cPlotNavigator
from measparser.signalproc import histogram2d, isSameTime
from measparser.SignalSource import cSignalSource

# TEST_SUMMARY_FILE = r"C:\KBData\sandbox\AEBS_C_AREL\temp\06_arel_w_vrel_n_agents\sil_mbt_tc_summary.csv"
# TEST_SUMMARY_FILE = r"C:\KBData\sandbox\AEBS_C_AREL\temp\07_arel_wo_vrel_n_agents\sil_mbt_tc_summary.csv"
TEST_SUMMARY_FILE = r"C:\KBData\sandbox\AEBS_C_AREL\temp\09_warndt_max_3.0s_wo_vrel_n_agents\sil_mbt_tc_summary.csv"

class View(iView):
  def check(self):
    return
  
  def fill(self):
    assert os.path.isfile(TEST_SUMMARY_FILE), "`%s` does not exist" % TEST_SUMMARY_FILE
    data = {}
    with open(TEST_SUMMARY_FILE, 'r') as f:
      reader = csv.reader(f, delimiter=';')
      for i_row, row in enumerate(reader):
        if i_row == 0:  # 'row' contains the header
          i = {v: k for k, v in enumerate(row)}  # {"Result":0, "Reason":1, ...}
          continue
        name = row[i["Name"]]
        if 'aOn' in name: continue
        key = name.replace("aOn", "").replace("aOff", "")
        assert "aOn" in name or "aOff" in name, "Unknown test: %s" % name
        var_sfx = "aOn" if "aOn" in name else "aOff"
        if key not in data:
          data[key] = {}
          data[key]["dx"] = float(row[i["dx(WP1)"]])
          data[key]["vx_ego"] = float(row[i["obst_vx(WP1)"]]) - float(row[i["ego_vx(WP1)"]])
          data[key]["ax_obj"] = float(row[i["obst_ax(WP1)"]])
          data[key]["obst_surely_stopped_in_casc"] = (float(row[i["obst_vx(avoid)"]]) == 0.0) and (float(row[i["ego_vx(avoid)"]]) == 0.0)
          data[key]["obst_maybe_stopped_in_casc"] = (float(row[i["obst_vx(avoid)"]]) == 0.0) and (float(row[i["ego_vx(avoid)"]]) > 0.0)
        data[key]["t_warn_%s" % var_sfx] = float(row[i["ttc(WP1)"]])
        data[key]["coll_%s" % var_sfx] = ( bool(int(row[i["IMPACT"]])) and
          row[i["Reason"]] != "Impact after successful cascade" )
    return data
  
  def view(self, data):
    data2 = {}
    possible_ax_objs = set(values["ax_obj"] for values in data.itervalues())
    for ax_obj in possible_ax_objs:
      data2[ax_obj] = np.array([
        (values["dx"],
         values["vx_ego"],
         values["t_warn_aOff"],
         False,#values["coll_aOn"],
         values["coll_aOff"],
         values["obst_surely_stopped_in_casc"],
         values["obst_maybe_stopped_in_casc"],
         )
        for values in data.itervalues() if values["ax_obj"] == ax_obj
      ])
    for ax_obj in data2.iterkeys():
      ###
      if int(ax_obj) != ax_obj:
        continue
      ###
      self.plot_one_acceleration(ax_obj, data2)
    
    # self.plot_ax_dt(data2)
    return
  
  def plot_one_acceleration(self, ax_obj, data2):
    mn = MatplotlibNavigator("Delta time for starting warning")
    self.sync.addStaticClient(mn)
    ax = mn.fig.add_subplot(1,1,1, projection='3d', title="ax=%.1f m/s^2" % ax_obj)
    ax.set_xlabel("dx [m]"); ax.set_ylabel("vxRel [km/h]"); ax.set_zlabel("Dt [s]")
    # ax.set_zlim(-1.5, 0.2)
    # trisurf
    act_data = data2[ax_obj].T
    ax.plot_trisurf(act_data[0], act_data[1], act_data[2])#, color=(1.0, 1.0, 1.0))
    # dots
    for row in data2[ax_obj]:
      # color = self.get_dot_color(row[3], row[4])
      color = self.get_dot_color(row[5], row[6])
      ax.plot([row[0]], [row[1]], color, zs=[row[2]], ms=10.0)
    return
  
  def plot_ax_dt(self, data2):
    dx_f = 40.0; vx_ego_f = 80.0
    dts = {}; colls = {}
    for ax_obj, arr in data2.iteritems():
      for dx, vx_ego, dt, coll1, coll2 in arr:
        if dx == dx_f and vx_ego == vx_ego_f:
          dts[ax_obj] = dt
          colls[ax_obj] = (coll1, coll2)
          break
    mn = cPlotNavigator("Delta time for starting warning")
    self.sync.addStaticClient(mn)
    ax = mn.addAxis()
    ax.set_title("dx=%.1f m, v=%.1f km/h" % (dx_f, vx_ego_f))
    ax.set_xlabel("(-1)*decel. [m/s^2]"); ax.set_ylabel("Dt [s]")
    # line
    x = np.array(sorted(dts.iterkeys()))
    y = np.array([dts[xi] for xi in x])
    mn.addSignal2Axis(ax, "Dt", x, y, unit="s")
    # dots
    for xi in x:
      color = self.get_dot_color(*colls[xi])
      ax.plot([xi], [dts[xi]], color)
    return
  

  @staticmethod
  def get_dot_color(obst_surely_stopped_in_casc, obst_maybe_stopped_in_casc):
    if obst_surely_stopped_in_casc:
      color = 'g'
    elif obst_maybe_stopped_in_casc:
      color = 'k'
    else:
      color = 'r'
    return color + '.'
  
  # @staticmethod
  # def get_dot_color(coll1, coll2):
    # color = ('g', 'm', 'r')[int(coll1)+int(coll2)]
    # return color + '.'

if __name__ == "__main__":
  view = View()
  view.view(view.fill(view.check()))

#    # surface
#    Dxs, Vx_egos = np.meshgrid(dxs, vx_egos)
#    Dts = np.zeros_like(Dxs)
#    for i in xrange(Dts.shape[0]):
#      for j in xrange(Dts.shape[1]):
#        for k in xrange(len(dxs)):
#          if Dxs[i,j] == dxs[k] and Vx_egos[i,j] == vx_egos[k]:
#            Dts[i,j] = dts[k]
#            break
#    ax.plot_surface(Dxs, Vx_egos, Dts)

