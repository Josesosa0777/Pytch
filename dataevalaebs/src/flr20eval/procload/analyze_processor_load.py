# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface

def_param = interface.NullParam

class Analyze(interface.iAnalyze):
  def analyze(self, Param):
    entries = self.batch.filter(class_name='dataevalaebs.search_proc_load.Search', title='proc load')
    self.interval_table.addEntries(entries)
    return

