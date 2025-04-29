# -*- dataeval: init -*-
import numpy
import os

import interface
import datavis
from view_aebs_main import _add_dots, querystr

DESC_SIGNALS = {
  "BrakePedPos": {
    "FLR20": {
      "RAIL": ["(EBC1_0B, EBC1_BrkPedPos_0B)",],
      "FLR20": ["(EBC1_0B, EBC1_BrkPedPos_0B)",],
      },
    },
  "SteerWhlAngle": {
    "FLR20": {
      "RAIL": ["(VDC2_0B, VDC2_SteerWhlAngle_0B)",],
      "FLR20": ["(VDC2_0B, VDC2_SteerWhlAngle_0B)",],
      },
    },
  "AEBSmainSw": {
    "FLR20": {
      "RAIL": ["(AEBS2_21, AEBS2_DriverActDemand_21)",],
      "FLR20": ["(AEBS2_21, AEBS2_DriverActDemand_21)",],
      },
    },
  "APkickdownSw": {
    "FLR20": {
      "RAIL": ["(EEC2_00, EEC2_APkickdwnSw_00)",],
      "FLR20": ["(EEC2_00, EEC2_APkickdwnSw_00)",],
      },
    },
  "TurnSigSw": {
    "FLR20": {
      "RAIL": ["(OEL_21, OEL_TurnSigSw_21)",],
      "FLR20": ["(OEL_21, OEL_TurnSigSw_21)",],
      },
    },
  }

PLOT_PROPS = {'BrkPedPos': {'ylim': (-10.0, 110.0),
                            'yticks': numpy.arange(0.0, 110.0, 10.0)},
              'SteerWhlAngle': {'ylim': (-10.5, 10.5),
                                'yticks': numpy.arange(-8.0, 10.0, 2.0)},
              'AEBSmainSw': {'ylim': (-0.5, 1.5),
                             'yticks': [0, 1]},
              'APkickdwnSw': {'ylim': (-0.5, 1.5),
                              'yticks': [0, 1]},
              'TurnSigSw': {'ylim': (-0.5, 2.5),
                            'yticks': [0, 1]},}

init_params = {
  'FLR20_RAIL': dict(sensor='AC100', algo='RAIL'),
  'FLR20_KB': dict(sensor='AC100', algo='KB'),
  'FLR20_FLR20': dict(sensor='AC100', algo='FLR20'),
}


class AC100:
  """
  AC100-specific parameters and functions.
  """
  permaname = 'AC100'
  productname = 'FLR20'


class KB:
  sgn_group=[{'AEBSState': ('AEBS1_2A', 'AEBSState_2A'),
              'BrkPedPos': ('EBC1_0B', 'EBC1_BrkPedPos_0B'),
              'SteerWhlAngle': ('VDC2_0B', 'VDC2_SteerWhlAngle_0B'),
              'AEBSmainSw': ('AEBS2_2A', 'AEBSMainSwitch_2A'),
              'APkickdwnSw': ('EEC2_00', 'EEC2_APkickdwnSw_00'),
              'TurnSigSw': ('OEL_21', 'OEL_TurnSigSw_21')},]


class FLR20:
  sgn_group=[{'AEBSState': ('AEBS1_2A', 'AEBSState_2A'),
              'BrkPedPos': ('EBC1_0B', 'EBC1_BrkPedPos_0B'),
              'SteerWhlAngle': ('VDC2_0B', 'VDC2_SteerWhlAngle_0B'),
              'AEBSmainSw': ('AEBS2_2A', 'AEBSMainSwitch_2A'),
              'APkickdwnSw': ('EEC2_00', 'EEC2_APkickdwnSw_00'),
              'TurnSigSw': ('OEL_21', 'OEL_TurnSigSw_21')},]


class RAIL:
  sgn_group=[{'AEBSState': ('AEBS1', 'Adv_Emergency_Braking_Sys_State'),
              'BrkPedPos': ('EBC1_0B', 'EBC1_BrkPedPos_0B'),
              'SteerWhlAngle': ('VDC2_0B', 'VDC2_SteerWhlAngle_0B'),
              'AEBSmainSw': ('AEBS2_21', 'AEBS2_DriverActDemand_21'),
              'APkickdwnSw': ('EEC2_00', 'EEC2_APkickdwnSw_00'),
              'TurnSigSw': ('OEL_21', 'OEL_TurnSigSw_21')},
             {'AEBSState': ('AEBS1_2A', 'AEBS1_AEBSState_2A'),
              'BrkPedPos': ('EBC1_0B', 'EBC1_BrkPedPos_0B'),
              'SteerWhlAngle': ('VDC2_0B', 'VDC2_SteerWhlAngle_0B'),
              'AEBSmainSw': ('AEBS2_21', 'AEBS2_DriverActDemand_21'),
              'APkickdwnSw': ('EEC2_00', 'EEC2_APkickdwnSw_00'),
              'TurnSigSw': ('OEL_21', 'OEL_TurnSigSw_21')},]


