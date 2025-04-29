# -*- dataeval: init -*-

"""
TBD
"""

import numpy as np

import datavis
from interface import iView

mps2kph = lambda v: v*3.6

def add_dots(dot_indices, time, signal, ax):
  for i in dot_indices:
    if i is None:
      continue
    val = signal[i]
    t = time[i]
    textoffset = (-10, 5)
    ax.plot(time[i], val, 'r.')
    text = "%.1f" % val
    ax.annotate(text, xy=(t,val),
        xytext=textoffset, textcoords='offset points')
  return

def add_dots_aebsstate(dot_indices, time, signal, ax):
  i_emer = dot_indices[2]
  for i in dot_indices:
    if i is None:
      continue
    val = signal[i]
    t = time[i]
    ax.plot(time[i], val, 'r.')
    if i_emer is not None:
      textoffset = (-10, 5)
      text = "%.1f s" % abs(time[i_emer] - time[i])
      ax.annotate(text, xy=(t,val),
          xytext=textoffset, textcoords='offset points')
  return

def find_index(cond, i_start=0):
  if i_start is None:
    return None
  mask = np.zeros(cond.size, dtype=bool)  # zeros_like does not work well with masked array (shallow copy from mask)
  mask[i_start:] = True
  if not np.ma.any(mask & cond):
    return None
  return np.ma.where(mask & cond)[0][0]

class View(iView):
  dep = 'calc_j1939_egomotion@aebs.fill',
  optdep = 'fill_flr20_aeb_track@aebs.fill',
  
  def check(self):
    sgs = [{
      "aebs_state": ("AEBS1_2A", "AEBS1_AEBSState_2A"),
      "xbr_demand": ("XBR_2A", "XBR_ExtAccelDem_2A"),
    }]
    group = self.source.selectSignalGroup(sgs)
    return group
  
  def view(self, group):
    base_title = 'AEBS cascade'
    title = "%s\n%s" % (base_title, self.source.getBaseName())
    pn = datavis.cPlotNavigator(title=title)
    # quick hack to store window position independently from the measurement
    pn.createWindowId = lambda x,title=None: base_title
    pn.getWindowId = lambda: base_title
    pn._windowId = pn.createWindowId(None)
    
    # process signals
    t = group.get_time("aebs_state")
    ego = self.modules.fill(self.dep[0]).rescale(t)
    if self.optdep[0] in self.passed_optdep:
      track = self.modules.fill(self.optdep[0]).rescale(t)
    else:
      self.logger.warning("Obstacle data not available")
      track = None
    
    # AEBS state
    yticks = {0: "not ready", 1: "temp. n/a", 2: "deact.", 3: "ready",
              4: "override", 5: "warning", 6: "part. brk.", 7: "emer. brk.",
              14: "error", 15: "n/a"}
    yticks = dict( (k, "(%s) %d"%(v,k)) for k, v in yticks.iteritems() )
    ax = pn.addAxis(ylabel="state", yticks=yticks)
    ax.set_ylim((-1.0, 8.0))
    time00, value00, unit00 = group.get_signal_with_unit("aebs_state", ScaleTime=t)
    ###
    i_warn = find_index(value00 == 5)
    i_part = find_index(value00 == 6, i_warn)
    i_emer = find_index(value00 == 7, i_part)
    if track is not None:
      i_end = find_index((track.dx < 1.0) | (ego.vx < 1.0), i_warn)
    else:
      i_end = find_index(ego.vx < 1.0, i_warn)
    if i_warn is not None and i_part is not None and abs(0.6-(t[i_part]-t[i_warn])) < 0.05:
      n_extra_cycles = 4
      self.logger.info("Warning phase in AEBS state is enlarged with %d cycles" % n_extra_cycles)
      value00 = value00.copy()
      value00[i_warn-n_extra_cycles : i_warn] = 5
      i_warn -= n_extra_cycles
    dots = (i_warn, i_part, i_emer, i_end)
    ###
    pn.addSignal2Axis(ax, "AEBSState", time00, value00, unit=unit00)
    add_dots_aebsstate(dots, t, value00, ax)
    # speed
    ax = pn.addAxis(ylabel='speed', ylim=(-5.0, 95.0))
    pn.addSignal2Axis(ax, 'host speed', t, mps2kph(ego.vx), unit='km/h')
    add_dots(dots, t, mps2kph(ego.vx), ax)
    if track is not None:
      track_vx_abs = ego.vx + track.vx
      pn.addSignal2Axis(ax, 'target speed', t, mps2kph(track_vx_abs), unit='km/h', color='r')
      add_dots(dots, t, mps2kph(track_vx_abs), ax)
    # dx
    if track is not None:
      ax = pn.addAxis(ylabel='long. dist.', ylim=(0.0, 80.0))
      pn.addSignal2Axis(ax, 'dx', t, track.dx, unit='m')
      add_dots(dots, t, track.dx, ax)
    # acceleration
    ax = pn.addAxis(ylabel='accel.', ylim=(-11.0, 11.0))
    time04, value04, unit04 = group.get_signal_with_unit("xbr_demand", ScaleTime=t)
    pn.addSignal2Axis(ax, "XBR_ExtAccelDem", time04, value04, unit='m/s^2', color='r')
    pn.addSignal2Axis(ax, 'host accel.', t, ego.ax, unit='m/s^2')
    
    ax.set_xlabel("time [s]")
    
    self.sync.addClient(pn)
    
    # print info
    texts = []
    NA = "n/a"
    
    val = "%.2f km/h" % mps2kph(ego.vx[i_warn]) if i_warn is not None else NA
    texts.append("Initial host speed: %s" % val)
    
    val = "%.2f km/h" % mps2kph(track.vx[i_warn]+ego.vx[i_warn]) if i_warn is not None and track is not None else NA
    texts.append("Initial target speed: %s" % val)
    
    val = "%.2f km/h" % mps2kph(ego.vx[i_end]) if i_end is not None else NA
    texts.append("Impact host speed: %s" % val)
    
    val = "%.2f s" % (-track.dx[i_emer]/track.vx[i_emer]) if i_emer is not None and track is not None else NA
    texts.append("TTC(EBP): %s" % val)
    
    val = "%.2f s" % (t[i_emer] - t[i_warn]) if i_emer is not None and i_warn is not None else NA
    texts.append("t(EBP)-t(WP1): %s" % val)
    
    val = "%.2f s" % (t[i_emer] - t[i_part]) if i_emer is not None and i_warn is not None else NA
    texts.append("t(EBP)-t(WP2): %s" % val)
    
    val = "%.2f km/h" % mps2kph(ego.vx[i_warn] - ego.vx[i_emer]) if i_warn is not None and i_emer is not None else NA
    texts.append("v(WP1)-v(EBP): %s" % val)
    
    val = "%.2f km/h" % mps2kph(ego.vx[i_warn] - ego.vx[i_end]) if i_warn is not None and i_end is not None else NA
    texts.append("v(WP1)-v(impact): %s" % val)
    
    print "=" * 50
    print "\n".join(texts)
    print "=" * 50
    return
