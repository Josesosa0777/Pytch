import numpy as np
import os
import sqlite3

import datavis
import interface
from measparser.signalgroup import SignalGroupError

class cParameter(interface.iParameter):
  def __init__(self, zoom):
    self.zoom = zoom
    self.genKeys()
    return

# instantiation of module parameters
AUTO_ZOOM = cParameter(None)
ZOOM_LEVEL_07 = cParameter(7)
ZOOM_LEVEL_08 = cParameter(8)
ZOOM_LEVEL_09 = cParameter(9)
ZOOM_LEVEL_10 = cParameter(10)
ZOOM_LEVEL_11 = cParameter(11)
ZOOM_LEVEL_12 = cParameter(12)
ZOOM_LEVEL_13 = cParameter(13)
ZOOM_LEVEL_14 = cParameter(14)
ZOOM_LEVEL_15 = cParameter(15)
ZOOM_LEVEL_16 = cParameter(16)


class cView(interface.iView):
  def check(self):
    batch = self.get_batch()
    try:
      start = batch.get_last_entry_start()
    except AssertionError, error:
      raise SignalGroupError(error.message)
    map_workspace_group =\
        batch.filter(start=start, type='measproc.FileWorkSpace',
                     class_name='dataevalaebs.searchAEBSWarnEval_Map.cSearch',
                     title='AEBS-MapData', order='measurement')
    report_group =\
        batch.filter(start=start, type='measproc.cFileReport',
                     class_name='dataevalaebs.searchAEBSWarnEval_AC100Warnings.cSearch',
                     order='measurement')
    return map_workspace_group, report_group

  def fill(self, map_workspace_group, report_group):
    return map_workspace_group, report_group

  def view(self, param, map_workspace_group, report_group):
    mapman = self.get_mapman()
    Client1 = datavis.StaticMapNavigator(mapman, title="Course")
    Client2 = datavis.StaticMapNavigator(mapman, title="Warnings")
    for text in Client1.fig.texts:
      text.set_visible(False)
    for text in Client2.fig.texts:
      text.set_visible(False)
    interface.Sync.addStaticClient(Client1)
    interface.Sync.addStaticClient(Client2)

    batch = self.get_batch()
    longitude = []
    latitude = []
    meas_with_GPS = []
    for entry in map_workspace_group:
      workspace = batch.wake_entry(entry)
      lon = workspace.workspace['Longitude']
      lat = workspace.workspace['Latitude']
      lon = lon.flatten()
      lat = lat.flatten()
      mask = np.logical_and(lat != 0.0, lon != 0.0)
      longitude.append(lon[mask])
      latitude.append(lat[mask])
      meas_path = batch.get_entry_attr(entry, 'fullmeas')
      meas_name = os.path.basename(meas_path)
      meas_with_GPS.append(meas_name)

    warn_db_create =\
        ("CREATE TABLE warn_intervals "
         "(meas_name TEXT, start_time REAL, end_time REAL, "
         "start_index INTEGER, end_index INTEGER, stationary INTEGER);")
    warn_db_insert = "INSERT INTO warn_intervals VALUES (?, ?, ?, ?, ?, ?);"
    warn_db_select_meas = ("SELECT meas_name FROM warn_intervals "
                           "ORDER BY meas_name;")
    warn_db_select_ints = ("SELECT start_time, end_time, start_index, "
                           "end_index, stationary FROM "
                           "warn_intervals WHERE meas_name = ? "
                           "ORDER BY start_time;")

    con = sqlite3.connect(':memory:')
    cur = con.cursor()
    cur.execute(warn_db_create)

    for entry in report_group:
      rep = batch.wake_entry(entry)
      time = np.load(rep.getTimeFile())
      title_data_l = rep.getTitle().lower().split("-")
      meas_path = batch.get_entry_attr(entry, 'fullmeas')
      meas_name = os.path.basename(meas_path)
      if meas_name in meas_with_GPS:
        if len(title_data_l) > 2:
          if title_data_l[1] == "activity":
            for interval in rep.IntervalList:
              start, end = interval
              cur.execute(warn_db_insert,
                          (meas_name, time[start], time[end], start, end,
                           rep.checkVote(interval, 'Stationary')))

    sel_meas = cur.execute(warn_db_select_meas)
    sel_meas = sel_meas.fetchall()
    if sel_meas:
      sel_meas = list(set(zip(*sel_meas)[0]))
      sel_meas.sort()
    else:
      sel_meas = []
    warn_intervals =\
        {'stationary': {'warning': [m[:] for m in [[]] * len(meas_with_GPS)],
                        'partial': [m[:] for m in [[]] * len(meas_with_GPS)],
                        'emergency': [m[:] for m in [[]] * len(meas_with_GPS)]},
         'moving': {'warning': [m[:] for m in [[]] * len(meas_with_GPS)],
                    'partial': [m[:] for m in [[]] * len(meas_with_GPS)],
                    'emergency': [m[:] for m in [[]] * len(meas_with_GPS)]}}
    for meas in sel_meas:
      prev_end = 0.0
      cur.execute(warn_db_select_ints, (meas,))
      int_data = cur.fetchall()
      meas_idx = meas_with_GPS.index(meas)
      warn_ints = []
      part_ints = []
      emer_ints = []
      for start_time, end_time, start_index, end_index, stationary in int_data:
        alarm_length = end_time - start_time
        if alarm_length < 0.6:
          warn_ints.append((start_index, end_index))
        elif 0.6 < alarm_length and alarm_length < 1.4:
          part_ints.append((start_index, end_index))
        else:
          emer_ints.append((start_index, end_index))

        if stationary:
          warnings = warn_intervals['stationary']
        else:
          warnings = warn_intervals['moving']
        if abs(start_time - prev_end) > 2.0:
          warnings['warning'][meas_idx].extend(warn_ints)
          warnings['partial'][meas_idx].extend(part_ints)
          warnings['emergency'][meas_idx].extend(emer_ints)
          warn_ints = []
          part_ints = []
          emer_ints = []
        if start_time - prev_end < 2.0:
          if warnings['warning'][meas_idx]:
            tmp_warn = warnings['warning'][meas_idx].pop()
            warn_ints.append(tmp_warn)
            tmp_list = []
            for warn_int in warn_ints:
              start, end = warn_int
              tmp_list.append((end-start, warn_int))
            tmp_list.sort(key=lambda row: row[0])
            warnings['warning'][meas_idx].append(tmp_list[-1][1])
          if warnings['partial'][meas_idx]:
            tmp_part = warnings['partial'][meas_idx].pop()
            part_ints.append(tmp_part)
            tmp_list = []
            for part_int in part_ints:
              start, end = part_int
              tmp_list.append((end-start, part_int))
            tmp_list.sort(key=lambda row: row[0])
            warnings['partial'][meas_idx].append(tmp_list[-1][1])
          if warnings['emergency'][meas_idx]:
            tmp_emer = warnings['emergency'][meas_idx].pop()
            emer_ints.append(tmp_emer)
            tmp_list = []
            for emer_int in emer_ints:
              start, end = emer_int
              tmp_list.append((end-start, emer_int))
            tmp_list.sort(key=lambda row: row[0])
            warnings['emergency'][meas_idx].append(tmp_list[-1][1])
          warn_ints = []
          part_ints = []
          emer_ints = []

        prev_end = end_time

    marker_styles =\
        {'stationary':\
            {'warning': {'event_color': 'Yellow', 'event_marker_size': 100.0,
                         'event_marker_style': 's'},
             'partial': {'event_color': 'Orange', 'event_marker_size': 100.0,
                         'event_marker_style': 's'},
             'emergency': {'event_color': 'Red', 'event_marker_size': 100.0,
                           'event_marker_style': 's'}},
         'moving':\
            {'warning': {'event_color': 'Yellow', 'event_marker_size': 100.0,
                         'event_marker_style': 'D'},
             'partial': {'event_color': 'Orange', 'event_marker_size': 100.0,
                         'event_marker_style': 'D'},
             'emergency': {'event_color': 'Red', 'event_marker_size': 100.0,
                           'event_marker_style': 'D'}}}

    Client1.set_route(longitude, latitude, param.zoom)
    Client1.draw_arrow()
    Client2.set_route(longitude, latitude, param.zoom)
    for stance in warn_intervals.keys():
      for warn_type in warn_intervals[stance].keys():
        Client2.set_markers(warn_intervals[stance][warn_type],
                            "%s %s" % (stance, warn_type),
                            **marker_styles[stance][warn_type])
