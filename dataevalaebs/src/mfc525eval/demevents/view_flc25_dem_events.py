# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

import logging
import os
import re

import datavis
import interface
import numpy as np
from PySide import QtGui

def_param = interface.NullParam

event_id = ("Dem_EventMemoryPrimary", "MFC5xx_Device_DEM_Dem_EventMemoryPrimaryI%dI_EventId")

messageGroup = {}
for m in xrange(30):
		fullName = event_id[1] % m
		shortName = event_id[1].split('_')[-1] + "{}".format(m)
		messageGroup[shortName] = (event_id[0], fullName)

logger = logging.getLogger('view_flc25_dem_events')


class View(interface.iView):
		def selectFile(self, File):
				self.SelectedFile, = File
				return

		def check(self):
				self.SelectedFile = ""
				Dialog = QtGui.QFileDialog()
				Dir = os.path.dirname(self.source.FileName)
				Dialog.setDirectory(Dir)
				Dialog.setFileMode(QtGui.QFileDialog.AnyFile)
				Dialog.filesSelected.connect(self.selectFile)
				Dialog.exec_()
				a2l_file_path = self.SelectedFile

				if not os.path.exists(a2l_file_path) or not a2l_file_path.endswith(".a2l"):
						logger.critical("a2l file is missing at path. Please selct correct file.")
						raise ValueError("missing a2l dependency file")

				group = self.source.selectSignalGroup([messageGroup])
				# Read a2l file, prepare dict for corresponding descriptions
				event_data = {}
				with open(a2l_file_path) as infile:
						start_flag = False
						for line in infile:
								result = re.search(r"TAB_VERB 520", line)
								if result:
										start_flag = True
										continue
								if start_flag:
										result1 = re.search(r"/end COMPU_VTAB", line)
										if result1:
												break
										else:
												event_ = re.sub('\s+', ' ', line).strip().split()
												event_data[event_[0]] = event_[1].lstrip('"').rstrip('"')
				return group, event_data

		def fill(self, group, event_data):
				return  group, event_data

		def view(self, param, group, event_data):
				client00 = datavis.cListNavigator(title = "FLC25 DEM Events")
				self.sync.addClient(client00)
				object_ids = []
				for i in range(len(group)):
						time00, value00 = group.get_signal("EventId{}".format(i))
						object_ids.append(value00)

						dem_event = object_ids[i]
						try:
								if object_ids[i][0] == 0: #This might have some meaning
										event_id = hex(0)
										description = ""
								else:
										event_id = hex(object_ids[i][0])
										description = event_data[str(object_ids[i][0])]

						except:
								event_id = hex(object_ids[i][0])
								description = ""
								logger.info("Missing event name in a2l file for an event id: {}".format(object_ids[i][0]))

						# dem_event[object_ids[i] == event_id] = description
						dem_event = np.where(dem_event == object_ids[i][0], description, 'U')
						client00.addsignal(str(i) + " : " + event_id, (time00, dem_event), groupname = "Event ID; Event Name", bg = '#FFFFE0')

				return
