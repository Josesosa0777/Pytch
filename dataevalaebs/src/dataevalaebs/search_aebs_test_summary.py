# -*- dataeval: init -*-

import numpy
from collections import OrderedDict

import measproc
import interface
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report
from search_fwdvehicledet import iter_events

EGO_SPEED_MIN = 10.0 / 3.6
REL_SPEED_THRESHOLD = - 10.0 / 3.6 # ego-vehicle is at least 10 km/h faster
SAFETY_DIST = 2.5
BP_THRESHOLD = 10.0
STEERING_THRESHOLD = 0.04
OVERRIDE_DELAY_THRESHOLD = 0.3
AEBS_OVERRIDEN_RATIO_MIN = 0.9
ICB_EXIT_TIME_MARGIN = 0.1
OBJ_SIM_DIST_THRESHOLD = 2.3
TEST_TYPE_DICT = {'undefined': 0,
                  'homologation - moving': 1,
                  'homologation - stationary': 2,
                  'driver override': 3,
                  'object cut in': 4,
                  'object cut out': 5,
                  'alley way': 6,
                  'exit ICB': 7,
                  'error handler - interface': 8,
                  'error handler - function': 9}

init_params = {'FLR20_RAIL': dict(sensor='AC100', algo='RAIL'),
               'FLR20_KB':   dict(sensor='AC100', algo='KB'),
               'FLR20_FLR20': dict(sensor='AC100', algo='FLR20')}


class AC100(object):
  """
  AC100-specific parameters.
  """
  ego_fill = 'calc_flr20_egomotion@aebs.fill'
  aebobj_fill = 'fill_flr20_aeb_track@aebs.fill'
  trackobj_fill = 'fill_flr20_raw_tracks@aebs.fill'
  radar_status_sgn_group =\
      [{"SWcharVer1": ("General_radar_status", "software_version_char_1"),
        "SWcharVer2": ("General_radar_status", "software_version_char_2"),
        "SWcharVer3": ("General_radar_status", "software_version_char_3"),
        "SWcharVer4": ("General_radar_status", "software_version_char_4"),
        "SWcharVer5": ("General_radar_status", "software_version_char_5"),
        "SWcharVer6": ("General_radar_status", "software_version_char_6"),
        "SWcharVer7": ("General_radar_status", "software_version_char_7"),
        "SWcharVer8": ("General_radar_status", "software_version_char_8")},]


class KB(object):
  """
  KB AEBS algorithm specific parameters. - old version
  """
  algo_fill = 'calc_aebs_phases@aebs.fill'
  do_sgn_group = [{"BrkPedPos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
                   "SteerWhlAngle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                   "TurnSignalSw": ("OEL_21", "OEL_TurnSigSw_21"),
                   "DriverActDemand": ("AEBS2_2A", "AEBSMainSwitch_2A"),
                   "APkickdwnSw": ("EEC2_00", "EEC2_APkickdwnSw_00")},]
  aeb_sgn_group = [{"ExtAccelDem": ("XBR_2A", "XBR_ExtAccelDem_2A"),
                    "AEBSState": ("AEBS1_2A", "AEBSState_2A")},]


class FLR20(object):
  """
  KB AEBS algorithm specific parameters.
  """
  algo_fill = 'calc_flr20_aebs_phases-radar@aebs.fill'
  do_sgn_group = [{"BrkPedPos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
                   "SteerWhlAngle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                   "TurnSignalSw": ("OEL_21", "OEL_TurnSigSw_21"),
                   "DriverActDemand": ("AEBS2_2A", "AEBSMainSwitch_2A"),
                   "APkickdwnSw": ("EEC2_00", "EEC2_APkickdwnSw_00")},]
  aeb_sgn_group = [{"ExtAccelDem": ("XBR_2A", "XBR_ExtAccelDem_2A"),
                    "AEBSState": ("AEBS1_2A", "AEBSState_2A")},]


