import interface
from measproc.Object import getObjects

import searchAEBSWarnEval_CVR2Warnings

DefParam = interface.NullParam

cvr3DeviceNames = ('MRR1plus', 'RadarFC')

class cSearch(searchAEBSWarnEval_CVR2Warnings.cSearch):
  sensorSignalGroups = []
  onlineWarningGroups = []
  for device in cvr3DeviceNames:
    sensorSignalGroup = {
      "vx_ego": (device, "evi.General_TC.vxvRef"),
      "ax_ego": (device, "evi.General_TC.axvRef"),
      "ay_ego": (device, "evi.General_TC.ayvRef"),
      "YR_ego": (device, "evi.General_TC.psiDtOpt"),
    }
    sensorSignalGroups.append(sensorSignalGroup)
    onlineWarningGroup = {
      "repPreStatus": (device, "repprew.__b_Rep.__b_RepBase.status"),
    }
    onlineWarningGroups.append(onlineWarningGroup)

  canSignalGroups = [
    {
      "BPAct_b":   ("EBC1_2Wab_EBS5Knorr", "EBS_Brake_switch"),
      "GPPos_uw":  ("EEC2",                "AP_position"),
    },
    {
      "BPAct_b":   ("EBC1_2Wab_EBS5Knorr", "EBS_Brake_switch"),
      "GPPos_uw":  ("EEC2-8CF00300",       "AP_position"),
    },
  ]

  dep = 'fillCVR3_POS@aebs.fill', 'fillCVR3_FUS@aebs.fill'

  sensor = 'CVR3'
  s1Label = 'SameLane_near'
  cipvIndexDefault = 1
  cipvIndexKBAvoidance = 6
  test_name = 'CVR3 Warning'

  def get_intros1_mask(self, objects):
    pos_obj, = getObjects(objects, label=self.s1Label)
    intro_obj, = getObjects(objects, label='Intro')
    mask = intro_obj['id'] == pos_obj['id']
    return mask