def explain(sensor_productname, algo_name):
  if sensor_productname != "FLR20" and algo_name not in ["RAIL", "FLR20"]:
    raise NotImplementedError  # TODO: add description
  
  from collections import OrderedDict
  
  from reportlab.platypus import Paragraph, Spacer
  from reportlab.lib.styles import getSampleStyleSheet
  from reportlab.lib.pagesizes import cm
  
  from datalab.tygra import ListItem, bold, italic
  
  styles = getSampleStyleSheet()
  story = []
  
  ptext = """
    The driver override evaluation plot shows several signals to help to analyze
    the reaction of AEBS on driver override.<br/>
    The selected area indicates the AEBS cascade, or more precisely, the
    period of the warning. The colored dots represent the beginning
    of the different phases.
  """
  story.append(Paragraph(ptext, styles['Normal']))
  story.append(Spacer(0, 0.5*cm))
  
  story.append(Paragraph(bold("Signals:"), styles['Normal']))
  
  desc = OrderedDict([(
    "BrakePedPos",
    OrderedDict([("Meaning", "Brake pedal position given in [%]."),
                 ("Source", "Electronic brake controller"),
                 ("Signals", ", ".join(DESC_SIGNALS["BrakePedPos"][sensor_productname][algo_name]))
    ])), (
    "SteerWhlAngle",
    OrderedDict([("Meaning", "Steering wheel angle given in [rad]."),
                 ("Source", "Vehicle dynamic stability controller"),
                 ("Signals", ", ".join(DESC_SIGNALS["SteerWhlAngle"][sensor_productname][algo_name]))
    ])), (
    "AEBSmainSw",
    OrderedDict([("Meaning", "AEBS main switch that tells if the AEBS was on or off."),
                 ("Source", "FLR20 AEBS"),
                 ("Signals", ", ".join(DESC_SIGNALS["AEBSmainSw"][sensor_productname][algo_name]))
    ])), (
    "APkickdownSw",
    OrderedDict([("Meaning", "Accelerator pedal kickdown switch."),
                 ("Source", "Electronic engine controller"),
                 ("Signals", ", ".join(DESC_SIGNALS["APkickdownSw"][sensor_productname][algo_name]))
    ])), (
    "TurnSigSw",
    OrderedDict([("Meaning", "Brake pedal position given in [%]."),
                 ("Source", "Electronic brake controller"),
                 ("Signals", ", ".join(DESC_SIGNALS["TurnSigSw"][sensor_productname][algo_name]))
    ])),])
  
  for signal, details in desc.iteritems():
    story.append(ListItem(bold(signal), styles['Normal'], level=0))
    for k, v in details.iteritems():
      story.append(ListItem("%s: %s"%(italic(k), v), styles['Normal'], level=1))
  ptext = """
    If any of the signals above is missing from the plots then that signal was
    missing.
  """
  story.append(Paragraph(ptext, styles['Normal']))
  return story


class View(interface.iView):
  def init(self, sensor, algo):
    assert sensor in globals(), "parameter class for %s not defined" % sensor
    assert algo in globals(), "parameter class for %s not defined" % algo
    self.sensor = globals()[sensor]
    self.algo = globals()[algo]
    return
  
  def check(self):
    source = self.get_source()
    group = source.filterSignalGroups(self.algo.sgn_group)
    group = source.selectFilteredSignalGroup(group)
    return group
  
  def fill(self, group):
    # load data from database (if any)
    measname = os.path.basename(self.get_source().FileName)
    int_data = self.get_batch().query(querystr, measname=measname)
    cascade_limits = [timestamps[0:2] for timestamps in int_data]
    warning_starts = [timestamps[2] for timestamps in int_data]
    partbrk_starts = [timestamps[3] for timestamps in int_data]
    emerbrk_starts = [timestamps[4] for timestamps in int_data]
    dots = (warning_starts, partbrk_starts, emerbrk_starts)
    return group, cascade_limits, dots
  
  def view(self, group, cascade_limits, dots):
    time = group.get_time('AEBSState')
    sgn_values = {}
    sgn_units = {}
    for sgn_name in group.keys():
      if sgn_name != 'AEBSState':
        _, sgn_values[sgn_name], sgn_units[sgn_name] =\
            group.get_signal_with_unit(sgn_name, ScaleTime=time)
    
    title = "%s driver override signals" % self.sensor.productname
    pn = datavis.cPlotNavigator(title=title)
    for sgn_name, sgn_value in sgn_values.iteritems():
      ax = pn.addAxis(ylabel=sgn_name, ylim=PLOT_PROPS[sgn_name]['ylim'])
      ax.set_yticks(PLOT_PROPS[sgn_name]['yticks'])
      pn.addSignal2Axis(ax, sgn_name, time, sgn_value,
                        unit=sgn_units[sgn_name], displayscaled=False)
      _add_dots(ax, time, sgn_value, *dots)
    
    # xlabel
    ax.set_xlabel("time [s]")
    # customize and register plotnavigator
    pn.setUserWindowTitle(title)
    for start, end in cascade_limits:
      for ax in pn.fig.axes:
        # highlight AEBS cascade
        ax.axvspan(start, end, facecolor='b', alpha=0.2)
    self.get_sync().addClient(pn)
    return
