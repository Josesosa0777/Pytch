# -*- dataeval: method -*-
# -*- coding: utf-8 -*-
from dmw.SignalFilters import *
import interface
import numpy as np

def_param = interface.NullParam

sgs = [{}, ]

class View(interface.iView):
    def check(self):
        group = self.source.selectSignalGroupOrEmpty(sgs)
        return group

    def fill(self, group):
        return group

    def view(self, param, group):
        return