class RAIL(object):
  """
  AEBS algorithm parameters that can be used with RAIL measurements.
  """
  algo_fill = 'calc_flr20_aebs_phases-rail@aebs.fill'
  do_sgn_group = [{"BrkPedPos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
                   "SteerWhlAngle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                   "TurnSignalSw": ("OEL_21", "OEL_TurnSigSw_21"),
                   "DriverActDemand": ("AEBS2_2A", "AEBSMainSwitch_2A"),
                   "APkickdwnSw": ("EEC2_00", "EEC2_APkickdwnSw_00")},
                  {"BrkPedPos": ("EBC1_0B", "EBC1_BrkPedPos_0B"),
                   "SteerWhlAngle": ("VDC2_0B", "VDC2_SteerWhlAngle_0B"),
                   "TurnSignalSw": ("OEL_21", "OEL_TurnSigSw_21"),
                   "DriverActDemand": ("AEBS2_21", "AEBS2_DriverActDemand_21"),
                   "APkickdwnSw": ("EEC2_00", "EEC2_APkickdwnSw_00")},]
  aeb_sgn_group = [{"ExtAccelDem": ("XBR_2A", "XBR_ExtAccelDem_2A"),
                    "AEBSState": ("AEBS1_2A", "AEBSState_2A")},
                   {"ExtAccelDem": ("XBR_2A", "XBR_ExtAccelDem_2A"),
                    "AEBSState": ("AEBS1_2A", "AEBS1_AEBSState_2A")},]
  testtype_sgn_group = [{"RaIL_testtype": ("Environment", "RaIL_testtype")},]
  overr_blk_sgn_grp = [{ "BlockingTime": ("CCP", "kbaebsParaebs.tBlockingTimeDueToOverride")},]


