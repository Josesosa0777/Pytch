# -*- dataeval: init -*-

import datavis
from interface import iView

#def_param = interface.NullParam


ACTL_sig =[
  {
 "ACTL":  ("MFC5xx Device.ACTL.EcuOmc_FreezeData","MFC5xx_Device_ACTL_EcuOmc_FreezeData_Status_CurrentState_u_StateId"),
  },
]

class View(iView):
  def check(self):
    # select signals
    group = self.source.selectLazySignalGroup(ACTL_sig)
    # # give warning for not available signals
    for alias in ACTL_sig[0]:
      if alias not in group:
        self.logger.warning("Signal for '%s' not available" % alias)

    return group

  def view(self, group):
    if "ACTL" in group:
        pn = datavis.cPlotNavigator(title="ACTL States")
        mapping_actl ={0: 'e_Orphan' , 1: 'OPMODE_STARTUP_IU', 3:'OPMODE_INFRASTRUCTURE_RUNNING',
                       4:'OPMODE_LIMITED_START',5:'LIMITED_ERROR_HANDLER',6:'VIDEOPROC_ON',
                       7:'OPMODE_NORMAL',
                       8:'STARTUP_IMGPROC',9:'DPU_APPL_LOADING',10:'DPU_INITIALIZATION',
                       11:'IMAGE_PENDING',12:'GS_CONFIRM_PENDING',
                       13:'LIMITED_FATAL_ERROR',14:'LIMITED_DPU_DEG',15:'LIMITED_DPUBOOT_ERROR',
                       16:'FUNCTION_OFF',17:'SENSOR_NOT_CALIBRATED',
                       18:'IDLE_PENDING',19:'IDLE_REQUESTED',
                       20:'SENSOR_MISALIGNED',21:'CALIBRATION',22:'EOL',
                       23:'ACAL',24:'GS_RESET'}

        axis00 = pn.addAxis(ylabel='ACTL', yticks=mapping_actl, ylim=(min(mapping_actl) - 1.0, max(mapping_actl) + 1.0))


        time_ACTL, value_ACTL, unit_ACTL = group.get_signal_with_unit("ACTL")
        pn.addSignal2Axis(axis00, "ACTL", time_ACTL, value_ACTL, unit=unit_ACTL)
        self.sync.addClient(pn)
    return
