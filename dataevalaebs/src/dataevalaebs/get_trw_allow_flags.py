# -*- dataeval: init -*-

from interface.Interfaces import iCalc

class Calc(iCalc):
  def check(self):
    groups = [{
      'cm_allow_entry_global_conditions': ('ACC_S03','cm_allow_entry_global_conditions'),
      'cm_cancel_global_conditions': ('ACC_S03','cm_cancel_global_conditions'),
      'cw_allow_entry': ('ACC_S03','cw_allow_entry'),
      'cw_cancel': ('ACC_S03','cw_cancel'),
      'cmb_allow_entry': ('ACC_S03','cmb_allow_entry'),
      'cmb_cancel': ('ACC_S03','cmb_cancel'),
    }]
    group = self.get_source().selectSignalGroup(groups)
    return group

