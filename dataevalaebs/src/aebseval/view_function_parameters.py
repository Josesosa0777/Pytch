# -*- dataeval: init -*-
import time

import interface
import datavis
import logging

logger = logging.getLogger("view_function_parameters")

init_params = {
		"AEBS_PARAM": dict(id=dict(aebs_param=True)),
		"ACC_PARAM": dict(id=dict(acc_param=True)),
		"PAEBS_PARAM": dict(id=dict(paebs_param=True)),
		"AOA_PARAM": dict(id=dict(aoa_param=True)),
		"HBA_PARAM": dict(id=dict(hba_param=True)),
		"IM_PARAM": dict(id=dict(im_param=True)),
		"OM_PARAM": dict(id=dict(om_param=True)),
		"TSR_PARAM": dict(id=dict(tsr_param=True)),
		"LK_PARAM": dict(id=dict(lk_param=True)),
}

aebs_sgs = []
acc_sgs = []
paebs_sgs = []
aoa_sgs = []
hba_sgs = []
im_sgs = []
om_sgs = []
tsr_sgs = []
lk_sgs = []


class View(interface.iView):
		def init(self, id):
				self.id = id
				return

		def check(self):
				if self.id.get("aebs_param"):
						signal_group = {}
						try:
								device_name = 'MTSI_stKBFreeze_100ms_t'
								for key, val in self.source.Parser.view_signal_list[device_name].items():
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AebsParams_" in key:
												signal_group[str(key)] = (device_name, str(key))
						except:
								device_name = 'MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t'
								for signal_name in self.source.Parser.iterSignalNames(device_name):
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AebsParams_" in signal_name:
												signal_group[str(signal_name)] = (device_name,str(signal_name) )
						aebs_sgs.append(signal_group)
						group = self.source.selectSignalGroupOrEmpty(aebs_sgs)
						return group
				elif self.id.get("acc_param"):
						signal_group = {}
						try:
								device_name = 'MTSI_stKBFreeze_100ms_t'
								for key, val in self.source.Parser.view_signal_list[device_name].items():
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AccParams_" in key:
												signal_group[str(key)] = (device_name, str(key))
						except:
								device_name = 'MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t'
								for signal_name in self.source.Parser.iterSignalNames(device_name):
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AccParams_" in signal_name:
												signal_group[str(signal_name)] = (device_name, str(signal_name))
						acc_sgs.append(signal_group)
						group = self.source.selectSignalGroupOrEmpty(acc_sgs)
						return group
				elif self.id.get("paebs_param"):
						signal_group = {}
						try:
								device_name = 'MTSI_stKBFreeze_100ms_t'
								for key, val in self.source.Parser.view_signal_list[device_name].items():
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_" in key:
												signal_group[str(key)] = (device_name, str(key))
						except:
								device_name = 'MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t'
								for signal_name in self.source.Parser.iterSignalNames(device_name):
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_" in signal_name:
												signal_group[str(signal_name)] = (device_name, str(signal_name))
						paebs_sgs.append(signal_group)
						group = self.source.selectSignalGroupOrEmpty(paebs_sgs)
						return group

				elif self.id.get("aoa_param"):
						signal_group = {}
						try:
								device_name = 'MTSI_stKBFreeze_100ms_t'
								for key, val in self.source.Parser.view_signal_list[device_name].items():
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_" in key:
												signal_group[str(key)] = (device_name, str(key))
						except:
								device_name = 'MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t'
								for signal_name in self.source.Parser.iterSignalNames(device_name):
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_" in signal_name:
												signal_group[str(signal_name)] = (device_name, str(signal_name))
						aoa_sgs.append(signal_group)
						group = self.source.selectSignalGroupOrEmpty(aoa_sgs)
						return group
				elif self.id.get("hba_param"):
						signal_group = {}
						try:
								device_name = 'MTSI_stKBFreeze_100ms_t'
								for key, val in self.source.Parser.view_signal_list[device_name].items():
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_HbaParams_" in key:
												signal_group[str(key)] = (device_name, str(key))
						except:
								device_name = 'MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t'
								for signal_name in self.source.Parser.iterSignalNames(device_name):
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_HbaParams_" in signal_name:
												signal_group[str(signal_name)] = (device_name, str(signal_name))
						hba_sgs.append(signal_group)
						group = self.source.selectSignalGroupOrEmpty(hba_sgs)
						return group
				elif self.id.get("im_param"):
						signal_group = {}
						try:
								device_name = 'MTSI_stKBFreeze_100ms_t'
								for key, val in self.source.Parser.view_signal_list[device_name].items():
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_" in key:
												signal_group[str(key)] = (device_name, str(key))
						except:
								device_name = 'MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t'
								for signal_name in self.source.Parser.iterSignalNames(device_name):
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_" in signal_name:
												signal_group[str(signal_name)] = (device_name, str(signal_name))
						im_sgs.append(signal_group)
						group = self.source.selectSignalGroupOrEmpty(im_sgs)
						return group
				elif self.id.get("om_param"):
						signal_group = {}
						try:
								device_name = 'MTSI_stKBFreeze_100ms_t'
								for key, val in self.source.Parser.view_signal_list[device_name].items():
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_OmParams_" in key:
												signal_group[str(key)] = (device_name, str(key))
						except:
								device_name = 'MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t'
								for signal_name in self.source.Parser.iterSignalNames(device_name):
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_OmParams_" in signal_name:
												signal_group[str(signal_name)] = (device_name, str(signal_name))
						om_sgs.append(signal_group)
						group = self.source.selectSignalGroupOrEmpty(om_sgs)
						return group
				elif self.id.get("tsr_param"):
						signal_group = {}
						try:
								device_name = 'MTSI_stKBFreeze_100ms_t'
								for key, val in self.source.Parser.view_signal_list[device_name].items():
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_TsrParams_" in key:
												signal_group[str(key)] = (device_name, str(key))
						except:
								device_name = 'MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t'
								for signal_name in self.source.Parser.iterSignalNames(device_name):
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_TsrParams_" in signal_name:
												signal_group[str(signal_name)] = (device_name, str(signal_name))
						tsr_sgs.append(signal_group)
						group = self.source.selectSignalGroupOrEmpty(tsr_sgs)
						return group
				elif self.id.get("lk_param"):
						signal_group = {}
						try:
								device_name = 'MTSI_stKBFreeze_100ms_t'
								for key, val in self.source.Parser.view_signal_list[device_name].items():
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkParams_" in key:
												signal_group[str(key)] = (device_name, str(key))
						except:
								device_name = 'MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t'
								for signal_name in self.source.Parser.iterSignalNames(device_name):
										if "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkParams_" in signal_name:
												signal_group[str(signal_name)] = (device_name, str(signal_name))
						lk_sgs.append(signal_group)
						group = self.source.selectSignalGroupOrEmpty(lk_sgs)
						return group


		def view(self, group):
				if self.id.get("aebs_param"):
						client00 = datavis.cListNavigator(title="AEBS Parameters")
						self.sync.addClient(client00)
						for key, value in group.iteritems():
								if key in group:
										time00, value00 = group.get_signal(key)
										client00.addsignal(key, (time00, value00), groupname="Default")
								else:
										logger.warning("Missing signal: {}".format(key))
						return
				elif self.id.get("acc_param"):
						client00 = datavis.cListNavigator(title="ACC Parameters")
						self.sync.addClient(client00)
						for key, value in group.iteritems():
								if key in group:
										time00, value00 = group.get_signal(key)
										client00.addsignal(key, (time00, value00), groupname="Default")
								else:
										logger.warning("Missing signal: {}".format(key))
						return
				elif self.id.get("paebs_param"):
						client00 = datavis.cListNavigator(title="PAEBS Parameters")
						self.sync.addClient(client00)
						for key, value in group.iteritems():
								if key in group:
										time00, value00 = group.get_signal(key)
										client00.addsignal(key, (time00, value00), groupname="Default")
								else:
										logger.warning("Missing signal: {}".format(key))
						return
				elif self.id.get("aoa_param"):
						client00 = datavis.cListNavigator(title="AOA Parameters")
						self.sync.addClient(client00)
						for key, value in group.iteritems():
								if key in group:
										time00, value00 = group.get_signal(key)
										client00.addsignal(key, (time00, value00), groupname="Default")
								else:
										logger.warning("Missing signal: {}".format(key))
						return
				elif self.id.get("hba_param"):
						client00 = datavis.cListNavigator(title="HBA Parameters")
						self.sync.addClient(client00)
						for key, value in group.iteritems():
								if key in group:
										time00, value00 = group.get_signal(key)
										client00.addsignal(key, (time00, value00), groupname="Default")
								else:
										logger.warning("Missing signal: {}".format(key))
						return
				elif self.id.get("im_param"):
						client00 = datavis.cListNavigator(title="IM Parameters")
						self.sync.addClient(client00)
						for key, value in group.iteritems():
								if key in group:
										time00, value00 = group.get_signal(key)
										client00.addsignal(key, (time00, value00), groupname="Default")
								else:
										logger.warning("Missing signal: {}".format(key))
						return
				elif self.id.get("om_param"):
						client00 = datavis.cListNavigator(title="OM Parameters")
						self.sync.addClient(client00)
						for key, value in group.iteritems():
								if key in group:
										time00, value00 = group.get_signal(key)
										client00.addsignal(key, (time00, value00), groupname="Default")
								else:
										logger.warning("Missing signal: {}".format(key))
						return
				elif self.id.get("tsr_param"):
						client00 = datavis.cListNavigator(title="TSR Parameters")
						self.sync.addClient(client00)
						for key, value in group.iteritems():
								if key in group:
										time00, value00 = group.get_signal(key)
										client00.addsignal(key, (time00, value00), groupname="Default")
								else:
										logger.warning("Missing signal: {}".format(key))
						return
				elif self.id.get("lk_param"):
						client00 = datavis.cListNavigator(title="LK Parameters")
						self.sync.addClient(client00)
						for key, value in group.iteritems():
								if key in group:
										time00, value00 = group.get_signal(key)
										client00.addsignal(key, (time00, value00), groupname="Default")
								else:
										logger.warning("Missing signal: {}".format(key))
						return

