# -*- dataeval: init -*-

from itertools import cycle
from datetime import datetime, timedelta

import numpy as np

import datavis
from interface import iView

init_params = {
  'yearly'  : dict(time_class='%Y'),
  'monthly' : dict(time_class='%Y-%m'),
  'weekly'  : dict(time_class='%Y-%m cw%W'),
  'daily'   : dict(time_class='%Y-%m-%d'),
}

class View(iView):
  def init(self, time_class):
    self.time_class = time_class
    return
  
  def check(self):
    ws_group = self.batch.filter(type='measproc.FileWorkSpace', title="quantity-histogram")
    assert ws_group, "no appropriate workspace found"
    return ws_group
  
  def view(self, ws_group):
    cum_hist = {}
    for entry in ws_group:
      # process time
      start_str = self.batch.get_entry_attr(entry, 'meas_start')
      start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S') - timedelta(hours=4)
      start_class = start.strftime(self.time_class)
      # process data
      workspace = self.batch.wake_entry(entry).workspace
      hist = workspace['hist']
      if start_class not in cum_hist:
        cum_hist[start_class] = np.zeros_like(hist)
      cum_hist[start_class] += hist
    else:
      bin_edges = workspace['bin_edges']  # hack to query bin_edges only once
    
    # create title
    for param in init_params:
      if init_params[param]['time_class'] == self.time_class:
        time_class_word = param
        break
    title = "FLR20 target number distributions - %s" % time_class_word
    # create navigator
    nav = datavis.MatplotlibNavigator(title=title)
    nav.setUserWindowTitle(title)
    ax = nav.fig.add_subplot(111, projection='3d')
    # create histogram
    bar_width = 0.8
    xs = bin_edges[:-1]-bar_width/2.0
    start_classes = sorted(cum_hist)
    colors = cycle(('r', 'g', 'b', 'y'))
    for z, start_class in enumerate(start_classes):
      c = colors.next()
      ax.bar(xs, cum_hist[start_class], zs=z, zdir='y', color=c, width=bar_width)
    ax.set_xlabel("#targets")
    ax.set_zlabel("#cycles")
    ax.set_yticks(xrange(len(start_classes)))
    ax.set_yticklabels(start_classes)
    
    # print numbers
    n_total_cycles = sum(np.sum(v)      for v in cum_hist.itervalues())
    n_gt20t_cycles = sum(np.sum(v[21:]) for v in cum_hist.itervalues())
    perc = float(n_gt20t_cycles) / n_total_cycles * 100.0
    self.logger.info("Total number of cycles: %d" % n_total_cycles)
    self.logger.info("Number of cycles with >20 targets: %d" % n_gt20t_cycles)
    self.logger.info("Percentage of >20 targets: %.1f" % perc)
    
    self.sync.addStaticClient(nav)
    return
