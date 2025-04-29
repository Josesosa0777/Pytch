# -*- dataeval: call -*-

import numpy as np

import datavis
import interface
from view_asso_cvr3_objectpairs import cView
from view_asso_cvr3_objectpairs import cParameter, call_params # used for scan

class ViewAssoFlr20pairs(cView):
  dep = 'calc_asso_flr20@aebs.fill',

  def check(self):
    modules = self.get_modules()
    a = modules.fill('calc_asso_flr20@aebs.fill')
    # print '1-1 violations:', a.scaleTime[ a.get_1to1_violations() ]
    return a
