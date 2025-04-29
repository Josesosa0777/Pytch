# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList

sgs = [{},]

class Search(iSearch):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def search(self, group):
    return
