import interface
import measproc
from aebs.par import grouptypes

import searchFoV_AC100_Target

param = interface.NullParam

class cSearch(searchFoV_AC100_Target.cSearch):
  dep = 'fillCVR3_LOC@aebs.fill',
  title = 'CVR3 FoV based on locations'
  ZERO_EPS = 1e-3
  R_SPLIT = 110
  ANGLE_STD_FILTER = 4

