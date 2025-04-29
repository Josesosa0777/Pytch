# -*- dataeval: init -*-
from collections import namedtuple, OrderedDict

from scipy.integrate import trapz

from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report
from aebs.labeling.track import labelMovState, labelAssoState,\
                                labelCmSystemStatus
from aebs.fill.calc_bendix_acc_activity import Calc as AccCalc
from aebs.fill.calc_bendix_cmt_warning import Calc as CmtCalc
from aebs.fill.calc_bendix_umo import Calc as UmoCalc
from aebs.fill.calc_bendix_stat_obj_alert import Calc as StatCalc

init_params = OrderedDict([
  ('cmt',
   dict(warning='calc_bendix_cmt_warning@aebs.fill', algo='2-AEB warning',
        target='fill_flr20_aeb_track@aebs.fill')),
  ('acc',
   dict(warning='calc_bendix_acc_activity@aebs.fill', algo='3-ACC activity',
        target='fill_flr20_acc_track@aebs.fill')),
  ('stat',
   dict(warning='calc_bendix_stat_obj_alert@aebs.fill',
        algo='4-Stationary object alert',
        target='fill_flr20_aeb_track@aebs.fill')),
  ('umo',
   dict(warning='calc_bendix_umo@aebs.fill', algo='9-UMO candidate qualified',
        target='fill_flr20_aeb_track@aebs.fill')),
  ('ldw',
   dict(warning='calc_bendix_ldw@aebs.fill', algo='13-LDW',
        target='fill_flr20_aeb_track@aebs.fill')),
  ('tsr',
   dict(warning='calc_bendix_tsr@aebs.fill', algo='14-TSR warning',
        target='fill_flr20_aeb_track@aebs.fill')),
])

class Search(iSearch):
  def init(self, warning, algo, target):
    Dep = namedtuple('Dep', ['ego', 'target', 'warning']) # Redmine #2009
    self.dep = Dep('calc_flr20_egomotion@aebs.fill', target, warning)
    OptDep = namedtuple('OptDep', ['lane'])
    self.optdep = OptDep('calc_flc20_lanes@aebs.fill')
    self.algo = algo
    return

  def check(self):
    sgs = [{
      "cm_system_status" : ("General_radar_status", "cm_system_status"),
      "XBR_AccelDemand":  ("XBRUS_2A", "XBRUS_AccelDemand_2A"),
      'XBR_ControlMode':  ('XBRUS_2A', 'XBRUS_ControlMode_2A'),
      'ttc': ('General_radar_status', 'ttc_cw'),
#      'gps_long': ('InternalGPS', 'GPS_x'),
#      'gps_lat': ('InternalGPS', 'GPS_y'),
#      'gps_alt': ('InternalGPS', 'GPS_z'),
    }]
    group = self.get_source().selectSignalGroup(sgs)
    return group

  def fill(self, group):
    modules = self.get_modules()
    t, warnings = modules.fill(self.dep.warning)
    intervals = cIntervalList.fromMask(t, warnings)

    egomotion = modules.fill(self.dep.ego).rescale(t)

    aeb = modules.fill(self.dep.target).rescale(t)
    
    if self.optdep.lane in self.passed_optdep:
      lanes = modules.fill(self.optdep.lane).rescale(t) # Redmine #2009
    else:
      lanes = None

    cm_system_status = group.get_value('cm_system_status', ScaleTime=t)
    accel_demand = group.get_value('XBR_AccelDemand', ScaleTime=t)
    ctrl_mode = group.get_value('XBR_ControlMode', ScaleTime=t)
    ttc = group.get_value('ttc', ScaleTime=t)
#    gps_lat = group.get_value('gps_lat', ScaleTime=t)
#    gps_long = group.get_value('gps_long', ScaleTime=t)
#    gps_alt = group.get_value('gps_alt', ScaleTime=t)


    ego_quas = 'ego vehicle'
    target_quas = 'target'
    lane_quas = 'lane' # Redmine #2009
    intervantion_quas = 'intervention'
    event_votes = 'Bendix event'
    moving_votes = 'moving state'
    asso_votes = 'asso state'
    cm_status_votes = 'cm system status'

    batch = self.get_batch()
    votes = batch.get_labelgroups(event_votes, moving_votes, asso_votes,
                                  cm_status_votes)
    quas = batch.get_quanamegroups(ego_quas, target_quas, intervantion_quas, lane_quas) # Redmine #2009
    report = Report(intervals, 'Bendix-event', votes=votes, names=quas)

    for idx, (start, end) in report.iterIntervalsWithId():
      report.vote(idx, event_votes, self.algo)
      report.set(idx, ego_quas, 'speed start', egomotion.vx[start])
      report.set(idx, ego_quas, 'speed end', egomotion.vx[end-1])
#      report.set(idx, ego_quas, 'gps lat start', gps_lat[start])
#      report.set(idx, ego_quas, 'gps long start', gps_long[start])
#      report.set(idx, ego_quas, 'gps alt start', gps_alt[start])
      report.set(idx, target_quas, 'dx start', aeb.dx[start])
      report.set(idx, target_quas, 'vx start', aeb.vx[start])
      report.set(idx, target_quas, 'ttc min', ttc[start])
      ### # Redmine #2009
      if lanes is not None:
        report.set(idx, lane_quas, 'left line view range start', lanes.left_line.view_range[start])
        report.set(idx, lane_quas, 'right line view range start', lanes.right_line.view_range[start])
      ###

      slicer = slice(start, end)
      mask = ctrl_mode[slicer] == AccCalc.CTRL_MODE
      masked_accel_demand = accel_demand[slicer][mask]
      speed_red = trapz(masked_accel_demand, t[slicer][mask])
      report.set(idx, intervantion_quas, 'speed reduction', speed_red)
      if masked_accel_demand.size:
        min_accel_demand = masked_accel_demand.min()
      else:
        min_accel_demand = float('nan')
      report.set(idx, intervantion_quas, 'accel demand min', min_accel_demand)

      labelMovState(report, idx, aeb, (start, start+1), wholetime=False)
      labelAssoState(report, idx, aeb, (start, start+1), wholetime=False)
      labelCmSystemStatus(report, idx, cm_system_status, (start, end))
    return report

  def search(self, report):
    self.get_batch().add_entry(report)
    return