class Search(interface.iSearch):
  def init(self, sensor, algo):
    assert sensor in globals(), "parameter class for %s not defined" % sensor
    assert algo in globals(), "parameter class for %s not defined" % algo
    self.sensor = globals()[sensor]
    self.algo = globals()[algo]
    self.algo_name = algo
    self.dep = (self.sensor.ego_fill, self.algo.algo_fill,
                self.sensor.aebobj_fill, self.sensor.trackobj_fill)
    return

  def _create_report(self, time, title, radar_sw_ver):
    batch = self.get_batch()
    votes = batch.get_labelgroups('result')
    empty_intervals = cIntervalList(time)
    report = Report(empty_intervals, title, votes=votes)
    report.setEntryComment(radar_sw_ver)
    return report

  def _vote_intervals(self, report, interval, vote, comment=''):
    if comment is not None:
      index = report.addInterval(interval)
      report.vote(index, 'result', vote)
      report.setComment(index, comment)
    return

  def _find_alley_way_obj_int(self, ego, tracks):
    source = self.get_source()
    # first, look for stationary objects either on the left or right side
    # that are being approached
    left_ints = {}
    right_ints = {}
    for idx, track in tracks.iteritems():
      ego_moving = ego.vx >= EGO_SPEED_MIN
      range_mask = numpy.zeros_like(track.time)
      range_diff = numpy.diff(track.range)
      range_mask[:-1] = range_diff < 0
      angle_mask = numpy.zeros_like(track.time)
      angle_diff = numpy.abs(numpy.diff(track.angle))
      angle_mask[:-1] = angle_diff > 0
      dy_mask = numpy.abs(track.dy) <= OBJ_SIM_DIST_THRESHOLD
      obj_is_appr = numpy.logical_and(range_mask, angle_mask)
      obj_is_appr = numpy.logical_and(dy_mask, obj_is_appr)
      mov_ego_stat_obj = numpy.logical_and(ego_moving, track.mov_state.stat)
      objs_on_left_mask = mov_ego_stat_obj & obj_is_appr & track.lane.left
      objs_on_right_mask = mov_ego_stat_obj & obj_is_appr & track.lane.right
      alley_way_left_int = source.compare(track.time, objs_on_left_mask,
                                          measproc.not_equal, 0)
      if alley_way_left_int.Intervals:
        longest_l_ints = alley_way_left_int.findLongestIntervals()
        left_ints[idx] = cIntervalList(track.time, Intervals=longest_l_ints)
      alley_way_right_int = source.compare(track.time, objs_on_right_mask,
                                           measproc.not_equal, 0)
      if alley_way_right_int.Intervals:
        longest_r_ints = alley_way_right_int.findLongestIntervals()
        right_ints[idx] = cIntervalList(track.time, Intervals=longest_r_ints)

    # then look for objects that are next to each other
    # (their dx values are almost equal)
    alley_way_left_obj_ints = OrderedDict()
    alley_way_right_obj_ints = OrderedDict()
    for right_idx, right_int in right_ints.iteritems():
      for left_idx, left_int in left_ints.iteritems():
        mutual_ints = right_int.intersect(left_int)
        for mutual_start, mutual_end in mutual_ints.Intervals:
          right_dx = tracks[right_idx].dx[mutual_start:mutual_end]
          left_dx = tracks[left_idx].dx[mutual_start:mutual_end]
          if numpy.allclose(right_dx, left_dx, 2, 0):
            mutual_idx = int((mutual_start + mutual_end) / 2)
            l_start, l_end = left_int.findInterval(mutual_idx)
            r_start, r_end = right_int.findInterval(mutual_idx)
            left_obj_ints =\
                alley_way_left_obj_ints.setdefault(left_idx,
                                                   cIntervalList(track.time))
            left_obj_ints.add(l_start, l_end)
            right_obj_ints =\
                alley_way_right_obj_ints.setdefault(right_idx,
                                                    cIntervalList(track.time))
            right_obj_ints.add(r_start, r_end)
    return alley_way_left_obj_ints, alley_way_right_obj_ints

  def _find_impending_aeb_int(self, ego, tracks):
    common_time = tracks[0].time
    imp_aeb_ints = []
    for obj, _, stab_int in iter_events(ego, tracks):
      obj.rescale(common_time)
      stab_ints = cIntervalList(common_time, [stab_int])
      imp_aeb_ints.extend(stab_ints.Intervals)
    imp_aeb_ints = cIntervalList(common_time, Intervals=imp_aeb_ints)
    return imp_aeb_ints

  def _eval_driver_override(self, aebs_active_interval, override_interval,
                            aebs_state, override_blocking_time):
    int_intersection = aebs_active_interval.intersect(override_interval)
    aebs_active_end = aebs_active_interval[0][-1]
    override_start, override_end = override_interval.findInterval(aebs_active_end)
    overr_start_time, _ = override_interval.getTimeInterval(override_start,
                                                            override_end)
    overr_blk_end_time = overr_start_time + override_blocking_time
    override_blk_end = override_interval.getTimeIndex(overr_blk_end_time)
    override_end = min(override_end, override_blk_end)
    delay_is_short = int_intersection.sumTime() <= OVERRIDE_DELAY_THRESHOLD
    state_counts = numpy.bincount(aebs_state[aebs_active_end:override_end])
    state_total_sum = numpy.sum(state_counts)
    # ratio of AEBS1.AEBSstate=4 (system is overridden by driver)
    # in the driver override interval
    if len(state_counts) > 4:
      aebs_overridden_ratio = float(state_counts[4]) / state_total_sum
      aebs_is_overriden = aebs_overridden_ratio >= AEBS_OVERRIDEN_RATIO_MIN
    else:
      aebs_is_overriden = False
    # ratio of AEBS1.AEBSstate=2 (system is deactivated by driver)
    # in the driver override interval
    if len(state_counts) > 2:
      aebs_deactivated_ratio = float(state_counts[2]) / state_total_sum
      aebs_is_deactivated = aebs_deactivated_ratio >= AEBS_OVERRIDEN_RATIO_MIN
    else:
      aebs_is_deactivated = False
    if delay_is_short & (aebs_is_overriden | aebs_is_deactivated):
      result = 'passed'
    else:
      result = 'failed'
    return result

  def _eval_icb_exiting(self, actual_xbr_int, ap_kickdown_int):
    time_margins = [ICB_EXIT_TIME_MARGIN, ICB_EXIT_TIME_MARGIN]
    if not ap_kickdown_int.isEmpty():
      comment = 'ICB with AP kick-down'
      if actual_xbr_int:
        marg_actual_xbr_int = actual_xbr_int.addMargin(TimeMargins=time_margins)
        marg_ap_kickdown_int = ap_kickdown_int.addMargin(TimeMargins=time_margins)
        ap_kickdown_xbr_neighbour =\
            marg_actual_xbr_int.intersect(marg_ap_kickdown_int)
        icb_exit_by_ap = not ap_kickdown_xbr_neighbour.isEmpty()
        if icb_exit_by_ap:
          result = 'passed'
        else:
          result = 'failed'
      else:
        result = 'inconclusive'
    else:
      comment = 'ICB without AP kick-down'
      result = 'passed'
    return comment, result

  def _check_aebs_if_ok(self, aeb_track, ego, warn_int, part_int, emer_int):
    if warn_int:
      if part_int and emer_int:
        warn_part_int = warn_int.union(part_int)
        casc_int = warn_part_int.union(emer_int)

        casc_start, casc_end = casc_int[0]
        stat_or_stopped =\
            numpy.logical_or(aeb_track.mov_state.stat[casc_start:casc_end],
                             aeb_track.mov_state.stopped[casc_start:casc_end])

        warn_start, _ = warn_int[0]
        part_start, part_end = part_int[0]
        emer_start, emer_end = emer_int[0]
        warn_start_time = emer_int.Time[emer_start] - warn_int.Time[warn_start]
        warn_start_ok = round(warn_start_time, 2) >= 1.4
        part_start_time = emer_int.Time[emer_start] - part_int.Time[part_start]
        part_start_ok = round(part_start_time, 2) >= 0.8
        emer_start_ok = aeb_track.ttc[emer_start] <= 3.0
        speed_red_in_part =\
            ego.vx[warn_start] - numpy.min(ego.vx[part_start:part_end])
        speed_red_in_part_ok =\
            speed_red_in_part <= max(15.0 / 3.6, ego.vx[warn_start] * 0.3)

        if numpy.all(stat_or_stopped):
          if numpy.min(ego.vx[emer_start:emer_end]) >= (2.0 / 3.6):
            speed_red_in_emer =\
                ego.vx[warn_start] - numpy.min(ego.vx[emer_start:emer_end])
            speed_red_in_emer_ok = speed_red_in_emer >= (20.0 / 3.6)
          else:
            speed_red_in_emer_ok = True
        else:
          dist_ok = numpy.min(aeb_track.range[emer_start:emer_end]) >= 0.1
          # rel vel is negative if ego is faster than the impending object
          vx_ok = numpy.max(aeb_track.vx[emer_start:emer_end]) >= -2.0
          speed_red_in_emer_ok = dist_ok and vx_ok

        cascade_eval_aspects = {'warning start': warn_start_ok,
                                'part brake start': part_start_ok,
                                'emer brake start': emer_start_ok,
                                'speed red in part': speed_red_in_part_ok,
                                'speed red in emer': speed_red_in_emer_ok}
      elif part_int:
        warn_start, _ = warn_int[0]
        part_start, part_end = part_int[0]
        speed_red_in_part =\
            ego.vx[warn_start] - numpy.min(ego.vx[part_start:part_end])
        speed_red_in_part_ok =\
            speed_red_in_part <= max(15.0 / 3.6, ego.vx[warn_start] * 0.3)

        cascade_eval_aspects = {'warning start': True,
                                'part brake start': True,
                                'emer brake start': False,
                                'speed red in part': speed_red_in_part_ok,
                                'speed red in emer': False}
      else:
        cascade_eval_aspects = {'warning start': True,
                                'part brake start': False,
                                'emer brake start': False,
                                'speed red in part': False,
                                'speed red in emer': False}
    else:
      cascade_eval_aspects = {'warning start': False,
                              'part brake start': False,
                              'emer brake start': False,
                              'speed red in part': False,
                              'speed red in emer': False}
    return cascade_eval_aspects

  def _check_test_type(self, imp_start, imp_end, test_type_sgn):
    if self.algo_name == 'RAIL':
      ret_val = 'undefined'
      if numpy.any(test_type_sgn):
        for ttype, tvalue in TEST_TYPE_DICT.iteritems():
          if numpy.all(test_type_sgn[imp_start:imp_end] == tvalue):
            ret_val = ttype
            break
    else:
      ret_val = None
    return ret_val

  def check(self):
    source = self.get_source()
    droverride_group = source.filterSignalGroups(self.algo.do_sgn_group)
    droverride_group = source.selectFilteredSignalGroup(droverride_group)
    aeb_group = source.selectSignalGroup(self.algo.aeb_sgn_group)
    if self.algo_name == 'RAIL':
      testtype_group =\
          source.selectSignalGroup(self.algo.testtype_sgn_group)
      blk_time_group = source.selectSignalGroup(self.algo.overr_blk_sgn_grp)
    else:
      testtype_group = None
      blk_time_group = None
    radar_stat_group =\
        source.selectSignalGroup(self.sensor.radar_status_sgn_group)
    return droverride_group, aeb_group, testtype_group, blk_time_group, radar_stat_group

  def fill(self, droverride_group, aeb_group, testtype_group, blk_time_group, radar_stat_group):
    modules = self.get_modules()
    source = self.get_source()
    aeb_track = modules.fill(self.sensor.aebobj_fill)
    raw_tracks = modules.fill(self.sensor.trackobj_fill)
    for raw_track in raw_tracks.itervalues():
      raw_track.rescale(aeb_track.time)
    ego = modules.fill(self.sensor.ego_fill)
    ego.rescale(aeb_track.time)
    aebs_phases = modules.fill(self.algo.algo_fill)
    aebs_phases = aebs_phases.rescale(aeb_track.time)

    if 'BrkPedPos' in droverride_group.keys():
      bp_pos = droverride_group.get_value('BrkPedPos', ScaleTime=aeb_track.time)
      bp_pos_on = source.compare(aeb_track.time, bp_pos, measproc.greater,
                                 BP_THRESHOLD)
    else:
      bp_pos_on = cIntervalList(aeb_track.time)

    if 'SteerWhlAngle' in droverride_group.keys():
      steer_whl_angle = droverride_group.get_value('SteerWhlAngle',
                                                   ScaleTime=aeb_track.time)
      steer_whl_angle_on =\
          source.compare(aeb_track.time, steer_whl_angle, measproc.greater,
                         STEERING_THRESHOLD)
    else:
      steer_whl_angle_on = cIntervalList(aeb_track.time)

    if 'TurnSignalSw' in droverride_group.keys():
      turn_sig_sw = droverride_group.get_value('TurnSignalSw',
                                               ScaleTime=aeb_track.time)
      turn_sig_sw_on = source.compare(aeb_track.time, turn_sig_sw,
                                      measproc.not_equal, 0.0)
    else:
      turn_sig_sw_on = cIntervalList(aeb_track.time)

    if 'DriverActDemand' in droverride_group.keys():
      aebs_main_sw = droverride_group.get_value('DriverActDemand',
                                                ScaleTime=aeb_track.time)
      aebs_main_sw_off = source.compare(aeb_track.time, aebs_main_sw,
                                        measproc.equal, 0.0)
    else:
      aebs_main_sw_off = cIntervalList(aeb_track.time)

    if 'APkickdwnSw' in droverride_group.keys():
      ap_kickdown = droverride_group.get_value('APkickdwnSw',
                                               ScaleTime=aeb_track.time)
      ap_kickdown_on = source.compare(aeb_track.time, ap_kickdown,
                                      measproc.not_equal, 0.0)
      ap_kickdown_on = ap_kickdown_on.drop(0.6)
    else:
      ap_kickdown_on = cIntervalList(aeb_track.time)

    ext_acc_dem = aeb_group.get_value('ExtAccelDem', ScaleTime=aeb_track.time)
    ext_acc_dem_on = source.compare(aeb_track.time, ext_acc_dem,
                                    measproc.less, 0.0)

    aebs_state = aeb_group.get_value('AEBSState', ScaleTime=aeb_track.time)

    if testtype_group:
      test_type_sgn = testtype_group.get_value('RaIL_testtype',
                                           ScaleTime=aeb_track.time)
    else:
      test_type_sgn = None

    if blk_time_group:
      override_blocking_time = blk_time_group.get_value('BlockingTime',
                                                        ScaleTime=aeb_track.time)
      # blocking time due to driver override value is constant throughout
      # the measurement
      override_blocking_time = override_blocking_time[0]
      override_blocking_time /= 2048.0   # normalize to seconds
    else:
      override_blocking_time = None

    radar_sw_ver_char1 = radar_stat_group.get_value('SWcharVer1',
                                                    ScaleTime=aeb_track.time)
    radar_sw_ver_char2 = radar_stat_group.get_value('SWcharVer2',
                                                    ScaleTime=aeb_track.time)
    radar_sw_ver_char3 = radar_stat_group.get_value('SWcharVer3',
                                                    ScaleTime=aeb_track.time)
    radar_sw_ver_char4 = radar_stat_group.get_value('SWcharVer4',
                                                    ScaleTime=aeb_track.time)
    radar_sw_ver_char5 = radar_stat_group.get_value('SWcharVer5',
                                                    ScaleTime=aeb_track.time)
    radar_sw_ver_char6 = radar_stat_group.get_value('SWcharVer6',
                                                    ScaleTime=aeb_track.time)
    radar_sw_ver_char7 = radar_stat_group.get_value('SWcharVer7',
                                                    ScaleTime=aeb_track.time)
    radar_sw_ver_char8 = radar_stat_group.get_value('SWcharVer8',
                                                    ScaleTime=aeb_track.time)
    radar_sw_ver = "%s%s%s%s%s%s%s%s" %\
        (chr(radar_sw_ver_char1[0]), chr(radar_sw_ver_char2[0]),
         chr(radar_sw_ver_char3[0]), chr(radar_sw_ver_char4[0]),
         chr(radar_sw_ver_char5[0]), chr(radar_sw_ver_char6[0]),
         chr(radar_sw_ver_char7[0]), chr(radar_sw_ver_char8[0]))

    all_driver_overrides =\
          [('driver override by BP press', bp_pos_on),
           ('driver override by steering', steer_whl_angle_on),
           ('driver override by turn signaling', turn_sig_sw_on),
           ('driver override by AEBS turn off', aebs_main_sw_off)]
    # AP kick-down should always be the last in the list
    all_driver_overrides.append(('driver override by AP kick-down',
                                 ap_kickdown_on))

    title = "AEBS overall test results"
    overall_report = self._create_report(aeb_track.time, title, radar_sw_ver)
    title = "AEBS cascade phase evaluation"
    casc_eval_report = self._create_report(aeb_track.time, title, radar_sw_ver)
    title = "AEBS test types"
    test_type_report = self._create_report(aeb_track.time, title, radar_sw_ver)

    aeb_casc = aebs_phases.warning | aebs_phases.partial_braking | aebs_phases.emergency_braking
    aw_left_obj, aw_right_obj = self._find_alley_way_obj_int(ego, raw_tracks)
    if aw_left_obj and aw_right_obj:
      for l_aw_ints in aw_left_obj.itervalues():
        for r_aw_ints in aw_right_obj.itervalues():
          extended_aw_ints = l_aw_ints.union(r_aw_ints)
          for start, end in extended_aw_ints:
            ttype = self._check_test_type(start, end, test_type_sgn)
            if ttype == "alley way":
              if numpy.any(aeb_casc[start:end]):
                result = 'failed'
              else:
                result = 'passed'
              self._vote_intervals(overall_report, (start, end), result,
                                   comment=ttype)
              self._vote_intervals(test_type_report, (start, end), result,
                                   comment='additional')

    imp_aeb_obj = self._find_impending_aeb_int(ego, raw_tracks)
    if self.algo_name == 'RAIL' and len(imp_aeb_obj) > 1:
      ego_moving = ego.vx >= EGO_SPEED_MIN
      post_filter_mask = cIntervalList.fromMask(aeb_track.time, ego_moving)
      filt_int = post_filter_mask.intersect(imp_aeb_obj)
      imp_aeb_obj = cIntervalList(aeb_track.time,
                                  Intervals=filt_int.findLongestIntervals())
    for imp_start, imp_end in imp_aeb_obj:
      actual_aeb_obj_int = cIntervalList(aeb_track.time,
                                         Intervals=[(imp_start, imp_end)])
      imp_aeb_obj_xbr = actual_aeb_obj_int.intersect(ext_acc_dem_on)
      
      # calculate values needed for ICB evaluation
      if imp_aeb_obj_xbr:
        aeb_xbr_start, aeb_xbr_end = imp_aeb_obj_xbr.findLongestIntervals()[0]
        interval_mid_pos = int((aeb_xbr_start + aeb_xbr_end) / 2)
        xbr_start, xbr_end = ext_acc_dem_on.findInterval(interval_mid_pos)
        actual_xbr_obj_int = cIntervalList(aeb_track.time,
                                           Intervals=[(xbr_start, xbr_end)])
        # in case of standstill reduce the length of impending object interval
        # by the time of the standing still
        after_imp_start = aeb_track.time[imp_start] <= ego.time
        before_imp_end = ego.time < aeb_track.time[imp_end-1]
        ego_stands = ego.vx <= 0.0
        standstill_mask = after_imp_start & before_imp_end & ego_stands
        imp_end_time = aeb_track.time[imp_end - 1]
        try:
          standstill_time = aeb_track.time[numpy.where(standstill_mask)][0]
        except IndexError:
          pass  # no standstill
        else:
          imp_end_time = min(imp_end_time, standstill_time)
        time_diff_imp_xbr = imp_end_time - aeb_track.time[xbr_end-1]
      else:
        actual_xbr_obj_int = None
        time_diff_imp_xbr = None
      
      warn_int = source.compare(aebs_phases.time, aebs_phases.warning,
                                measproc.not_equal, 0)
      warn_int = warn_int.intersect(actual_aeb_obj_int)
      # there could be a second warning phase after emergency brake phase because
      # of the prolongation timer of the warning that should be left out of the
      # evaluation
      if warn_int:
        warn_int = cIntervalList(aebs_phases.time, Intervals=[warn_int[0]])
        part_int = source.compare(aebs_phases.time, aebs_phases.partial_braking,
                                  measproc.not_equal, 0)
        part_int = part_int.intersect(actual_aeb_obj_int)
        emer_int = source.compare(aebs_phases.time, aebs_phases.emergency_braking,
                                  measproc.not_equal, 0)
        emer_int = emer_int.intersect(actual_aeb_obj_int)
        aebs_active_int = warn_int.union(part_int)
        aebs_active_int = aebs_active_int.union(emer_int)
      else:
        warn_int = cIntervalList(aebs_phases.time)
        part_int = cIntervalList(aebs_phases.time)
        emer_int = cIntervalList(aebs_phases.time)
        aebs_active_int = cIntervalList(aebs_phases.time)

      cascade_eval_aspects = self._check_aebs_if_ok(aeb_track, ego, warn_int,
                                                    part_int, emer_int)
      ttype = self._check_test_type(imp_start, imp_end, test_type_sgn)

      if ttype not in ['object cut out', 'alley way', 'driver override', 'exit ICB',
                       'error handler - interface', 'error handler - function']:
        for comment, aspect in cascade_eval_aspects.iteritems():
          result = "passed" if aspect else "failed"
          self._vote_intervals(casc_eval_report, (imp_start, imp_end),
                               result, comment)
      
      if ttype in [None, 'undefined']:
        # ordinary or ARaIL-independent evaluation (test type not set)
        if time_diff_imp_xbr >= -0.5:
          if cascade_eval_aspects['speed red in emer']:
            # no interruption by driver override and speed reduction is sufficient
            if numpy.all(cascade_eval_aspects.values()):
              # legislation requirements for the cascade are all OK
              result = 'passed'
            else:
              result = 'failed'
            self._vote_intervals(overall_report, (imp_start, imp_end), result)
            self._vote_intervals(test_type_report, (imp_start, imp_end),
                                 result, comment=ttype)
          else:
            # crash occurred; check if cascade was interrupted by an override
            for comment, override in all_driver_overrides:
              if actual_aeb_obj_int.intersect(override):
                result = self._eval_driver_override(aebs_active_int,
                                                    override, aebs_state,
                                                    override_blocking_time)
                self._vote_intervals(overall_report, (imp_start, imp_end), result,
                                     comment=comment)
                self._vote_intervals(test_type_report, (imp_start, imp_end),
                                     result, comment=ttype)
                break
        else:
          # in-crash braking occurred
          comment, result = self._eval_icb_exiting(actual_xbr_obj_int,
                                                   ap_kickdown_on)
          self._vote_intervals(overall_report, (imp_start, imp_end), result,
                               comment=comment)
          self._vote_intervals(test_type_report, (imp_start, imp_end),
                               result, comment=ttype)
      else:
        # ARaIL-dependent evaluation (test type is set)
        if ttype in ['homologation - moving', 'homologation - stationary']:
          if numpy.all(cascade_eval_aspects.values()):
            # legislation requirements for the cascade are all OK
            result = 'passed'
          else:
            result = 'failed'
          self._vote_intervals(overall_report, (imp_start, imp_end), result)
          self._vote_intervals(test_type_report, (imp_start, imp_end),
                               result, comment='homologation')
        if ttype in ['object cut in']:
          if numpy.all(cascade_eval_aspects.values()):
            # legislation requirements for the cascade are all OK
            result = 'passed'
          else:
            result = 'failed'
          self._vote_intervals(overall_report, (imp_start, imp_end), result)
          self._vote_intervals(test_type_report, (imp_start, imp_end),
                               result, comment='additional')
        if ttype in ['object cut out']:
          result = 'failed' if aebs_active_int else 'passed'
          self._vote_intervals(overall_report, (imp_start, imp_end), result)
          self._vote_intervals(test_type_report, (imp_start, imp_end),
                               result, comment='additional')
        elif ttype in ['driver override']:
          for comment, override in all_driver_overrides:
            if actual_aeb_obj_int.intersect(override):
              result = self._eval_driver_override(aebs_active_int,
                                                  override, aebs_state,
                                                  override_blocking_time)
              self._vote_intervals(overall_report, (imp_start, imp_end), result,
                                   comment=comment)
              self._vote_intervals(test_type_report, (imp_start, imp_end),
                                   result, comment=ttype)
              break
        elif ttype in ['exit ICB']:
          comment, result = self._eval_icb_exiting(actual_xbr_obj_int,
                                                   ap_kickdown_on)
          self._vote_intervals(overall_report, (imp_start, imp_end), result,
                               comment=comment)
          self._vote_intervals(test_type_report, (imp_start, imp_end),
                               result, comment='additional')
      
      
      
      
      
      
      
      
      
      
