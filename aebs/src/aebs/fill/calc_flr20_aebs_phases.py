# -*- dataeval: init -*-
import numpy

import interface
from primitives.aebs import AebsPhases
from measparser.signalproc import rescale

init_params = {
  'radar': dict(
    sgn_group=[{'AEBSState': ('AEBS1_2A', 'AEBSState_2A'),
                'CollisionWarningLevel': ('AEBS1_2A', 'CollisionWarningLevel_2A')},
               {'AEBSState': ('AEBS1_2A', 'AEBS1_AEBSState_2A'),
                'CollisionWarningLevel': ('AEBS1_2A', 'AEBS1_ColisionWarningLevel_2A')},
               {'AEBSState': ('AEBS1_2A', 'AEBS1_AEBSState_2A'),
                'CollisionWarningLevel': ('AEBS1_2A', 'AEBS1_CollisionWarningLevel_2A')},
               {'AEBSState': ('AEBS1_2A', 'AEBS1_AEBSState_2A_C1'),
                'CollisionWarningLevel': ('AEBS1_2A', 'AEBS1_CollWarningLevel_2A_C1'),},]),
  'autobox': dict(
    sgn_group=[{'AEBSState': ('AEBS1_FD', 'AEBSState_FD'),
                'CollisionWarningLevel': ('AEBS1_FD', 'CollisionWarningLevel_FD')},]),
  'wabco': dict(
    sgn_group=[{'AEBSState': ('AEBS1', 'AEBS_St'),
                'CollisionWarningLevel': ('AEBS1', 'CollWarnSt')},]),
  'rail': dict(
    sgn_group=[{'AEBSState': ('AEBS1', 'Adv_Emergency_Braking_Sys_State'),
                'CollisionWarningLevel': ('AEBS1', 'Collision_Warning_Status')},
               {'AEBSState': ('AEBS1_2A', 'AEBS1_AEBSState_2A'),
                'CollisionWarningLevel': ('AEBS1_2A', 'AEBS1_CollisionWarningLevel_2A')},]),
  'continental': dict(
    sgn_group=[{'AEBSState': ('AEBS1_2A', 'AEBS1_AEBSState_2A_C3'),
                'CollisionWarningLevel': ('AEBS1_2A', 'AEBS1_CollWarningLevel_2A_C3')}, ]),
}


def _wabco_hack_needed(source):
  ENABLE_HACK_FOR_DAF_WABCO = True
  return ENABLE_HACK_FOR_DAF_WABCO and "DAF_Wabco" in source.FileName


class Calc(interface.iCalc):
  WARNING = 5
  PARTIAL = 6
  EMERGENCY = 7
  IN_CRASH = 6
  def init(self, sgn_group):
    self.sgn_group = sgn_group
    self.group = None  # used by user scripts
    if _wabco_hack_needed(self.source):
      self.optdep = {'ego': 'calc_egomotion'}
    return

  def check(self):
    self.group = self.source.selectLazySignalGroup(self.sgn_group).items()
    group = self.source.selectSignalGroup(self.sgn_group)
    time, status = group.get_signal('AEBSState')
    level = group.get_value('CollisionWarningLevel', ScaleTime=time)
    return time, status, level

  def fill(self, time, status, level):
    in_crash_level = level == self.IN_CRASH
    warning = status == self.WARNING
    if _wabco_hack_needed(self.source):
      # ignore warnings during standstill (if possible)
      if self.optdep['ego'] in self.passed_optdep:
        ego = self.modules.fill(self.optdep['ego'])
        _, ego_vx = rescale(ego.time, ego.vx, time)
        warning &= (ego_vx > 1.0)
    partial = status == self.PARTIAL
    emergency = status == self.EMERGENCY
    emergency[in_crash_level] = False
    in_crash = (status == self.EMERGENCY) & in_crash_level

    acoustical = numpy.zeros_like(warning)
    optical = numpy.zeros_like(warning)

    phases = AebsPhases(
      time,
      warning, partial, emergency, in_crash,
      acoustical, optical
    )
    return phases
