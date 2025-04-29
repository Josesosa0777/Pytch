# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import interface
import numpy as np
import datavis
def_param = interface.NullParam

sgs  = [
{
  "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas", "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState"),
  "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas", "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state"),
  "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas", "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state"),
  "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus": ("MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_StateOutputIfMeas", "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus"),
},
]

class View(interface.iView):
  def check(self):
    group = self.source.selectSignalGroupOrEmpty(sgs)
    return group

  def fill(self, group):
    return group

  def view(self, param, group):
    client00 = datavis.cPlotNavigator(title="FLC25 CEM States")
    self.sync.addClient(client00)
    mapping = {0: 'FAILED', 1: 'DEGRADED',2: 'AVAILABLE'}
    mapping_cem = {0: 'OFF', 1: 'INIT',2: 'NORMAL',3: 'FAILURE'}
    mapping_eSig = {0: 'AL_SIG_STATE_INIT',1: 'AL_SIG_STATE_OK',2: 'AL_SIG_STATE_INVALID'}
    axis00 = client00.addAxis(ylabel='SensorState',yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
    time_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state, value_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state, unit_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state = group.get_signal_with_unit("MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state")
    client00.addSignal2Axis(axis00, "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state", time_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state, value_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state, unit=unit_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorCamera_state)
    time_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state, value_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state, unit_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state = group.get_signal_with_unit("MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state")
    client00.addSignal2Axis(axis00, "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state", time_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state, value_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state, unit=unit_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sensorRadar_state)
    axis01 = client00.addAxis(ylabel='CemState',yticks=mapping_cem, ylim=(min(mapping_cem) - 0.5, max(mapping_cem) + 0.5))
    time_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState, value_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState, unit_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState = group.get_signal_with_unit("MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState")
    client00.addSignal2Axis(axis01, "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState", time_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState, value_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState, unit=unit_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_CemState)
    axis02 = client00.addAxis(ylabel='eSigState',yticks=mapping_eSig, ylim=(min(mapping_eSig) - 0.5, max(mapping_eSig) + 0.5))
    time_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus, value_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus, unit_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus = group.get_signal_with_unit("MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus")
    client00.addSignal2Axis(axis02, "MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus", time_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus, value_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus, unit=unit_MFC5xx_Device_CEM_FDP_KB_CEM_FDP_KB_M_p_StateOutputIfMeas_sSigHeader_eSigStatus)
    return
