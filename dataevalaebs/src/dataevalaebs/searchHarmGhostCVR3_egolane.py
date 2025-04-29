import interface
from searchHarmGhostLRR3_egolane import cHarmGhostLRR3_egolane

DefParam = interface.NullParam

class cSearch(cHarmGhostLRR3_egolane):
  dep = 'fillCVR3_ATS@aebs.fill', 'fillIBEO@aebs.fill'
  SignalGroups = [{'vxvRef': ('ECU', 'evi.General_T20.vxvRef')}]
  pass

