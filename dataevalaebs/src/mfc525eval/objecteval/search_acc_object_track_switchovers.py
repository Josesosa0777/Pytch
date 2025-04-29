# -*- dataeval: init -*-

"""
:Name:
	search_flc25_object_track_switchovers.py
:Type:
	Search script

:Full Path:
	dataevalaebs/src/mfc525eval/objecteval/search_flc25_object_track_switchovers.py

:Sensors:
	FLC25(CEM_TPF)

:Short Description:
	Continental MFC525 Camera is used for detection of objects in front of vehicles.
	MFC525 stores detected objects in object arrays[Maximum 100] internally with IDs 0-99.
	These IDs are automatically assigned to the detected objects by continental camera software.
	KB functions are highly dependent upon object IDs. So changing object IDs while vehicle is
	running for same detected object can hamper ACC or other main functions. So idea is to
	find out scenarios where same physical object ID changes it ID.

:Large Description:
	Usage:
		- Find out scenarios where same physical object ID changes it ID
		- Stores all such events in the database

:Dependencies:
	- calc_flc25_object_track_switchovers@aebs.fill

:Output Data Image/s:
	.. image:: ../images/search_flc25_object_track_switchovers_1.png

:Event:
	FLC25 Event

:Event Labels:
	Object Track Switchover

:Event Values:
	Previous Object ID
	Previous Object Values (vx, vx_abs, dx, dy)
	New Object ID
	New Object Values (vx, vx_abs, dx, dy)

.. note::
	For source code click on [source] tag beside functions
"""
from interface.Interfaces import iSearch
from measproc.IntervalList import cIntervalList, maskToIntervals
from measproc.report2 import Report


class Search(iSearch):
		dep = {
				'track_switchovers': "calc_acc_object_track_switchovers@aebs.fill"
		}

		def fill(self):
				time, track_switchovers = self.modules.fill(self.dep['track_switchovers'])
				votes = self.batch.get_labelgroups('FLC25 events', 'FLC25 CEM TPF Old ID', 'FLC25 CEM TPF New ID')
				report = Report(cIntervalList(time), 'FLC25 events', votes = votes)
				batch = self.get_batch()

				qua_group = 'FLC25 Object SwitchOver check'
				quas = batch.get_quanamegroup(qua_group)
				report.setNames(qua_group, quas)

				intervals = track_switchovers.keys()
				jumps = [[start] for start, end in intervals]

				for jump, interval in zip(jumps, intervals):
						data = track_switchovers[interval]
						idx = report.addInterval(interval)
						report.vote(idx, 'FLC25 events', "Object Track SwitchOver")
						report.vote(idx, 'FLC25 CEM TPF Old ID', str(data[0][0]))
						report.vote(idx, 'FLC25 CEM TPF New ID', str(data[1][0]))
						report.set(idx, qua_group, 'Old Track End(vx)', data[0][4])
						report.set(idx, qua_group, 'Old Track End(vx_abs)', data[0][5])
						report.set(idx, qua_group, 'Old Track End(dx)', data[0][6])
						report.set(idx, qua_group, 'Old Track End(dy)', data[0][7])

						report.set(idx, qua_group, 'New Track St(vx)', data[1][4])
						report.set(idx, qua_group, 'New Track St(vx_abs)', data[1][5])
						report.set(idx, qua_group, 'New Track St(dx)', data[1][6])
						report.set(idx, qua_group, 'New Track St(dy)', data[1][7])
				return report

		def search(self, report):
				self.batch.add_entry(report)
				return
