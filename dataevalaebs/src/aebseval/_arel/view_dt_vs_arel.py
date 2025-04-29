# -*- dataeval: init -*-

"""
Plot the delta time min/mean/max values versus relative acceleration at the start
of the AEBS warning based on data coming from MBT and cython simulation. Linear
approximation of these values are shown with a line passing through the NCAP
50kph,40m,-2m/s/s sample point and the origin.
"""

import os

import numpy as np
import pandas as pd

from interface import iView
from datavis.MatplotlibNavigator import MatplotlibNavigator

TEST_SUMMARY_FILE = r"C:\KBData\sandbox\AEBS_C_AREL\temp\20_formula_w_deceleration_6__dt_max_3s\mbt_summary_d3_lin_regr.csv"


class View(iView):
  def check(self):
    assert os.path.isfile(TEST_SUMMARY_FILE), "`%s` does not exist" % TEST_SUMMARY_FILE
    return

  def fill(self):
    df = pd.read_csv(TEST_SUMMARY_FILE, sep=';')
    return df

  def view(self, df):
    mn = MatplotlibNavigator("dt at warning start vs. arel")
    self.sync.addStaticClient(mn)
    ax = mn.fig.gca()
    ax.set_xlabel("arel [m/s/s]")
    ax.set_ylabel("dt (min/mean/max) [s]")
    # collect dt values at warning start
    arel2dts = {}
    dt_ncap = None
    for arel, df_gb_arel in df.groupby('arel'):
      dts = []
      for name, df_gb_arel_gb_name in df_gb_arel.groupby('name'):
        # only collect valid dt values (where aAvoid is reasonable)
        aAvoidDelta = abs( df_gb_arel_gb_name.aAvoidOff.values[-1] - df_gb_arel_gb_name.aAvoidOn.values[-1] )
        if (aAvoidDelta < 0.5) and (-5.0 > df_gb_arel_gb_name.aAvoidOff.values[-1] > -8.0):
          dts.append( df_gb_arel_gb_name.tWarnDt.values[-1] )
        else:
          print 'skipped due to invalid dt:', name
      arel2dts[arel] = dts
    # prepare arrays for plotting
    size = len(arel2dts)
    x = np.empty(size)
    y = np.empty(size)
    lb = np.empty(size)
    ub = np.empty(size)
    for i, arel in enumerate( sorted(arel2dts) ):
      dts = arel2dts[arel]
      # print arel, len(dts)
      x[i] = arel
      y[i] = np.mean(dts)
      lb[i] = y[i] - np.min(dts)
      ub[i] = np.max(dts) - y[i]
    ax.errorbar(x, y, yerr=[lb,ub], fmt='o')
    # get dt for NCAP 50kph,40m,-2m/s/s
    df_ncap = df[ df.name.str.contains('ev50rv0ra0d40aOffnra_2[^\d]') ] # handle different naming conventions
    dt_ncap = df_ncap.tWarnDt.values[-1]
    print 'dt_ncap = ', dt_ncap
    # plot line passing through origin (0m/s/s,0s) and NCAP (-2m/s/s,dt_ncap)
    slope = dt_ncap / -2.
    x = np.linspace(df.arel.min(), 0.)
    y = slope *  x
    ax.plot(x,y)
    ax.plot([-2., 0.], [dt_ncap, 0.], 'ro')
    ax.set_xlim(df.arel.min()-.1, .1)
    ax.set_ylim(-.1, df.tWarnDt.max() + .1)
    return
