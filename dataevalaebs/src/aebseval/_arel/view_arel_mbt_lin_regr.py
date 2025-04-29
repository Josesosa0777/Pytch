# -*- dataeval: init -*-

import os

import numpy as np
import pandas as pd

from interface import iView
from datavis.MatplotlibNavigator import MatplotlibNavigator

# TEST_SUMMARY_FILE = r"C:\KBData\sandbox\AEBS_C_AREL\temp\11_ssb_warndt_max_3.0s_wo_vrel_n_agents\sil_mbt_tc_summary_d3_mpl.csv"
TEST_SUMMARY_FILE = r"C:\KBData\sandbox\AEBS_C_AREL\temp\11_ssb_warndt_max_3.0s_wo_vrel_n_agents\sil_mbt_tc_summary_d3_lin_regr.csv"


def lin_regr_ls(df, varnames, ordname):
  # linear regression with least-squares
  X = np.vstack( [np.ones_like(df[varnames[0]])] + [df[varname] for varname in varnames] ).T
  Y = df[ordname]
  A = np.linalg.lstsq(X,Y)[0]
  return A

def create_mask(df):
  mask = np.zeros_like(df.aAvoidOff.values, dtype=np.bool)
  aAvoidDelta = np.abs( df.aAvoidOff.values - df.aAvoidOn.values)
  if (aAvoidDelta[-1] < 0.5) and (-5.0 > df.aAvoidOff.values[-1] > -10.):
    mask[-1] = True
  # mask = (aAvoidDelta < 1.) & (df.aAvoidOff.values < -5.5)
  return mask

def plot_plane(df, A, ax):
  c0,c1,c2 = A
  x = np.arange( df.dx.min(),   df.dx.max()   )
  y = np.arange( df.vrel.min(), df.vrel.max() )
  dx, vrel = np.meshgrid(x,y)
  wdt = c0 + c1*dx + c2*vrel
  ax.plot_surface(dx, vrel, wdt, alpha=.1)
  ax.set_zlim(df.tWarnDt.min(), df.tWarnDt.max())
  return

def plot_one_acceleration(arel, df, ax, verbose=False):
  # ax.plot(df.dx.values, df.vrel.values, 'b.', zs=df.tWarnDt.values, ms=10.0)
  # plot NCAP 50/40/aObst in red
  for name, df_gb_name in df.groupby('name'):
    dx = df_gb_name.dx.values
    vrel = df_gb_name.vrel.values
    dt = df_gb_name.tWarnDt.values
    rgba_colors = np.zeros( (dt.size,4) )
    # plot NCAP 50/40/aObst in red
    color_chn = 0 if 'ev50rv0ra0d40' in name else 2 # color = 'r' if 'ev50rv0ra0d40' in name else 'b'
    rgba_colors[:,color_chn] = 1.0
    mask = create_mask(df_gb_name)
    alphas = np.where(mask, 1.0, 0.05)
    rgba_colors[:, 3] = alphas
    ax.scatter(dx, vrel, zs=dt, color=rgba_colors)
  # linear regression with least-squares
  # mask = create_mask(df)
  # A = lin_regr_ls(df[mask], ['dx', 'vrel'], 'tWarnDt')
  # if verbose:
    # print 'c0,c1,c2 = ', A
  # # plot the plane
  # plot_plane(df, A, ax)
  return


class View(iView):
  def check(self):
    assert os.path.isfile(TEST_SUMMARY_FILE), "`%s` does not exist" % TEST_SUMMARY_FILE
    return

  def fill(self):
    df = pd.read_csv(TEST_SUMMARY_FILE, sep=';')
    return df

  def view(self, df):
    mn = MatplotlibNavigator("Delta time for starting warning")
    self.sync.addStaticClient(mn)
    fig = mn.fig
    ax = fig.gca(projection='3d')
    ax.set_xlabel("dx [m]"); ax.set_ylabel("vxRel [m/s]"); ax.set_zlabel("Dt [s]")
    for arel, df_gb_arel in df.groupby('arel'):
      # if arel != -2.0: continue
      plot_one_acceleration(arel, df_gb_arel, ax)
    # A = lin_regr_ls(df, ['dx', 'vrel', 'arel'], 'tWarnDt')
    return