#      if imp_aeb_obj_xbr:
#        aeb_xbr_start, aeb_xbr_end = imp_aeb_obj_xbr.findLongestIntervals()[0]
#        interval_mid_pos = int((aeb_xbr_start + aeb_xbr_end) / 2)
#        xbr_start, xbr_end = ext_acc_dem_on.findInterval(interval_mid_pos)
#        actual_xbr_obj_int = cIntervalList(aeb_track.time,
#                                           Intervals=[(xbr_start, xbr_end)])
#
#        # in case of standstill reduce the length of impending object interval
#        # by the time of the standing still
#        after_imp_start = aeb_track.time[imp_start] <= ego.time
#        before_imp_end = ego.time < aeb_track.time[imp_end-1]
#        ego_stands = ego.vx <= 0.0
#        standstill_mask = after_imp_start & before_imp_end & ego_stands
#        imp_end_time = aeb_track.time[imp_end - 1]
#        try:
#          standstill_time = aeb_track.time[numpy.where(standstill_mask)][0]
#        except IndexError:
#          pass  # no standstill
#        else:
#          imp_end_time = min(imp_end_time, standstill_time)
#        time_diff_imp_xbr = imp_end_time - aeb_track.time[xbr_end-1]
#
#        if time_diff_imp_xbr >= -0.5:
#          if ttype not in [None, 'undefined']:
#            if ttype in ['homologation', 'additional']:
#              if numpy.all(cascade_eval_aspects.values()):
#                # legislation requirements for the cascade are all OK
#                result = 'passed'
#              else:
#                result = 'failed'
#              self._vote_intervals(overall_report, (imp_start, imp_end), result)
#              self._vote_intervals(test_type_report, (imp_start, imp_end),
#                                   result, comment=ttype)
#            elif ttype in ['driver override']:
#              for comment, override in all_driver_overrides:
#                if actual_aeb_obj_int.intersect(override):
#                  result = self._eval_driver_override(aebs_active_int,
#                                                      override, aebs_state,
#                                                      override_blocking_time)
#                  self._vote_intervals(overall_report, (imp_start, imp_end), result,
#                                       comment=comment)
#                  self._vote_intervals(test_type_report, (imp_start, imp_end),
#                                       result, comment=ttype)
#                  break
#          else:
#            if cascade_eval_aspects['speed red in emer']:
#              # no interruption by driver override and speed reduction is sufficient
#              if numpy.all(cascade_eval_aspects.values()):
#                # legislation requirements for the cascade are all OK
#                result = 'passed'
#              else:
#                result = 'failed'
#              self._vote_intervals(overall_report, (imp_start, imp_end), result)
#              self._vote_intervals(test_type_report, (imp_start, imp_end),
#                                   result, comment=ttype)
#            else:
#              # crash occurred; check if cascade was interrupted by an override
#              for comment, override in all_driver_overrides:
#                if actual_aeb_obj_int.intersect(override):
#                  result = self._eval_driver_override(aebs_active_int,
#                                                      override, aebs_state,
#                                                      override_blocking_time)
#                  self._vote_intervals(overall_report, (imp_start, imp_end), result,
#                                       comment=comment)
#                  self._vote_intervals(test_type_report, (imp_start, imp_end),
#                                       result, comment=ttype)
#                  break
#        else:
#          # in-crash braking occurred
#          comment, result = self._eval_icb_exiting(actual_xbr_obj_int,
#                                                   ap_kickdown_on)
#          self._vote_intervals(overall_report, (imp_start, imp_end), result,
#                               comment=comment)
#          self._vote_intervals(test_type_report, (imp_start, imp_end),
#                               result, comment=ttype)
#      else:
#        # no XBR brake request on impending AEB track --> test failed
#        self._vote_intervals(overall_report, (imp_start, imp_end), 'failed')
#        self._vote_intervals(test_type_report, (imp_start, imp_end),
#                             'failed', comment=ttype)
    return overall_report, casc_eval_report, test_type_report

  def search(self, overall_report, casc_eval_report, test_type_report):
    batch = self.get_batch()
    tags = ('AEBS',)
    result = self.FAILED if overall_report.isEmpty() else self.PASSED
    batch.add_entry(overall_report, result=result, tags=tags)
    result = self.FAILED if casc_eval_report.isEmpty() else self.PASSED
    batch.add_entry(casc_eval_report, result=result, tags=tags)
    result = self.FAILED if test_type_report.isEmpty() else self.PASSED
    batch.add_entry(test_type_report, result=result, tags=tags)
    return
